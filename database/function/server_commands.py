from sqlalchemy import delete, select, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.server_gpt import server_neuroapi


async def create_server_settings(
        session: AsyncSession, id: int, endpoint: str, commit: bool = False) -> server_neuroapi | None:
    """ This function adds a new user to the database """
    stmt = insert(
        server_neuroapi
    ).values(
        id=id,
        endpoint=endpoint
    ).on_conflict_do_nothing().returning(server_neuroapi)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


async def count_gpt_endpoint(session: AsyncSession):
    """ This function gets count id from the database """
    stmt = func.max(server_neuroapi.id)
    result = await session.execute(stmt)
    count = result.scalars().first()
    return count


async def delete_gpt_endpoint(session: AsyncSession, id: int, commit: bool = False):
    """ This function removes the user from the database """
    stmt = delete(server_neuroapi).where(server_neuroapi.id == id)
    await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()


async def select_gpt_endpoint(session: AsyncSession, endpoint: str) -> server_neuroapi | None:
    """ This function gets user from the database """
    stmt = select(server_neuroapi).where(server_neuroapi.endpoint == endpoint)
    result = await session.execute(stmt)
    return result.scalars().first()


async def select_all_gpt_endpoint(session: AsyncSession):
    query = select(server_neuroapi)
    stmt = await session.execute(query)
    result = stmt.scalars().all()
    return result
