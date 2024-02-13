"""Module for creating interactive menu in console."""
from __future__ import annotations

import os
import sys

from task3_dsw.database import AddInvoice, AddPayment, Database, Invoice, Payment
from task3_dsw.logger import logger
from task3_dsw.nbp_api import NBPApiClient, NBPApiError


class Action:
    """Action class for creating action in interactive menu."""

    def __init__(self, name: str, tag: str, description: str) -> None:
        """Initialize Action class."""
        self.name = name
        self.tag = tag
        self.description = description

    def __str__(self) -> str:
        """Return name of action."""
        return f"{self.name}"

    def execute(self) -> None:
        """Execute action."""
        logger.debug("Execute action: %s", self.name)


class WithDatabaseAction(Action):
    """WithDatabaseAction class for creating action with database in interactive menu."""

    def __init__(
        self, name: str, tag: str, description: str, database: Database
    ) -> None:
        """Initialize AddInvoiceAction class."""
        super().__init__(name, tag, description)
        self.database = database

    def get_avaiable_currency(self) -> str:
        """Get avaiable currencies from settings and add PLN."""
        avaiable_currency = ", ".join(self.database.settings.CURRENCIES)
        if "PLN" not in self.database.settings.CURRENCIES:
            avaiable_currency += ", PLN"
        return avaiable_currency

    def print_available_invoices(self, invoices: list[Invoice]) -> str:
        """
        Print available invoices.

        Args:
        ----
            invoices: list of invoices

        Returns:
        -------
            str: string with invoices
        """
        # With id number to choice in menu
        available_invoice = "\n".join(
            [f"{invoices.index(invoice)} - {invoice}" for invoice in invoices]
        )
        print(
            f"Dostepne faktury: \n Invoice index - <id | amount | currency | date> \n {available_invoice}"
        )

    def print_available_payments(self, payments: list[Payment]) -> str:
        """
        Print available payments.

        Args:
        ----
            payments: list of payments

        Returns:
        -------
            str: string with payments

        """
        # With id number to choice in menu
        available_payments = "\n".join(
            [f"{payments.index(payment)} - {payment}" for payment in payments]
        )
        print(
            f"Dostepne płatności dla tej faktury: \n  Invoice index - <id | invoice_id | currency | date> \n {available_payments}"
        )

    def ask_for_invoice_index(self) -> Invoice | None:
        """
        Ask user for invoice index.

        Returns
        -------
            int: invoice index
        """
        self.database.load()
        invoices = self.database.get_invoices()
        self.print_available_invoices(invoices)
        invoice_index = int(input("Wprowadz index faktury: "))

        # Get invoice from database
        invoice = self.database.get_invoice(invoice_index=invoice_index)

        # Check if invoice exists in database
        if invoice is None:
            logger.error(f"Invoice with index {invoice_index} not exists.")
            return None
        # Print invoice
        print(f"Wybrałes fakture {invoice}")
        return invoice

    def ask_for_payment_index(self, invoice: Invoice) -> Payment | None:
        """
        Ask user for payment index.

        Returns
        -------
            int: payment index
        """
        payments = self.database.get_payments(invoice)

        if len(payments) == 0:
            msg = f"Brak płatnosci dla faktury {invoice}"
            raise ValueError(msg)

            # Print available payments
        self.print_available_payments(payments)

        payment_index = int(input("Wprowadz index płatności: "))
        # Load data from database
        self.database.load()

        try:
            return payments[payment_index]
        except IndexError as e:
            msg = f"Payment with index {payment_index} not exists."
            raise ValueError(msg) from e


class ExitAction(Action):
    """ExitAction class for creating exit action in interactive menu."""

    def execute(self) -> None:
        """Execute action."""
        logger.debug("Execute action: %s", self.name)
        sys.exit(0)


class AddInvoiceAction(WithDatabaseAction):
    """AddInvoiceAction class for creating add invoice action in interactive menu."""

    def execute(self) -> None:
        """Execute action for adding invoice."""
        try:
            # Get avaiable currencies from settings and add PLN
            avaiable_currency = self.get_avaiable_currency()

            # Ask user for invoice data
            amount = float(input("Wprowadź kwote faktury: "))
            currency = input(f"Wprowadź walute [{avaiable_currency}]: ")
            date = input("Wprowadź date: [YYYY-MM-DD]: ")

            # Load data from database
            self.database.load()

            # Add invoice to database
            invoice_schema = self.database.add_invoice(
                invoice=AddInvoice(
                    amount=amount,
                    currency=currency,
                    date=date,
                )
            )

            # Save data to database
            logger.debug("Added invoice: %s", invoice_schema)
            self.database.save()
        except ValueError as e:
            logger.error("Invalid value: %s", e)
        except FileNotFoundError as e:
            logger.error("Something went wrong: %s", e)


class AddPaymentAction(WithDatabaseAction):
    """AddPaymentAction class for creating add payment action in interactive menu."""

    def execute(self) -> None:
        """Execute action for adding payment."""
        try:
            # Get avaiable currencies from settings and add PLN
            avaiable_currency = self.get_avaiable_currency()

            # Ask user for payment data
            invoice = self.ask_for_invoice_index()
            if invoice is None:
                return
            amount = float(input("Wprowadź kwote: "))
            currency = input(f"Wprowadź walute [{avaiable_currency}]: ")
            date = input("Wprowadź date: [YYYY-MM-DD]: ")
            # Load data from database
            self.database.load()

            # Add payment to database
            payment_schema = self.database.add_payment(
                invoice=invoice,
                payment=AddPayment(amount=amount, currency=currency, date=date),
            )

            # Save data to database
            logger.debug("Added payment: %s", payment_schema)
            self.database.save()
        except ValueError as e:
            logger.error("Invalid value: %s", e)

        except FileNotFoundError as e:
            logger.error("Something went wrong: %s", e)


class CalculateExchangeRateDifferenceAction(WithDatabaseAction):
    """Calculate exchange rate difference action in interactive menu."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        tag: str,
        description: str,
        database: Database,
        nbp_api_client: NBPApiClient,
    ) -> None:
        """Initialize CalculateExchangeRateDifferenceAction class."""
        super().__init__(name, tag, description, database)
        self.nbp_api_client = nbp_api_client

    def execute(self) -> None:
        """Execute action for calculating exchange rate difference."""
        try:
            # Load data from database
            self.database.load()
            invoice = self.ask_for_invoice_index()

            if invoice is None:
                return

            payment = self.ask_for_payment_index(invoice)

            # Calculate exchange rate difference

            exchange_rate_difference = self.database.calculate_difference(
                invoice=invoice, payment=payment
            )
            logger.debug("Exchange rate difference: %s", exchange_rate_difference)

            if exchange_rate_difference == 0:
                print("Brak różnicy kursowej")
                return
            # Print exchange rate difference
            print(
                f""""
**Różnica kursowa**: \n
Różnica: {exchange_rate_difference} {payment.currency} \n
"""
            )
            self.database.save()
        except ValueError as e:
            logger.error("Invalid value: %s", e)

        except FileNotFoundError as e:
            logger.error("Something went wrong: %s", e)

        except NBPApiError as e:
            logger.error("Something went wrong: %s", e)


class CheckInvoiceStatusAction(WithDatabaseAction):
    """CheckInvoiceStatusAction class for creating check invoice status action in interactive menu."""

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        tag: str,
        description: str,
        database: Database,
        nbp_api_client: NBPApiClient,
    ) -> None:
        """Initialize CalculateExchangeRateDifferenceAction class."""
        super().__init__(name, tag, description, database)
        self.nbp_api_client = nbp_api_client

    def execute(self) -> None:
        """Execute action for checking invoice status."""
        try:
            self.database.load()
            invoice = self.ask_for_invoice_index()
            if invoice is None:
                return
            (
                sum_of_payments,
                invoice_amount,
                status,
            ) = self.database.calulate_payments_for_invoice(invoice=invoice)
            self.database.save()
            print(
                f"Kwota faktury: <{invoice.amount} | {invoice.currency}> {invoice_amount:.2f} PLN"
            )
            print(f"Suma płatności: {sum_of_payments:.2f} PLN")
            print(f"Status faktury: {status.value}")

        except (FileNotFoundError, ValueError, NBPApiError) as e:
            logger.error("Something went wrong: <%s> %s", e.__class__.__name__, e)


class InteractiveMenu:
    """InteractiveMenu class for creating interactive menu in console."""

    def __init__(self) -> None:
        """Initialize InteractiveMenu class."""
        self.actions = []

    def run(self) -> None:
        """Run interactive menu."""
        while True:
            self.print_actions()
            action_id = input("Choose action: ")
            logger.debug("User choose action: %s", action_id)
            self.run_action(int(action_id))

    def add_action(self, action: Action) -> None:
        """
        Add action to interactive menu.

        Args:
        ----
            action: action to add
        """
        self.actions.append(action)

    def print_actions(self) -> None:
        """Print all actions in interactive menu."""
        for action in self.actions:
            print("{}. {}".format(self.actions.index(action) + 1, action))  # noqa: UP032

    def run_action(self, action_id: int) -> None:
        """
        Run action from interactive menu.

        Args:
        ----
            action_id: id of action

        Raises:
        ------
            IndexError: if action with given id not exists
        """
        try:
            os.system("clear")  # noqa: S605, S607
            action = self.actions[action_id - 1]
            logger.debug("Run action: %s", action)
            print(f"**{action.name}**\n{action.description}\n")
            action.execute()
        except IndexError:
            logger.error("Action with id %s not exists.", action_id)
