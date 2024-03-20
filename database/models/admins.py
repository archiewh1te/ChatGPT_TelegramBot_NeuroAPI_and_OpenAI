from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import TimedBaseModel


class Admin(TimedBaseModel):
    __tablename__ = 'admins'
    user_id: Mapped[int] = mapped_column(BigInteger, autoincrement=False, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    user_name: Mapped[Optional[str]] = mapped_column(String(32))
    status: Mapped[Optional[str]] = mapped_column(String(32))
    flag: Mapped[Optional[str]] = mapped_column(String(32))