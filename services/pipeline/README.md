# Pipeline

## Setup

```sh
uv sync
```

## Run

```sh
uv run main.py
```

## Scripts

### `extract.py`

Scrapes RSS feeds from BBC News UK and OK! Magazine, parses entries into validated `Article` models (via Pydantic), and logs progress.

```sh
uv run extract.py
```

## Lint

```sh
uv run ruff check .
```

## Format

```sh
uv run ruff format .
```

## Typecheck

```sh
uv run pyrefly check .
```

## Test

```sh
uv run pytest
```