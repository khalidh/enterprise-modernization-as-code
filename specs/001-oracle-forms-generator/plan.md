# Implementation Plan: Oracle Forms YAML-to-XML Generator

**Branch**: `001-oracle-forms-generator` | **Date**: 2026-10-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-oracle-forms-generator/spec.md`

## Summary

Build a Python plugin pipeline that safely loads and validates `customer.yaml`, edits only the designated form, field, and button nodes in an Oracle Forms 14.1.2 XML export using `xml.etree.ElementTree`, validates the result, and writes per-run artifacts under `generated/oracle-forms/`. Keep generation, XML validation, pytest orchestration, Oracle conversion, and AI repair in separate modules. Make Oracle conversion and AI repair configurable capabilities; retain JSON reports and error logs for every run.

## Technical Context

**Language/Version**: Python 3; develop and verify in the repository's Python 3.13.15 environment; no compatibility claim below Python 3.11.

**Primary Dependencies**: PyYAML for safe YAML parsing; `xml.etree.ElementTree` from the Python standard library for XML tree manipulation; pytest for regression tests. Oracle Forms conversion utilities are optional external tools.

**Storage**: Local files only. Inputs and the original template remain in their source locations; reports, logs, generated XML, and optional FMB outputs are stored under `generated/oracle-forms/`.

**Testing**: pytest, launched and captured through a dedicated test-runner module. Converter tests use a fake executable by default and do not require an Oracle installation.

**Target Platform**: Python 3 on the project development platform. The optional Oracle conversion process must run in an environment supported by the installed Oracle Forms 14.1.2 tools.

**Project Type**: Local Python plugin/adapter with a command-line orchestration entry point.

**Performance Goals**: No latency target for the MVP; one small form is processed per run.

**Constraints**: Use the genuine Oracle Forms 14.1.2 export as the XML baseline; never modify the original XML template or source FMB; validate YAML before generation; preserve non-target XML subtrees; retain per-run JSON and error logs; run pytest after each code or generated-artifact change; stop AI repair after at most three attempts.

**Scale/Scope**: One `HELLO_WORLD` form per model with one field and one button; one XML result and optionally one converted FMB per run.

## Constitution Check

**Pre-design gate: PASS**

- Template compatibility: generation edits a real Forms 14.1.2 export; the repository's current template file is empty, so obtaining and verifying the export is a prerequisite to implementation.
- Preservation and FMB immutability: edit only target nodes in a parsed copy; never write to the template or source FMB paths.
- Input validation: safely parse and validate the full YAML model before creating generated XML.
- Test-gated changes: keep pytest orchestration independent and run it after each code or generated-artifact modification.
- Bounded, auditable repair: AI repair is isolated, limited to three attempts, and retains reports and logs.

No constitution exception is required. Oracle tool availability is an optional integration condition, not a reason to weaken XML generation or validation.

## Project Structure

### Documentation (this feature)

```text
specs/001-oracle-forms-generator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── customer-model.md
│   ├── plugin-config.md
│   └── run-report.schema.json
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
adapters/oracle-forms/
├── plugin.yaml
├── generator/
│   ├── generate.py          # Template-based XML generation only
│   ├── validate.py          # YAML and generated XML validation
│   ├── orchestrate.py       # Per-run pipeline and artifact publication
│   ├── test_runner.py       # pytest process orchestration and test logs
│   ├── oracle_converter.py  # Configured optional XML-to-FMB process
│   └── repair_loop.py       # Provider-neutral, bounded AI repair
└── templates/
	└── hello_world.xml      # Genuine Oracle Forms 14.1.2 export
agents/forms-repair/SKILL.md
model/customer.yaml
generated/oracle-forms/<form>/<run-id>/
tests/test_oracle_forms.py
```

**Structure Decision**: Extend the existing adapter layout rather than introducing a new package tree. Keep module boundaries aligned with the user-requested responsibilities. `orchestrate.py` owns ordering and reporting but contains no XML-editing, validation, pytest, converter, or AI-provider implementation. Each run receives a unique output directory so a later failure cannot erase earlier diagnostics.

## Phase 0: Research

See [research.md](research.md). The architecture choices are resolved. Two environment assets remain implementation prerequisites rather than open design questions: a verified Forms 14.1.2 XML export and a locally configured Oracle conversion executable when FMB conversion is to be exercised.

## Phase 1: Design & Contracts

- [Data model](data-model.md) defines the validated form model, generated run, report, and error records.
- [Customer model contract](contracts/customer-model.md) defines the YAML shape and MVP object constraints.
- [Plugin configuration contract](contracts/plugin-config.md) defines template/output paths, converter settings, and opt-in repair settings.
- [Run report schema](contracts/run-report.schema.json) defines the JSON status, stages, outputs, and errors.
- [Quickstart](quickstart.md) describes prerequisites and end-to-end validation without requiring Oracle tools for the XML MVP.

**Post-design gate: PASS**

The design preserves all constitution constraints. Generation and repair target only a staged copy; publication follows YAML and XML validation; configured Oracle conversion writes a distinct output; pytest is isolated in `test_runner.py`; each AI repair attempt is bounded and logged. The initial template asset and optional Oracle converter configuration must be supplied before their corresponding integration tests can pass.
