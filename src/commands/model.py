from typing import Dict, List, Tuple

import typer
from rich.console import Console
from typer import Typer

app = Typer()
console = Console()


def get_model_template() -> str:
    with open("src/templates/model.py", "r") as file:
        content = file.read()

    return content


def tab(n: int = 1) -> str:
    return " " * n * 4


def gen_updated_deleted_txt() -> str:
    updated_txt = "updated_at: Mapped[DateTime] = mapped_column("
    updated_txt += f"\n{tab(2)}DateTime(timezone=True),"
    updated_txt += f"\n{tab(2)}server_default=TextClause("
    updated_txt += f"\n{tab(3)}SettingsEngine().get_updated_at(),  # pyright: ignore"
    updated_txt += f"\n{tab(2)}),"
    updated_txt += f"\n{tab(2)}nullable=False,"
    updated_txt += f"\n{tab()})"

    deleted_txt = f"\n{tab()}deleted: Mapped[Boolean] = mapped_column("
    deleted_txt += f"\n{tab(2)}Boolean,"
    deleted_txt += f"\n{tab(2)}nullable=False,"
    deleted_txt += f"\n{tab(2)}server_default=TextClause('FALSE'),"
    deleted_txt += f"\n{tab()})"

    updated_txt += deleted_txt

    return updated_txt


def gen_mapped_column(
    name: str,
    c_type: str,
    length: int,
    unique: bool,
    index: bool,
) -> str:
    column = f"\n{tab()}{name}: Mapped[{c_type}] = mapped_column("

    if unique or index:
        column += f"\n{tab(2)}{c_type}{f'({length})' if length else ''},"
        column += f"\n{tab(2)}nullable=False,"
        if unique:
            column += f"\n{tab(2)}unique=True,"
        if index:
            column += f"\n{tab(2)}index=True,"

        # add )
    return column


def custom_imports(types: List[str]) -> str:
    return ", " + ", ".join(types)


@app.command()
def create(model: str):
    console.print(f"\nCreating model: {model}")

    is_duplicate = typer.confirm("\nIs this a duplicate table?", default=False)

    classname = model.title()

    with open("src/templates/model.py", "r") as file:
        content = file.read()

    template = content.replace("{MODELNAME}", model)
    template = template.replace("{CLASSNAME}", classname)

    imports = []

    if not is_duplicate:
        autoincrement = "\n\tautoincrement=True,"
        updated_deleted = gen_updated_deleted_txt()
        settings_import = "\nfrom ..settings.config import SettingsEngine"
        imports.append("Boolean")
    else:
        autoincrement = ""
        updated_deleted = ""
        settings_import = ""

    template = template.replace("{AUTOINCREMENT}", autoincrement)
    template = template.replace("{UPDATED_DELETED}", updated_deleted)
    template = template.replace("{SETTINGS_IMPORT}", settings_import)

    console.print("Insert columns names and types.")

    columns: Dict[str, Tuple[str, int, bool, bool]] = {}
    while True:
        col_name = typer.prompt("Column Name")

        if col_name == "end":
            break

        col_type = typer.prompt("Column Type (use SQL types, ex: String, Boolean)")

        length = 0
        if col_type == "String":
            length = typer.prompt("Insert String length")

        unique = typer.prompt("Is unique field?", prompt_suffix=" ")
        index = typer.prompt("Is an index field?", prompt_suffix=" ")

        columns[col_name] = (col_type, length, unique, index)

    for name, c_type in columns.items():
        if c_type not in imports:
            imports.append(c_type)

        gen_mapped_column(name, *c_type)

    template = template.replace("{CUSTOM_IMPORTS}", custom_imports(imports))

    console.print()
    console.print("-" * 80)
    console.print(template, markup=False)
    console.print("-" * 80)


if __name__ == "__main__":
    app()
