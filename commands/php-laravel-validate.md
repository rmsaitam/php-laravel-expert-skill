---
description: Validate a PHP-LARAVEL-IMPL.md artifact against the PHP and Laravel implementation report contract, including Pest unit and feature coverage evidence.
argument-hint: "[path/to/PHP-LARAVEL-IMPL.md]"
---

# Validate PHP Laravel Report

Validate an existing `PHP-LARAVEL-IMPL.md` produced by the `php-laravel` skill.

## Instructions

- Default to `PHP-LARAVEL-IMPL.md` at the repository root when no path is provided.
- Run:

  ```bash
  python3 scripts/validate_report.py PHP-LARAVEL-IMPL.md
  ```

  From the plugin repository root, prefix the script path with `skills/php-laravel/`.

- Use `--strict` to treat warnings as failures, `--json` for machine-readable output and `--min-coverage N` to change the default 80% gate.
- The validator requires `framework=pest`, at least one `context=unit` and one `context=feature` test, and a coverage marker with `tool=pest`, `driver=xdebug|pcov` and `scope=business`.
- Do not modify the report unless the user explicitly asks for fixes. If fixes are requested, preserve the artifact markers and re-run the validator.
