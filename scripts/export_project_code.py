#!/usr/bin/env python3
"""
Собирает исходники PM Meetup (Django + React) в один Markdown с заголовками
по файлам — удобно для обзора архитектуры или контекста для LLM.

Пример из корня репозитория:
  python scripts/export_project_code.py
  python scripts/export_project_code.py -o docs_pm_meetup/exports/code_dump.md
  python scripts/export_project_code.py --include-md
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Каталоги не обходим (артефакты, зависимости, кэш)
SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".venv",
        "venv",
        "env",
        "ENV",
        ".idea",
        "node_modules",
        "build",
        "dist",
        ".next",
        "coverage",
        "htmlcov",
        ".tox",
        ".turbo",
        "staticfiles",
        "media",
        "static",
        "__MACOSX",
        ".obsidian",
        ".cursor",
        "mcps",
        "commits",
        ".docker",
        "eggs",
        ".eggs",
    }
)

# Суффиксы файлов, которые считаем «кодом/текстом» для дампа
TEXT_SUFFIXES = frozenset(
    {
        ".py",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".sh",
        ".ps1",
        ".sql",
        ".ini",
        ".cfg",
        ".conf",
        ".txt",
        ".dot",
        ".example",
        ".gitignore",
        ".gitattributes",
        ".dockerignore",
    }
)

# Имена файлов без суффикса или с нестандартным именем
EXTRA_FILENAMES = frozenset(
    {
        "Dockerfile",
        "Makefile",
        "requirements.txt",
        "manage.py",
        "Procfile",
        "nginx.conf",
        "nginx.prod.conf.template",
    }
)

# Не включать (секреты, локальные БД)
SKIP_FILE_NAMES = frozenset(
    {
        ".env",
        ".env.local",
        ".env.development",
        ".env.production",
        ".env.development.local",
        ".env.production.local",
        ".env.test.local",
        "db.sqlite3",
        "db.sqlite3-journal",
        "local_settings.py",
        "google_sheets_key.json",
        "id_rsa",
        "id_ed25519",
    }
)


def fence_lang(path: Path) -> str:
    s = path.suffix.lower()
    if s == ".py":
        return "python"
    if s in (".yml", ".yaml"):
        return "yaml"
    if s == ".json":
        return "json"
    if s in (".html", ".htm"):
        return "html"
    if s == ".css":
        return "css"
    if s in (".scss", ".sass"):
        return "scss"
    if s == ".less":
        return "less"
    if s in (".js", ".jsx"):
        return "javascript"
    if s in (".ts", ".tsx"):
        return "typescript"
    if s == ".sh":
        return "bash"
    if s == ".ps1":
        return "powershell"
    if s == ".sql":
        return "sql"
    if s == ".toml":
        return "toml"
    if s == ".conf":
        return "nginx"
    if s == ".dot":
        return "dot"
    if s in (".txt", ".gitignore", ".gitattributes", ".dockerignore", ".example"):
        return "text"
    if path.name == "Dockerfile":
        return "dockerfile"
    if path.name == "Makefile":
        return "makefile"
    return ""


def should_include_file(
    path: Path, max_bytes: int, text_suffixes: frozenset[str]
) -> bool:
    name = path.name
    if name in SKIP_FILE_NAMES:
        return False
    if name.endswith(".min.js") or name.endswith(".min.css"):
        return False
    try:
        st = path.stat()
    except OSError:
        return False
    if not path.is_file() or st.st_size > max_bytes:
        return False
    if name in EXTRA_FILENAMES:
        return True
    if path.suffix.lower() in text_suffixes:
        return True
    return False


def iter_code_files(
    root: Path, max_bytes: int, text_suffixes: frozenset[str]
) -> list[Path]:
    """Обход без захода в venv / node_modules / staticfiles — дерево остаётся управляемым."""
    out: list[Path] = []
    root = root.resolve()

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        base = Path(dirpath)
        for name in filenames:
            p = base / name
            if should_include_file(p, max_bytes, text_suffixes):
                out.append(p)
    out.sort(key=lambda x: x.as_posix().lower())
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Экспорт кода PM Meetup в один .md с заголовками по файлам."
    )
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        default=None,
        help="Корень проекта (по умолчанию: родитель каталога scripts/).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help=(
            "Путь к выходному .md "
            "(по умолчанию: docs_pm_meetup/exports/PROJECT_CODE_EXPORT.md)."
        ),
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=512_000,
        help="Пропускать файлы больше этого размера (по умолчанию 512 KiB).",
    )
    parser.add_argument(
        "--include-md",
        action="store_true",
        help="Включать также .md из проекта (кроме самого выходного файла).",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = (args.root or script_dir.parent).resolve()
    out_path = (
        args.output
        if args.output is not None
        else root / "docs_pm_meetup" / "exports" / "PROJECT_CODE_EXPORT.md"
    ).resolve()

    if not root.is_dir():
        print(f"Корень не найден: {root}", file=sys.stderr)
        return 1

    suffixes = set(TEXT_SUFFIXES)
    if args.include_md:
        suffixes.add(".md")
    text_suffixes = frozenset(suffixes)

    files = iter_code_files(root, args.max_bytes, text_suffixes)
    files = [p for p in files if p.resolve() != out_path]

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines: list[str] = [
        "# PM Meetup — экспорт исходного кода",
        "",
        f"_Сгенерировано: {generated}. Корень: `{root.as_posix()}`._",
        "",
        "Стек: Django (backend), React (`frontend/`), Docker/nginx. "
        "Каждый файл — отдельный раздел с путём в заголовке второго уровня.",
        "",
    ]

    for path in files:
        rel = path.relative_to(root).as_posix()
        lang = fence_lang(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            lines.append(f"## `{rel}`")
            lines.append("")
            lines.append(f"_Не удалось прочитать: {e}_")
            lines.append("")
            continue

        lines.append(f"## `{rel}`")
        lines.append("")
        lines.append(f"```{lang}".rstrip())
        if text and not text.endswith("\n"):
            text = text + "\n"
        lines.append(text)
        lines.append("```")
        lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    print(f"Записано файлов: {len(files)}")
    print(f"Выход: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
