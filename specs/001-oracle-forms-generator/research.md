# Research: Oracle Forms YAML-to-XML Generator

## Decisions

### Python pipeline and dependency boundary

- **Decision**: Use Python 3, PyYAML, the standard-library `xml.etree.ElementTree`, and pytest. Keep Oracle Forms utilities and the AI repair provider outside the required runtime dependencies.
- **Rationale**: These choices are explicit in the feature request. ElementTree avoids adding an XML runtime dependency, while PyYAML provides the required YAML input support. Optional external tools must not block XML generation and validation.
- **Alternatives considered**: Building XML as strings was rejected because it risks escaping errors and loss of template structure. Making Oracle or AI packages mandatory was rejected because those installations are not present or specified in the repository.

### YAML loading and validation

- **Decision**: Load YAML with PyYAML's safe loader, then apply explicit structural and semantic validation before any generation or output publication.
- **Rationale**: Safe loading avoids constructing arbitrary Python objects from input. A distinct validation module makes the constitution's validation-before-generation gate testable.
- **Alternatives considered**: Directly reading values from an unchecked YAML mapping was rejected because malformed or incomplete input could create partial artifacts.

### XML generation and preservation

- **Decision**: Parse a genuine Oracle Forms 14.1.2 XML export with ElementTree, locate its existing target form, field, and button nodes, and update only the configured names and labels on a staged tree. Preserve unrelated elements and namespaces; never serialize over the source template.
- **Rationale**: Updating the exported objects in place minimizes assumptions about Oracle's proprietary XML structure and preserves unrelated nodes. The original template remains an immutable input.
- **Alternatives considered**: Building an Oracle Forms document from scratch was rejected because it would not be grounded in the supported export format. Guessing XML element names without a real export was rejected.
- **Validation prerequisite**: `adapters/oracle-forms/templates/hello_world.xml` is currently empty. Implementation must replace it with a verified Oracle Forms 14.1.2 export before defining selectors or claiming Oracle compatibility. Tests must verify the actual export's namespace and preservation behavior.

### Output, report, and error retention

- **Decision**: Create a unique run directory below `generated/oracle-forms/` before validation. Store the JSON report and error log there for both successful and failed runs; publish XML only after it passes validation. Store a converted FMB in the same run directory as a separate file.
- **Rationale**: Unique run directories preserve prior output and diagnostics. Staging prevents an invalid candidate from appearing as a successful result. A missing Oracle converter is represented as unavailable while a valid XML result remains successful.
- **Alternatives considered**: Reusing one fixed output path was rejected because a later run could erase prior logs or partially replace a valid form.

### Oracle XML-to-FMB integration

- **Decision**: Define the converter as a configured external process in `plugin.yaml`, with an executable and argument list containing explicit input/output placeholders. Detect whether the configured executable can run; invoke without a shell; record unavailable, success, or failure in the report.
- **Rationale**: The repository contains no Oracle Forms command name, installation path, environment-variable contract, or conversion script. Configuration avoids hard-coding an unverified command and lets each licensed Forms 14.1.2 installation supply its supported invocation.
- **Alternatives considered**: Hard-coding a remembered utility name or assuming it is on `PATH` was rejected because the current repository provides no version-specific evidence. Requiring Oracle tools for every run was rejected because XML generation is independently useful.
- **Remaining environment dependency**: To exercise FMB conversion, an operator must configure the command and test it against their Oracle Forms 14.1.2 installation. No command name is asserted by this plan.

### Test orchestration and AI repair

- **Decision**: Keep pytest invocation in `test_runner.py`, called explicitly by development/CI and after every AI repair mutation. Keep AI repair in `repair_loop.py` behind a provider-neutral callable configured separately. Permit no more than three repair attempts; each attempt is followed by validation and the regression suite.
- **Rationale**: Separate responsibilities make generation deterministic and keep pytest output and AI changes auditable. A provider-neutral boundary satisfies the AI-repair requirement without selecting a vendor or requiring credentials for non-repair workflows.
- **Alternatives considered**: Embedding pytest process control in XML generation was rejected because it couples product behavior to development tests. Unbounded repair or a direct AI dependency was rejected by the constitution and the unspecified provider.

## Risks and Mitigations

- **Oracle XML compatibility cannot be established with the empty template**: Treat a genuine Forms 14.1.2 export as an implementation gate; add round-trip and non-target-object preservation tests against it.
- **ElementTree serialization can normalize prefixes or formatting**: Validate namespace handling and semantic object preservation with the genuine template. Do not require byte-for-byte equality of generated XML formatting; require the original template file itself to remain unchanged.
- **Converter invocation differs by installation**: Keep executable and argument construction configurable, avoid shell interpolation, and use a fake converter in default tests.
- **AI-generated edits can damage unrelated content**: Restrict repair to a staged generated candidate, revalidate after each attempt, retain diffs/logs, and stop after the third failed attempt.