from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User


async def create_user(
        session: AsyncSession, user_id: int, first_name: str, last_name: str, subscription: str, tokkens: str,
        gpt_model: str, status: str, access: int, reason: str, commit: bool = False
) -> User | None:
    """ This function adds a new user to the database """
    stmt = insert(
        User
    ).values(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        subscription=subscription,
        tokkens=tokkens,
        gpt_model=gpt_model,
        status=status,
        access=access,
        reason=reason
    ).on_conflict_do_nothing().returning(User)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


async def delete_user(session: AsyncSession, user_id: int, commit: bool = False):
    """ This function removes the user from the database """
    stmt = delete(User).where(User.user_id == user_id)
    await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()


async def select_user(session: AsyncSession, user_id: int) -> User | None:
    """ This function gets user from the database """
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalars().first()


async def select_user_filter(session: AsyncSession, user_id: int, status: str) -> User | None:
    """ This function gets user filter from the database """
    stmt = select(User).where(User.user_id == user_id, User.status == status)
    result = await session.execute(stmt)
    return result.scalars().first()


# async def select_allusers(session: AsyncSession):
#     """ This function gets all users from the database """
#     sql = select(User).order_by(User.user_id)
#     users_sql = await session.execute(sql)
#     users = users_sql.scalars()
#     return users


# async def select_allusers1(session: AsyncSession):
#     """ This function gets all users from the database """
#     sql = select(User).order_by(User.user_id)
#     users_sql = await session.execute(sql)
#     users = users_sql.fetchall()
#     return users


async def select_allusers(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    users = result.scalars().all()
    return users


# Изменяет модель GPT
async def update_model(session: AsyncSession, user_id: int, gpt_model: str, commit: bool = False) -> User | None:
    """ This function changes the model of the user in the model gpt """
    stmt = update(
        User
    ).where(
        User.user_id == user_id
    ).values(
        gpt_model=gpt_model
    ).returning(User)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


# Меняет статус пользователя
async def update_status(session: AsyncSession, user_id: int, status: str, commit: bool = False) -> User | None:
    """ This function changes the status of the user in the database """
    stmt = update(
        User
    ).where(
        User.user_id == user_id
    ).values(
        status=status
    ).returning(User)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


# Меняет количество попыток
async def update_tokkens(session: AsyncSession, user_id: int, tokkens: str, commit: bool = False) -> User | None:
    """ This function changes the tokkens of the user in the tokkens """
    stmt = update(
        User
    ).where(
        User.user_id == user_id
    ).values(
        tokkens=tokkens
    ).returning(User)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()


# Меняет статус подписки
async def update_subscription(session: AsyncSession, user_id: int, subscription: str,
                              commit: bool = False) -> User | None:
    """ This function changes the tokkens of the user in the tokkens """
    stmt = update(
        User
    ).where(
        User.user_id == user_id
    ).values(
        subscription=subscription
    ).returning(User)
    result = await session.execute(stmt)

    if commit:
        await session.commit()
    else:
        await session.flush()

    return result.scalars().first()
