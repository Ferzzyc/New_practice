from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pymysql import Connection

from application.services.menu_service import MenuService
from infrastructure.db.mysql import mysql_conn
from .user_deps import check_session

router = APIRouter(prefix="/menu", tags=["menu"])


class MenuItemCreate(BaseModel):
    menu_item_name: str
    menu_item_link: Optional[str] = None
    menu_item_order: Optional[int] = 0
    menu_item_parent_id: Optional[int] = None
    icon_name: Optional[str] = None
    menu_item_is_hidden: Optional[bool] = False
    menu_item_description: Optional[str] = None
    menu_item_sidebar_hidden: Optional[bool] = False


class MenuItemResponse(MenuItemCreate):
    menu_item_id: int


class MenuItemUpdatePatch(BaseModel):
    menu_item_name: Optional[str] = None
    menu_item_link: Optional[str] = None
    menu_item_order: Optional[int] = None
    menu_item_parent_id: Optional[int] = None
    icon_name: Optional[str] = None
    menu_item_is_hidden: Optional[bool] = None
    menu_item_description: Optional[str] = None
    menu_item_sidebar_hidden: Optional[bool] = None


@router.get("/get_menu_items", summary="Получение всех пунктов меню")
async def get_menu_items(conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    items = service.get_all_menu_items()
    return {"menu_items": items}


@router.post(
    "/create_menu_item",
    summary="Создаёт пункт меню (требует вход)",
    status_code=201,
    response_model=MenuItemResponse
)
async def create_menu_item(
    item: MenuItemCreate,
    conn: Connection = Depends(mysql_conn),
    session_id: str = Depends(check_session)
):
    service = MenuService(conn)
    created_item = service.create_menu_item(**item.model_dump())
    return MenuItemResponse(**created_item)


@router.patch(
    "/{menu_item_id}",
    response_model=MenuItemResponse,
    summary="Частичное обновление пункта меню (требует вход)"
)
async def update_menu_item_patch(
    menu_item_id: int,
    item_data: MenuItemUpdatePatch,
    conn: Connection = Depends(mysql_conn),
    session_id: str = Depends(check_session)
):
    service = MenuService(conn)
    fields = item_data.model_dump(exclude_unset=True)
    updated_item = service.update_menu_item_partial(menu_item_id, fields)
    if updated_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return MenuItemResponse(**updated_item)


@router.delete("/{menu_item_id}", summary="Удаление пункта меню (требует вход)")
async def delete_menu_item(
    menu_item_id: int,
    conn: Connection = Depends(mysql_conn),
    session_id: str = Depends(check_session)
):
    service = MenuService(conn)
    deleted = service.delete_menu_item(menu_item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"detail": f"Menu item {menu_item_id} successfully deleted"}

@router.get("/user/{user_id}", summary="Получение пунктов меню конкретного пользователя")
async def get_user_menu_items(user_id: int, conn: Connection = Depends(mysql_conn)):
    service = MenuService(conn)
    items = service.get_menu_items_by_user_id(user_id)
    return {"user_id": user_id, "menu_items": items}


@router.post(
    "/user/{user_id}/assign/{menu_item_id}",
    summary="Привязать пункт меню к пользователю (требует вход)"
)
async def assign_menu_to_user(
    user_id: int,
    menu_item_id: int,
    conn: Connection = Depends(mysql_conn),
    session_id: str = Depends(check_session)
):
    service = MenuService(conn)
    success = service.assign_menu_item_to_user(user_id, menu_item_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Не удалось привязать пункт меню (проверьте существование user_id и menu_item_id)"
        )
    return {"detail": f"Menu item {menu_item_id} assigned to user {user_id}"}