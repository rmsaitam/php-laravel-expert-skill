from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

EXIT_OK = 0
EXIT_STRICT = 1
EXIT_CONFIG = 2
EXIT_PARSE = 3

DESCRIPTOR = "composer.json"
FIRST_PARTY = (
    "sanctum",
    "horizon",
    "telescope",
    "cashier",
    "scout",
    "pennant",
    "octane",
    "livewire",
)


class ConfigError(Exception):
    pass


class ParseError(Exception):
    pass


def item(code: str, message: str, source: str) -> dict:
    return {"code": code, "message": message, "source": source}


def find_descriptor(root: Path) -> str:
    if (root / DESCRIPTOR).is_file():
        return DESCRIPTOR
    raise ConfigError(
        "No composer.json found. Provide the composer descriptor or the exact PHP and "
        "Laravel versions before continuing."
    )


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ParseError(f"Invalid JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ParseError(f"{path} must contain a JSON object.")
    return data


def load_lock(root: Path) -> dict | None:
    path = root / "composer.lock"
    if not path.is_file():
        return None
    return load_json(path)


def normalize_version(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().strip("'\"")
    if cleaned.startswith("v"):
        cleaned = cleaned[1:]
    match = re.match(r"^\d+(?:\.\d+)*(?:[.-][0-9A-Za-z.-]+)?$", cleaned)
    return cleaned if match else None


def normalize_constraint(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"^[\^~>=<!\s]+", "", value.strip())
    cleaned = cleaned.split("|", 1)[0].split(" - ", 1)[0].strip()
    return normalize_version(cleaned)


def parse_major(value: str | None) -> int | None:
    match = re.match(r"^(\d+)", (value or "").strip())
    return int(match.group(1)) if match else None


def parse_php_floor(value: str | None) -> str | None:
    match = re.search(r"(\d+)\.(\d+)(?:\.\d+)?", value or "")
    return f"{match.group(1)}.{match.group(2)}" if match else None


def constraint_major(value: str | None) -> int | None:
    return parse_major(normalize_constraint(value))


def locked_version(packages: list, name: str) -> str | None:
    for package in packages:
        if isinstance(package, dict) and package.get("name") == name:
            return normalize_version(str(package.get("version", "")))
    return None


def detect_test_dependencies(names: list[str]) -> list[str]:
    joined = " ".join(names).lower()
    detected: list[str] = []
    if "pestphp/pest" in joined:
        detected.append("pest")
    if "pestphp/pest-plugin-laravel" in joined:
        detected.append("pest-plugin-laravel")
    if "phpunit/phpunit" in joined:
        detected.append("phpunit")
    if "mockery/mockery" in joined:
        detected.append("mockery")
    return sorted(detected)


def detect_first_party(names: list[str]) -> list[str]:
    detected = set()
    for name in names:
        if not name.startswith("laravel/"):
            continue
        short = name.split("/", 1)[1]
        if short in FIRST_PARTY:
            detected.add(short)
    return sorted(detected)


def read_php_version_file(root: Path) -> str | None:
    path = root / ".php-version"
    if not path.is_file():
        return None
    return normalize_version(path.read_text(encoding="utf-8").strip())


def scan_config_keys(root: Path) -> list[str]:
    keys: set[str] = set()
    example = root / ".env.example"
    if example.is_file():
        for line in example.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            match = re.match(r"^([A-Z][A-Z0-9_]*)\s*=", stripped)
            if match:
                keys.add(match.group(1))
    config_dir = root / "config"
    if config_dir.is_dir():
        for path in config_dir.glob("*.php"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for match in re.finditer(r"\benv\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]", text):
                keys.add(match.group(1))
    return sorted(keys)


def scan_test_layout(root: Path) -> dict:
    tests = root / "tests"
    return {
        "unit": (tests / "Unit").is_dir(),
        "feature": (tests / "Feature").is_dir(),
        "pestConfig": (tests / "Pest.php").is_file(),
    }


def scan_architecture(root: Path) -> list[str]:
    app = root / "app"
    relative_dirs = (
        "Actions",
        "Services",
        "Repositories",
        "Jobs",
        "Policies",
        "Rules",
        "Http/Requests",
        "Http/Resources",
        "Enums",
        "Observers",
        "Domain",
        "Modules",
    )
    return sorted(name for name in relative_dirs if (app / name).is_dir())


def scan_coverage_source(root: Path) -> bool:
    for name in ("phpunit.xml", "phpunit.xml.dist"):
        path = root / name
        if not path.is_file():
            continue
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            return False
        for element in tree.getroot().iter():
            if element.tag.endswith("source") or element.tag.endswith("coverage"):
                for child in element.iter():
                    if child.tag.endswith("directory"):
                        return True
    return False


def detect_stack(root: Path) -> dict:
    root = Path(root).resolve()
    find_descriptor(root)
    composer = load_json(root / DESCRIPTOR)
    lock = load_lock(root)

    require = composer.get("require") or {}
    require_dev = composer.get("require-dev") or {}
    platform = (composer.get("config") or {}).get("platform") or {}
    packages = lock.get("packages", []) if lock else []
    packages_dev = lock.get("packages-dev", []) if lock else []

    php_constraint = require.get("php")
    laravel_constraint = require.get("laravel/framework")
    php_version_file = read_php_version_file(root)
    php_platform = platform.get("php")
    php_lock = (lock or {}).get("platform-overrides", {}).get("php")
    laravel_lock = locked_version(packages, "laravel/framework")

    php_version = (
        normalize_version(php_version_file)
        or normalize_version(php_platform)
        or normalize_version(php_lock)
        or parse_php_floor(php_constraint)
    )
    laravel_version = laravel_lock or normalize_constraint(laravel_constraint)

    if php_version_file:
        php_source = "php-version"
    elif php_platform:
        php_source = "platform"
    elif php_lock:
        php_source = "lock"
    elif php_constraint:
        php_source = "constraint"
    else:
        php_source = None

    laravel_source = "lock" if laravel_lock else "constraint" if laravel_constraint else None

    dependency_names = list(require) + list(require_dev)
    dependency_names += [
        str(package.get("name", ""))
        for package in packages + packages_dev
        if isinstance(package, dict) and package.get("name")
    ]
    test_dependencies = detect_test_dependencies(dependency_names)
    first_party = detect_first_party(dependency_names)
    coverage_source = scan_coverage_source(root)
    test_layout = scan_test_layout(root)

    warnings: list[dict] = []
    blockers: list[dict] = []
    if not php_version:
        blockers.append(item("missing-php-version", "PHP version not found in composer.json.", DESCRIPTOR))
    if not laravel_version:
        blockers.append(
            item("missing-laravel-version", "laravel/framework not found in composer.json.", DESCRIPTOR)
        )
    if laravel_source == "constraint":
        warnings.append(item("inexact-laravel-version", "Laravel version comes from a range constraint.", DESCRIPTOR))
    if php_source == "constraint":
        warnings.append(item("inexact-php-version", "PHP version comes from a range constraint.", DESCRIPTOR))
    if lock is None:
        warnings.append(item("missing-lock", "composer.lock is absent; exact versions are unavailable.", DESCRIPTOR))
    if laravel_lock and laravel_constraint and constraint_major(laravel_constraint) != parse_major(laravel_lock):
        warnings.append(
            item("version-source-conflict", "composer.json and composer.lock disagree on the Laravel major.", DESCRIPTOR)
        )
    if "pest" not in test_dependencies:
        warnings.append(item("pest-missing", "pestphp/pest is not installed in the project.", DESCRIPTOR))
    if not coverage_source:
        warnings.append(item("coverage-source-missing", "phpunit.xml has no <source><include> directory.", "phpunit.xml"))

    return {
        "projectRoot": str(root),
        "descriptor": DESCRIPTOR,
        "packageManager": "composer",
        "php": {"version": php_version, "constraint": php_constraint, "source": php_source},
        "laravel": {
            "version": laravel_version,
            "constraint": laravel_constraint,
            "major": parse_major(laravel_version),
            "source": laravel_source,
        },
        "firstPartyPackages": first_party,
        "testDependencies": test_dependencies,
        "capabilities": {
            "pest": "pest" in test_dependencies,
            "pestLaravelPlugin": "pest-plugin-laravel" in test_dependencies,
            "mockery": "mockery" in test_dependencies,
            "coverageConfigured": coverage_source,
            "coverageDriver": "unknown",
        },
        "testLayout": test_layout,
        "architecturePatterns": scan_architecture(root),
        "configKeys": scan_config_keys(root),
        "warnings": warnings,
        "blockers": blockers,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detect_stack.py",
        description="Detect PHP, Laravel, packages and Pest setup from a Composer project.",
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root directory.")
    parser.add_argument("--output", help="Write the JSON result to this path.")
    parser.add_argument("--json", action="store_true", help="Print the JSON result to stdout.")
    parser.add_argument("--strict", action="store_true", help="Fail when warnings are present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = detect_stack(Path(args.root))
    except ConfigError as exc:
        print(f"[ERROR] config: {exc}", file=sys.stderr)
        return EXIT_CONFIG
    except ParseError as exc:
        print(f"[ERROR] parse: {exc}", file=sys.stderr)
        return EXIT_PARSE

    payload = json.dumps(data, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    if args.json or not args.output:
        print(payload)

    if data["blockers"]:
        return EXIT_CONFIG
    if args.strict and data["warnings"]:
        return EXIT_STRICT
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
