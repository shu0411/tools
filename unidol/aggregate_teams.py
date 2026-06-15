"""
UNIDOL チーム集約ツール
チーム名をキーに複数行を1行に集約する。

使い方:
  python aggregate_teams.py output/edited_unidol_teams_reading.csv

  # 出力先を指定
  python aggregate_teams.py output/edited_unidol_teams_reading.csv --output output/aggregated.csv
"""

import csv
import argparse
from collections import defaultdict

OUTPUT_FIELDNAMES = ["team_name", "reading_katakana", "reading_hiragana", "region", "university"]


def aggregate(input_csv: str, output_csv: str) -> None:
    with open(input_csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # team_name ごとに行をグループ化し、year 昇順でソート
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["team_name"]].append(row)
    for name in groups:
        groups[name].sort(key=lambda r: r.get("year", ""))

    def unique_nonempty(values: list[str]) -> list[str]:
        seen = []
        for v in values:
            if v and v not in seen:
                seen.append(v)
        return seen

    results = []
    for team_name, team_rows in groups.items():
        # reading_katakana: year昇順で最初の空白でない値
        reading_katakana = next(
            (r["reading_katakana"] for r in team_rows if r.get("reading_katakana")), ""
        )

        # reading_hiragana / region / university: 重複除去してカンマ区切り
        reading_hiragana = ",".join(unique_nonempty([r.get("reading_hiragana", "") for r in team_rows]))
        region = ",".join(unique_nonempty([r.get("region", "") for r in team_rows]))
        university = ",".join(unique_nonempty([r.get("university", "") for r in team_rows]))

        results.append({
            "team_name": team_name,
            "reading_katakana": reading_katakana,
            "reading_hiragana": reading_hiragana,
            "region": region,
            "university": university,
        })

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    print(f"集約前: {len(rows)} 行  →  集約後: {len(results)} 行")
    print(f"出力: {output_csv}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="入力CSVファイル")
    parser.add_argument("--output", type=str, default=None, help="出力先（省略時は aggregated_teams.csv）")
    args = parser.parse_args()

    output = args.output or "output/aggregated_teams.csv"
    aggregate(args.input, output)


if __name__ == "__main__":
    main()
