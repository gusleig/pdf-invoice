import os
import pytest
from datetime import datetime
from invoice_generator.generator import InvoiceGenerator


@pytest.fixture
def sample_params():
    return {
        "name": "John Doe",
        "company_name": "Test Company",
        "invoice_number": 1,
        "language": "en",
        "due_date": "20250215",
        "bill_to": "Client Corp",
        "ship_to": "123 Test St\nTest City, TS\n12345",
        "item": "Test Services",
        "payment_terms": "Month",
        "total_value": 1000.00
    }


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
    expected_start = due_date.replace(day=1).strftime('%b %d, %Y')
    expected_end = due_date.strftime('%b %d, %Y')
    expected_range = f"{expected_start} - {expected_end}"
    assert date_range == expected_range


def test_address_formatting(generator):
    address = "Line 1\\nLine 2\\nLine 3"
    formatted = generator.format_address(address)
    assert formatted == "Line 1<br/>Line 2<br/>Line 3"


def test_language_handling(sample_params):
    # Test English
    generator_en = InvoiceGenerator(sample_params)
    elements_en = generator_en.create_header()
    assert any("INVOICE" in str(element) for element in elements_en)

    # Test Portuguese
    sample_params["language"] = "pt"
    generator_pt = InvoiceGenerator(sample_params)
    elements_pt = generator_pt.create_header()
    assert any("FATURA" in str(element) for element in elements_pt)