from fastapi import FastAPI
from routes import auth, route

app = FastAPI()

app.include_router(auth.router)
app.include_router(route.router)

@app.get("/")
def ping():
    return {"message": "App is alive."}