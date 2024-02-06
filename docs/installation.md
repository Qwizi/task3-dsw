# Instalacja

1. **Instalacja Poetry**: [Poetry](https://python-poetry.org/docs/#installation) to narzędzie do zarządzania zależnościami i pakowaniem w Pythonie. Możesz użyć [pipx](https://pipx.pypa.io/stable/installation/) do jego globalnej instalacji, co jest zalecane.

    ```shell
    pipx install poetry
    ```

2. **Klonowanie repozytorium**: To stworzy kopię tego projektu na twoim lokalnym komputerze..

    ```shell
    git clone https://github.com/Qwizi/task3-dsw
    ```

3. **Instalacja zależności**: Przejdź do katalogu sklonowanego projektu i zainstaluj niezbędne zależności..

    ```shell
    cd task3-dsw
    poetry install
    ```

4. **Aktywacja środowiska wirtualnego**: Aktywuje środowisko wirtualne.

    ```shell
    poetry shell
    ```
5. **Instalacja pre-commit** (Opcjonalne): Instaluje hooki potrzebne dla współautorów projektu
    ```shell
    pre-commit install --hook-type pre-commit --hook-type pre-push
    ```