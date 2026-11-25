# Pest unit and feature tests

## Coverage scope (business code only)

The 80% gate applies to code with behavior, not to framework boilerplate. Include in `phpunit.xml` only the paths that contain logic: `app/Actions`, `app/Services`, `app/Jobs`, `app/Policies`, `app/Rules`, custom casts, observers and the changed application files that contain branches.

Exclude from the gate: `config/`, `routes/`, `bootstrap/`, service providers, migrations, seeders, factories, Eloquent models without custom logic, pure DTOs, mapping-only API Resources, Blade views and generated code. Record the exact include list in the artifact under **Configurations** when it changes.

Never lower `--min=80` or exclude business files to make the gate pass. Add tests for the uncovered branches instead.

## Unit tests (`tests/Unit`)

- Cover Actions, Services, Jobs, Rules and helper logic in isolation.
- Instantiate the class directly with explicit collaborators; do not boot the Laravel application.
- Mock collaborators with `Mockery::mock()` and declare expectations with `shouldReceive()`.
- Cover success, validation failure, dependency failure and edge branches of the changed behavior.
- Use `expect()` assertions focused on outcomes and side effects, not on implementation details.

```php
it('creates an order from validated data', function () {
    $client = Mockery::mock(PaymentClient::class);
    $client->shouldReceive('charge')->once()->andReturn('tx_123');

    $order = (new CreateOrder($client))->handle(['total' => 100]);

    expect($order->reference)->toBe('ORD-1');
});
```

## Feature tests (`tests/Feature`)

- Exercise HTTP endpoints, middleware, authorization, validation, database state and dispatched jobs through the real application.
- Bind the app's `TestCase` and database trait in `tests/Pest.php`:

```php
pest()->extend(Tests\TestCase::class)
    ->use(Illuminate\Foundation\Testing\RefreshDatabase::class)
    ->in('Feature');
```

- Use `postJson()` / `getJson()` with `assertStatus()`, `assertJson()` and `assertJsonValidationErrors()`.
- Use `actingAs()` for authenticated routes and `assertForbidden()` for authorization failures.
- Use `assertDatabaseHas()`, `Event::fake()`, `Queue::fake()` and `Http::fake()` to assert observable effects.

## Coverage driver and gate

Coverage requires Xdebug 3.0+ or PCOV. With Xdebug, set `XDEBUG_MODE=coverage`.

```bash
./vendor/bin/pest
XDEBUG_MODE=coverage ./vendor/bin/pest --coverage --min=80
```

With PCOV:

```bash
./vendor/bin/pest --coverage --min=80
```

`phpunit.xml` needs a source include:

```xml
<source>
  <include>
    <directory suffix=".php">./app/Actions</directory>
    <directory suffix=".php">./app/Services</directory>
  </include>
</source>
```

Record the exact command, exit status and measured percentage. If Pest or a coverage driver is missing, ask before installing it and show the exact command; never claim a test or coverage run that did not happen.
