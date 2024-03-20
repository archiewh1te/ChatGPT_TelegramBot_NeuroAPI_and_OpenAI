from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import TimedBaseModel


class User(TimedBaseModel):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column(BigInteger, autoincrement=False, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    subscription: Mapped[Optional[str]] = mapped_column(String(32))
    tokkens: Mapped[Optional[str]] = mapped_column(String(20))
    gpt_model: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[int]] = mapped_column(String(30))
    access: Mapped[int] = mapped_column(BigInteger)
    reason: Mapped[Optional[str]] = mapped_column(String(100))


