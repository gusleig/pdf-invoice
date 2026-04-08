from datetime import datetime, timedelta
from types import SimpleNamespace
import os

import pytest

from invoice_generator.generator import InvoiceGenerator


@pytest.fixture
def sample_params():
    return SimpleNamespace(
        name="John Doe",
        company="Test Company",
        invoice_number=1,
        language="en",
        due_date="20250215",
        bill_to="Client Corp",
        ship_to="123 Test St\nTest City, TS\n12345",
        item="Test Services",
        payment_terms="Month",
        total_value=1000.00,
        currency="USD",
    )


@pytest.fixture
def generator(sample_params):
    return InvoiceGenerator(sample_params)


def test_invoice_generation(generator, tmp_path):
    output_file = tmp_path / "test_invoice.pdf"
    generator.generate(str(output_file))
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0


def test_date_range_calculation(generator):
    date_range = generator.get_date_range()
    due_date = datetime.strptime(generator.params.due_date, '%Y%m%d')
    if due_date.month == 1:
        previous_month = due_date.replace(year=due_date.year - 1, month=12, day=1)
    else:
        previous_month = due_date.replace(month=due_date.month - 1, day=1)

    if previous_month.month == 12:
        next_month = previous_month.replace(year=previous_month.year + 1, month=1)
    else:
        next_month = previous_month.replace(month=previous_month.month + 1)

    expected_start = previous_month.strftime('%b %d, %Y')
    expected_end = (next_month - timedelta(days=1)).strftime('%b %d, %Y')
    expected_range = f"{expected_start} - {expected_end}"
    assert date_range == expected_range


def test_address_formatting(generator):
    address = "Line 1\\nLine 2\\nLine 3"
    formatted = generator.format_address(address)
    assert formatted == "Line 1<br/>Line 2<br/>Line 3"


def test_language_handling(sample_params):
    # Test English
    generator_en = InvoiceGenerator(sample_params)
    assert generator_en.get_labels()["invoice_title"] == "INVOICE"
    assert generator_en.get_labels()["bill_to"] == "Bill To:"

    # Test Portuguese
    sample_params.language = "pt"
    generator_pt = InvoiceGenerator(sample_params)
    labels_pt = generator_pt.get_labels()
    assert labels_pt["invoice_title"] == "FATURA"
    assert labels_pt["bill_to"] == "Faturar A:"
    assert labels_pt["ship_to"] == "Morada:"
    assert labels_pt["payment_terms"] == "Condições de Pagamento"
    assert labels_pt["due_date"] == "Data de Vencimento"
    assert labels_pt["tax"] == "IVA (0%)"


def test_currency_formatting(sample_params):
    sample_params.currency = "EUR"
    generator = InvoiceGenerator(sample_params)

    assert generator.format_currency(500) == "500,00 €"


def test_brl_currency_formatting(sample_params):
    sample_params.currency = "BRL"
    generator = InvoiceGenerator(sample_params)

    assert generator.format_currency(1234.5) == "R$ 1.234,50"


def test_usd_currency_formatting(sample_params):
    sample_params.currency = "USD"
    generator = InvoiceGenerator(sample_params)

    assert generator.format_currency(1234.5) == "US$ 1,234.50"
