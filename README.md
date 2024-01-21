# Task 3 DSW

# Getting Started
1. [Install Poetry](https://python-poetry.org/docs/#installation).
U can use also [pipx](https://github.com/pypa/pipx#readme) to install it globally (recommended):
```shell
pipx install poetry
```
2. Clone repository
```shell
git clone https://github.com/Qwizi/task3-dsw
```

3. Install dependencies
```shell
cd task3-dsw
poetry install
```
After that activate virtual environment and install pre-commit hooks

```shell
poetry shell
pre-commit install --hook-type pre-commit --hook-type pre-push
```

