from typing import Optional

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import TimedBaseModel


class Gpt_model(TimedBaseModel):
    __tablename__ = 'gpt_models'
    gpt_id: Mapped[int] = mapped_column(BigInteger, autoincrement=False, primary_key=True)
    data_model: Mapped[Optional[str]] = mapped_column(String(100))
