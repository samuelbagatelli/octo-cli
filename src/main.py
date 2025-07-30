from rich import print
from typer import Typer

from commands import model

app = Typer()
app.add_typer(model.app, name="model")


if __name__ == "__main__":
    print("Welcome to [#F75E5B]OCTO[/]:octopus:!")
    app()
