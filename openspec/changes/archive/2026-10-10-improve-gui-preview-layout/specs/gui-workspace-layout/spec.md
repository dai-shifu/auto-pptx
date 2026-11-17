## ADDED Requirements

### Requirement: Fixed controls surround a resizable workspace

The GUI SHALL keep file selection and Sheet settings above the workspace and the generation button and status below it. At all supported window sizes, including 1000×600, these controls SHALL remain visible and usable while the middle workspace absorbs available height changes.

#### Scenario: Window is reduced to its minimum size

- **WHEN** the user reduces the window from 1400×850 to 1000×600
- **THEN** file selection, Sheet settings, the generation button, and status remain visible
- **AND** the workspace resizes without pushing those controls outside the window

### Requirement: Preview and mapping panes have an adjustable height boundary

The workspace SHALL contain vertically arranged preview and mapping panes separated by a draggable divider. The initial layout SHALL allocate approximately 70% of workspace height to the preview. The preview pane SHALL retain at least 180px height and the mapping pane at least 100px, including their local controls, during resizing and divider dragging at supported window sizes.

#### Scenario: User adjusts the divider

- **WHEN** the user drags the divider to give mapping configuration more height
- **THEN** mapping configuration grows and the preview shrinks within the same workspace
- **AND** neither pane crosses its minimum height and the generation controls remain visible

#### Scenario: Window resizes after a divider adjustment

- **WHEN** the user resizes the window after adjusting the divider
- **THEN** the layout preserves the adjusted pane proportion where minimum heights allow it
- **AND** both pane minimum heights are enforced when space is reduced

### Requirement: Mapping configuration scrolls independently

The mapping pane SHALL bound its content to its assigned height and provide independent vertical scrolling when mapping items exceed that height. Mapping items SHALL adapt their arrangement to the available pane width, with no more than four items per row, and SHALL remain operable at the minimum supported window width.

#### Scenario: Many Excel headers create many mapping items

- **WHEN** the Sheet contains enough headers to exceed the mapping pane's visible height
- **THEN** the user can scroll within the mapping pane to reach the last mapping item
- **AND** the content does not increase the workspace's outer height or hide the preview or generation button

#### Scenario: Mapping pane width changes

- **WHEN** the window width decreases and four mapping items no longer fit in one row
- **THEN** mapping items reflow into fewer columns
- **AND** existing mapping choices remain unchanged and each mapping control remains usable

#### Scenario: Mouse wheel scrolling is scoped to the active region

- **WHEN** the user scrolls over mapping content and then over the preview
- **THEN** each wheel action scrolls the corresponding region only
- **AND** mapping combobox interactions retain their existing behavior

### Requirement: Layout changes preserve application state

Window resizing, divider dragging, column resizing by the layout, and mapping-item reflow SHALL preserve checked Excel row identifiers, explicit mapping choices, and the selected template column. Generation SHALL continue to use the full stored data and existing Excel-column-to-placeholder mapping direction.

#### Scenario: Selected rows and mappings survive layout changes

- **WHEN** the user checks rows, changes a mapping, and then resizes the window and moves the divider
- **THEN** the same Excel row identifiers remain checked and the mapping and template-column selections remain unchanged
- **AND** generation receives the same selected rows and mapping as before the layout adjustment
