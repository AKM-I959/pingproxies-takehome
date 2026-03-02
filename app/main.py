from fastapi import FastAPI
from routes import auth

app = FastAPI()

app.include_router(auth.router)

@app.get("/")
def ping():
    return {"message": "App is alive."}