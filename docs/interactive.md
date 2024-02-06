# Tryb interaktywny
Aby uruchomić tryb interaktywny, użyj argumentu **-i** lub **--interactive**. Możesz to zrobić poprzez wpisanie jednej z poniższych komend:
```shell
python main.py -i
```
lub
```shell
python main.py --interactive
```
Po uruchomieniu, wyświetli się menu z różnymi opcjami do wyboru:

```console
1. Dodaj fakture
2. Dodaj płatność
3. Oblicz różnice kursów
4. Sprawdź status faktury
5. Wyjdź
Choose action: 
```

## 1. Dodaj fakture
Wybierając opcję "Dodaj fakturę", zostaniesz poproszony o wypełnienie następujących informacji:
```console
**Dodaj fakture**
Akcja dodawania faktury do bazy danych

Wprowadź kwote faktury: 100
Wprowadź walute [USD, EUR, PLN]: EUR
Wprowadź date: [YYYY-MM-DD]: 2024-02-06
```
Po wprowadzeniu poprawnych danych, faktura zostanie zapisana do pliku  **database.json**

## 2. Dodaj płatność
Wybierając "Dodaj płatność", otrzymasz listę dodanych faktur. Następnie wybierz index faktury, do której chcesz dodać płatność:
```console
**Dodaj płatność**
Dodaj płatność

Dostepne faktury: 
 Invoice index - <id | amount | currency | date> 
 0 - <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Wprowadz index faktury: 0
```
Po wybraniu faktury uzupełnij informacje o płatności:
```console
Wybrałes fakture <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Wprowadź kwote: 100
Wprowadź walute [USD, EUR, PLN]: PLN
Wprowadź date: [YYYY-MM-DD]: 2024-02-06
```

## 3. Oblicz różnice kursów
Wybierając tę opcję, zobaczysz listę faktur. Wybierz index faktury, dla której chcesz obliczyć różnicę kursową:
```console
**Oblicz różnice kursów**
Akcja obliczania różnic kursów

Dostepne faktury: 
 Invoice index - <id | amount | currency | date> 
 0 - <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Wprowadz index faktury: 0
```
Następnie zostanie wyswietlona lista z dostępnymi płatnoscami dla faktury
```console
Wybrałes fakture <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Dostepne płatności dla tej faktury: 
  Invoice index - <id | invoice_id | currency | date> 
 0 - <13db40a0-052b-413f-905a-6ed4773168b8 | 058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | PLN | 2024-02-06>
Wprowadz index płatności: 0
```
Następnie zostanie wyświetlona różnica kursowa:
```console
**Różnica kursowa**: 

Faktura: <kod waluty: EUR | data: 2024-02-06 | kurs: 4.3435> 

Płatność: <kod waluty: PLN | data: 2024-02-06 | kurs: 1.0> 

Różnica: -3.34
```

## 4. Sprawdź status faktury
ybierz tę opcję, aby sprawdzić status faktury. Po wybraniu indexu faktury, zostanie wyświetlony jej status oraz suma płatności:
```console
**Sprawdź status faktury**
Akcja sprawdzania statusu faktury.
Wymaga podania numeru faktury.
Dla uproszeczenia przekszalcamy wartosc faktury oraz płatności do PLN.

Dostepne faktury: 
 Invoice index - <id | amount | currency | date> 
 0 - <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Wprowadz index faktury: 0
Wybrałes fakture <058bc60f-2b15-45d6-b824-a8fef1b201d4 | 100.0 | EUR | 2024-02-06 | InvoiceStatus.UNPAID>
Kwota faktury: <100.0 | EUR> 434.35 PLN
Suma płatności: 100.00 PLN
Status faktury: Nie zaplacona
```