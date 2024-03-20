from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.admins import Admin


async def create_admin(
        session: AsyncSession, user_id: int, first_name: str, last_name: str, user_name: str, status: str, flag: str, commit: bool = False
) -> Admin | None:
    """ This function adds a new user to the database """
    stmt = insert(
        Admin
    ).values(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        user_name=user_name,
        status=status,
        flag=flag

    ).on_conflict_do_nothing().returning(Admin)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


async def delete_admin(session: AsyncSession, user_id: int, commit: bool = False):
    """ This function removes the user from the database """
    stmt = delete(Admin).where(Admin.user_id == user_id)
    await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()


async def select_admin(session: AsyncSession, user_id: int) -> Admin | None:
    """ This function gets user from the database """
    stmt = select(Admin).where(Admin.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def select_admin_filter(session: AsyncSession, user_id: int, flag: str) -> Admin | None:
    """ This function gets admin from the database """
    stmt = select(Admin).where(Admin.user_id == user_id, Admin.flag == flag)
    result = await session.execute(stmt)
    return result.scalars().first()

async def select_alladmins(session: AsyncSession):
    """ This function gets user from the database """
    sql = select(Admin).order_by(Admin.user_id)
    admin_sql = await session.execute(sql)
    admins = admin_sql.scalars()
    return admins


async def update_language(session: AsyncSession, user_id: int, language_code: str, commit: bool = False) -> Admin | None:
    """ This function changes the language of the user in the database """
    stmt = update(
        Admin
    ).where(
        Admin.user_id == user_id
    ).values(
        language_code=language_code
    ).returning(Admin)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()
