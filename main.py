from fastapi import FastAPI
from interfaces.api.user_router import router as user_router

app = FastAPI(title="Sakovskii API")

app.include_router(user_router)

#uvicorn main:app --reload