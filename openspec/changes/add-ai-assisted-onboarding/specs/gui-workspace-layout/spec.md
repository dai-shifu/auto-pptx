## MODIFIED Requirements

### Requirement: Fixed controls surround a resizable workspace

The GUI SHALL keep file selection and Sheet settings above the workspace and only the generation button and status below it. The GUI SHALL NOT provide a separate preflight report or share summary. At all supported window sizes, including 1000×600, these controls SHALL remain visible and usable while the middle workspace absorbs available height changes.

#### Scenario: Window is reduced to its minimum size

- **WHEN** the user reduces the window from its initial size to 1000×600
- **THEN** file selection, Sheet settings, the generation button, and status remain visible, with no other bottom-bar action
- **AND** the workspace resizes without pushing those controls outside the window

#### Scenario: Window first opens

- **WHEN** the application starts
- **THEN** its initial size SHALL be 1600×950 where the screen has enough space
- **AND** the application SHALL reduce the initial size on smaller screens, while retaining the 1000×600 minimum
