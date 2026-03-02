from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, Field, select
from typing import Optional
from decimal import Decimal
from database import get_db

router = APIRouter()

#Models to easily parse any requests or the database.

class User(BaseModel):
    username: str
    password: str

class ResidentialProxyUser(SQLModel, table=True):
    __tablename__ = "residential_proxy_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    proxy_user_id: str = Field(unique=True, index=True)
    proxy_user_password: str
    proxy_user_available_bandwidth: Decimal

@router.post("/auth")
def auth_user(request: User, db: Session = Depends(get_db)):

    #1. Parse request

    userParts = request.username.split("_")
    #Username is always either 6 or 7 parts (depending on city e.g. new_york vs london)
    if len(userParts) < 6:
        raise HTTPException(status_code=401, detail="Invalid username.")
    
    name = f"{userParts[0]}_{userParts[1]}"
    country = userParts[3]
    city = userParts[5]
    if len(userParts) == 7:
        city += f"_{userParts[6]}"

    #2. Query DB

    query = select(ResidentialProxyUser).where(ResidentialProxyUser.proxy_user_id == name)
    user = db.exec(query).first()

    #3. Check if we have a match

    if not user:
        return JSONResponse(
            status_code=401,
            content={"internal_error_code": 1002, "error_message": "user not found"}
        )
    if user.proxy_user_password != request.password:
        return JSONResponse(
            status_code=401,
            content={"internal_error_code": 1001, "error_message": "invalid password"}
        )
    
    #4. If it passes the checks then send the formatted context

    return {
        "context": {
            "auth_service": {
                "proxy_user_id": user.proxy_user_id,
                "available_bandwidth": user.proxy_user_available_bandwidth,
                "residential_params": {
                    "country": country,
                    "city": city
                }
            }
        },
        "available_bandwidth": user.proxy_user_available_bandwidth
    }
    
    
    