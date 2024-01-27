"""Main module of the program."""


import argparse

from task3_dsw import nbp_api, settings
from task3_dsw.invoices import (
    create_invoices_file,
)
from task3_dsw.logger import logger
from task3_dsw.payments import (
    create_payments_file,
)


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

    # if args.currencies exists then set settings.CURRENCIES to args.currencies -> https://trello.com/c/JDvW1IvO
    if args.currencies:
        settings.CURRENCIES = args.currencies

    # initialize NBPApiClient with settings
    nbp_api_client = nbp_api.NBPApiClient()

    if args.interactive:
        logger.warning("We are in interactive mode.")
    else:
        logger.info("We are in non-interactive mode.")
        logger.info(
            nbp_api_client.get_exchange_rate(
                data=nbp_api.ExchangeRateSchema(code="xD", date="2021-01-04")
            )
        )


if __name__ == "__main__":
    main()
