# Report template

Use this scaffold for `PHP-LARAVEL-IMPL.md`. Keep every marker and section; write `No changes.` where a section has no content.

````markdown
<!-- php-laravel:artifact type=implementation version=1 -->
# PHP Laravel Implementation: order creation endpoint

- Status: Final
- Date: 2026-11-25
- Reviewer: PHP Laravel Agent
- Artifact: PHP-LARAVEL-IMPL.md
- PHP Version: 8.3
- Laravel Version: 12.0
- Dependency Source: lock
- Test Framework: pest
- Coverage Scope: business
- Changes Applied: 1
- Tests Run: ./vendor/bin/pest
- Coverage: 88%
- Coverage Tool: pest
- Review Language: English

<!-- php-laravel:section id=analysis -->
## Brief Analysis

The repository already uses invokable Actions, Form Requests and API Resources. This change follows those patterns and keeps the controller responsible only for receiving input and returning the response.

<!-- php-laravel:section id=stack -->
## Detected Stack

<!-- php-laravel:stack php=8.3 laravel=12.0 source=lock test=pest -->

The detector read `composer.json` and `composer.lock`: PHP 8.3, Laravel 12.0, `pestphp/pest`, `pestphp/pest-plugin-laravel`, `laravel/sanctum`, and a `<source>` include in `phpunit.xml`.

<!-- php-laravel:section id=design -->
## Design

- Layers: the existing `app/Actions` pattern owns the business rule; the controller stays thin.
- Validation and authorization: `StoreOrderRequest` validates input and authorizes the customer.
- Persistence: writes run inside `DB::transaction()` in the Action, with eager loading for the response.
- Test strategy: isolated Pest unit test for the Action and a Pest feature test for the HTTP contract.

<!-- php-laravel:section id=implementation -->
## Clean and Complete Code

<!-- php-laravel:change id=CHG-001 status=implemented -->
### CHG-001: Create the order action and endpoint

- File: app/Actions/CreateOrder.php:1
- Change: Added an invokable Action with transaction, validation result and resource mapping.
- Design: The Form Request owns validation/authorization; the Action owns persistence; the controller maps the response.

```php
final class CreateOrder
{
    public function handle(array $payload): Order
    {
        return DB::transaction(fn (): Order => Order::query()->create($payload));
    }
}
```

<!-- php-laravel:section id=tests -->
## Pest Tests

<!-- php-laravel:test id=T-001 framework=pest context=unit mock=true -->
### T-001: CreateOrder unit coverage

- File: tests/Unit/CreateOrderTest.php
- Cases: success, validation failure and persistence exception.
- Coverage: transaction path, mapping and exception propagation.

<!-- php-laravel:test id=T-002 framework=pest context=feature mock=false -->
### T-002: Order endpoint feature coverage

- File: tests/Feature/StoreOrderTest.php
- Cases: 201 response, validation errors, forbidden user and persisted database state.
- Coverage: Form Request, Policy, controller, Action and API Resource.

Feature tests extend `Tests\TestCase` and use `RefreshDatabase` through `tests/Pest.php`. Unit tests instantiate the Action directly with a `Mockery` collaborator and never boot the application.

<!-- php-laravel:section id=validation -->
## Validation

<!-- php-laravel:coverage value=88 gate=80 tool=pest driver=xdebug scope=business -->

- [x] `./vendor/bin/pest` passed with 24 tests.
- [x] `XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80` passed.
- [x] Pest reported 88% coverage on business files, above the 80% gate.
- [x] No framework boilerplate was added to the coverage include list.

<!-- php-laravel:section id=configurations -->
## Configurations

<!-- php-laravel:config id=CFG-001 file=phpunit.xml -->
### CFG-001: Limit coverage to business code

- Property: source.include app/Actions and app/Services
- Reason: The 80% gate measures changed business logic instead of framework boilerplate.

<!-- php-laravel:section id=evidence -->
## Evidence

<!-- php-laravel:evidence id=EV-001 command=./vendor/bin/pest status=passed -->
### EV-001: Pest unit and feature run

- Result: 24 tests passed, 0 failures.
- Coverage: 88% reported by Pest with Xdebug on business files.

<!-- php-laravel:section id=assumptions -->
## Assumptions

- The exact versions in `composer.lock` are authoritative.
- No new package was introduced.

<!-- php-laravel:section id=traceability -->
## Traceability

| Change | Test | Evidence |
| --- | --- | --- |
| CHG-001 | T-001 | EV-001 |
| CHG-001 | T-002 | EV-001 |
````
