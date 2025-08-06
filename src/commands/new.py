from string import Template

from rich.console import Console
from typer import Typer

app = Typer()
console = Console()


@app.command()
def model(name: str):
    console.print(f"\nCreating new model: {name}")

    with open("templates/model.py.template", "r") as file:
        src = Template(file.read())

    with open("templates/engine_import.py.template", "r") as file:
        engine_import = file.read()

    variables = {
        "CLASS_NAME": name.title(),
        "MODEL_NAME": name,
        "CUSTOM_IMPORTS": ", Boolean",
        "ENGINE_IMPORT": engine_import,
    }

    result = src.safe_substitute(variables)

    console.print(result, markup=False)
