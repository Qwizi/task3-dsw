"""Main module of the program."""


import argparse

from task3_dsw import settings
from task3_dsw.database import Database
from task3_dsw.logger import logger
from task3_dsw.menu import (
    AddInvoiceAction,
    AddPaymentAction,
    CalculateExchangeRateDifferenceAction,
    CheckInvoiceStatusAction,
    ExitAction,
    InteractiveMenu,
)
from task3_dsw.nbp_api import NBPApiClient


def create_parser() -> argparse.ArgumentParser:
    """Create parser for command line arguments."""
    parser = argparse.ArgumentParser(
        description="Program for calculating exchange rate differences."
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Interactive mode.",
    )
    parser.add_argument(
        "-c",
        "--currencies",
        nargs="+",
        type=str,
        help="Currency codes.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="File with invoices",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("-o", "--output", type=str, help="Nazwa pliku wynikowego")

    return parser


def main() -> None:
    """Main function of the program."""
    # Create parser for command line arguments and parse them
    parser = create_parser()
    args = parser.parse_args()

    # if args.currencies exists then set settings.CURRENCIES to args.currencies -> https://trello.com/c/JDvW1IvO
    if args.currencies:
        settings.CURRENCIES = args.currencies

    if args.verbose:
        settings.DEBUG = args.verbose
        logger.setLevel("DEBUG")

    # initialize NBPApiClient
    nbp_api_client = NBPApiClient()

    # initialize Database
    database = Database(settings=settings, nbp_api_client=nbp_api_client)
    database.load()

    if args.interactive:
        logger.debug("We are in interactive mode.")
        # initialize InteractiveMenu
        interactive_menu = InteractiveMenu()
        interactive_menu.add_action(
            AddInvoiceAction(
                name="Dodaj fakture",
                tag="add_invoice",
                description="Akcja dodawania faktury do bazy danych",
                database=database,
            )
        )
        interactive_menu.add_action(
            AddPaymentAction(
                name="Dodaj płatność",
                tag="add_payment",
                description="Dodaj płatność",
                database=database,
            )
        )
        interactive_menu.add_action(
            CalculateExchangeRateDifferenceAction(
                name="Oblicz różnice kursów",
                tag="calculate_exchange_rate_difference",
                description="Akcja obliczania różnic kursów",
                database=database,
                nbp_api_client=nbp_api_client,
            )
        )
        interactive_menu.add_action(
            CheckInvoiceStatusAction(
                name="Sprawdź status faktury",
                tag="check_invoice_status",
                description="Akcja sprawdzania statusu faktury.\nWymaga podania numeru faktury.\nDla uproszeczenia przekszalcamy wartosc faktury oraz płatności do PLN.",
                database=database,
                nbp_api_client=nbp_api_client,
            )
        )
        interactive_menu.add_action(
            ExitAction(name="Wyjdź", tag="exit", description="Wyjdź")
        )
        interactive_menu.run()
    else:
        logger.debug("We are in non-interactive mode.")
        if args.file:
            settings.DATABASE_PATH = args.file
            database = Database(
                settings=settings,
                nbp_api_client=nbp_api_client,
                output_file="output.json" if args.output is None else args.output,
            )
            database.load()
            invoices = database.get_invoices()
            for invoice in invoices:
                database.calulate_payments_for_invoice(invoice)
                payments = database.get_payments(invoice.id)
                for payment in payments:
                    database.calculate_difference(invoice, payment)
                database.save()


if __name__ == "__main__":
    main()
