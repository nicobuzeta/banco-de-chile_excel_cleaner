from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import xlrd

from ..base import Importer
from ..models import Transaction
from ..registry import ImporterRegistry


@ImporterRegistry.register
class BancoChileCurrentCreditImporter(Importer):
    """Importer for Banco de Chile credit card statements (.xls format)."""

    name = "banco-chile-current-credit"
    description = "Banco de Chile credit card statements (XLS)"
    supported_extensions = (".xls",)

    HEADER_ROW = 17
    DATE_COL = 1
    DESCRIPTION_COL = 4
    CUOTAS_COL = 7
    AMOUNT_COL = 10

    def parse(self, file_path: Path) -> Sequence[Transaction]:
        """Parse transactions from Banco de Chile XLS file."""
        workbook = xlrd.open_workbook(str(file_path))
        sheet = workbook.sheet_by_index(0)

        self._verify_structure(sheet)

        transactions = []
        for row_idx in range(self.HEADER_ROW + 1, sheet.nrows):
            date_val = sheet.cell(row_idx, self.DATE_COL).value
            if not date_val:
                continue

            date_str = str(date_val).strip()
            parsed_date = datetime.strptime(date_str, "%d/%m/%Y").date()

            description = str(sheet.cell(row_idx, self.DESCRIPTION_COL).value).strip()
            amount = Decimal(str(int(sheet.cell(row_idx, self.AMOUNT_COL).value)))

            cuotas = str(sheet.cell(row_idx, self.CUOTAS_COL).value).strip()
            if cuotas != "01/01":
                raise ValueError(f"Expected cuotas '01/01', got '{cuotas}'")

            transactions.append(
                Transaction(
                    date=parsed_date,
                    description=description,
                    amount=amount * -1,
                )
            )

        return transactions

    def _verify_structure(self, sheet: xlrd.sheet.Sheet) -> None:
        """Verify the Excel file has the expected structure."""
        expected = [
            (self.DATE_COL, "Fecha"),
            (self.DESCRIPTION_COL, "Descripción"),
            (self.CUOTAS_COL, "Cuotas"),
        ]
        for col, expected_value in expected:
            actual = sheet.cell(self.HEADER_ROW, col).value
            if actual != expected_value:
                raise ValueError(
                    f"Expected '{expected_value}' at row {self.HEADER_ROW}, "
                    f"col {col}, got '{actual}'"
                )
