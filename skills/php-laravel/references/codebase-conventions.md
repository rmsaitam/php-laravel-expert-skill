# Codebase conventions

Read these files before designing any change: `composer.json`, `composer.lock`, `README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, ADRs under `docs/`, `phpunit.xml`, `tests/Pest.php`, `.env.example`, and the nearest existing example of the class being changed.

## Capture table

| Topic | What to record |
| --- | --- |
| Layout | `app/Actions`, `app/Services`, `app/Repositories`, DDD `Domain`/`Modules`, or plain MVC |
| Naming | Controller suffixes, Action verbs, Service names, Job names, namespace root |
| Validation | Form Requests in `app/Http/Requests` vs inline `$request->validate()` |
| Authorization | Policies, Gates, `authorize()` in Form Requests, middleware used in routes |
| Data shape | API Resources, DTOs, array responses, model serialization |
| Errors | Exceptions, `abort()`, handler mapping, JSON error envelope |
| Persistence | Eloquent only, repositories, query scopes, transaction style |
| Async | Jobs, Events/Listeners, Notifications, scheduling |
| Tests | Pest `tests/Unit` vs `tests/Feature`, `tests/Pest.php` setup, mocks via `Mockery`, database traits |
| Configuration | `config/*.php` files, `env()` key prefixes, `.env.example` conventions |

## Rules

- Copy the local style exactly. Do not reformat unrelated code or rename existing classes.
- Do not introduce a new architectural layer when the repository already solves the same problem.
- Reuse existing Traits, Helpers, Form Requests, Resources, Policies, Services and Jobs before creating files.
- If the project has no test directory, ask before introducing Pest and show the exact Composer command.
- Keep every new file under the namespace and directory conventions already observed.
