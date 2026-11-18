## MODIFIED Requirements

### Requirement: Tooltips fit the screen and retain complete content

The tooltip SHALL wrap long text and stay within the available screen area. If the complete text exceeds the constrained tooltip height, the tooltip SHALL allow its content to be scrolled. Moving from the source cell into the tooltip SHALL keep it available for reading and scrolling; leaving both SHALL dismiss it. These behaviors SHALL hold on Windows and Linux after the window is mapped and its layout has settled, both on first display and when the same tooltip window is reused.

#### Scenario: Very long value is hovered near the screen edge

- **WHEN** the user hovers over a clipped value near a screen edge whose full text exceeds the tooltip's available area
- **THEN** the tooltip is positioned within the screen, wraps the text, and allows access to all remaining content by scrolling

#### Scenario: First long tooltip scrolls to its final content

- **WHEN** a long tooltip is first displayed and its mapped layout has settled
- **THEN** scrolling to the bottom exposes the final content without truncation
- **AND** the complete original value remains available

#### Scenario: Pointer crosses into the mapped tooltip

- **WHEN** the pointer moves from the source cell into the actual mapped tooltip and remains there beyond the dismissal delay
- **THEN** the tooltip remains available for reading and scrolling
- **AND** leaving both the source target and tooltip dismisses it

## ADDED Requirements

### Requirement: Short tooltips use their settled content height

For clipped content that fits within the available tooltip height, the GUI SHALL size the tooltip to its wrapped content and padding using the actual display font and mapped text width, and SHALL hide the vertical scrollbar. The GUI SHALL NOT retain the maximum tooltip height merely because the text widget had not received its final width when measured. This requirement SHALL apply on Windows and Linux without prescribing a fixed pixel height across fonts, screen sizes or scaling settings.

#### Scenario: Short clipped value is shown for the first time

- **WHEN** a short clipped value is first displayed and the mapped tooltip layout has settled
- **THEN** the tooltip height fits the wrapped content and padding
- **AND** the vertical scrollbar is hidden and the full value is retained

#### Scenario: A tooltip window is reused for different content lengths

- **WHEN** the same tooltip window is used for short, long and then short content
- **THEN** each settled layout reflects its current content
- **AND** the long value can be scrolled while the short values use compact heights without a vertical scrollbar
