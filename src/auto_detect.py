from dataclasses import dataclass

from pptx import Presentation
from pptx.slide import Slide

from .pptx_engine import PLACEHOLDER_RE, iter_replaceable_text_frames
from .template_matching import build_template_index


@dataclass(frozen=True)
class MappingConflict:
    """An automatic mapping that was left unresolved to avoid ambiguity."""

    placeholder: str
    candidates: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class MappingSuggestionResult:
    """Detailed placeholder-to-column suggestions and their conflicts."""

    mapping: dict[str, str | None]
    conflicts: tuple[MappingConflict, ...]


@dataclass(frozen=True)
class TemplateColumnCandidate:
    header: str
    matches: int
    token_count: int


@dataclass(frozen=True)
class DetectionResult:
    """Detailed result for template-column and placeholder detection."""

    template_column: str | None
    mapping: dict[str, str]
    conflicts: tuple[MappingConflict, ...]
    template_candidates: tuple[TemplateColumnCandidate, ...] = ()


@dataclass(frozen=True)
class TemplateMetadata:
    """PPT-derived detection inputs that are safe to cache independently."""

    template_names: tuple[str, ...]
    placeholders: tuple[str, ...]


def tokenize_template_value(value: str) -> list[str]:
    """Split a template cell value into its non-empty slash-delimited names."""
    return [token.strip() for token in str(value).split("/") if token.strip()]


def _template_column_scores(
    headers: list[str], rows: list[list[str]], tpl_names: set[str]
) -> list[tuple[float, int, int]]:
    """Return ``(match ratio, match count, token count)`` for each column."""
    scores: list[tuple[float, int, int]] = []
    for col_idx, _header in enumerate(headers):
        tokens = {
            token
            for row in rows
            if col_idx < len(row) and row[col_idx]
            for token in tokenize_template_value(row[col_idx])
        }
        matches = len(tokens & tpl_names)
        ratio = matches / len(tokens) if tokens else 0.0
        scores.append((ratio, matches, len(tokens)))
    return scores


def _best_template_columns(
    headers: list[str], rows: list[list[str]], tpl_names: set[str]
) -> tuple[TemplateColumnCandidate, ...]:
    scores = _template_column_scores(headers, rows, tpl_names)
    best_score = max(((ratio, matches) for ratio, matches, _ in scores), default=(0.0, 0))
    return tuple(
        TemplateColumnCandidate(header, matches, total)
        for header, (ratio, matches, total) in zip(headers, scores)
        if matches and (ratio, matches) == best_score
    )


def detect_template_column(
    headers: list[str], rows: list[list[str]], tpl_names: set[str]
) -> str | None:
    """Detect the first column with the best score."""
    candidates = _best_template_columns(headers, rows, tpl_names)
    return candidates[0].header if candidates else None


def suggest_mapping_detailed(
    excel_columns: list[str], placeholders: list[str]
) -> MappingSuggestionResult:
    """Suggest a deterministic, one-to-one placeholder-to-column mapping.

    Exact case-insensitive matches are resolved before fuzzy matches. Equal
    candidates and placeholders competing for the same column are deliberately
    left unresolved and surfaced as conflicts.
    """
    ordered_placeholders = list(dict.fromkeys(placeholders))
    mapping: dict[str, str | None] = {
        placeholder: None for placeholder in ordered_placeholders
    }
    conflicts: list[MappingConflict] = []
    used_column_indexes: set[int] = set()
    conflicted_placeholders: set[str] = set()

    # Pass 1: resolve only mutually unique exact pairs so input order never
    # decides which of two claimants silently wins.
    exact_by_placeholder: dict[str, list[int]] = {}
    for placeholder in ordered_placeholders:
        exact_by_placeholder[placeholder] = [
            index
            for index, column in enumerate(excel_columns)
            if column.casefold() == placeholder.casefold()
        ]

    exact_claimants: dict[int, list[str]] = {}
    for placeholder, indexes in exact_by_placeholder.items():
        for index in indexes:
            exact_claimants.setdefault(index, []).append(placeholder)

    for placeholder in ordered_placeholders:
        indexes = exact_by_placeholder[placeholder]
        if not indexes:
            continue
        if len(indexes) > 1:
            conflicts.append(
                MappingConflict(
                    placeholder,
                    tuple(excel_columns[index] for index in indexes),
                    "equal_exact_candidates",
                )
            )
            conflicted_placeholders.add(placeholder)
            continue

        index = indexes[0]
        if len(exact_claimants[index]) > 1:
            conflicts.append(
                MappingConflict(
                    placeholder,
                    (excel_columns[index],),
                    "competing_placeholders",
                )
            )
            conflicted_placeholders.add(placeholder)
            continue

        mapping[placeholder] = excel_columns[index]
        used_column_indexes.add(index)

    # Pass 2: each remaining placeholder proposes its unique best fuzzy match.
    fuzzy_proposals: dict[str, tuple[int, int]] = {}
    for placeholder in ordered_placeholders:
        if mapping[placeholder] is not None or placeholder in conflicted_placeholders:
            continue
        distances = [
            (_levenshtein(column.casefold(), placeholder.casefold()), index)
            for index, column in enumerate(excel_columns)
            if index not in used_column_indexes
        ]
        eligible = [(distance, index) for distance, index in distances if distance <= 2]
        if not eligible:
            continue

        best_distance = min(distance for distance, _index in eligible)
        best_indexes = [
            index for distance, index in eligible if distance == best_distance
        ]
        if len(best_indexes) > 1:
            conflicts.append(
                MappingConflict(
                    placeholder,
                    tuple(excel_columns[index] for index in best_indexes),
                    "equal_fuzzy_candidates",
                )
            )
            conflicted_placeholders.add(placeholder)
            continue
        fuzzy_proposals[placeholder] = (best_distance, best_indexes[0])

    proposals_by_column: dict[int, list[tuple[str, int]]] = {}
    for placeholder, (distance, index) in fuzzy_proposals.items():
        proposals_by_column.setdefault(index, []).append((placeholder, distance))

    for index, proposals in proposals_by_column.items():
        best_distance = min(distance for _placeholder, distance in proposals)
        winners = [
            placeholder
            for placeholder, distance in proposals
            if distance == best_distance
        ]
        if len(winners) == 1:
            mapping[winners[0]] = excel_columns[index]

        for placeholder, _distance in proposals:
            if mapping[placeholder] is None:
                conflicts.append(
                    MappingConflict(
                        placeholder,
                        (excel_columns[index],),
                        "competing_placeholders",
                    )
                )

    return MappingSuggestionResult(mapping, tuple(conflicts))


def suggest_mapping(
    excel_columns: list[str], placeholders: list[str]
) -> dict[str, str | None]:
    """Return compatible placeholder-to-column suggestions without diagnostics."""
    return suggest_mapping_detailed(excel_columns, placeholders).mapping


def _levenshtein(a: str, b: str) -> int:
    """Calculate the Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            insert = prev[j + 1] + 1
            delete = curr[j] + 1
            substitute = prev[j] + (0 if ca == cb else 1)
            curr.append(min(insert, delete, substitute))
        prev = curr

    return prev[-1]


def detect_and_suggest_detailed(
    prs: Presentation, headers: list[str], rows: list[list[str]]
) -> DetectionResult:
    """Detect the template column and return mapping conflict diagnostics."""
    return detect_from_metadata(analyze_template(prs), headers, rows)


def analyze_template(prs: Presentation) -> TemplateMetadata:
    """Extract the ordered PPT-only metadata used by automatic detection."""
    return TemplateMetadata(
        template_names=tuple(build_template_index(prs)),
        placeholders=tuple(collect_placeholders(prs)),
    )


def detect_from_metadata(
    metadata: TemplateMetadata, headers: list[str], rows: list[list[str]]
) -> DetectionResult:
    """Run Excel-dependent detection against reusable template metadata."""
    candidates = _best_template_columns(headers, rows, set(metadata.template_names))
    template_col = candidates[0].header if candidates else None
    suggested = suggest_mapping_detailed(headers, list(metadata.placeholders))
    mapping = {
        excel_col: placeholder
        for placeholder, excel_col in suggested.mapping.items()
        if excel_col is not None
    }
    return DetectionResult(template_col, mapping, suggested.conflicts, candidates)


def detect_and_suggest(
    prs: Presentation, headers: list[str], rows: list[list[str]]
) -> tuple[str | None, dict[str, str]]:
    """Return the compatible ``(template_column, excel-to-placeholder mapping)``."""
    result = detect_and_suggest_detailed(prs, headers, rows)
    return result.template_column, result.mapping


def collect_slide_placeholders(slide: Slide) -> list[str]:
    """Collect unique placeholders that can be replaced on this slide."""
    names: dict[str, None] = {}
    for frame in iter_replaceable_text_frames(slide):
        for paragraph in frame.paragraphs:
            text = "".join(run.text for run in paragraph.runs)
            for match in PLACEHOLDER_RE.finditer(text):
                names[match.group(1)] = None
    return list(names)


def collect_placeholders(prs: Presentation) -> list[str]:
    """Collect unique placeholders in first-seen template order."""
    return list(dict.fromkeys(
        name for slide in prs.slides for name in collect_slide_placeholders(slide)
    ))


def detect_header_row(tpl_names: set[str], rows: list[list[str]]) -> int:
    """Detect a header row from valid headers and downstream template evidence.

    Up to the first five rows are considered. A candidate needs at least two
    unique, non-empty headers and positive template-column evidence below it.
    Row 1 is the stable fallback when no candidate has such evidence.
    """
    best_row = 1
    best_score: tuple[float, int] | None = None

    for index, candidate in enumerate(rows[:5]):
        headers = [str(cell).strip() for cell in candidate]
        non_empty = [header for header in headers if header]
        normalized = [header.casefold() for header in non_empty]
        if len(non_empty) < 2 or len(set(normalized)) != len(normalized):
            continue

        scores = _template_column_scores(headers, rows[index + 1 :], tpl_names)
        evidence = max(
            ((ratio, matches) for ratio, matches, _total in scores),
            default=(0.0, 0),
        )
        if evidence[1] == 0:
            continue
        if best_score is None or evidence > best_score:
            best_score = evidence
            best_row = index + 1

    return best_row
