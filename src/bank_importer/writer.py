import csv
from collections.abc import Sequence
from pathlib import Path

from .models import Transaction


def write_csv(transactions: Sequence[Transaction], output_path: Path) -> None:
    """Write transactions to a CSV file in standardized format."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount", "opposing_account"])
        for t in transactions:
            writer.writerow([
                t.date.isoformat(),
                t.description,
                str(t.amount),
                t.opposing_account,
            ])
