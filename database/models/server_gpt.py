from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import TimedBaseModel


class server_neuroapi(TimedBaseModel):
    __tablename__ = 'server_neuroapi'
    id: Mapped[int] = mapped_column(BigInteger, autoincrement=False, primary_key=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(100))