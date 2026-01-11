import csv
import sys
from pathlib import Path

import xlrd
from pydantic import BaseModel, field_validator
from tap import Tap


class Args(Tap):
    input_file: str  # Input Excel file path (.xls)
    output: str | None = None  # Output CSV file path (optional, defaults to input name with .csv)

    def configure(self) -> None:
        self.add_argument("input_file")


class Transaction(BaseModel):
    date: str
    description: str
    cuotas: str
    amount: int
    opposing_account: str = "Cash Account"

    @field_validator("cuotas")
    @classmethod
    def validate_cuotas(cls, v: str) -> str:
        if v != "01/01":
            raise ValueError(f"Expected cuotas '01/01', got '{v}'")
        return v


HEADER_ROW = 17
DATE_COL = 1
DESCRIPTION_COL = 4
CUOTAS_COL = 7
AMOUNT_COL = 10


def verify_structure(sheet: xlrd.sheet.Sheet) -> None:
    """Verify the Excel file has the expected structure."""
    assert sheet.cell(HEADER_ROW, DATE_COL).value == "Fecha", (
        f"Expected 'Fecha' at row {HEADER_ROW}, col {DATE_COL}"
    )
    assert sheet.cell(HEADER_ROW, DESCRIPTION_COL).value == "Descripción", (
        f"Expected 'Descripción' at row {HEADER_ROW}, col {DESCRIPTION_COL}"
    )
    assert sheet.cell(HEADER_ROW, CUOTAS_COL).value == "Cuotas", (
        f"Expected 'Cuotas' at row {HEADER_ROW}, col {CUOTAS_COL}"
    )
    assert sheet.cell(HEADER_ROW, AMOUNT_COL - 2).value == "Monto ($)", (
        f"Expected 'Monto ($)' at row {HEADER_ROW}, col {AMOUNT_COL - 2}"
    )


def parse_transactions(sheet: xlrd.sheet.Sheet) -> list[Transaction]:
    """Parse transactions from the Excel sheet."""
    transactions = []

    for row_idx in range(HEADER_ROW + 1, sheet.nrows):
        date_val = sheet.cell(row_idx, DATE_COL).value
        if not date_val:
            continue

        date = str(date_val).strip()
        description = str(sheet.cell(row_idx, DESCRIPTION_COL).value).strip()
        cuotas = str(sheet.cell(row_idx, CUOTAS_COL).value).strip()
        amount = int(sheet.cell(row_idx, AMOUNT_COL).value)

        transaction = Transaction(
            date=date,
            description=description,
            cuotas=cuotas,
            amount=amount,
        )
        transactions.append(transaction)

    return transactions


def write_csv(transactions: list[Transaction], output_path: Path) -> None:
    """Write transactions to a CSV file."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "description", "amount", "opposing_account"])
        for t in transactions:
            writer.writerow([t.date, t.description, t.amount, t.opposing_account])


def main() -> None:
    args = Args().parse_args()

    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".csv")

    workbook = xlrd.open_workbook(input_path)
    sheet = workbook.sheet_by_index(0)

    verify_structure(sheet)

    transactions = parse_transactions(sheet)

    write_csv(transactions, output_path)

    print(f"Wrote {len(transactions)} transactions to {output_path}")


if __name__ == "__main__":
    main()
