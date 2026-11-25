# Configuration, security and resilience

## Configuration

Read runtime values with `config('services.payment.base_uri')`, never with `env()` outside `config/*.php`. Declare every new key in `.env.example` with an empty or obvious development value, then document only its key name in the **Configurations** section of the artifact. Never inspect `.env` or `.env.example` contents to harvest values; rely on detector key names only and never copy, quote or emit an environment value into context or the artifact.

## Secrets

- Never write `APP_KEY`, passwords, API tokens or private keys into code, tests, docs or the artifact.
- Reference secrets through environment variables and configuration files.
- Redact secrets found in user-provided context as `[REDACTED]`.
- The detector returns `.env.example` key names only; it must never leak values.

## Authorization and input

- Authorize every mutation with a Policy, Gate or Form Request `authorize()`.
- Validate and normalize all input through Form Requests with declared rules.
- Use `$fillable` or explicit attribute assignment to prevent mass assignment.
- Escape output in Blade (`{{ }}`), and return API Resources for JSON so sensitive attributes stay hidden.
- Keep CSRF protection enabled for web routes; use Sanctum for API authentication when already installed.

## External calls and resilience

- Use `Http` with explicit `timeout()` and `retry()` only when the project already applies that pattern.
- Do not add backoff, circuit breakers or new packages unless the requirement demands them and the user approves.
- Use `Cache::remember()` for expensive reads only when invalidation is defined.
- Reuse existing logging, health checks and telemetry conventions; do not introduce new observability agents.

## Test doubles for external systems

Use `Http::fake()`, `Queue::fake()`, `Event::fake()`, `Storage::fake()` and `Bus::fake()` in Pest feature tests. Use `Mockery::mock()` with `shouldReceive()` for isolated unit tests.
