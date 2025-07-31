from textwrap import dedent
from typing import List, TypedDict

import typer
from rich.console import Console


class ColumnAttribute(TypedDict):
    name: str
    type: str
    type_length: int
    unique: bool
    index: bool


class ModelService:
    def __init__(self, template: str, modelname: str) -> None:
        self._template = template
        self._modelname = modelname

        self._import_types: List[str] = []

        self._console = Console()

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value: str) -> None:
        self._template = value

    @property
    def modelname(self) -> str:
        return self._modelname

    @modelname.setter
    def modelname(self, value: str) -> None:
        self._modelname = value

    @property
    def import_types(self) -> List[str]:
        return self._import_types

    def ask_is_duplicate(self) -> bool:
        is_duplicate = typer.confirm("\nIs this a duplicate table?", default=False)

        return is_duplicate

    def generate_file(self) -> None:
        pass

    def _generate_content(self) -> str:
        self._replace_modelname()
        self._replace_classname()

        self._check_duplicate()

        self._generate_and_replace_custom_columns()

        return self.template

    def _generate_and_replace_custom_columns(self) -> None:
        columns = self.ask_for_columns()

        custom_imports = self._generate_custom_imports([column["type"]])
        custom_columns = self._generate_custom_columns(columns)

        self._replace_custom_imports(custom_imports)
        self._replace_custom_columns(custom_columns)

    def ask_for_columns(self) -> List[ColumnAttribute]:
        self._console.print("Defining columns. Type [bold]'END'[/bold] to finish.")

        columns: List[ColumnAttribute] = []
        while True:
            column_name = typer.prompt("Column Name")
            if column_name == "END":
                break

            column_type = typer.prompt("Column Type (use SQL types, ex: String)")
            type_length = 0
            if column_type == "String":
                type_length = self.ask_for_string_length()

            unique = self.ask_is_unique()
            index = self.ask_is_index()

            columns.append(
                {
                    "name": column_name,
                    "type": column_type,
                    "type_length": type_length,
                    "unique": unique,
                    "index": index,
                }
            )

        return columns

    def ask_for_string_length(self) -> int:
        type_length = typer.prompt("Insert String length")

        return type_length

    def ask_is_unique(self) -> bool:
        unique = typer.confirm("Is unique field?", default=True)

        return unique

    def ask_is_index(self) -> bool:
        index = typer.confirm("Is an index field?", default=True)

        return index

    def _generate_custom_imports(self, columns: List[str]) -> str:
        return ""

    def _generate_custom_columns(self, columns: List[ColumnAttribute]) -> str:
        return ""

    def _replace_custom_imports(self, custom_imports: str) -> None:
        self.template = self.template.replace("{CUSTOM_IMPORTS}", custom_imports)

    def _replace_custom_columns(self, custom_columns: str) -> None:
        self.template = self.template.replace("{CUSTOM_COLUMNS}", custom_columns)

    def _replace_modelname(self) -> None:
        self.template = self.template.replace("{MODELNAME}", self.modelname)

    def _replace_classname(self) -> None:
        self.template = self.template.replace(
            "{CLASSNAME}",
            self._parse_classname(),
        )

    def _parse_classname(self) -> str:
        return self.modelname.title()

    def _check_duplicate(self) -> None:
        is_duplicate = self.ask_is_duplicate()

        if is_duplicate:
            self._replace_for_duplicate_table()
            return

        self._replace_for_non_duplicate_table()

    def _replace_for_duplicate_table(self) -> None:
        self._replace_settings_import("")
        self._replace_autoincrement("")
        self._replace_updated_deleted("")

    def _replace_for_non_duplicate_table(self) -> None:
        self._replace_settings_import("\nfrom ..settings.config import SettingsEngine")
        self._replace_autoincrement("\n\tautoincrement=True,")
        self._replace_updated_deleted(self._generate_updated_deleted_columns())

    def _replace_settings_import(self, new: str) -> None:
        self.template = self.template.replace("{SETTINGS_IMPORT}", new)

    def _replace_autoincrement(self, new: str) -> None:
        self.template = self.template.replace("{AUTOINCREMENT}", new)

    def _replace_updated_deleted(self, new: str) -> None:
        self.template = self.template.replace("{UPDATED_DELETED}", new)

    @classmethod
    def _generate_updated_deleted_columns(cls) -> str:
        updated = cls._generate_updated_column()
        deleted = cls._generate_deleted_column()

        return f"{updated}\n{deleted}"

    @staticmethod
    def _generate_updated_column() -> str:
        return dedent(
            """
            updated_at: Mapped[DateTime] = mapped_column(
                DateTime(timezone=True),
                server_default=TextClause(
                    SettingsEngine().get_updated_at(),  # pyright: ignore
                ),
                nullable=False,
            )
        """
        ).strip()

    @staticmethod
    def _generate_deleted_column() -> str:
        return dedent(
            """
            deleted: Mapped[Boolean] = mapped_column(
                Boolean,
                nullable=False,
                server_default=TextClause("False")
            )
        """
        ).strip()
