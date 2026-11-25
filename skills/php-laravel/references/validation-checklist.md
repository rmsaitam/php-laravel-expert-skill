# Validation checklist

Use this checklist after writing `PHP-LARAVEL-IMPL.md` and before handing off. `validate_report.py` enforces the machine-checkable items.

## Artifact contract

- [ ] One `php-laravel:artifact` marker with `type=implementation` and `version=1`.
- [ ] Every required section marker appears exactly once and has content.
- [ ] Stable IDs: `CHG-NNN`, `T-NNN`, `CFG-NNN`, `EV-NNN`.
- [ ] Traceability table links every change, test and evidence ID.

## Stack and design

- [ ] `detect_stack.py` ran and the stack marker matches the metadata fields.
- [ ] The artifact names the detected descriptor (`composer.json` / `composer.lock`).
- [ ] PHP/Laravel versions and dependency source are recorded, including inexact-version assumptions.
- [ ] Existing architecture and naming conventions were followed.
- [ ] Native Laravel features were preferred; no unnecessary dependency was added.

## Implementation

- [ ] Controllers are thin; Form Requests own validation and authorization.
- [ ] Policies or Gates protect mutations; API Resources protect JSON output.
- [ ] `$fillable` is explicit and no raw request array reaches `create()`/`update()`.
- [ ] Eloquent queries avoid N+1 with `with()`/`loadMissing()`.
- [ ] Multi-write logic uses `DB::transaction()` outside the controller.
- [ ] Secrets come from `config()` backed by `.env.example`; no value is exposed.

## Tests and coverage

- [ ] At least one Pest unit entry (`context=unit`) and one Pest feature entry (`context=feature`).
- [ ] Unit tests isolate collaborators with `Mockery` and do not boot Laravel.
- [ ] Feature tests use `RefreshDatabase` and assert HTTP + persistence effects.
- [ ] `./vendor/bin/pest` was executed and recorded.
- [ ] `XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80` (or PCOV equivalent) passed.
- [ ] Coverage marker declares `tool=pest`, `driver=xdebug|pcov`, `scope=business` and value >= gate.
- [ ] The `<source><include>` list contains only business code.

## Final commands

```bash
python3 skills/php-laravel/scripts/validate_report.py PHP-LARAVEL-IMPL.md
python3 skills/php-laravel/scripts/validate_report.py PHP-LARAVEL-IMPL.md --strict
```

Return the artifact path, detected versions, coverage percentage, command results and remaining risks. Do not end with an approval verdict.
