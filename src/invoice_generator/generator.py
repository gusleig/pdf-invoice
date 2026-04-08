import argparse
from datetime import datetime, timedelta
import os
import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch


class InvoiceGenerator:
    def __init__(self, params):
        self.params = params
        self.styles = getSampleStyleSheet()
        self.init_custom_styles()

    def init_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='InvoiceTitle',
            fontSize=24,
            spaceAfter=30,
            alignment=2  # Right alignment
        ))

        self.styles.add(ParagraphStyle(
            name='InvoiceNumber',
            fontSize=16,
            textColor=colors.gray,
            alignment=2
        ))

        self.styles.add(ParagraphStyle(
            name='BillingLabel',
            parent=self.styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
        ))

        self.styles.add(ParagraphStyle(
            name='BillingValue',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
        ))

    def format_address(self, address):
        return address.replace('\\n', '<br/>')

    def get_labels(self):
        if self.params.language == 'pt':
            return {
                'invoice_title': 'FATURA',
                'bill_to': 'Faturar A:',
                'ship_to': 'Morada:',
                'date': 'Data',
                'payment_terms': 'Condições de Pagamento',
                'due_date': 'Data de Vencimento',
                'total_due': 'Total em Dívida',
                'item': 'ITEM',
                'quantity': 'QUANTIDADE',
                'rate': 'PREÇO',
                'amount': 'VALOR',
                'subtotal': 'Subtotal',
                'tax': 'IVA (0%)',
                'total': 'Total',
            }

        return {
            'invoice_title': 'INVOICE',
            'bill_to': 'Bill To:',
            'ship_to': 'Ship To:',
            'date': 'Date',
            'payment_terms': 'Payment Terms',
            'due_date': 'Due Date',
            'total_due': 'Total Due',
            'item': 'ITEM',
            'quantity': 'QUANTITY',
            'rate': 'RATE',
            'amount': 'AMOUNT',
            'subtotal': 'Subtotal',
            'tax': 'Tax (0%)',
            'total': 'Total',
        }

    def format_currency(self, value):
        currency = getattr(self.params, 'currency', 'USD').upper()
        amount = f"{value:,.2f}"

        if currency == 'EUR':
            return f"{amount.replace(',', 'X').replace('.', ',').replace('X', '.')} €"

        if currency == 'BRL':
            formatted_amount = amount.replace(',', 'X').replace('.', ',').replace('X', '.')
            return f"R$ {formatted_amount}"

        return f"US$ {amount}"

    def get_date_range(self):
        # Get the month before the due date
        due_date = datetime.strptime(self.params.due_date, '%Y%m%d')
        if due_date.month == 1:
            previous_month = due_date.replace(year=due_date.year - 1, month=12, day=1)
        else:
            previous_month = due_date.replace(month=due_date.month - 1, day=1)

        # Calculate the last day of the previous month
        if previous_month.month == 12:
            next_month = previous_month.replace(year=previous_month.year + 1, month=1)
        else:
            next_month = previous_month.replace(month=previous_month.month + 1)
        last_day = (next_month - timedelta(days=1)).day

        start_date = previous_month.strftime('%b %d, %Y')
        end_date = previous_month.replace(day=last_day).strftime('%b %d, %Y')
        return f"{start_date} - {end_date}"

    def create_header(self):
        elements = []
        labels = self.get_labels()

        # Company details
        elements.append(Paragraph(self.params.name, self.styles['Normal']))
        elements.append(Paragraph(self.params.company, self.styles['Normal']))
        elements.append(Spacer(1, 20))

        # Invoice title and number
        elements.append(Paragraph(labels['invoice_title'], self.styles['InvoiceTitle']))
        elements.append(Paragraph(f"#{self.params.invoice_number}", self.styles['InvoiceNumber']))
        elements.append(Spacer(1, 20))

        return elements

    def create_billing_info(self):
        labels = self.get_labels()
        today = datetime.now().strftime('%b %d, %Y')
        due_date = datetime.strptime(self.params.due_date, '%Y%m%d').strftime('%b %d, %Y')
        bill_to = Paragraph(self.format_address(self.params.bill_to), self.styles['BillingValue'])
        ship_to = Paragraph(self.format_address(self.params.ship_to), self.styles['BillingValue'])
        label_style = self.styles['BillingLabel']
        value_style = self.styles['BillingValue']

        data = [
            [
                Paragraph(labels['bill_to'], label_style),
                Paragraph(labels['ship_to'], label_style),
                Paragraph(labels['date'], label_style),
                Paragraph(today, label_style),
            ],
            [bill_to, ship_to,
             Paragraph(labels['payment_terms'], label_style), Paragraph(self.params.payment_terms, value_style)],
            ['', '', Paragraph(labels['due_date'], label_style), Paragraph(due_date, value_style)],
            ['', '', Paragraph(labels['total_due'], label_style),
             Paragraph(self.format_currency(self.params.total_value), value_style)]
        ]

        table = Table(data, colWidths=[1.85 * inch, 2.05 * inch, 1.7 * inch, 0.9 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        return [table, Spacer(1, 20)]

    def create_invoice_table(self):
        labels = self.get_labels()
        headers = [labels['item'], labels['quantity'], labels['rate'], labels['amount']]

        item_desc = f"{self.params.item}\n{self.get_date_range()}"

        data = [headers,
                [Paragraph(item_desc, self.styles['Normal']), '1',
                 self.format_currency(self.params.total_value),
                 self.format_currency(self.params.total_value)]]

        data.extend([
            ['', '', labels['subtotal'], self.format_currency(self.params.total_value)],
            ['', '', labels['tax'], self.format_currency(0)],
            ['', '', labels['total'], self.format_currency(self.params.total_value)]
        ])

        table = Table(data, colWidths=[4 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ]))

        return [table]

    def generate(self, output_filename):
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        elements = []
        elements.extend(self.create_header())
        elements.extend(self.create_billing_info())
        elements.extend(self.create_invoice_table())

        doc.build(elements)


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml')

    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('defaults', {})


def ensure_output_directory(directory):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_parser():
    """Create argument parser with defaults from config."""
    config = load_config()

    parser = argparse.ArgumentParser(description='Generate PDF Invoice')
    parser.add_argument('--name', default=config.get('name'), help='Full name')
    parser.add_argument('--company', default=config.get('company'), help='Company name')
    parser.add_argument('--invoice-number', type=int, required=True, help='Invoice number')
    parser.add_argument('--language', choices=['en', 'pt'], default=config.get('language'), help='Invoice language')
    parser.add_argument('--due-date', required=True, help='Due date (YYYYMMDD)')
    parser.add_argument('--bill-to', default=config.get('bill_to'), help='Bill to company')
    parser.add_argument('--ship-to', default=config.get('ship_to'), help='Shipping address')
    parser.add_argument('--item', default=config.get('item'), help='Item description')
    parser.add_argument('--payment-terms', default=config.get('payment_terms'), help='Payment terms')
    parser.add_argument('--total-value', type=float, required=True, help='Total value')
    parser.add_argument('--currency', choices=['USD', 'EUR', 'BRL'],
                        default=config.get('currency', 'USD').upper(),
                        help='Currency code')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--output-dir', default=config.get('output_dir'),
                        help='Output directory for generated invoices')
    parser.add_argument('--config', help='Path to custom config file')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # If any required values are missing from both command line and config, exit with error
    required_fields = ['name', 'company', 'language', 'bill_to', 'ship_to', 'item', 'payment_terms']
    missing_fields = [field for field in required_fields if getattr(args, field) is None]

    if missing_fields:
        parser.error(f"The following required arguments are missing: {', '.join(missing_fields)}")

    # Determine output directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if args.output_dir:
        # If absolute path is provided, use it as is
        if os.path.isabs(args.output_dir):
            output_dir = args.output_dir
        else:
            # If relative path is provided, make it relative to project root
            output_dir = os.path.join(project_root, args.output_dir)
    else:
        # Default to 'invoices' in project root
        output_dir = os.path.join(project_root, 'invoices')

    ensure_output_directory(output_dir)

    # Generate output filename
    if args.output:
        output_filename = os.path.join(output_dir, args.output)
    else:
        output_filename = os.path.join(output_dir, f"invoice_{args.invoice_number}.pdf")

    generator = InvoiceGenerator(args)
    generator.generate(output_filename)
    print(f"Invoice generated: {output_filename}")


if __name__ == '__main__':
    main()
