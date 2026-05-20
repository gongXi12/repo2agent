"""Main module for sample Python project."""

from flask import Flask

app = Flask(__name__)


def hello():
    """Say hello."""
    return "world"


def fetch_data(url: str) -> dict:
    """Fetch data from a URL."""
    return {"url": url}


class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b


@app.route("/api/data")
def get_data():
    """Get data endpoint."""
    return {"data": 123}
