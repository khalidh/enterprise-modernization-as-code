# Tasks: Oracle Forms YAML-to-XML Generator

**Input**: Design documents from `specs/001-oracle-forms-generator/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, and `contracts/`

**Tests**: Required by the feature specification. Use pytest; run it after each code, configuration, or generated-artifact modification.

**Organization**: Tasks are grouped by user story to support incremental implementation and verification.

## Format

Every task follows `- [ ] Tnnn [P?] [Story?] Description with exact file path`. `[P]` is used only where files and validation can safely proceed independently. Story labels appear only in user-story phases.

## Phase 1: Setup

**Purpose**: Establish the testable project inputs and configuration.

- [ ] T001 Add a passing repository-layout smoke test in `tests/test_oracle_forms.py` and run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T002 Add `PyYAML` and `pytest` dependencies to `requirements.txt`, install them with `python -m pip install -r requirements.txt`, then run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T003 [P] Configure the template path, output root, optional converter, and disabled-by-default AI repair with a three-attempt cap in `adapters/oracle-forms/plugin.yaml`; then run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T004 [P] Add the contract-conforming `HELLO_WORLD` model with one `field` named `NOM_CLIENT` and one `button` named `BTN_BONJOUR` to `model/customer.yaml`; then run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T005 [P] Obtain a genuine Oracle Forms 14.1.2 export containing the target form, field, and button and place it at `adapters/oracle-forms/templates/hello_world.xml`; do not synthesize or modify an existing source FMB, then run `python -m pytest -q tests/test_oracle_forms.py`.

## Phase 2: Foundational

**Purpose**: Establish safe input parsing and the independent pytest runner before story implementation.

- [ ] T006 Add tests for valid YAML loading, malformed YAML, missing required fields, duplicate names, and the exact-one-field/exact-one-button rule in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new behavior tests fail.
- [ ] T007 Implement safe YAML loading and customer-model validation in `adapters/oracle-forms/generator/validate.py`, including source line/column when PyYAML provides it; immediately run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T008 Add tests for pytest command construction, captured output, exit status, and retained test logs in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new behavior tests fail.
- [ ] T009 Implement the separate pytest process runner in `adapters/oracle-forms/generator/test_runner.py`; capture stdout/stderr and retain a log, then immediately run `python -m pytest -q tests/test_oracle_forms.py`.

## Phase 3: User Story 1 - Generate the HELLO_WORLD Form (Priority: P1) 🎯 MVP

**Goal**: Generate a valid Oracle Forms XML result from a valid MVP YAML model and the exported template.

**Independent Test**: Run the generator with `model/customer.yaml`; verify well-formed XML with one `HELLO_WORLD` form, one `NOM_CLIENT` field, one `BTN_BONJOUR` button, and an unchanged source template.

### Tests for User Story 1

- [ ] T010 [US1] Add generation tests using the genuine template in `tests/test_oracle_forms.py`; assert well-formed XML, required object types/names, preservation of unrelated objects, and unchanged template bytes, then run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new behavior tests fail.

### Implementation for User Story 1

- [ ] T011 [US1] Implement template-based form generation with `xml.etree.ElementTree` in `adapters/oracle-forms/generator/generate.py`; update only the existing target nodes and run `python -m pytest -q tests/test_oracle_forms.py` immediately after the change.
- [ ] T012 [US1] Add successful-run integration tests for staging and output placement in `tests/test_oracle_forms.py`; assert the XML is under `generated/oracle-forms/<form>/<run-id>/` and run `python -m pytest -q tests/test_oracle_forms.py`, confirming the new orchestration assertions fail.
- [ ] T013 [US1] Implement the successful generation path, unique run directory, and publication-after-validation flow in `adapters/oracle-forms/generator/orchestrate.py`; run `python -m pytest -q tests/test_oracle_forms.py` immediately after the change.

**Checkpoint**: US1 is independently demonstrable without Oracle conversion tools or an AI provider.

## Phase 4: User Story 2 - Customize Object Names and Labels (Priority: P2)

**Goal**: Apply YAML-provided names and labels to the matching template object types, including XML-escaped text.

**Independent Test**: Change field and button names/labels in a valid temporary YAML file and assert the generated XML values match exactly.

### Tests for User Story 2

- [ ] T014 [US2] Add tests for customized form/object names, labels, object-type mapping, and XML-special characters in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new behavior assertions fail.

### Implementation for User Story 2

- [ ] T015 [US2] Apply validated form, field, and button names and labels to their corresponding template nodes in `adapters/oracle-forms/generator/generate.py`; run `python -m pytest -q tests/test_oracle_forms.py` immediately after the change.

**Checkpoint**: US2 is independently demonstrable by changing only the YAML values and rerunning generation.

## Phase 5: User Story 3 - Diagnose Invalid Input and Output (Priority: P2)

**Goal**: Reject invalid input/output and retain actionable JSON reports and logs without publishing invalid XML.

**Independent Test**: Exercise malformed YAML, missing values, malformed XML, and missing target objects; inspect each run's JSON report and error log and verify invalid XML is not published.

### Tests for User Story 3

- [ ] T016 [US3] Add failure-path tests for YAML and XML validation, report schema, source locations, retained logs, and suppression of invalid XML in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new assertions fail.

### Implementation for User Story 3

- [ ] T017 [US3] Implement ElementTree well-formedness checks and required-object/name checks in `adapters/oracle-forms/generator/validate.py`; run `python -m pytest -q tests/test_oracle_forms.py` immediately after the change.
- [ ] T018 [US3] Implement structured JSON failure reports and retained per-run error logs in `adapters/oracle-forms/generator/orchestrate.py`, matching `specs/001-oracle-forms-generator/contracts/run-report.schema.json`; ensure invalid XML is not published and run `python -m pytest -q tests/test_oracle_forms.py` immediately after the change.

**Checkpoint**: US3 is independently demonstrable with invalid fixtures and does not require an Oracle installation.

## Phase 6: User Story 4 - Convert XML to FMB When Oracle Tools Are Available (Priority: P3)

**Goal**: Convert validated XML through the configured Oracle tool when available, without coupling conversion availability to XML success.

**Independent Test**: Use a fake configured converter to verify success and failure paths; verify an absent converter is reported as unavailable. Run the real converter acceptance case only in an Oracle Forms 14.1.2 environment.

### Tests for User Story 4

- [ ] T019 [US4] Add fake-process tests for converter success, nonzero exit, missing executable, argument substitution, and separate FMB output in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new assertions fail.

### Implementation for User Story 4

- [ ] T020 [US4] Implement configured XML-to-FMB execution without shell interpolation in `adapters/oracle-forms/generator/oracle_converter.py`; support `{input_xml}` and `{output_fmb}` arguments and immediately run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T021 [US4] Integrate converter availability and results into the run report and separate output paths in `adapters/oracle-forms/generator/orchestrate.py`; immediately run `python -m pytest -q tests/test_oracle_forms.py`.

**Checkpoint**: US4 is independently demonstrable with a fake converter; the licensed Oracle conversion test remains conditional on configured Oracle tools.

## Phase 7: Polish - AI Repair and Cross-Cutting Validation

**Purpose**: Add bounded, auditable repair and verify the full quickstart.

- [ ] T022 Add tests for repair disabled, provider failure, successful repair, immutable source files, and stopping after exactly three failed attempts in `tests/test_oracle_forms.py`; run `python -m pytest -q tests/test_oracle_forms.py` and confirm the new behavior assertions fail.
- [ ] T023 Implement provider-neutral AI repair with a hard maximum of three attempts, validation and pytest after each candidate change, and retained attempt logs in `adapters/oracle-forms/generator/repair_loop.py`; immediately run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T024 Integrate the repair loop only for failed staged candidates in `adapters/oracle-forms/generator/orchestrate.py`; enforce the configured cap, preserve YAML/template/source FMB, and immediately run `python -m pytest -q tests/test_oracle_forms.py`.
- [ ] T025 Document the permitted repair scope, retry limit, and log-retention behavior in `agents/forms-repair/SKILL.md`; run `python -m pytest -q tests/test_oracle_forms.py` after the documentation change.
- [ ] T026 Run the complete suite through `adapters/oracle-forms/generator/test_runner.py` and validate the end-to-end steps in `specs/001-oracle-forms-generator/quickstart.md`; confirm generated artifacts remain under `generated/oracle-forms/` and all reports/logs remain available.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001-T002 establish pytest and dependencies. T003-T005 can proceed in parallel after T002 because they edit independent input/config/template files.
- **Foundational (Phase 2)**: Depends on Setup. T006-T007 establish input validation; T008-T009 establish test orchestration. These block story implementation.
- **US1 (Phase 3)**: Depends on the validated model, configured paths, and genuine template in Phase 1 plus Phase 2. It is the MVP.
- **US2 (Phase 4)**: Depends on US1 generation and its template mapping.
- **US3 (Phase 5)**: Depends on the shared validator and successful-run orchestration from US1; adds failure reports and log retention.
- **US4 (Phase 6)**: Depends on US1 output and US3 report contract. A real converter test additionally requires Oracle Forms 14.1.2 tools and local command configuration.
- **Polish (Phase 7)**: Depends on US1-3; US4 is needed only when AI repair is expected to handle conversion failures.

### User Story Dependencies

- **US1 (P1)**: After Setup and Foundational; delivers XML generation without Oracle conversion or AI repair.
- **US2 (P2)**: After US1 because it extends the generator's target-node mapping.
- **US3 (P2)**: After the foundational validator and US1 orchestration; can be implemented before US2 if work is serialized around shared files.
- **US4 (P3)**: After US1 and the report contract; Oracle tools are optional for all other stories.

### Parallel Opportunities

- After T002, T003 (`plugin.yaml`), T004 (`customer.yaml`), and T005 (template asset) touch separate files and may be prepared in parallel; serialize their smoke-test runs if they share one workspace.
- Within each story, test-first tasks precede implementation and commonly share `tests/test_oracle_forms.py`; do not parallelize those pairs in one working tree.
- US2 and US3 both modify generator/validation/report surfaces; serialize them in a single checkout even though their input fixtures are conceptually independent.
- US4's fake converter tests and converter implementation are sequential; real Oracle verification can be run separately once its environment is configured.

### Parallel Execution Examples

```text
Setup after T002 (separate files):
T003 adapters/oracle-forms/plugin.yaml
T004 model/customer.yaml
T005 adapters/oracle-forms/templates/hello_world.xml

US1: T010 test -> T011 generator -> T012 integration test -> T013 orchestration
US2: T014 test -> T015 customization
US3: T016 test -> T017 validation -> T018 JSON report/logging
US4: T019 fake-tool test -> T020 converter -> T021 integration
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational tasks, including supplying a genuine Forms 14.1.2 template.
2. Complete US1 tests and implementation.
3. Run pytest and the independent US1 generation check; stop if the template or preservation checks fail.
4. Demonstrate well-formed XML under `generated/oracle-forms/` before proceeding.

### Incremental Delivery

1. Add US2 YAML-driven customization and XML escaping.
2. Add US3 JSON diagnostics and retained logs for all invalid paths.
3. Add US4 optional conversion using fake-process tests, then validate against Oracle tools when available.
4. Add AI repair last, retaining a strict three-attempt cap and running validation/pytest after each candidate change.

## Completion Criteria

- All tasks are checked only after completion; all task entries use the required checkbox, sequential ID, applicable parallel/story labels, and exact file path.
- The full pytest suite passes after the final implementation change.
- XML outputs, JSON reports, converted FMB outputs, and error logs stay under `generated/oracle-forms/`.
- Original template and source FMB remain unchanged; no AI repair path exceeds three attempts.
