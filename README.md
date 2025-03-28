# Invoice Generator

A Python-based PDF invoice generator that creates professional invoices with customizable parameters.

## Features

- Generate professional PDF invoices
- Supports both English and Portuguese languages
- Customizable company and billing information
- Automatic date handling and formatting
- Clean and modern invoice design

## Installation

Clone the repository and install the package:

```bash
git clone https://github.com/yourusername/invoice-generator.git
cd invoice-generator
pip install -e .
```

For development installation:

```bash
pip install -e ".[dev]"
```

## Usage

You can use the invoice generator either as a command-line tool or as a Python package.

### Command Line

```bash
invoice-generator \
  --name "Your Name" \
  --company "Your Company" \
  --invoice-number 1 \
  --language en \
  --due-date 20250215 \
  --bill-to "Client Company" \
  --ship-to "123 Street Name\nCity, State\nPostal Code" \
  --item "Service Description" \
  --payment-terms "Month" \
  --total-value 1000.00 \
  --output "invoice.pdf"
```

or a simplified version if you have a config.yaml file:

```bash

invoice-generator --invoice-number 6 --due-date 20250415 --total-value 10000

```

### Python Package

```python
from invoice_generator.generator import InvoiceGenerator

params = {
    "name": "Your Name",
    "company": "Your Company",
    "invoice_number": 1,
    "language": "en",
    "due_date": "20250215",
    "bill_to": "Client Company",
    "ship_to": "123 Street Name\nCity, State\nPostal Code",
    "item": "Service Description",
    "payment_terms": "Month",
    "total_value": 1000.00
}

generator = InvoiceGenerator(params)
generator.generate("invoice.pdf")
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

2. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Run tests:
```bash
pytest
```

4. Format code:
```bash
black src tests
isort src tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.