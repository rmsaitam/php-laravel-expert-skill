import json
import shutil

import pytest

import detect_stack as ds


def make_project(
    tmp_path,
    *,
    composer=None,
    lock=None,
    env=None,
    phpunit=None,
    layout=True,
):
    project = tmp_path / "project"
    project.mkdir()
    if composer:
        shutil.copy(composer, project / "composer.json")
    if lock:
        shutil.copy(lock, project / "composer.lock")
    if env:
        shutil.copy(env, project / ".env.example")
    if phpunit:
        shutil.copy(phpunit, project / "phpunit.xml")
    if layout:
        (project / "tests" / "Unit").mkdir(parents=True)
        (project / "tests" / "Feature").mkdir(parents=True)
        (project / "tests" / "Pest.php").write_text("<?php\n", encoding="utf-8")
        (project / "app" / "Actions").mkdir(parents=True)
        (project / "app" / "Services").mkdir(parents=True)
        (project / "app" / "Http" / "Requests").mkdir(parents=True)
        (project / "config").mkdir(parents=True)
        (project / "config" / "services.php").write_text(
            "<?php\nreturn ['token' => env('PAYMENT_TOKEN', 'unused')];\n",
            encoding="utf-8",
        )
    return project


def codes(items):
    return {item["code"] for item in items}


def test_detects_locked_laravel12_stack(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        composer=fixtures / "composer-laravel12.json",
        lock=fixtures / "composer-lock.json",
        env=fixtures / ".env.example",
        phpunit=fixtures / "phpunit.xml",
    )

    data = ds.detect_stack(project)

    assert data["descriptor"] == "composer.json"
    assert data["packageManager"] == "composer"
    assert data["php"] == {"version": "8.3.4", "constraint": "^8.3", "source": "lock"}
    assert data["laravel"]["version"] == "12.47.0"
    assert data["laravel"]["major"] == 12
    assert data["laravel"]["source"] == "lock"
    assert data["firstPartyPackages"] == ["sanctum", "scout"]
    assert data["testDependencies"] == [
        "mockery",
        "pest",
        "pest-plugin-laravel",
        "phpunit",
    ]
    assert data["capabilities"]["pest"] is True
    assert data["capabilities"]["pestLaravelPlugin"] is True
    assert data["capabilities"]["mockery"] is True
    assert data["capabilities"]["coverageConfigured"] is True
    assert data["capabilities"]["coverageDriver"] == "unknown"
    assert data["testLayout"] == {"unit": True, "feature": True, "pestConfig": True}
    assert data["architecturePatterns"] == ["Actions", "Http/Requests", "Services"]
    assert data["warnings"] == []
    assert data["blockers"] == []


def test_constraint_fallback_produces_warnings(fixtures, tmp_path):
    project = make_project(tmp_path, composer=fixtures / "composer-laravel10.json", layout=False)

    data = ds.detect_stack(project)

    assert data["php"]["version"] == "8.1"
    assert data["php"]["source"] == "constraint"
    assert data["laravel"]["version"] == "10.0"
    assert data["laravel"]["major"] == 10
    assert data["laravel"]["source"] == "constraint"
    assert codes(data["warnings"]) == {
        "inexact-laravel-version",
        "inexact-php-version",
        "missing-lock",
        "pest-missing",
        "coverage-source-missing",
    }
    assert data["blockers"] == []


def test_config_keys_are_collected_without_values(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        composer=fixtures / "composer-laravel12.json",
        lock=fixtures / "composer-lock.json",
        env=fixtures / ".env.example",
        phpunit=fixtures / "phpunit.xml",
    )

    payload = json.dumps(ds.detect_stack(project))

    assert "APP_KEY" in payload
    assert "DB_PASSWORD" in payload
    assert "PAYMENT_TOKEN" in payload
    assert "super-secret-value" not in payload
    assert "https://payments.example.test" not in payload
    assert "unused" not in payload


def test_missing_descriptor_raises_config_error(tmp_path):
    with pytest.raises(ds.ConfigError):
        ds.detect_stack(tmp_path)


def test_malformed_composer_raises_parse_error(tmp_path):
    project = make_project(tmp_path)
    (project / "composer.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(ds.ParseError):
        ds.detect_stack(project)


def test_malformed_lock_raises_parse_error(fixtures, tmp_path):
    project = make_project(tmp_path, composer=fixtures / "composer-laravel12.json")
    (project / "composer.lock").write_text("[]", encoding="utf-8")

    with pytest.raises(ds.ParseError):
        ds.detect_stack(project)


def test_missing_versions_are_blockers(tmp_path):
    project = make_project(tmp_path)
    (project / "composer.json").write_text('{"require": {}}', encoding="utf-8")

    data = ds.detect_stack(project)

    assert codes(data["blockers"]) == {"missing-php-version", "missing-laravel-version"}


def test_version_source_conflict_becomes_warning(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        composer=fixtures / "composer-laravel12.json",
        lock=fixtures / "composer-lock.json",
        phpunit=fixtures / "phpunit.xml",
    )
    lock = json.loads((project / "composer.lock").read_text(encoding="utf-8"))
    lock["packages"][0]["version"] = "v11.5.0"
    (project / "composer.lock").write_text(json.dumps(lock), encoding="utf-8")

    data = ds.detect_stack(project)

    assert data["laravel"]["version"] == "11.5.0"
    assert "version-source-conflict" in codes(data["warnings"])


def test_php_version_file_overrides_constraints(fixtures, tmp_path):
    project = make_project(tmp_path, composer=fixtures / "composer-laravel12.json")
    (project / "composer.lock").write_text(
        json.dumps({"packages": [], "packages-dev": []}), encoding="utf-8"
    )
    (project / ".php-version").write_text("8.4.1\n", encoding="utf-8")

    data = ds.detect_stack(project)

    assert data["php"]["version"] == "8.4.1"
    assert data["php"]["source"] == "php-version"


def test_platform_config_overrides_constraint(fixtures, tmp_path):
    project = make_project(tmp_path, composer=fixtures / "composer-laravel12.json")
    composer = json.loads((project / "composer.json").read_text(encoding="utf-8"))
    composer["config"] = {"platform": {"php": "8.2.7"}}
    (project / "composer.json").write_text(json.dumps(composer), encoding="utf-8")

    data = ds.detect_stack(project)

    assert data["php"]["version"] == "8.2.7"
    assert data["php"]["source"] == "platform"


def test_version_helpers():
    assert ds.normalize_version("v12.47.0") == "12.47.0"
    assert ds.normalize_version("^12.0") is None
    assert ds.normalize_constraint("^12.0") == "12.0"
    assert ds.normalize_constraint(">=8.2") == "8.2"
    assert ds.normalize_constraint("8.1 - 8.3") == "8.1"
    assert ds.normalize_constraint("not-a-version") is None
    assert ds.parse_php_floor(">=8.1 <8.4") == "8.1"
    assert ds.parse_php_floor("*") is None
    assert ds.constraint_major("^11.0") == 11
    assert ds.parse_major("12.47.0") == 12


def test_dependency_helpers():
    assert ds.detect_test_dependencies(
        ["pestphp/pest", "mockery/mockery", "phpunit/phpunit", "pestphp/pest"]
    ) == ["mockery", "pest", "phpunit"]
    assert ds.detect_test_dependencies([]) == []
    assert ds.detect_first_party(
        ["laravel/sanctum", "laravel/framework", "unknown/package", "laravel/horizon"]
    ) == ["horizon", "sanctum"]
    assert ds.locked_version([{"name": "laravel/framework", "version": "v12.0.1"}], "missing") is None


def test_scan_coverage_source_handles_invalid_xml(tmp_path):
    (tmp_path / "phpunit.xml").write_text("<phpunit><broken>", encoding="utf-8")

    assert ds.scan_coverage_source(tmp_path) is False


def test_scan_config_keys_ignores_comments_and_lowercase(tmp_path):
    (tmp_path / ".env.example").write_text(
        "# APP_SECRET=hidden\napp_name=ignored\nAPP_NAME=Acme\n",
        encoding="utf-8",
    )

    assert ds.scan_config_keys(tmp_path) == ["APP_NAME"]


def test_cli_writes_stack_json(fixtures, tmp_path):
    project = make_project(
        tmp_path,
        composer=fixtures / "composer-laravel12.json",
        lock=fixtures / "composer-lock.json",
        phpunit=fixtures / "phpunit.xml",
    )
    output = tmp_path / "stack.json"

    code = ds.main([str(project), "--output", str(output)])

    assert code == ds.EXIT_OK
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["laravel"]["version"] == "12.47.0"


def test_cli_returns_config_code_for_missing_descriptor(tmp_path):
    assert ds.main([str(tmp_path)]) == ds.EXIT_CONFIG


def test_cli_returns_parse_code_for_invalid_composer(tmp_path):
    project = make_project(tmp_path)
    (project / "composer.json").write_text("{", encoding="utf-8")

    assert ds.main([str(project)]) == ds.EXIT_PARSE


def test_cli_strict_mode_fails_on_warnings(fixtures, tmp_path):
    project = make_project(tmp_path, composer=fixtures / "composer-laravel10.json", layout=False)

    assert ds.main([str(project), "--strict"]) == ds.EXIT_STRICT


def test_cli_json_flag_prints_payload(fixtures, tmp_path, capsys):
    project = make_project(
        tmp_path,
        composer=fixtures / "composer-laravel12.json",
        lock=fixtures / "composer-lock.json",
        phpunit=fixtures / "phpunit.xml",
    )

    assert ds.main([str(project), "--json"]) == ds.EXIT_OK
    assert json.loads(capsys.readouterr().out)["php"]["version"] == "8.3.4"
