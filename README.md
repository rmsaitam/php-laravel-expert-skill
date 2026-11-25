# PHP Laravel

[![skills.sh](https://skills.sh/b/rmsaitam/php-laravel-expert)](https://skills.sh/rmsaitam/php-laravel-expert)

A version-aware PHP and Laravel implementation skill for coding agents. Before suggesting any class, API, validation rule or dependency, the skill inspects `composer.json` and `composer.lock` to identify the exact PHP version, Laravel version and installed packages. If no `composer.json` is available, it stops and asks for the descriptor or the exact versions instead of guessing.

The skill follows the conventions already present in the codebase and the official Laravel documentation. It prefers native Laravel features (Form Requests, Policies, Eloquent, API Resources, queues, events, `Str`, `Arr`, `Number`, `Carbon`, `Http`, Collections, Cache and Storage), avoids unnecessary packages, keeps controllers thin, protects against mass assignment and data leaks, and writes Pest unit and feature tests with an 80% coverage gate on business logic (`scope=business`).

## Supported agents

| Agent | Manifest |
| --- | --- |
| Claude Code | `.claude-plugin/plugin.json` |
| Codex | `.codex-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| GitHub Copilot CLI | `.github/plugin/marketplace.json` |
| Antigravity | `plugin.json` |
| skills.sh / generic Agent Skills | `skills/php-laravel/SKILL.md` |

## Install

```bash
npx skills add rmsaitam/php-laravel-expert
npx skills add rmsaitam/php-laravel-expert -g -y
npx skills add rmsaitam/php-laravel-expert --list
```

Claude Code:

```text
/plugin marketplace add rmsaitam/php-laravel-expert
/plugin install php-laravel
```

Manual install for generic Agent Skills:

```bash
mkdir -p ~/.agents/skills
cp -R skills/php-laravel ~/.agents/skills/php-laravel
python3 scripts/validate_plugin.py .
```

## What it does

1. Runs `detect_stack.py` to produce a normalized stack report: PHP version, Laravel version, version source, installed first-party packages, test dependencies, test layout, architecture patterns and `.env.example` configuration keys (never values).
2. Loads repository standards and mirrors existing Actions, Services, Repositories, Form Requests, Resources, Policies, Jobs and test patterns.
3. Implements the change with native Laravel features, a thin controller, explicit authorization, safe Eloquent usage and no new dependency without a proven need.
4. Adds isolated Pest unit tests for business logic and Pest feature tests for HTTP, authorization and database behavior. Coverage is enforced with `XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80` (or `./vendor/bin/pest --coverage --min=80` with PCOV) over business files only.
5. Writes and validates a traceable `PHP-LARAVEL-IMPL.md` artifact with `validate_report.py`.

The final answer always follows this format: **Brief Analysis**, **Clean and Complete Code**, **Configurations**.

## Artifact markers

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

## Development

```bash
make test        # run the test suite
make coverage    # run tests with an 80% coverage gate
make validate    # validate the plugin structure
make check       # coverage plus plugin validation
```

The executable test suite of this plugin uses pytest and covers `detect_stack.py`, `validate_report.py` and `validate_plugin.py`. The generated Laravel code contract requires Pest unit plus feature tests and 80% coverage measured by Pest with Xdebug or PCOV over business code only.

## Official documentation

The `references/official-docs.md` file maps each rule to the official Laravel and Pest documentation and to the Context7 library IDs used to verify current APIs.

## License

MIT
