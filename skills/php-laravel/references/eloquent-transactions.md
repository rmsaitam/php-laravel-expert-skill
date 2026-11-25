# Eloquent and transactions

## Mass assignment

Declare `$fillable` explicitly (or use `Model::unguard()` only in tightly controlled imports). Never pass an unfiltered request payload into `create()`, `update()` or `fill()`.

```php
final class Order extends Model
{
    protected $fillable = ['customer_id', 'reference', 'total'];

    protected $casts = [
        'total' => 'decimal:2',
        'paid_at' => 'immutable_datetime',
    ];
}
```

## Reuse query logic

Use local scopes and global scopes already present in the project. Add a scope when the same predicate appears in more than one place; do not duplicate `where()` chains across Services and controllers.

```php
public function scopePending(Builder $query): Builder
{
    return $query->whereNull('paid_at');
}
```

## Avoid N+1

Use `with()` for known relations, `withCount()` for counts, `loadMissing()` for conditional loads, and select only needed columns. When serializing nested resources to JSON, eager-load the exact relationships those Resources read.

```php
$orders = Order::query()
    ->with('customer:id,name')
    ->latest()
    ->paginate();
```

## Transaction boundary

Wrap multi-write operations in `DB::transaction()` in the Action or Service layer, never in the controller. Keep the closure small and avoid external HTTP calls inside it.

```php
public function handle(array $payload): Order
{
    return DB::transaction(function () use ($payload): Order {
        $order = Order::query()->create($payload);
        $order->items()->createMany($payload['items']);

        return $order;
    });
}
```

## Response safety

Return API Resources from JSON controllers so hidden columns, tokens and internal IDs are not serialized by accident. Define the response shape explicitly.

```php
return (new OrderResource($order))->response()->setStatusCode(201);
```

## Test impact

Unit tests mock the model boundary through the injected collaborator. Feature tests use `RefreshDatabase` and assert both the HTTP response and the persisted state with `assertDatabaseHas()`.
