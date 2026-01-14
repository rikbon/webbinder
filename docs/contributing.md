# Contributing to WebBinder

We welcome contributions!

## Development Setup

1.  Clone the repo:
    ```bash
    git clone https://github.com/rikbon/webbinder
    ```
2.  Install dependencies:
    ```bash
    conda env create -f environment.yml
    conda activate webbinder
    ```

## Code Style

-   Use **Python 3.9+**.
-   The project is purely **AsyncIO** based. Do not introduce blocking IO calls (like `requests` or `time.sleep`) in the crawler loop.
-   Add type hints to function signatures.

## Running Tests

Ensure all tests pass before submitting a PR.
```bash
python -m pytest tests
```

## Pull Request Process

1.  Fork the repository and branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  Ensure the test suite passes.
4.  Issue that pull request!
