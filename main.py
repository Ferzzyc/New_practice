from fastapi import FastAPI
from interfaces.api.user_router import router as user_router
from interfaces.api.menu_router import router as menu_router

app = FastAPI(title="Sakovskii API")

app.include_router(user_router)
app.include_router(menu_router)
#uvicorn main:app --reload