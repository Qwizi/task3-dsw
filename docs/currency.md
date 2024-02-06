# Konfiguracja walut

### 1. Zmienna środowiskowa
Aby ustawić listę dostępnych walut przy użyciu zmiennej środowiskowej, wykonaj następującą komendę:
```shell
export CURRENCIES=[\"USD\",\"EUR\"]
```

### 2. Argument programu
Możesz również skonfigurować dostępne waluty za pomocą argumentu **-c** lub **--currencies**, podając wybrane waluty oddzielone spacją:
```shell
python main.py -c USD EUR
```
lub
```shell
python main.py --currencies USD EUR
```
