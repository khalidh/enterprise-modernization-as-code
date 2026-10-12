<!--
Sync Impact Report
Version change: none -> 1.0.0 (initial constitution)
Modified principles: none; established five initial principles
Added sections: Oracle Forms Constraints; Development Workflow
Removed sections: none
Follow-up TODOs: confirm the original ratification date
-->

# Enterprise Modernization as Code Constitution

## Core Principles

### I. Oracle Forms 14.1.2 Template Compatibility
The Oracle Forms generator MUST use an XML template exported by Oracle Forms 14.1.2 as its generation baseline. Generated artifacts MUST remain compatible with that template's structure and conventions.

### II. Preserve Unrelated Objects
Generation and repair MUST preserve all Oracle Forms objects that are outside the requested change. A change MUST be limited to the objects explicitly covered by the input model and feature requirements.

### III. Source FMB Immutability
The generator MUST NOT modify, overwrite, or delete the source FMB file. Generated or repaired output MUST be written separately so the original binary source remains intact.

### IV. Validate Inputs Before Generation
The YAML model MUST be parsed and validated against the expected structure and constraints before generation begins. Invalid YAML or model data MUST stop generation and produce an actionable error; generation MUST NOT proceed with invalid input.

### V. Test-Gated, Bounded, and Auditable Changes
The applicable test suite MUST run after every modification. Automatic repair MUST stop after at most three attempts for a given generation operation. Error logs MUST be retained for diagnosis, including when generation, validation, tests, or repair fail.

## Oracle Forms Constraints

- The Oracle Forms 14.1.2 exported XML template is the authoritative baseline for generated XML.
- Source FMB files are read-only inputs; output MUST use a distinct path.
- Preservation checks MUST cover non-target objects, not only the generated target object.
- YAML validation MUST complete successfully before any output is generated or modified.

## Development Workflow

- Run the relevant tests after each code or generated-artifact modification and address failures before proceeding.
- Keep automatic repair attempts bounded to three; a failed third attempt MUST leave the error logs available and report failure rather than silently accepting output.
- Retain error logs across retries and make them available when validation, generation, or tests fail.
- Reviews and releases MUST verify compliance with every core principle and constraint in this constitution.

## Governance

This constitution governs design, implementation, generation, repair, and validation of the Oracle Forms generator. Amendments MUST be reviewed, documented, and reflected in this file. Each amendment MUST update the version and last-amended date. Version changes follow semantic versioning: MAJOR for incompatible governance changes, MINOR for new or materially expanded principles or constraints, and PATCH for clarifications that do not change requirements. Every change to generated behavior or its validation MUST be reviewed against the principles above. Non-compliance MUST be corrected before the change is accepted; any exception requires an explicit amendment to this constitution.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date not provided | **Last Amended**: 2026-10-09
