# The Laravel way

Prefer the framework before any third-party package. The table maps common needs to native APIs.

| Need | Native Laravel / PHP solution |
| --- | --- |
| Validation | Form Requests, validation rules, `Validator`, custom Rules |
| Authorization | Gates, Policies, `$this->authorize()`, Form Request `authorize()` |
| Persistence | Eloquent, Query Builder, scopes, casts, accessors/mutators, eager loading |
| Async work | Queues, Jobs, Events & Listeners, Notifications, `Schedule` |
| Strings / arrays | `Illuminate\Support\Str`, `Arr`, `Number`, `Collection` |
| Dates | `Illuminate\Support\Carbon` |
| HTTP calls | `Illuminate\Support\Facades\Http` (Guzzle wrapper), `Http::fake()` in tests |
| Files / cache | `Storage`, `Cache`, `File` |
| Responses | API Resources, `JsonResponse`, `redirect()`, `view()` |
| Config / secrets | `config()` backed by `env()` and `.env.example` |

## Zero unnecessary dependencies

Do not suggest a package when the core already solves the requirement. When a core solution is genuinely insufficient (advanced PDF, complex spreadsheets, payment SDKs), prefer official ecosystem packages: Sanctum, Horizon, Telescope, Cashier, Scout and Pennant. Any other package needs an explicit need, the exact Composer command and user approval.

## Anti-patterns to reject

- Business rules inside routes, controllers, Blade views or Artisan commands.
- Raw SQL concatenation, `$request->all()` passed to `create()` without `$fillable`/`safe()`.
- `Model::all()` or lazy relationship access inside loops (N+1).
- Manual `curl` calls, manual JSON encoding for API responses, or manual date parsing.
- Hardcoded credentials, tokens, hostnames or environment URLs.
- Returning full Eloquent models with hidden columns from JSON endpoints.
- Gate or Policy checks duplicated in controllers when a Form Request already authorizes the action.

## Official verification

Use the Context7 IDs in `official-docs.md` to confirm signatures that may have changed between detected Laravel majors before writing code.
