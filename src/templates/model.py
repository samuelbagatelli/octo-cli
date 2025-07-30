from datetime import datetime

from sqlalchemy import BigInteger, DateTime, TextClause{CUSTOM_IMPORTS}
from sqlalchemy.orm import Mapped, mapped_column{RELATIONSHIP_IMPORT}

from ..prefix.prefix_base import PrefixBase{SETTINGS_IMPORT}


class {CLASSNAME}(PrefixBase):
    __incomplete_tablename__ = "{MODELNAME}"

    id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,{AUTOINCREMENT}
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=TextClause("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    {UPDATED_DELETED}
    {CUSTOM_COLUMNS}
    {CUSTOM_RELATIONSHIPS}

    def __repr__(self) -> str:
        return f"<{CLASSNAME}(id={self.id})>"
    
    def asdict(self) -> dict:
        return {col.key: getattr(self, col.key) for col in self.__table__.columns}
