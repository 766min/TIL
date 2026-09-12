#!/usr/bin/env python3
"""README.md의 학습 현황 뱃지/표를 각 폴더의 .md 파일 개수 기준으로 자동 갱신한다."""

import re
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"

# (폴더명, 표에 표시할 라벨) — 표시 순서 그대로 유지
CATEGORIES = [
    ("GIT HUB", "🔧 GIT HUB"),
    ("PYTHON", "🐍 PYTHON"),
    ("ML", "🤖 ML"),
    ("SQL", "🗄️ SQL"),
]

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def collect_dates(folder: Path):
    dates = []
    if not folder.exists():
        return dates
    for f in folder.iterdir():
        m = DATE_RE.match(f.name)
        if m:
            dates.append(datetime.strptime(m.group(1), "%Y-%m-%d").date())
    return sorted(dates)


def fmt(d):
    return d.strftime("%Y.%m.%d")


def build_stats_table():
    rows = []
    total_count = 0
    all_dates = []

    for folder_name, label in CATEGORIES:
        dates = collect_dates(REPO_ROOT / folder_name)
        count = len(dates)
        total_count += count
        all_dates.extend(dates)
        if dates:
            period = f"{fmt(dates[0])} ~ {fmt(dates[-1])}"
        else:
            period = "-"
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

    stats_table, total_count, all_dates = build_stats_table()
    badges = build_badges(total_count, all_dates)

    text = replace_block(text, "<!-- STATS:START -->", "<!-- STATS:END -->", stats_table)
    text = replace_block(text, "<!-- BADGES:START -->", "<!-- BADGES:END -->", badges)

    README_PATH.write_text(text, encoding="utf-8")
    print(f"README 업데이트 완료 — 총 {total_count}개 노트")


if __name__ == "__main__":
    main()
