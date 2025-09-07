import os
import aiomysql
from fastapi import HTTPException


async def get_db_connection():
    conn = await aiomysql.connect(host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'),
                                  user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                                  db=os.getenv('DB_NAME'), charset='utf8')
    return conn


async def fetch_one(query, *params):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            result = await cur.fetchone()
            return result
    finally:
        conn.close()
