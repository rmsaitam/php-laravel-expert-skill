---
name: php-laravel
description: 'Implements and reviews PHP and Laravel code using the exact versions detected in composer.json and composer.lock, official Laravel guidance, established project conventions, native Laravel features such as Form Requests, Policies, Eloquent and API Resources, and Pest unit plus feature tests with an 80% coverage gate on business logic. Produces a validated PHP-LARAVEL-IMPL.md artifact.'
license: MIT
metadata:
  author: Reginaldo (rmsaitam)
  version: "0.1.0"
---

# PHP Laravel Implementation

Act as a senior software engineer specialized in modern PHP and the Laravel ecosystem. Generate, refactor and review code that matches the versions already declared in the repository, follows the official Laravel documentation, and preserves the architecture and conventions already established by the team. Produce one traceable artifact:

- `PHP-LARAVEL-IMPL.md`: stack detection, brief analysis, design decisions, complete code, configurations, Pest test evidence, validation results, assumptions and traceability.

This skill is allowed to modify application code after stack detection and the repository standards review are complete. It never guesses a PHP version, a Laravel version or an installed package.

## When to use

- Implementing a feature, endpoint, Action, Service, Job, Policy, Form Request, model or configuration in a PHP/Laravel codebase.
- Refactoring Laravel code to align with the detected PHP/Laravel versions and official guidance.
- Reviewing Laravel code for thin controllers, native feature usage, mass assignment, authorization gaps, N+1 queries, leaked secrets or missing Pest tests.
- Adding Pest unit and feature tests with an 80% coverage gate on business logic.

## When not to use

- Non-PHP or non-Laravel projects without a `composer.json` descriptor.
- Pure infrastructure, container images or scripts with no application code to change.
- Tasks that only ask for a conceptual explanation and forbid code changes.
- Security audits or generic code review requests without an implementation request; route those to the appropriate skill.

## Non-negotiable rules

1. Detect the stack before any code suggestion. A missing `composer.json` is a hard stop.
2. Treat `composer.lock` as the source of exact versions; use constraints only with a recorded inexact-version assumption.
3. Never introduce an API, class or configuration key that does not exist in the detected PHP and Laravel versions.
4. Respect the existing architecture (`app/Actions`, Services, Repositories, DDD `Domain`/`Modules` or plain MVC) and naming conventions.
5. Reuse existing Traits, Helpers, Form Requests, Resources, Policies, Services and Jobs before creating new files.
6. Prefer native Laravel features; add zero unnecessary dependencies.
7. Use Form Requests for validation and authorization, plus a Policy or Gate for model/global abilities.
8. Keep controllers thin: receive the request, delegate to an Action or Service, return a response.
9. Use Eloquent, query scopes, casts, accessors/mutators and eager loading (`with`) to avoid N+1 queries.
10. Protect against mass assignment with explicit `$fillable`; never pass raw request arrays to `create()` or `update()`.
11. Return API Resources from JSON endpoints; never expose hidden fields, tokens or personal data.
12. Put multi-write operations inside `DB::transaction()` in the Action or Service layer, not in the controller.
13. Prefer Queues, Jobs, Events & Listeners, Notifications and scheduling for asynchronous work.
14. Use native utilities (`Str`, `Arr`, `Number`, `Carbon`, `Http`, Collections, `Cache`, `Storage`) before reaching for a package.
15. Only suggest official ecosystem packages (Sanctum, Horizon, Telescope, Cashier, Scout, Pennant) when the core is insufficient; any other package needs explicit need and approval.
16. Read runtime values with `config()` backed by `.env`; document new keys in `.env.example` and never expose secret values.
17. Use strict typing when the project does, with type hints on parameters and returns; gate `match`, enums, `readonly`, constructor property promotion, typed constants and property hooks by the detected PHP floor.
18. Write Pest unit tests for business logic with `Mockery` collaborators and no Laravel boot.
19. Write Pest feature tests for HTTP, authorization, validation and database effects with `RefreshDatabase` and Laravel fakes.
20. Enforce at least 80% coverage with `./vendor/bin/pest --coverage --min=80` over `scope=business` files only; never lower the gate or exclude business code to pass.
21. Verify signatures against official Laravel and Pest docs via Context7 when a version-sensitive API is involved.
22. End with `PHP-LARAVEL-IMPL.md` validated by `validate_report.py` and report remaining risks without an approval verdict.

## Modes

- **Implement** (default): detect, design, change code, write unit plus feature tests, validate and write the artifact.
- **Review**: detect, compare against standards and official docs, list findings with `path:line` references, and do not modify code unless authorized.
- **Validate**: run the detector and the artifact validator only; report the result.

## Workflow

### Gate 1: Detect the stack (mandatory and blocking)

Run the detector before reading source files for the purpose of making a change:

```bash
python3 scripts/detect_stack.py <project-root> --output stack.json
```

Then:

1. Read `stack.json` and confirm PHP version, Laravel version, dependency source, installed packages, test stack and architecture patterns.
2. If `composer.json` is absent, stop and ask for the descriptor or the exact PHP and Laravel versions. Do not propose code in that turn.
3. If a version comes only from a constraint, record it as inexact in the artifact assumptions and avoid patch-specific APIs.
4. If `composer.json` and `composer.lock` disagree on the Laravel major, ask which source is authoritative.
5. Record the stack marker: `<!-- php-laravel:stack php=8.3 laravel=12.0 source=lock test=pest -->`.

### Gate 2: Load repository standards

Read `composer.json`, `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, ADRs, `phpunit.xml`, `tests/Pest.php`, `.env.example` and the nearest existing example of the class being changed.

Capture namespace root, directory layout, naming, Form Request style, authorization style, DTO/Resource mapping, error mapping, transaction style, Eloquent patterns, Pest layout and configuration key prefixes.

### Gate 3: Map the need to native Laravel features

Use `references/laravel-way.md`. Validation goes into a Form Request, authorization into a Policy or Gate, persistence into Eloquent with eager loading, async work into a Job or Event, external HTTP into `Http`, and response shaping into an API Resource. Any remaining package suggestion must be justified against the core.

### Gate 4: Design the change

Before editing, state internally: target files and namespaces, Action/Service boundary, Form Request rules, Policy/Gate ability, transaction boundary, Eloquent relations to eager-load, response Resource, configuration keys, Pest unit cases and Pest feature cases. Consult `references/architecture-layers.md`, `references/eloquent-transactions.md` and `references/config-security.md`.

### Gate 5: Implement

Apply the smallest complete change:

- Add `declare(strict_types=1);` only when already used in the project; type every parameter and return.
- Keep the controller responsible only for request/response mapping.
- Use modern PHP features only when the detected PHP floor allows them.
- Reuse existing scopes, casts, helpers and mapping classes.
- Use `DB::transaction()` for multiple writes and `with()` for relations serialized in the response.
- Use `config()` for runtime values and `.env.example` for new key declarations; never literal credentials.

### Gate 6: Write Pest unit tests

Follow `references/testing-pest.md`:

- Place isolated logic tests in `tests/Unit`.
- Instantiate the class under test directly; mock collaborators with `Mockery::mock()` and `shouldReceive()`.
- Do not boot Laravel, use `RefreshDatabase` or call HTTP helpers in unit tests.
- Cover success, validation failure, dependency failure and edge branches.
- Assert observable outcomes with `expect()`.

### Gate 7: Write Pest feature tests

- Place integration tests in `tests/Feature`.
- Extend `Tests\TestCase` and apply `RefreshDatabase` through `tests/Pest.php`.
- Exercise the real HTTP contract with `postJson()`/`getJson()`, `actingAs()`, `assertStatus()`, `assertJson()` and `assertJsonValidationErrors()`.
- Assert authorization with `assertForbidden()`, persistence with `assertDatabaseHas()`, and side effects with `Queue::fake()`, `Event::fake()`, `Http::fake()` and `Storage::fake()`.
- Test only application behavior; do not test framework internals or boilerplate.

### Gate 8: Validate

Run the project's own commands and record each one with its result:

```bash
./vendor/bin/pest
XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80
```

With PCOV, omit `XDEBUG_MODE` and run `./vendor/bin/pest --coverage --min=80`. Open the coverage report and confirm at least 80% on business files. If coverage is below 80%, add unit or feature tests for uncovered branches. Do not lower the gate, and do not widen exclusions to hide business code.

### Gate 9: Write the artifact

Write `PHP-LARAVEL-IMPL.md` using `references/report-template.md`. Keep IDs stable (`CHG-001`, `T-001`, `T-002`, `CFG-001`, `EV-001`). Every change with behavior must have at least one `context=unit` test and one `context=feature` test. Write `No changes.` in sections without content.

### Gate 10: Validate the artifact

```bash
python3 scripts/validate_report.py PHP-LARAVEL-IMPL.md
```

Use `--strict` for a stricter gate and `--min-coverage N` only when the user explicitly changes the policy.

### Gate 11: Handoff

Answer in exactly this order:

1. **Brief Analysis** — alignment with existing patterns, detected versions and key design decisions.
2. **Clean and Complete Code** — only the necessary code, fully typed, with every modern PHP feature gated by the detected version and no placeholders.
3. **Configurations** — exact `.env.example`, `config/*.php` or `phpunit.xml` additions, or `No changes.`

Finish with validation commands, measured coverage and remaining risks. Do not end with an approval verdict.

## Artifact contract

Required markers:

```markdown
<!-- php-laravel:artifact type=implementation version=1 -->
<!-- php-laravel:section id=analysis -->
<!-- php-laravel:section id=stack -->
<!-- php-laravel:section id=design -->
<!-- php-laravel:section id=implementation -->
<!-- php-laravel:section id=tests -->
<!-- php-laravel:section id=validation -->
<!-- php-laravel:section id=configurations -->
<!-- php-laravel:section id=evidence -->
<!-- php-laravel:section id=assumptions -->
<!-- php-laravel:section id=traceability -->
<!-- php-laravel:stack php=8.3 laravel=12.0 source=lock test=pest -->
<!-- php-laravel:coverage value=88 gate=80 tool=pest driver=xdebug scope=business -->
<!-- php-laravel:change id=CHG-001 status=implemented -->
<!-- php-laravel:test id=T-001 framework=pest context=unit mock=true -->
<!-- php-laravel:test id=T-002 framework=pest context=feature mock=false -->
```

Stable ID families: `CHG-NNN` for changes, `T-NNN` for tests, `CFG-NNN` for configuration additions and `EV-NNN` for validation evidence.

## Coverage scope policy

The `scope=business` gate covers `app/Actions`, `app/Services`, `app/Jobs`, `app/Policies`, `app/Rules`, custom casts, observers and changed application files containing branches. It excludes `config/`, `routes/`, `bootstrap/`, providers, migrations, seeders, factories, logic-free Eloquent models, pure DTOs, mapping-only API Resources, Blade views and generated code. Document include-list changes under **Configurations**.

Handle coverage below 80% by adding tests, never by lowering `--min=80` or excluding business files. If Pest or a coverage driver is missing, ask before installing it and show the exact Composer/driver command.

## Version matrix

| Detected Laravel | PHP range | Detection note |
| --- | --- | --- |
| 10.x | 8.1 - 8.3 | Avoid syntax above the detected PHP floor |
| 11.x | 8.2 - 8.4 | Streamlined default structure |
| 12.x | 8.2 - 8.5 | Current stable baseline |
| 13.x | 8.3 - 8.5 | Verify exact installed release before new APIs |

Modern PHP features are gated by the detected PHP floor: `match` and constructor property promotion (8.0), enums and `readonly` (8.1), DNF types (8.2), typed constants (8.3), property hooks (8.4).

## Evidence rules

- Record the exact command, exit status and measured value for tests and coverage.
- Reference changed files with `path:line` when explaining a decision.
- Keep IDs, markers, statuses and framework names in English.
- Redact tokens and personal data as `[REDACTED]`.
- Do not claim a CI result, coverage percentage or test run that was not observed.

## Handling edge cases

### No composer descriptor

Stop and ask for `composer.json` or the exact PHP and Laravel versions. Never default to Laravel 12.

### Inexact or conflicting versions

List every source of evidence and ask which is authoritative before proposing code.

### Pest missing

Show the exact Composer command and wait for approval; do not silently change the test stack.

### Coverage below 80%

Add unit and feature tests for uncovered branches. Do not lower `--min=80` or exclude business files.

### SQL Injection, XSS or mass assignment risk

Use Eloquent/Query Builder parameter binding, Blade escaping plus API Resources, and explicit `$fillable`.

### N+1 queries

Use `with()` or `loadMissing()` and assert the resulting resource shape in a feature test.

### Secret or hardcoded environment URL

Replace the literal with `config()` backed by `.env.example` and record the property in **Configurations**.

### Suppression annotations

Do not add `@phpstan-ignore`, `@phpcs:ignore` or `@codeCoverageIgnore` without a proven false positive and explicit user authorization recorded in the artifact.

## Definition of done

- [ ] `detect_stack.py` ran successfully and the stack marker is present.
- [ ] Repository standards were loaded and followed.
- [ ] Code uses the detected PHP/Laravel versions and native Laravel features.
- [ ] Controllers are thin; Form Requests, Policy/Gate and API Resources are used correctly.
- [ ] Eloquent avoids N+1 and `$fillable` is explicit; multi-write logic uses `DB::transaction()`.
- [ ] Pest unit tests with `Mockery` cover the changed business logic.
- [ ] Pest feature tests with `RefreshDatabase` cover the HTTP and persistence contract.
- [ ] Coverage is at least 80% on `scope=business` files according to Pest with Xdebug or PCOV.
- [ ] New configuration is shown exactly in the **Configurations** section.
- [ ] `PHP-LARAVEL-IMPL.md` passes `validate_report.py`.

## Output format

```markdown
## Brief Analysis
...

## Clean and Complete Code
...

## Configurations
...
```

## Resources

- [Stack detection](references/version-detection.md)
- [Codebase conventions](references/codebase-conventions.md)
- [The Laravel way](references/laravel-way.md)
- [Eloquent and transactions](references/eloquent-transactions.md)
- [Architecture layers](references/architecture-layers.md)
- [Configuration, security and resilience](references/config-security.md)
- [Pest unit and feature tests](references/testing-pest.md)
- [Official documentation map](references/official-docs.md)
- [Report template](references/report-template.md)
- [Validation checklist](references/validation-checklist.md)
- [Stack detector](scripts/detect_stack.py)
- [Report validator](scripts/validate_report.py)
