#!/usr/bin/env python3
"""Validate YAML documents and shell syntax in the documentation."""

from pathlib import Path
import re
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
FENCE = re.compile(
    r"^```(?P<language>[^\s`]*)[^\n]*\n(?P<body>.*?)^```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)
HEREDOC = re.compile(
    r"<<(?P<delimiter>[A-Za-z_][A-Za-z0-9_]*)[ \t]*\r?\n"
    r"(?P<body>.*?)^[ \t]*(?P=delimiter)[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


def fail(path: Path, line: int, kind: str, message: str) -> None:
    relative = path.relative_to(ROOT)
    print(f"{relative}:{line}: {kind}: {message}", file=sys.stderr)


def validate_yaml(path: Path, body: str, line: int, label: str) -> bool:
    try:
        list(yaml.safe_load_all(body))
        return True
    except yaml.YAMLError as error:
        fail(path, line, label, str(error).splitlines()[0])
        return False


def main() -> int:
    markdown_files = sorted(
        path for path in ROOT.rglob("*.md") if ".git" not in path.parts
    )
    yaml_documents = 0
    shell_blocks = 0
    errors = 0

    for path in markdown_files:
        content = path.read_text(encoding="utf-8")
        for fence in FENCE.finditer(content):
            language = fence.group("language").lower()
            body = fence.group("body")
            line = content.count("\n", 0, fence.start()) + 1

            if language in {"yaml", "yml"}:
                yaml_documents += 1
                errors += not validate_yaml(path, body, line, "YAML")
            elif language in {"shell", "sh", "bash"}:
                shell_blocks += 1
                result = subprocess.run(
                    ["bash", "-n"],
                    input=body,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                if result.returncode:
                    fail(path, line, "shell syntax", result.stderr.strip())
                    errors += 1

                for heredoc in HEREDOC.finditer(body):
                    yaml_documents += 1
                    heredoc_line = line + body.count("\n", 0, heredoc.start())
                    errors += not validate_yaml(
                        path, heredoc.group("body"), heredoc_line, "YAML heredoc"
                    )

    for path in sorted(ROOT.rglob("*.yaml")) + sorted(ROOT.rglob("*.yml")):
        if ".git" in path.parts:
            continue
        yaml_documents += 1
        errors += not validate_yaml(path, path.read_text(encoding="utf-8"), 1, "YAML")

    if errors:
        print(f"Documentation checks found {errors} error(s).", file=sys.stderr)
        return 1

    print(
        f"Validated {len(markdown_files)} Markdown files, {yaml_documents} YAML "
        f"documents, and {shell_blocks} shell examples."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
