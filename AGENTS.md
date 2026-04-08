# Repository Guidelines

## Project Structure & Module Organization
This repository uses a `src/` layout. Core code lives in `src/invoice_generator/`, with the CLI entry point and PDF generation logic in `generator.py`. Tests live in `tests/`, currently centered on `tests/test_generator.py`. Root-level files include `pyproject.toml` for packaging and tool configuration, `requirements.txt` and `requirements-dev.txt` for dependencies, and `example.config.yaml` as the template for local invoice defaults.

## Build, Test, and Development Commands
Set up a virtual environment first, then install in editable mode:

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Key commands:

```bash
pytest
pytest --cov=invoice_generator
black src tests
isort src tests
flake8 src tests
mypy src
```

Use `invoice-generator --help` to inspect CLI options. Example local run:

```bash
invoice-generator --invoice-number 6 --due-date 20250415 --total-value 10000
```

## Coding Style & Naming Conventions
Target Python 3.8+ and follow the existing style in `src/invoice_generator/generator.py`: 4-space indentation, snake_case for functions and variables, and PascalCase for classes such as `InvoiceGenerator`. Keep modules focused and small. Format with `black` using the configured 88-character line length, and sort imports with `isort` using the Black profile.

## Testing Guidelines
Tests use `pytest`; files must match `test_*.py` per `pyproject.toml`. Prefer small, behavior-focused tests that exercise invoice generation, date calculations, and CLI/config handling. Use `tmp_path` for PDF output assertions instead of writing into the repository. When changing command-line arguments or config loading, add or update tests in `tests/test_generator.py`.

## Commit & Pull Request Guidelines
Git history is minimal and informal (`first commit`, `read me change`), so use short imperative commit messages moving forward, such as `Add config fallback test` or `Fix output directory handling`. Keep commits narrowly scoped. PRs should include a brief summary, note any CLI or config changes, and attach a sample generated PDF or screenshot when layout changes affect invoice output.

## Configuration Tips
Keep personal billing defaults in a local `config.yaml` derived from `example.config.yaml`. Do not commit real client data, addresses, or generated invoices unless they are sanitized examples.
