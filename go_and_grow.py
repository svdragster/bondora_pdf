import argparse
import locale
import re
from decimal import Decimal

import PyPDF2

if __name__ == '__main__':
    my_parser = argparse.ArgumentParser(
        description='Sum the values in a Bondora Go & Grow statement pdf grouped by payment type'
    )
    my_parser.add_argument(
        'file',
        help='The path to a Bondora Go & Grow statement pdf'
    )
    my_parser.add_argument(
        '--currency',
        default='€',
        help='The currency symbol, e.g. €'
    )

    my_parser.add_argument(
        '--locale',
        help='The locale to parse the values with, e.g. in de_DE.utf8 1,23 is a float(1.23)'
    )

    # Execute parse_args()
    args = my_parser.parse_args()

    if args.locale:
        locale.setlocale(locale.LC_ALL, args.locale)

    pdfFileObj = open(args.file, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

    payment_types_in_sum = {}
    for page in pdfReader.pages:
        # extracting text from page
        text = page.extract_text()
        for line in text.splitlines():
            if re.match(r"\d\d\.\d\d\.\d\d\d\d\s\w+.+", line):
                # 01.01.1970 Transfer €1,23 €1.234,56
                # 01.01.1970 Go & Grow returns  €1,23 €1.234,56
                parts = line.split(f" {args.currency}")
                first_white_space = re.search(r"\s", parts[0]).start()
                payment_type = parts[0][first_white_space + 1:]  # e.g. 'Transfer' or 'Go & Grow returns'

                value = locale.atof(parts[1])
                new_value = payment_types_in_sum.get(payment_type, 0.0) + value
                payment_types_in_sum[payment_type] = new_value

    for k, v in payment_types_in_sum.items():
        decimal = Decimal(v)
        print(f"{k:25}", f"{decimal:10.2f}{args.currency}")

    pdfFileObj.close()
