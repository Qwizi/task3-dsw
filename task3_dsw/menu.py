"""Module for creating interactive menu in console."""
import sys

from task3_dsw.invoices import (
    Invoice,
    add_invoice_to_file,
    get_invoice_from_file,
)
from task3_dsw.logger import logger
from task3_dsw.payments import Payment, add_payment_to_file


class Action:
    """Action class for creating action in interactive menu."""

    def __init__(self, name: str, tag: str, description: str) -> None:
        """Initialize Action class."""
        self.name = name
        self.tag = tag
        self.description = description

    def __str__(self) -> str:
        """Return name of action."""
        return f"{self.name}: {self.description}"

    def execute(self) -> None:
        """Execute action."""
        logger.debug("Execute action: %s", self.name)


class ExitAction(Action):
    """ExitAction class for creating exit action in interactive menu."""

    def execute(self) -> None:
        """Execute action."""
        logger.debug("Execute action: %s", self.name)
        sys.exit(0)


class AddInvoiceAction(Action):
    """AddInvoiceAction class for creating add invoice action in interactive menu."""

    def execute(self) -> None:
        """Execute action for adding invoice."""
        try:
            amount = float(input("Enter amount: "))
            currency = input("Enter currency: ")
            date = input("Enter date: ")
            invoice_schema = add_invoice_to_file(
                data=Invoice(amount=amount, currency=currency, date=date)
            )
            logger.debug("Added invoice: %s", invoice_schema)
        except ValueError as e:
            logger.error("Invalid value: %s", e)
        except FileNotFoundError as e:
            logger.error("Something went wrong: %s", e)


class AddPaymentAction(Action):
    """AddPaymentAction class for creating add payment action in interactive menu."""

    def execute(self) -> None:
        """Execute action for adding payment."""
        try:
            invoice_id = input("Enter invoice id: ")
            amount = float(input("Enter amount: "))
            currency = input("Enter currency: ")
            date = input("Enter date: ")

            invoice_from_file = get_invoice_from_file(invoice_id=invoice_id)
            if invoice_from_file is None:
                logger.error(f"Invoice with id {invoice_id} not exists.")
                return
            payment_schema = add_payment_to_file(
                data=Payment(
                    amount=amount, currency=currency, date=date, invoice_id=invoice_id
                )
            )
            logger.debug("Added payment: %s", payment_schema)
        except ValueError as e:
            logger.error("Invalid value: %s", e)

        except FileNotFoundError as e:
            logger.error("Something went wrong: %s", e)


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
            print("{}. {}".format(self.actions.index(action) + 1, action))  # noqa: UP032, T201

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
            action = self.actions[action_id - 1]
            logger.debug("Run action: %s", action)
            action.execute()
        except IndexError:
            logger.error("Action with id %s not exists.", action_id)
