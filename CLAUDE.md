# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PDF invoice generator CLI tool that creates professional invoices using ReportLab. Supports English and Portuguese. Users can supply all parameters via CLI flags or set defaults in a `config.yaml` file (copy `example.config.yaml` to `config.yaml`).

## Commands

```bash
# Setup
uv sync --group dev

# Run the CLI
uv run invoice-generator --invoice-number 6 --due-date 20250415 --total-value 10000

# Tests
uv run pytest                       # all tests
uv run pytest tests/test_generator.py::test_invoice_generation  # single test
uv run pytest --cov=src             # with coverage

# Lint & format
uv run black src tests
uv run isort src tests
uv run flake8 src tests
uv run mypy src
```

## Architecture

Single-module package at `src/invoice_generator/generator.py`:

- **`InvoiceGenerator`** — takes a params object (argparse Namespace or dict-like), builds PDF elements via ReportLab Platypus (header, billing info table, line-item table), and writes to file with `generate(output_filename)`.
- **`main()`** — CLI entrypoint registered as `invoice-generator` script. Merges `config.yaml` defaults with CLI args; required-only flags are `--invoice-number`, `--due-date`, `--total-value`.
- **`load_config()`** — reads `config.yaml` from project root (gitignored; `example.config.yaml` is the template).

Date handling: `due_date` is always `YYYYMMDD` format. `get_date_range()` computes the previous calendar month for the invoice period.

Output defaults to `invoices/` directory in project root (auto-created). Override with `--output-dir` or `--output`.

## Key Dependencies

- **reportlab** — PDF generation (Platypus for layout, `SimpleDocTemplate` + `Table`/`Paragraph`)
- **Pillow** — required by reportlab for image support
- **PyYAML** — config file parsing
