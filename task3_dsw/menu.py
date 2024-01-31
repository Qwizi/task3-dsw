"""Module for creating interactive menu in console."""
from __future__ import annotations

import os
import sys

from task3_dsw.database import AddInvoice, AddPayment, Database, Invoice, Payment
from task3_dsw.logger import logger
from task3_dsw.nbp_api import ExchangeRateSchema, NBPApiClient, NBPApiError


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

    def ask_for_payment_index(self, invoice_id: str) -> Payment | None:
        """
        Ask user for payment index.

        Returns
        -------
            int: payment index
        """
        payments = self.database.get_payments(invoice_id=invoice_id)

        if len(payments) == 0:
            msg = f"Brak płatnosci dla faktury {invoice_id}"
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
                payment=AddPayment(
                    amount=amount, currency=currency, date=date, invoice_id=invoice.id
                )
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

            payment = self.ask_for_payment_index(invoice_id=invoice.id)

            # Calculate exchange rate difference
            (
                invoice_exchange_rate,
                payment_exchange_rate,
                exchange_rate_difference,
            ) = self.nbp_api_client.calculate_difference(
                invoice=invoice, payment=payment
            )

            if exchange_rate_difference == 0:
                print("Brak różnicy kursowej")
                return
            # Print exchange rate difference
            print(
                f""""
**Różnica kursowa**: \n
Faktura: <kod waluty: {invoice_exchange_rate.code} | data: {invoice_exchange_rate.rates[0].effectiveDate} | kurs: {invoice_exchange_rate.rates[0].mid}> \n
Płatność: <kod waluty: {payment_exchange_rate.code} | data: {payment_exchange_rate.rates[0].effectiveDate} | kurs: {payment_exchange_rate.rates[0].mid}> \n
Różnica: {exchange_rate_difference:.2f}
"""
            )
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

    def sum_of_payments(self, payments: list[Payment]) -> float:
        """
        Calculate sum of payments.

        For make it easier we calculate sum of payments in PLN.
        So if payment currency is not PLN then we calculate exchange rate.
        """
        sum_of_payments = 0
        for payment in payments:
            # if payment is in PLN then we can add payment amount to sum of payments
            if payment.currency == "PLN":
                sum_of_payments += payment.amount
            # If payment currency is not PLN then we need to calculate exchange rate
            else:
                payment_exchange_rate = self.nbp_api_client.get_exchange_rate(
                    ExchangeRateSchema(
                        table="A", code=payment.currency, date=payment.date
                    )
                )
                sum_of_payments += payment.amount * payment_exchange_rate.rates[0].mid
        return sum_of_payments

    def calculate_invoice_amount(self, invoice: Invoice) -> float:
        """
        Calculate invoice amount.

        For make it easier we calculate invoice amount in PLN.
        So if invoice currency is not PLN then we calculate exchange rate.
        """
        # If invoice currency is not PLN then we need to calculate exchange rate
        if invoice.currency != "PLN":
            invoice_exchange_rate = self.nbp_api_client.get_exchange_rate(
                ExchangeRateSchema(table="A", code=invoice.currency, date=invoice.date)
            )
            return invoice.amount * invoice_exchange_rate.rates[0].mid
        return invoice.amount

    def execute(self) -> None:
        """Execute action for checking invoice status."""
        try:
            self.database.load()
            invoice = self.ask_for_invoice_index()
            if invoice is None:
                return
            payments = self.database.get_payments(invoice_id=invoice.id)
            if len(payments) == 0:
                print("Brak płatności dla tej faktury")
                return
            self.print_available_payments(payments)

            # Calculate sum of payments
            sum_of_payments = self.sum_of_payments(payments=payments)
            # Calculate invoice amount
            invoice_amount = self.calculate_invoice_amount(invoice=invoice)

            print(
                f"Kwota faktury: <{invoice.amount} | {invoice.currency}> {invoice_amount:.2f} PLN"
            )
            print(f"Suma płatności: {sum_of_payments:.2f} PLN")
            print("Status faktury: ", end="")

            # Check invoice status
            # If invoice amount is equal to sum of payments then invoice is paid
            if invoice_amount == sum_of_payments:
                print("Faktura opłacona")
            # If invoice amount is greater than sum of payments then invoice is not paid
            elif invoice_amount > sum_of_payments:
                print(
                    f"Brakuje {invoice_amount - sum_of_payments:.2f} PLN do opłacenia faktury"
                )
            # If invoice amount is less than sum of payments then invoice is overpaid
            elif invoice_amount < sum_of_payments:
                print(f"Przeplacono {sum_of_payments - invoice_amount:.2f} PLN")

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
