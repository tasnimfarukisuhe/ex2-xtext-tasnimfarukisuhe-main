#!/usr/bin/env python3
"""
Run "mvn clean verify", parse JUnit XML results, and write report.md.
Outputs "points=X/Y" to $GITHUB_OUTPUT when running in GitHub Actions.
Exit code: 1 if any test failed or Maven failed, 0 if all passed.
"""

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

REPORT_PATH = "report.md"


def _extract_maven_error_lines(output: str) -> list[str]:
    lines: list[str] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        lower_line = line.lower()

        is_maven_error = line.startswith("[ERROR]")
        is_tycho_error = " error " in lower_line and "info" not in lower_line
        is_failure_marker = (
            "build failure" in lower_line
            or "failed to execute goal" in lower_line
            or "problems running workflow" in lower_line
        )

        if not (is_maven_error or is_tycho_error or is_failure_marker):
            continue

        # Skip generic Maven guidance noise.
        if "help 1" in lower_line or "re-run maven" in lower_line:
            continue

        cleaned = line
        if cleaned.startswith("[ERROR]"):
            cleaned = cleaned.replace("[ERROR]", "", 1).strip()

        if cleaned and cleaned not in lines:
            lines.append(cleaned)

    return lines[:8]


def read_maven_log(log_path: str) -> tuple[int, list[str]]:
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            output = f.read()
    except FileNotFoundError:
        return 1, ["maven.log not found. Did the Maven build run?"]
    
    # Infer exit code from Maven output
    maven_exit_code = 1 if "BUILD FAILURE" in output else 0
    return maven_exit_code, _extract_maven_error_lines(output)


def _strip_ns(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _candidate_report_files(root: Path) -> list[Path]:
    patterns = [
        "**/target/surefire-reports/TEST-*.xml",
        "**/target/failsafe-reports/TEST-*.xml",
        "**/target/surefire-reports/*.xml",
        "**/target/failsafe-reports/*.xml",
        "**/target/**/TEST-*.xml",
    ]

    found: dict[str, Path] = {}

    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file():
                found[str(path.resolve())] = path

    return sorted(found.values(), key=lambda p: str(p))


def _extract_hint(message: str) -> str:
    # Keep concise, human-readable assertion details and skip stack-trace noise.
    raw_lines = [line.strip() for line in message.splitlines() if line.strip()]
    if not raw_lines:
        return ""

    useful: list[str] = []
    for line in raw_lines:
        if line.startswith("at "):
            continue
        if line.startswith("org.") and "(" in line and ")" in line:
            continue
        useful.append(line)

    if not useful:
        useful = raw_lines

    if useful[0].lower().startswith("java.lang.assertionerror") and len(useful) > 1:
        useful = useful[1:]

    if useful[0].endswith("got:") and len(useful) > 1:
        return " | ".join(useful[:2])

    return " | ".join(useful[:2])


def parse_junit_reports(root: Path) -> dict[str, Any]:
    files = _candidate_report_files(root)

    suites: list[dict[str, Any]] = []
    total = 0
    passed = 0
    failed = 0
    skipped = 0

    for xml_file in files:
        try:
            tree = ET.parse(xml_file)
        except ET.ParseError:
            continue

        xml_root = tree.getroot()
        root_tag = _strip_ns(xml_root.tag)

        if root_tag == "testsuite":
            suite_nodes = [xml_root]
        elif root_tag == "testsuites":
            suite_nodes = [
                node for node in xml_root if _strip_ns(node.tag) == "testsuite"
            ]
        else:
            continue

        for suite in suite_nodes:
            suite_name = suite.attrib.get("name", xml_file.stem)
            cases: list[dict[str, str]] = []

            for case in suite.iter():
                if _strip_ns(case.tag) != "testcase":
                    continue

                class_name = case.attrib.get("classname", "")
                case_name = case.attrib.get("name", "(unnamed test)")

                status = "passed"
                hint = ""

                for child in list(case):
                    child_tag = _strip_ns(child.tag)
                    if child_tag == "skipped":
                        status = "skipped"
                        break
                    if child_tag in ("failure", "error"):
                        status = "failed"
                        hint = _extract_hint(child.attrib.get("message", "") or (child.text or ""))
                        break

                total += 1
                if status == "passed":
                    passed += 1
                elif status == "failed":
                    failed += 1
                else:
                    skipped += 1

                cases.append(
                    {
                        "classname": class_name,
                        "name": case_name,
                        "status": status,
                        "hint": hint,
                    }
                )

            if cases:
                suites.append(
                    {
                        "name": suite_name,
                        "file": xml_file,
                        "cases": cases,
                    }
                )

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "suites": suites,
        "files": files,
    }


def build_report(
    data: dict[str, Any], maven_exit_code: int, maven_error_lines: list[str]
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = data["total"]
    passed = data["passed"]
    failed = data["failed"]
    skipped = data["skipped"]

    if failed == 0 and maven_exit_code == 0:
        overall = "✅ All tests passed"
    elif failed > 0 and maven_exit_code != 0:
        overall = f"❌ Build failed and {failed} test(s) failed"
    elif failed > 0:
        overall = f"❌ {failed} test(s) failed"
    else:
        overall = f"❌ Maven exited with code {maven_exit_code}"

    lines = [
        "# Test Report",
        "",
        f"**{overall}** &nbsp;·&nbsp; {passed}/{total} passing &nbsp;·&nbsp; {skipped} skipped &nbsp;·&nbsp; {now}",
        "",
    ]

    if not data["suites"]:
        if maven_exit_code != 0:
            lines += [
                "Build failed before test reports were produced.",
                "",
            ]
            if maven_error_lines:
                lines.append("### Build Failure Summary")
                lines.append("")
                for error_line in maven_error_lines:
                    lines.append(f"- ❌ {error_line}")
                lines.append("")
        else:
            lines += [
                "No JUnit XML reports were found under `**/target/**`.",
                "",
                "Expected locations include `target/surefire-reports` or `target/failsafe-reports`.",
                "",
            ]
        return "\n".join(lines)

    if maven_exit_code != 0 and maven_error_lines:
        lines += [
            "### Build Failure Summary",
            "",
        ]
        for error_line in maven_error_lines:
            lines.append(f"- ❌ {error_line}")
        lines += [
            "",
        ]

    for suite in data["suites"]:
        suite_path = os.path.relpath(suite["file"]).replace("\\", "/")
        lines.append(f"## `{suite['name']}`")
        lines.append(f"_Source: `{suite_path}`_")
        lines.append("")

        for case in suite["cases"]:
            if case["status"] == "passed":
                icon = "✅"
            elif case["status"] == "failed":
                icon = "❌"
            else:
                icon = "⏭️"

            label = f"{case['classname']}::{case['name']}" if case["classname"] else case["name"]
            lines.append(f"- {icon} {label}")

            if case["status"] == "failed" and case["hint"]:
                lines.append(f"  > 💬 {case['hint']}")

        lines.append("")

    lines += ["---", ""]
    if failed > 0:
        lines.append(
            "> ⚠️ Read the messages above - each one tells you exactly what to implement next."
        )
    elif maven_exit_code != 0:
        lines.append(
            "> ⚠️ Maven failed, but no failed test case was parsed from JUnit XML. Check the Maven logs."
        )
    else:
        lines.append("> 🎉 All tests pass! Your implementation looks promising.")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    maven_exit_code, maven_error_lines = read_maven_log("maven.log")
    data = parse_junit_reports(Path.cwd())

    report = build_report(data, maven_exit_code, maven_error_lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as file_handle:
        file_handle.write(report)
    print("report.md written.")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as file_handle:
            file_handle.write(f"points={data['passed']}/{data['total']}\n")

    has_failures = data["failed"] > 0
    sys.exit(1 if has_failures or maven_exit_code != 0 else 0)
