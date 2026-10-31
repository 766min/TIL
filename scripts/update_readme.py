#!/usr/bin/env python3
"""README.md의 폴더 구조/학습 현황/카테고리별 목록을 각 폴더의 .md 파일 기준으로 자동 갱신한다."""

import re
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

# (폴더명, 표/트리에 쓸 짧은 라벨, 트리 설명, 섹션 제목) — 표시 순서 그대로 유지
CATEGORIES = [
    ("GIT HUB", "🔧 GIT HUB", "Git & GitHub 기초", "🔧 GIT HUB"),
    ("PYTHON", "🐍 PYTHON", "파이썬 문법 & 활용", "🐍 PYTHON"),
    ("ML", "🤖 ML", "머신러닝 & 딥러닝", "🤖 ML (머신러닝 & 딥러닝)"),
    ("SQL", "🗄️ SQL", "SQL & 데이터베이스", "🗄️ SQL & 데이터베이스"),
    ("HTML", "🌐 HTML", "HTML & 웹 마크업", "🌐 HTML"),
    ("JS", "⚡ JS", "JavaScript", "⚡ JS"),
    ("TS", "🔷 TS", "TypeScript", "🔷 TS"),
    ("NEXTJS", "⚛️ NEXTJS", "React & Next.js", "⚛️ NEXTJS"),
    ("BACKEND", "🚀 BACKEND", "FastAPI & 백엔드", "🚀 BACKEND"),
]

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
TOPIC_RE = re.compile(r"^##\s*공부한 내용\s*\|\s*(.+?)\s*$")


def collect_entries(folder: Path):
    """해당 폴더의 (날짜, 파일명, 주제) 목록을 날짜순으로 반환한다."""
    entries = []
    if not folder.exists():
        return entries
    for f in folder.iterdir():
        m = DATE_RE.match(f.name)
        if not m:
            continue
        date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        topic = ""
        for line in f.read_text(encoding="utf-8").splitlines():
            tm = TOPIC_RE.match(line.strip())
            if tm:
                topic = tm.group(1)
                break
        entries.append((date, f.name, topic))
    return sorted(entries, key=lambda e: e[0])


def fmt(d):
    return d.strftime("%Y.%m.%d")


def build_tree():
    lines = ["```", "TIL/"]
    for i, (folder_name, _, tree_desc, _) in enumerate(CATEGORIES):
        branch = "└──" if i == len(CATEGORIES) - 1 else "├──"
        padded = f"{folder_name}/".ljust(14)
        lines.append(f"{branch} {padded}{_emoji(folder_name)} {tree_desc}")
    lines.append("```")
    return "\n".join(lines)


def _emoji(folder_name):
    for fn, label, _, _ in CATEGORIES:
        if fn == folder_name:
            return label.split(" ", 1)[0]
    return ""


def build_stats_table(all_entries):
    rows = []
    total_count = 0
    all_dates = []

    for folder_name, label, _, _ in CATEGORIES:
        entries = all_entries[folder_name]
        dates = [d for d, _, _ in entries]
        count = len(dates)
        total_count += count
        all_dates.extend(dates)
        period = f"{fmt(dates[0])} ~ {fmt(dates[-1])}" if dates else "-"
        rows.append(f"| {label} | {count}개 | {period} |")

    if all_dates:
        all_dates.sort()
        total_period = f"**{fmt(all_dates[0])} ~ {fmt(all_dates[-1])}**"
    else:
        total_period = "-"

    table = (
        "| 카테고리 | 노트 수 | 기간 |\n"
        "| --- | --- | --- |\n"
        + "\n".join(rows)
        + f"\n| **합계** | **{total_count}개** | {total_period} |"
    )
    return table, total_count, all_dates


def build_badges(total_count, all_dates):
    if all_dates:
        period_text = f"{fmt(all_dates[0])}_~_{fmt(all_dates[-1])}"
    else:
        period_text = "기록없음"
    badges = (
        f"![Total Notes](https://img.shields.io/badge/총_학습노트-{total_count}개-brightgreen?style=flat-square)\n"
        f"![Period](https://img.shields.io/badge/기록기간-{period_text}-lightgrey?style=flat-square)"
    )
    return badges


def build_lists(all_entries):
    sections = []
    for folder_name, _, _, heading in CATEGORIES:
        entries = all_entries[folder_name]
        if not entries:
            continue
        items = []
        for date, filename, topic in entries:
            link = f"{folder_name}/{filename}" if " " not in folder_name else f"<{folder_name}/{filename}>"
            date_str = date.strftime("%Y-%m-%d")
            if topic:
                items.append(f"- [{date_str}]({link}) — {topic}")
            else:
                items.append(f"- [{date_str}]({link})")
        block = (
            f"## {heading}\n\n"
            f"<details>\n"
            f"<summary>전체 목록 보기 ({len(entries)}개)</summary>\n\n"
            + "\n".join(items)
            + "\n\n</details>"
        )
        sections.append(block)
    return "\n\n---\n\n".join(sections)


def replace_block(text, start_marker, end_marker, new_content):
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker), re.DOTALL
    )
    replacement = f"{start_marker}\n{new_content}\n{end_marker}"
    if not pattern.search(text):
        raise ValueError(f"마커를 찾을 수 없습니다: {start_marker} ~ {end_marker}")
    return pattern.sub(replacement, text)


def main():
    text = README_PATH.read_text(encoding="utf-8")

    all_entries = {folder_name: collect_entries(REPO_ROOT / folder_name) for folder_name, _, _, _ in CATEGORIES}

    tree = build_tree()
    stats_table, total_count, all_dates = build_stats_table(all_entries)
    badges = build_badges(total_count, all_dates)
    lists = build_lists(all_entries)

    text = replace_block(text, "<!-- TREE:START -->", "<!-- TREE:END -->", tree)
    text = replace_block(text, "<!-- STATS:START -->", "<!-- STATS:END -->", stats_table)
    text = replace_block(text, "<!-- BADGES:START -->", "<!-- BADGES:END -->", badges)
    text = replace_block(text, "<!-- LISTS:START -->", "<!-- LISTS:END -->", lists)

    README_PATH.write_text(text, encoding="utf-8")
    print(f"README 업데이트 완료 — 총 {total_count}개 노트")


if __name__ == "__main__":
    main()
