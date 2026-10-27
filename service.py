
from connection import *
import connection


async def created_user(username, full_name, telegram_id):
    try:
        conn = await connection_db()
        await conn.execute("""
            INSERT INTO users (username, full_name, telegram_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING
        """, username, full_name, int(telegram_id))
        return True
    except Exception as error:
        print(f"Create user error: {error}")
    finally:
            await conn.close()


async def get_user(telegram_id):
    try:
        conn = await connection_db()
        return await conn.fetchrow("""
            SELECT * FROM users
            WHERE telegram_id = $1
        """, int(telegram_id))
    except Exception as error:
        print(f"Get user error: {error}")
        return None
    finally:
            await conn.close()


async def get_user_tasks(telegram_id):
    try:
        conn = await connection_db()
        return await conn.fetch("""
            SELECT * FROM tasks
            WHERE user_id = $1
            ORDER BY task_id DESC
        """, int(telegram_id))
    except Exception as error:
        print(f"Get tasks error: {error}")
        return []
    finally:
            await conn.close()


async def get_task(task_id, telegram_id):
    try:
        conn = await connection_db()
        return await conn.fetchrow("""
            SELECT * FROM tasks
            WHERE task_id = $1 AND user_id = $2
        """, int(task_id), int(telegram_id))
    except Exception as error:
        print(f"Get task error: {error}")
        return None
    finally:
            await conn.close()


async def create_task(telegram_id, title):
    try:
        conn = await connection_db()
        await conn.execute("""
            INSERT INTO tasks (user_id, title)
            VALUES ($1, $2)
        """, int(telegram_id), title)
        return True
    except Exception as error:
        print(f"Create task error: {error}")
    finally:
            await conn.close()


async def delete_task(task_id, telegram_id):
    try:
        conn = await connection_db()
        result = await conn.execute("""
            DELETE FROM tasks
            WHERE task_id = $1 AND user_id = $2
        """, int(task_id), int(telegram_id))
        return result == "DELETE 1"
    except Exception as error:
        print(f"Delete task error: {error}")
    finally:
            await conn.close()


async def change_status(task_id, telegram_id):
    try:
        conn = await connection_db()
        task = await conn.fetchrow("""
            SELECT status FROM tasks
            WHERE task_id = $1 AND user_id = $2
        """, int(task_id), int(telegram_id))
        if not task:
            return None
        new_status = not task["status"]
        result = await conn.execute("""
            UPDATE tasks
            SET status = $1
            WHERE task_id = $2 AND user_id = $3
        """, new_status, int(task_id), int(telegram_id))
        if result == "UPDATE 1":
            return new_status
        return None
    except Exception as error:
        print(f"Change status error: {error}")
        return None
    finally:
            await conn.close()


async def update_task(task_id, telegram_id, title):
    try:
        conn = await connection_db()
        result = await conn.execute("""
            UPDATE tasks
            SET title = $1
            WHERE task_id = $2 AND user_id = $3
        """, title, int(task_id), int(telegram_id))
        return result == "UPDATE 1"
    except Exception as error:
        print(f"Update task error: {error}")
    finally:
            await conn.close()
