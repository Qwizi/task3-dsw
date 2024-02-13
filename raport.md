## Raport z Wykonania Programu w Pythonie
Data: 2024-02-13

## Wprowadzenie
Projekt "Task 3 DSW" to program stworzony do obliczania różnic kursowych walut, mający na celu ułatwienie zarządzania finansami w różnych walutach.

## Cel Programu
Głównym celem programu jest automatyzacja procesu kalkulacji różnic kursowych, co umożliwia użytkownikom efektywniejsze zarządzanie transakcjami walutowymi.

## Projekt i Implementacja
Program wykorzystuje Python 3.11+, Poetry do zarządzania zależnościami oraz Git do kontroli wersji. Implementacja kładzie nacisk na czytelność i modularność kodu, zgodnie z zasadami PEP 8.

## Kod źródłowy
Kod źródłowy programu został zaprojektowany z myślą o łatwej rozbudowie i utrzymaniu. Przykładowa klasa z akcja do menu
```python
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
```

## Efektywność i Optymalizacja
Program zoptymalizowano pod kątem wydajności, zarówno w trybie interaktywnym, jak i wsadowym, zapewniając szybkie przetwarzanie danych.

## Dokumentacja
Dokumentacja projektu jest dostępna online pod tym adresem https://task3-dsw.readthedocs.io/pl/latest/ i zawiera szczegółowe instrukcje instalacji, konfiguracji oraz użytkowania programu.

## Podsumowanie
"Task 3 DSW" to kompleksowe narzędzie do obliczania różnic kursowych, zaprojektowane z myślą o łatwości użycia, efektywności i skalowalności. Projekt jest w pełni udokumentowany i przestrzega standardów kodowania.

---
Podpis
[Adrian Ciołek, Mateusz Cyran, Kamil Duszyński]