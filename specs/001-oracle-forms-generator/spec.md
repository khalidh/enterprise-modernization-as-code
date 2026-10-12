### Business Rules

- **BR-001**: Each configured field MUST have a name, label, and supported type before it can be generated.
- **BR-002**: Field and button names MUST be valid Oracle Forms identifiers and MUST be unique across the fields and buttons in the form.
- **BR-003**: A field type MUST be either `text` or `number`; unsupported types MUST be rejected before XML generation.
- **BR-004**: A field MAY map to a database column different from its form-object name. If no column is configured, the field-object name is used as the column name.
- **BR-005**: A text field MAY specify a maximum length, which MUST be a positive integer. When omitted, the compatible template prototype supplies the default length.
- **BR-006**: Configured field and button labels MUST be applied to their corresponding form objects and preserved in the generated output.

### Key Entities *(include if data involved)*
# Feature Specification: Oracle Forms YAML-to-XML Generator

**Feature Branch**: `001-oracle-forms-generator`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Create an MVP plugin that transforms `customer.yaml` into Oracle Forms XML for a `HELLO_WORLD` form with a `NOM_CLIENT` field and `BTN_BONJOUR` button, supports YAML-driven names and labels, validates the generated XML, reports errors in JSON, and converts XML to FMB when Oracle tools are available.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate the HELLO_WORLD Form (Priority: P1)

As a form developer, I provide a valid customer model and obtain an Oracle Forms XML form based on the supplied Oracle Forms 14.1.2 template, so I can review and use the generated form.

**Why this priority**: Generating the required form is the core value of the MVP.

**Independent Test**: Provide a valid model for the MVP and verify that one XML output is produced, is well formed, contains the expected form, field, and button, and leaves the original template unchanged.

**Acceptance Scenarios**:

1. **Given** a valid model and an available Oracle Forms 14.1.2 XML template, **When** the user runs the generator, **Then** it produces a well-formed XML form named `HELLO_WORLD` containing a field named `NOM_CLIENT` and a button named `BTN_BONJOUR`.
2. **Given** a generation run, **When** it completes, **Then** the original template and any source FMB remain unchanged.

### User Story 2 - Customize Object Names and Labels (Priority: P2)

As a form developer, I can change the supported object names and labels in the customer model and have those values reflected in the generated form, so the output matches the customer-specific form definition.

**Why this priority**: YAML-driven customization makes the generator reusable beyond a single hard-coded example.

**Independent Test**: Change the field and button names and labels in a valid model, generate the form, and compare the corresponding XML object values with the model.

**Acceptance Scenarios**:

1. **Given** a valid model with customized field and button names and labels, **When** the user generates XML, **Then** each supported name and label in the output matches its model value.
2. **Given** a valid model with the MVP names `NOM_CLIENT` and `BTN_BONJOUR`, **When** the user generates XML, **Then** those names appear on the corresponding field and button rather than being assigned to another object type.

### User Story 3 - Diagnose Invalid Input and Output (Priority: P2)

As a form developer, I receive a machine-readable explanation when the model is invalid or the generated XML fails validation, so I can correct the input without accepting a broken form.

**Why this priority**: Clear validation and error reporting prevent malformed or misleading output from being used.

**Independent Test**: Submit malformed YAML, a model missing required values, and a case that produces invalid XML; verify each failure is reported in JSON and no invalid XML is accepted as successful output.

**Acceptance Scenarios**:

1. **Given** malformed YAML or a missing required model value, **When** the user runs generation, **Then** generation stops before producing XML and a JSON error report identifies the failure.
2. **Given** XML that is not well formed or does not contain the required objects, **When** output validation runs, **Then** the run is reported as failed in JSON and its error details remain available in the error log.
3. **Given** a successful generation and validation, **When** the user inspects the JSON report, **Then** it reports success and contains no errors.

### User Story 4 - Convert XML to FMB When Oracle Tools Are Available (Priority: P3)

As a form developer with the required Oracle conversion tools available, I can convert the validated XML to an FMB file, so I can continue in the Oracle Forms environment.

**Why this priority**: FMB conversion completes the downstream workflow but depends on tools that may not be installed in every environment.

**Independent Test**: With Oracle conversion tools available, convert a valid generated XML file and verify that a separate FMB output is produced successfully; without those tools, verify that conversion is reported as unavailable rather than successful.

**Acceptance Scenarios**:

1. **Given** valid generated XML and available Oracle conversion tools, **When** conversion runs, **Then** it succeeds and writes the FMB output separately from any source FMB.
2. **Given** valid generated XML and unavailable Oracle conversion tools, **When** the workflow checks conversion, **Then** it clearly reports that conversion could not be run while retaining the XML validation result.

### Edge Cases

- The YAML file is missing, empty, malformed, or contains unsupported structure; generation stops and reports the input error in JSON.
- A required form, object name, or label is absent or empty; validation identifies the missing value before XML generation.
- A configured name or label contains characters requiring XML escaping; the generated XML remains well formed and preserves the intended text.
- The XML template is missing or is not the required Oracle Forms 14.1.2 export; generation stops without changing the template or source FMB.
- XML generation succeeds but XML validation fails; the output is not reported as successful, and error details are retained.
- Oracle conversion tools are unavailable; XML generation and validation remain independently usable, and FMB conversion is reported as skipped or unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The plugin MUST accept `customer.yaml` as the MVP form model and MUST validate its syntax and required values before generating output.
- **FR-002**: The plugin MUST generate an Oracle Forms XML form named `HELLO_WORLD` from a template exported by Oracle Forms 14.1.2.
- **FR-003**: The MVP output MUST include a field named `NOM_CLIENT` and a button named `BTN_BONJOUR` as distinct Oracle Forms objects.
- **FR-004**: Supported form and object names and labels MUST be configurable through the YAML model and MUST appear on their corresponding generated objects.
- **FR-005**: The plugin MUST preserve the original XML template and source FMB; generated XML and any converted FMB MUST be written as separate outputs.
- **FR-006**: The plugin MUST validate generated XML for well-formedness and the presence and names of the required objects before reporting success.
- **FR-007**: The plugin MUST produce a JSON report for each run that states success or failure and provides an error collection with a description and source location when available.
- **FR-008**: The plugin MUST retain error logs for input, generation, XML validation, test, and conversion failures so users can diagnose unsuccessful runs.
- **FR-009**: The feature MUST include an automated regression test suite covering valid generation, YAML-driven customization, invalid input, XML validation, required objects, template preservation, and error reporting.
- **FR-010**: When Oracle conversion tools are available, the plugin MUST support conversion of validated XML to a separate FMB output and report whether conversion succeeded; when unavailable, it MUST report conversion as unavailable without invalidating successful XML generation and validation.
- **FR-011**: The automated regression suite MUST run after each code or generated-artifact modification, and automatic correction MUST stop after no more than three attempts for one generation operation.

### Key Entities *(include if feature involves data)*

- **Customer model**: The YAML-provided form definition, including the form name and supported object names and labels.
- **Form object**: A named Oracle Forms element, including the MVP form, field, and button, with its configured label where applicable.
- **XML template**: The original Oracle Forms 14.1.2-exported XML document used as the generation baseline and preserved unchanged.
- **Generated form**: The separate XML output containing the configured form objects and validated before success is reported.
- **Run report**: The JSON result describing generation, validation, and optional conversion status, including errors when present.
- **Error log**: Retained diagnostic details for failures during validation, generation, tests, or conversion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All valid MVP model cases in the acceptance suite produce well-formed XML containing exactly one `HELLO_WORLD` form, one `NOM_CLIENT` field, and one `BTN_BONJOUR` button.
- **SC-002**: In 100% of customization cases in the acceptance suite, generated object names and labels match the corresponding YAML values.
- **SC-003**: In 100% of invalid-input and invalid-output cases in the acceptance suite, the run reports failure in JSON, identifies the error, and does not report invalid XML as successful.
- **SC-004**: After every acceptance-suite generation case, the original XML template and any supplied source FMB remain unchanged.
- **SC-005**: When Oracle conversion tools are available, every conversion acceptance case produces a separate FMB output successfully; when unavailable, the report identifies the conversion as unavailable.
- **SC-006**: The automated regression suite passes after the final change, and every failed run retains its diagnostic log.

## Assumptions

- The MVP handles one form per input model and supports one field and one button; additional object types and multiple forms are out of scope.
- The YAML model supplies labels for the form objects; no default label text is prescribed by this specification.
- The existing project template is an Oracle Forms 14.1.2 export. If it is missing or its provenance cannot be established, generation must fail rather than silently use another template.
- Oracle conversion utilities may not be installed. Their absence prevents only XML-to-FMB conversion, not XML generation or XML validation.
- The requested automated regression suite will use pytest; the suite's required behaviors are specified here without depending on a particular test implementation.
