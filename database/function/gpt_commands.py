from sqlalchemy import delete, select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.gpt import Gpt_model


async def create_gpt_model(
        session: AsyncSession, gpt_id: int, data_model: str, commit: bool = False) -> Gpt_model | None:
    """ This function adds a new user to the database """
    stmt = insert(
        Gpt_model
    ).values(
        gpt_id=gpt_id,
        data_model=data_model
    ).on_conflict_do_nothing().returning(Gpt_model)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


async def count_gpt_model(session: AsyncSession):
    """ This function gets count id from the database """
    stmt = func.max(Gpt_model.gpt_id)
    result = await session.execute(stmt)
    count = result.scalars().first()
    return count


async def delete_gpt_model(session: AsyncSession, gpt_id: int, commit: bool = False):
    """ This function removes the user from the database """
    stmt = delete(Gpt_model).where(Gpt_model.gpt_id == gpt_id)
    await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()


async def select_gpt_model(session: AsyncSession, data_model: str) -> Gpt_model | None:
    """ This function gets user from the database """
    stmt = select(Gpt_model).where(Gpt_model.data_model == data_model)
    result = await session.execute(stmt)
    return result.scalars().first()


async def select_all_gpt_model(session: AsyncSession):
    query = select(Gpt_model)
    stmt = await session.execute(query)
    result = stmt.scalars().all()
    return result



