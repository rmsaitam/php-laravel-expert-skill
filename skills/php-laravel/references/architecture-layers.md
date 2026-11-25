# Architecture layers

## Thin controllers

A controller receives the request, delegates to an Action or Service and returns a response. It contains no business rules, no query building and no authorization logic beyond what the route/Form Request already declares.

```php
final class StoreOrderController
{
    public function __invoke(StoreOrderRequest $request, CreateOrder $action): JsonResponse
    {
        $order = $action->handle($request->validated());

        return (new OrderResource($order))->response()->setStatusCode(201);
    }
}
```

## Reuse the detected structure

| Existing structure | Placement rule |
| --- | --- |
| `app/Actions` | One invokable class per use case, `handle()` or `__invoke()` |
| `app/Services` | Cohesive domain operations shared by multiple callers |
| `app/Repositories` | Keep only if already in use; do not add a repository over plain Eloquent |
| DDD `Domain`/`Modules` | Keep entities, value objects and domain services inside the existing module |
| Plain MVC | Put logic in models only when the project already does so; otherwise prefer an Action |

## Requests and Policies

- Put input shape, validation rules, messages and `authorize()` in a Form Request.
- Use Policies for model-level abilities and Gates for global abilities.
- Call `$this->authorize()` or `Gate::authorize()` before mutations; never rely on the frontend.
- Return `403` automatically from `authorize(): false`.

## Jobs and events

Use a Queueable Job for work that must happen after the response. Use Events/Listeners when several independent reactions exist. Dispatch from the Action or Service, not from the controller when the project already dispatches there.

## New file checklist

Before creating a file, search for an existing class with the same responsibility. If none exists, choose the directory that matches the detected architecture and keep the class `final` when the codebase favors final classes.
