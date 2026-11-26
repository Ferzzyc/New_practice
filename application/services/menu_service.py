from typing import Optional
import pymysql
from pymysql import Connection


class MenuService:
    def __init__(self, conn: Connection):
        self.connection = conn

    def get_menu_item_by_id(self, menu_item_id: int) -> dict | None:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT 
                menu_item_id,
                menu_item_name,
                menu_item_link,
                menu_item_order,
                menu_item_parent_id,
                icon_name,
                menu_item_is_hidden,
                menu_item_description,
                menu_item_sidebar_hidden
            FROM menu_items
            WHERE menu_item_id = %s
            """,
            (menu_item_id,)
        )
        item = cursor.fetchone()
        cursor.close()
        return item

    def get_all_menu_items(self) -> list:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            SELECT 
                menu_item_id,
                menu_item_name,
                menu_item_link,
                menu_item_order,
                menu_item_parent_id,
                icon_name,
                menu_item_is_hidden,
                menu_item_description,
                menu_item_sidebar_hidden
            FROM menu_items
            ORDER BY menu_item_order ASC
            """
        )
        items = cursor.fetchall()
        cursor.close()
        return list(items)

    def create_menu_item(
        self,
        menu_item_name: str,
        menu_item_link: Optional[str] = None,
        menu_item_order: Optional[int] = 0,
        menu_item_parent_id: Optional[int] = None,
        icon_name: Optional[str] = None,
        menu_item_is_hidden: Optional[bool] = False,
        menu_item_description: Optional[str] = None,
        menu_item_sidebar_hidden: Optional[bool] = False
    ) -> dict:
        cursor = self.connection.cursor(cursor=pymysql.cursors.DictCursor)
        cursor.execute(
            """
            INSERT INTO menu_items (
                menu_item_name, 
                menu_item_link, 
                menu_item_order, 
                menu_item_parent_id, 
                icon_name, 
                menu_item_is_hidden, 
                menu_item_description, 
                menu_item_sidebar_hidden
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                menu_item_name,
                menu_item_link,
                menu_item_order,
                menu_item_parent_id,
                icon_name,
                int(bool(menu_item_is_hidden)),
                menu_item_description,
                int(bool(menu_item_sidebar_hidden))
            )
        )
        self.connection.commit()
        item_id = cursor.lastrowid
        cursor.close()
        return self.get_menu_item_by_id(item_id)

    def update_menu_item_partial(self, menu_item_id: int, fields_to_update: dict) -> dict | None:
        if not self.get_menu_item_by_id(menu_item_id):
            return None
        if not fields_to_update:
            return self.get_menu_item_by_id(menu_item_id)

        allowed_columns = {
            "menu_item_name",
            "menu_item_link",
            "menu_item_order",
            "menu_item_parent_id",
            "icon_name",
            "menu_item_is_hidden",
            "menu_item_description",
            "menu_item_sidebar_hidden",
        }

        set_clauses = []
        values = []
        for key, value in fields_to_update.items():
            if key in allowed_columns and value is not None:
                set_clauses.append(f"{key} = %s")
                if key in ("menu_item_is_hidden", "menu_item_sidebar_hidden"):
                    values.append(int(bool(value)))
                else:
                    values.append(value)

        if not set_clauses:
            return self.get_menu_item_by_id(menu_item_id)

        values.append(menu_item_id)
        query = f"UPDATE menu_items SET {', '.join(set_clauses)} WHERE menu_item_id = %s"

        cursor = self.connection.cursor()
        cursor.execute(query, tuple(values))
        self.connection.commit()
        cursor.close()
        return self.get_menu_item_by_id(menu_item_id)

    def delete_menu_item(self, menu_item_id: int) -> bool:
        if not self.get_menu_item_by_id(menu_item_id):
            return False
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM menu_items WHERE menu_item_id = %s", (menu_item_id,))
        self.connection.commit()
        cursor.close()
        return True
