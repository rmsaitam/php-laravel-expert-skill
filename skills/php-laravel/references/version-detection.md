# Version detection

Run the detector before reading source files for the purpose of making a change:

```bash
python3 scripts/detect_stack.py <project-root> --output stack.json
```

From the plugin repository root, prefix the script path with `skills/php-laravel/`.

## Evidence sources

| Field | Preferred source | Fallback | Behavior |
| --- | --- | --- | --- |
| PHP version | `.php-version`, `config.platform.php` in `composer.json`, `platform-overrides.php` in `composer.lock` | `require.php` constraint floor (`^8.3` -> `8.3`) | Missing value is a blocker; a constraint-only value is a warning |
| Laravel version | `laravel/framework` in `composer.lock` | `require["laravel/framework"]` constraint major (`^12.0` -> `12.0`) | Missing package is a blocker; a constraint-only value is a warning |
| Test stack | `require-dev` and `packages-dev` | `tests/Pest.php`, `tests/Unit`, `tests/Feature` | Missing Pest is a warning; ask before adding it |
| Coverage setup | `<source><include>` in `phpunit.xml` / `phpunit.xml.dist` | none | Missing include is a warning |
| Architecture | directories under `app/` | none | Mirrored, never invented |
| Configuration keys | `.env.example` and `env('KEY')` calls under `config/` | none | Keys only; values are never emitted |

## Output fields

`projectRoot`, `descriptor`, `packageManager`, `php{version,constraint,source}`, `laravel{version,constraint,major,source}`, `firstPartyPackages`, `testDependencies`, `capabilities{pest,pestLaravelPlugin,mockery,coverageConfigured,coverageDriver}`, `testLayout`, `architecturePatterns`, `configKeys`, `warnings`, `blockers`.

The `source` field is authoritative. When `source=constraint`, state the inexact version in the artifact assumptions and avoid APIs introduced in a patch release.

## Laravel version matrix

| Laravel | PHP range | Notes |
| --- | --- | --- |
| 10.x | 8.1 - 8.3 | Legacy maintenance; avoid new syntax above the detected PHP floor |
| 11.x | 8.2 - 8.4 | Streamlined default structure |
| 12.x | 8.2 - 8.5 | Current stable baseline |
| 13.x | 8.3 - 8.5 | Verify the exact installed release before relying on new APIs |

## Modern PHP gating

Only use a feature when the detected PHP floor supports it: `match` and constructor property promotion (8.0), enums and `readonly` properties (8.1), DNF types (8.2), typed class constants (8.3), property hooks and asymmetric visibility (8.4). Add `declare(strict_types=1);` only when the project already does so.

## Stop conditions

- No `composer.json`: stop and ask for the descriptor or the exact PHP and Laravel versions.
- Invalid `composer.json` or `composer.lock`: report the exact file and parse error.
- Missing `laravel/framework` or PHP version: report the blocker codes and do not propose code.
- `composer.json` and `composer.lock` disagree on the Laravel major: ask which source is authoritative.

## Security boundary

The detector extracts key names only. It never reads `.env` values and never writes a token, password or `APP_KEY` into `stack.json`. Redact any secret that appears in user-provided context as `[REDACTED]`.
