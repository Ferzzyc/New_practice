from typing import Optional
import argon2
import pymysql
from pymysql import Connection
from application.services.session_service import SessionService


class UserService:
    def __init__(self, conn: Connection):
        self.connection = conn
        self.PH = argon2.PasswordHasher()
        self.session_service = SessionService(conn)

    def get_user_by_login(self, login: str) -> Optional[dict]:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT
                user_id,
                user_first_name as first_name,
                user_last_name as last_name,
                user_login as login,
                user_email as email,
                user_password_hash as password
            FROM users
            WHERE user_login = %s
            """,
            (login,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result

    def authenticate(self, user: dict, password: str) -> bool:
        try:
            return self.PH.verify(user['password'], password)
        except argon2.exceptions.VerifyMismatchError:
            return False

    def authorization(self, login: str, password: str) -> Optional[str]:
        user = self.get_user_by_login(login)
        if user is None:
            return None
        if self.authenticate(user, password):
            return self.session_service.create_session(user['user_id'])
        return None

    def get_user_by_id(self, user_id: int) -> dict | None:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT
                user_first_name as first_name,
                user_last_name as last_name,
                user_login as login,
                user_email as email,
                user_password_hash as password
            FROM users
            WHERE user_id = %s
            """,
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_all_users(self) -> list:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT
                user_first_name as first_name,
                user_last_name as last_name,
                user_login as login,
                user_email as email,
                user_password_hash as password
            FROM users
            """
        )
        users = cursor.fetchall()
        cursor.close()
        return list(users)

    def create_user(self, first_name: str, last_name: str, login: str, email: str, password: str) -> dict:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        password_hash = self.PH.hash(password)
        cursor.execute(
            """
            INSERT INTO users (user_first_name, user_last_name, user_login, user_email, user_password_hash)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (first_name, last_name, login, email, password_hash)
        )
        self.connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return self.get_user_by_id(user_id)

    def update_user_full(self, user_id: int, first_name: str, last_name: str, login: str, email: str, password: str) -> dict | None:
        if not self.get_user_by_id(user_id):
            return None
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        password_hash = self.PH.hash(password)
        cursor.execute(
            """
            UPDATE users
            SET user_first_name = %s,
                user_last_name = %s,
                user_login = %s,
                user_email = %s,
                user_password_hash = %s
            WHERE user_id = %s
            """,
            (first_name, last_name, login, email, password_hash, user_id)
        )
        self.connection.commit()
        cursor.close()
        return self.get_user_by_id(user_id)

    def update_user_partial(self, user_id: int, fields_to_update: dict) -> dict | None:
        if not self.get_user_by_id(user_id):
            return None
        if not fields_to_update:
            return self.get_user_by_id(user_id)

        column_map = {
            "first_name": "user_first_name",
            "last_name": "user_last_name",
            "login": "user_login",
            "email": "user_email",
            "password": "user_password_hash",
        }

        set_clauses = []
        values = []
        for key, value in fields_to_update.items():
            if key in column_map and value is not None:
                set_clauses.append(f"{column_map[key]} = %s")
                if key == "password":
                    values.append(self.PH.hash(value))
                else:
                    values.append(value)

        if not set_clauses:
            return self.get_user_by_id(user_id)

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE user_id = %s"

        cursor = self.connection.cursor()
        cursor.execute(query, tuple(values))
        self.connection.commit()
        cursor.close()
        return self.get_user_by_id(user_id)

    def delete_user(self, user_id: int) -> bool:
        if not self.get_user_by_id(user_id):
            return False
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        self.connection.commit()
        cursor.close()
        return True

