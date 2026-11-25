import datetime
from typing import Optional
import pymysql
from pymysql import Connection
from secrets import token_hex


class SessionService:
    def __init__(self, conn: Connection):
        self.conn = conn

    def create_session(self, user_id: int) -> Optional[str]:
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        session_id = token_hex(64)
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        try:
            cursor.execute(
                """
                INSERT INTO users_sessions(user_session_id, user_id, expires_at)
                VALUES (%s, %s, %s)
                """,
                (session_id, user_id, expires_at)
            )
            self.conn.commit()
            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            self.conn.rollback()
            return None
        finally:
            cursor.close()

    def check_session(self, session_id: str) -> bool:
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                """
                SELECT user_session_id, expires_at 
                FROM users_sessions 
                WHERE user_session_id = %s AND expires_at > UTC_TIMESTAMP()
                LIMIT 1
                """,
                (session_id,)
            )
            session = cursor.fetchone()
            return session is not None
        finally:
            cursor.close()

    def delete_session(self, session_id: str) -> str:
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute(
                """
                DELETE FROM users_sessions
                WHERE user_session_id = %s
                """,
                (session_id,)
            )
            self.conn.commit()
            return session_id
        finally:
            cursor.close()
