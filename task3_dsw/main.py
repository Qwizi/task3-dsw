"""Main module of the program."""


import argparse

from task3_dsw import nbp_api
from task3_dsw.invoices import (
    create_invoices_file,
)
from task3_dsw.logger import logger
from task3_dsw.payments import (
    create_payments_file,
)
from task3_dsw.settings import Settings


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
    return parser


def main() -> None:
    """Main function of the program."""
    # Create parser for command line arguments and parse them
    parser = create_parser()
    args = parser.parse_args()

    # Create files if not exists
    create_invoices_file()
    create_payments_file()

    settings = Settings()

    # if args.currencies exists then set settings.CURRENCIES to args.currencies -> https://trello.com/c/JDvW1IvO
    if args.currencies:
        settings.CURRENCIES = args.currencies

    # initialize NBPApiClient with settings
    nbp_api_client = nbp_api.NBPApiClient(settings)

    if args.interactive:
        logger.warning("We are in interactive mode.")
    else:
        exchange_rate_response = nbp_api_client.get_exchange_rate(
            nbp_api.ExchangeRateSchema(
                table="A",
                code="USD",
                date="2021-07-01",
            )
        )
        logger.info(exchange_rate_response)
        logger.info("We are in non-interactive mode.")


if __name__ == "__main__":
    main()
