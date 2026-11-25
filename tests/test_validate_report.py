import json

import pytest

import validate_report as vr


@pytest.fixture
def valid(fixtures):
    return (fixtures / "valid_report.md").read_text(encoding="utf-8")


def mutate(text, old, new):
    assert old in text
    return text.replace(old, new, 1)


def codes(report):
    return {issue.code for issue in report.errors}


def run(text, min_coverage=80, strict=False):
    report = vr.Report()
    vr.validate_report(text, report, min_coverage=min_coverage, strict=strict)
    return report


def test_valid_fixture_passes(valid):
    report = run(valid)

    assert report.ok
    assert report.errors == []


def test_missing_artifact_marker(valid):
    text = mutate(valid, "<!-- php-laravel:artifact type=implementation version=1 -->", "")

    assert "missing-artifact-marker" in codes(run(text))


def test_wrong_artifact_type(valid):
    text = mutate(valid, "type=implementation", "type=review")

    assert "wrong-artifact-type" in codes(run(text))


def test_wrong_artifact_version(valid):
    text = mutate(valid, "version=1 -->", "version=2 -->")

    assert "artifact-version" in codes(run(text))


def test_duplicate_artifact_marker(valid):
    text = valid + "\n<!-- php-laravel:artifact type=implementation version=1 -->\n"

    assert "duplicate-artifact-marker" in codes(run(text))


def test_missing_section(valid):
    text = mutate(valid, "<!-- php-laravel:section id=evidence -->", "<!-- php-laravel:section id=proof -->")

    assert "missing-section" in codes(run(text))
    assert "unknown-section" in codes(run(text))


def test_duplicate_section(valid):
    text = valid + "\n<!-- php-laravel:section id=analysis -->\ncontent\n"

    assert "duplicate-section" in codes(run(text))


def test_empty_section(valid):
    start = valid.index("<!-- php-laravel:section id=design -->")
    end = valid.index("<!-- php-laravel:section id=implementation -->")
    text = valid[:start] + "<!-- php-laravel:section id=design -->\n\n" + valid[end:]

    assert "empty-section" in codes(run(text))


def test_metadata_is_complete(valid):
    text = mutate(valid, "- Reviewer: PHP Laravel Agent\n", "")

    assert "missing-metadata" in codes(run(text))


def test_invalid_status(valid):
    text = mutate(valid, "- Status: Final", "- Status: Unknown")

    assert "invalid-status" in codes(run(text))


def test_invalid_date(valid):
    text = mutate(valid, "- Date: 2026-11-25", "- Date: 25-11-2026")

    assert "invalid-date" in codes(run(text))


def test_coverage_below_gate_in_metadata(valid):
    text = mutate(valid, "- Coverage: 88%", "- Coverage: 79%")

    assert "coverage-below-gate" in codes(run(text))


def test_invalid_coverage_format(valid):
    text = mutate(valid, "- Coverage: 88%", "- Coverage: high")

    assert "invalid-coverage" in codes(run(text))


def test_invalid_php_version(valid):
    text = mutate(valid, "- PHP Version: 8.3", "- PHP Version: latest")

    assert "invalid-php-version" in codes(run(text))


def test_invalid_laravel_version(valid):
    text = mutate(valid, "- Laravel Version: 12.0", "- Laravel Version: latest")

    assert "invalid-laravel-version" in codes(run(text))


def test_invalid_dependency_source(valid):
    text = mutate(valid, "- Dependency Source: lock", "- Dependency Source: guess")

    assert "invalid-dependency-source" in codes(run(text))


def test_invalid_test_framework(valid):
    text = mutate(valid, "- Test Framework: pest", "- Test Framework: phpunit")

    assert "invalid-test-framework" in codes(run(text))


def test_invalid_coverage_scope_in_metadata(valid):
    text = mutate(valid, "- Coverage Scope: business", "- Coverage Scope: all")

    assert "invalid-coverage-scope" in codes(run(text))


def test_invalid_coverage_tool(valid):
    text = mutate(valid, "- Coverage Tool: pest", "- Coverage Tool: jacoco")

    assert "invalid-coverage-tool" in codes(run(text))


def test_stack_marker_must_match_metadata(valid):
    text = mutate(valid, "source=lock test=pest -->", "source=constraint test=pest -->")

    assert "stack-mismatch" in codes(run(text))


def test_strict_mode_promotes_stack_warning(valid):
    text = mutate(valid, "The detector read `composer.json` and `composer.lock`:", "The detector read the descriptor:")

    report = run(text, strict=True)

    assert "unverified-stack" in {issue.code for issue in report.warnings}
    assert not report.ok


def test_missing_unit_test(valid):
    text = mutate(
        valid,
        "<!-- php-laravel:test id=T-001 framework=pest context=unit mock=true -->",
        "",
    )

    assert "missing-unit-test" in codes(run(text))


def test_missing_feature_test(valid):
    text = mutate(
        valid,
        "<!-- php-laravel:test id=T-002 framework=pest context=feature mock=false -->",
        "",
    )

    assert "missing-feature-test" in codes(run(text))


def test_invalid_test_context(valid):
    text = mutate(valid, "context=feature mock=false", "context=integration mock=false")

    assert "invalid-test-context" in codes(run(text))


def test_invalid_mock_attribute(valid):
    text = mutate(valid, "context=unit mock=true", "context=unit mock=yes")

    assert "invalid-mock-attribute" in codes(run(text))


def test_test_framework_must_be_pest(valid):
    text = mutate(valid, "id=T-001 framework=pest", "id=T-001 framework=phpunit")

    assert "pest-required" in codes(run(text))


def test_duplicate_test_id(valid):
    text = mutate(valid, "id=T-002 framework=pest", "id=T-001 framework=pest")

    assert "duplicate-test-id" in codes(run(text))


def test_invalid_change_status(valid):
    text = mutate(valid, "id=CHG-001 status=implemented", "id=CHG-001 status=unknown")

    assert "invalid-change-status" in codes(run(text))


def test_change_count_must_match(valid):
    text = mutate(valid, "- Changes Applied: 1", "- Changes Applied: 2")

    assert "count-mismatch" in codes(run(text))


def test_missing_change_fields(valid):
    text = mutate(valid, "- Design: The Form Request owns validation/authorization; the Action owns persistence; the controller maps the response.\n", "")

    assert "missing-design" in codes(run(text))


def test_invalid_config_file(valid):
    text = mutate(valid, "id=CFG-001 file=phpunit.xml", "id=CFG-001 file=.env")

    assert "invalid-config-file" in codes(run(text))


def test_no_config_changes_is_allowed(valid):
    start = valid.index("<!-- php-laravel:config id=CFG-001")
    end = valid.index("<!-- php-laravel:section id=evidence -->")
    text = valid[:start] + "No changes.\n\n" + valid[end:]

    assert run(text).ok


def test_missing_config_declaration(valid):
    start = valid.index("<!-- php-laravel:config id=CFG-001")
    end = valid.index("<!-- php-laravel:section id=evidence -->")
    text = valid[:start] + valid[end:]

    assert "missing-config-declaration" in codes(run(text))


def test_missing_coverage_marker(valid):
    text = mutate(
        valid,
        "<!-- php-laravel:coverage value=88 gate=80 tool=pest driver=xdebug scope=business -->",
        "",
    )

    assert "missing-coverage-marker" in codes(run(text))


def test_invalid_coverage_driver(valid):
    text = mutate(valid, "driver=xdebug scope=business", "driver=none scope=business")

    assert "invalid-coverage-driver" in codes(run(text))


def test_invalid_coverage_scope_in_marker(valid):
    text = mutate(valid, "driver=xdebug scope=business", "driver=xdebug scope=all")

    assert "invalid-coverage-scope" in codes(run(text))


def test_coverage_gate_cannot_be_lowered_in_marker(valid):
    text = mutate(valid, "value=88 gate=80", "value=88 gate=70")

    assert "coverage-below-gate" in codes(run(text))


def test_insufficient_validation_checkboxes(valid):
    lines = valid.splitlines(keepends=True)
    text = "".join(line for line in lines if "- [x]" not in line or line.index("- [x]") < 0)

    assert "insufficient-validation" in codes(run(text))


def test_missing_evidence(valid):
    text = mutate(
        valid,
        "<!-- php-laravel:evidence id=EV-001 command=./vendor/bin/pest status=passed -->",
        "",
    )

    assert "missing-evidence" in codes(run(text))


def test_evidence_must_include_passed_status(valid):
    text = mutate(valid, "status=passed -->", "status=partial -->")

    assert "evidence-not-passed" in codes(run(text))


def test_traceability_gap(valid):
    text = mutate(valid, "| CHG-001 | T-002 | EV-001 |\n", "")

    assert "traceability-gap" in codes(run(text))


def test_placeholder_rejected(valid):
    text = valid + "\nTODO finish this section\n"

    assert "placeholder" in codes(run(text))


def test_secret_rejected(valid):
    text = valid + "\npassword=super-secret-value\n"

    assert "secret" in codes(run(text))


def test_approval_verdict_rejected(valid):
    text = valid + "\nLGTM\n"

    assert "approval-verdict" in codes(run(text))


def test_suppression_requires_approval(valid):
    text = valid + "\n@codeCoverageIgnore is used here.\n"

    assert "suppression-without-approval" in codes(run(text))


def test_suppression_with_approval_passes(valid):
    text = valid + "\n@codeCoverageIgnore is used here. Suppression approved.\n"

    assert run(text).ok


def test_custom_min_coverage_gate(valid):
    report = run(valid, min_coverage=90)

    assert "coverage-below-gate" in codes(report)


def test_cli_json_pass(valid, tmp_path, capsys):
    path = tmp_path / "PHP-LARAVEL-IMPL.md"
    path.write_text(valid, encoding="utf-8")

    code = vr.main([str(path), "--json"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "PASS"


def test_cli_fails_on_invalid_report(tmp_path, capsys):
    path = tmp_path / "PHP-LARAVEL-IMPL.md"
    path.write_text("not an artifact\n", encoding="utf-8")

    assert vr.main([str(path)]) == 1
    assert "[ERROR]" in capsys.readouterr().out


def test_cli_reports_missing_file(tmp_path, capsys):
    assert vr.main([str(tmp_path / "missing.md")]) == 1
    assert "missing-report" in capsys.readouterr().out
