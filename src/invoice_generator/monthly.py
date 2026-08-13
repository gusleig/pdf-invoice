"""Monthly invoice runner.

Reads per-company configs from companies/*.yaml, previews the next invoice
(number, period, value) and generates it with a company-tagged filename.
The invoice counter (last_invoice_number) is bumped in the YAML after each run.
"""

import argparse
import glob
import os
import sys
from datetime import datetime, timedelta

import yaml

from invoice_generator.generator import InvoiceGenerator, ensure_output_directory

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COMPANIES_DIR = os.path.join(PROJECT_ROOT, "companies")

MONTHS_PT = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def previous_month(due_date):
    """Return (first_day, last_day) of the month before due_date."""
    first_of_due_month = due_date.replace(day=1)
    last_day = first_of_due_month - timedelta(days=1)
    return last_day.replace(day=1), last_day


def list_company_files(only_slug=None):
    files = sorted(glob.glob(os.path.join(COMPANIES_DIR, "*.yaml")))
    files = [f for f in files if os.path.basename(f) != "example.yaml"]
    if only_slug:
        files = [
            f for f in files if os.path.splitext(os.path.basename(f))[0] == only_slug
        ]
    return files


def build_params(company, invoice_number, due_date, total_value):
    defaults = company["defaults"]
    start, end = previous_month(due_date)
    item = defaults["item"].format(
        start_day=start.day,
        end_day=end.day,
        month_pt=MONTHS_PT[start.month - 1],
        month_en=start.strftime("%B"),
        year=start.year,
    )
    return argparse.Namespace(
        name=defaults["name"],
        company=defaults["company"],
        invoice_number=invoice_number,
        language=defaults["language"],
        due_date=due_date.strftime("%Y%m%d"),
        bill_to=defaults["bill_to"],
        ship_to=defaults["ship_to"],
        item=item,
        payment_terms=defaults["payment_terms"],
        total_value=float(total_value),
        currency=defaults["currency"],
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate the monthly invoice for each company"
    )
    parser.add_argument(
        "company",
        nargs="?",
        help="Company slug (companies/<slug>.yaml). Default: all companies",
    )
    parser.add_argument("--due-date", help="Due date (YYYYMMDD). Default: today")
    parser.add_argument("--total", type=float, help="Override total value for this run")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview only, generate nothing"
    )
    parser.add_argument(
        "-y", "--yes", action="store_true", help="Generate without confirmation"
    )
    args = parser.parse_args()

    files = list_company_files(args.company)
    if not files:
        sys.exit(
            f"No company config found in {COMPANIES_DIR}"
            + (f" for slug '{args.company}'" if args.company else "")
        )

    due_date = (
        datetime.strptime(args.due_date, "%Y%m%d")
        if args.due_date
        else datetime.today()
    )
    output_dir = os.path.join(PROJECT_ROOT, "invoices")
    ensure_output_directory(output_dir)

    for path in files:
        with open(path, "r") as f:
            company = yaml.safe_load(f)

        slug = company["slug"]
        invoice_number = company["last_invoice_number"] + 1
        total_value = (
            args.total if args.total is not None else company["defaults"]["total_value"]
        )
        params = build_params(company, invoice_number, due_date, total_value)
        start, _ = previous_month(due_date)
        filename = f"invoice_{slug}_{invoice_number}_{start.strftime('%Y-%m')}.pdf"
        output_path = os.path.join(output_dir, filename)

        print(f"\n[{slug}] {company['defaults']['company']}")
        print(f"  Invoice number: #{invoice_number}")
        print(
            f"  Period:         {params.item.split(chr(10))[0]}"
            f" ({start.strftime('%b %Y')})"
        )
        print(f"  Due date:       {due_date.strftime('%Y-%m-%d')}")
        print(f"  Total:          {params.currency} {params.total_value:,.2f}")
        print(f"  Output:         invoices/{filename}")

        if args.dry_run:
            continue
        if os.path.exists(output_path):
            print(f"  Skipped: invoices/{filename} already exists")
            continue
        if not args.yes:
            answer = input("  Generate? [y/N] ").strip().lower()
            if answer not in ("y", "yes"):
                print("  Skipped")
                continue

        InvoiceGenerator(params).generate(output_path)
        company["last_invoice_number"] = invoice_number
        with open(path, "w") as f:
            yaml.safe_dump(company, f, allow_unicode=True, sort_keys=False)
        print(f"  Generated: invoices/{filename}")


if __name__ == "__main__":
    main()
