---
description: Implement PHP and Laravel changes using the detected composer.json and composer.lock versions, official Laravel guidance, codebase conventions, native features, and Pest unit plus feature tests with an 80% coverage gate on business logic.
argument-hint: "[--project-root PATH] [--scope DESCRIPTION] [--output PATH]"
---

# PHP Laravel

Invoke the `php-laravel` skill. The skill must first detect the stack; it must not suggest dependencies, APIs or code before that gate is complete.

## Instructions

- Run `python3 scripts/detect_stack.py <project-root> --output stack.json` from the installed skill directory as the first action. From the plugin repository root, use `python3 skills/php-laravel/scripts/detect_stack.py <project-root> --output stack.json`. If there is no `composer.json`, stop and ask for the descriptor or the exact PHP and Laravel versions.
- Treat `composer.lock` as authoritative for exact versions; record inexact constraint assumptions.
- Follow the existing app layout, naming, Form Request, Policy, Resource and Pest style. Do not introduce a new library or architectural layer without an explicit need.
- Keep controllers thin. Put validation and authorization in Form Requests, Policies or Gates; put business rules in an Action or Service and multi-write logic in `DB::transaction()`.
- Use Eloquent, eager loading (`with`), explicit `$fillable` and API Resources. Avoid N+1 queries and data leaks.
- Write isolated Pest unit tests with `Mockery` and no application boot, plus Pest feature tests with `RefreshDatabase`, HTTP assertions and Laravel fakes.
- Run `./vendor/bin/pest` and `XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80` (or the PCOV equivalent). Record the exact commands, results and measured coverage on `scope=business` files.
- Enforce at least 80% coverage. Add tests instead of lowering the gate or excluding business code.
- Write only `PHP-LARAVEL-IMPL.md` at the repository root unless the user supplies another path.
- Before finishing, run:

  ```bash
  python3 scripts/validate_report.py PHP-LARAVEL-IMPL.md
  ```

  From the plugin repository root, prefix the script path with `skills/php-laravel/`.

- Report the artifact path, detected PHP and Laravel versions, main changes, unit and feature test commands, measured coverage and remaining risks.
