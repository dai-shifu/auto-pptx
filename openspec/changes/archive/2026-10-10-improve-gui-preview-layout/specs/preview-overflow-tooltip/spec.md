## ADDED Requirements

### Requirement: Tooltips reveal content that does not fit the preview

The GUI SHALL show a tooltip after approximately 400ms of continuous hovering over a data cell or heading whose full text is not visible. It SHALL determine overflow using the actual display font and available text width, and SHALL also recognize hidden multiline content. Checkbox cells, empty values, and fully visible content SHALL NOT trigger a tooltip.

#### Scenario: Long data value is clipped by the column width

- **WHEN** a cell's text is wider than its available text area and the pointer remains over that cell for the hover delay
- **THEN** a tooltip shows the complete original cell value
- **AND** the stored Treeview value and generation data remain unchanged

#### Scenario: Heading text does not fit

- **WHEN** the pointer remains over a clipped heading for the hover delay
- **THEN** the tooltip shows the complete column heading using the heading's overflow measurement

#### Scenario: Content is fully visible or empty

- **WHEN** the pointer remains over a fully visible value, an empty cell, or the checkbox column
- **THEN** no tooltip is shown

#### Scenario: Cell contains hidden lines

- **WHEN** a cell contains multiple lines but the row displays only part of those lines
- **THEN** hovering for the delay reveals the complete multiline value

### Requirement: Tooltips fit the screen and retain complete content

The tooltip SHALL wrap long text and stay within the available screen area. If the complete text exceeds the constrained tooltip height, the tooltip SHALL allow its content to be scrolled. Moving from the source cell into the tooltip SHALL keep it available for reading and scrolling; leaving both SHALL dismiss it.

#### Scenario: Very long value is hovered near the screen edge

- **WHEN** the user hovers over a clipped value near a screen edge whose full text exceeds the tooltip's available area
- **THEN** the tooltip is positioned within the screen, wraps the text, and allows access to all remaining content by scrolling

### Requirement: Tooltip lifecycle follows preview changes

The GUI SHALL maintain at most one visible tooltip and one pending hover callback. Moving to a different target, leaving the target and tooltip, clicking in the preview, scrolling the preview, changing column widths, moving the workspace divider, refreshing preview data, or closing the application SHALL dismiss the old tooltip and cancel obsolete callbacks. Newly shown tooltips SHALL refer only to the current valid target.

#### Scenario: Pointer moves before the hover delay expires

- **WHEN** the pointer leaves one cell and enters another before the delay expires
- **THEN** the first cell's pending tooltip is canceled
- **AND** only the new target can trigger a tooltip after its own hover delay

#### Scenario: Data refresh invalidates the hovered row

- **WHEN** a Sheet or template-column change rebuilds the preview while a tooltip is visible or pending
- **THEN** the tooltip is dismissed and the pending callback is canceled
- **AND** no stale text is shown and no callback accesses the deleted row

#### Scenario: Scrolling or resizing changes the hovered geometry

- **WHEN** the preview scrolls, the column widths change, or the workspace divider moves
- **THEN** the visible tooltip and pending callback are cleared

#### Scenario: Application closes with a pending tooltip

- **WHEN** the window is destroyed with a visible or pending tooltip
- **THEN** the tooltip window and scheduled callback are cleaned up without accessing destroyed widgets

### Requirement: Hover processing is independent of total preview rows

The GUI SHALL evaluate overflow only for the hovered target and reuse the tooltip window. Repeated pointer-motion events within the same target SHALL NOT scan the full preview or continuously restart the hover delay.

#### Scenario: Hovering a preview containing 300 rows

- **WHEN** the user moves the pointer within one clipped cell in a 300-row preview
- **THEN** the hover delay can complete and tooltip processing examines only that target
- **AND** no per-row or per-cell tooltip windows are created
