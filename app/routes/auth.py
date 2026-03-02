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
    proxy_user_available_bandwidth: float

@router.post("/auth")
def auth_user(request: User, db: Session = Depends(get_db)):

    #1. Parse request

    #e.g alice residential c    gb  city london
    #e.g alice residential c    us
    #e.g alice residential city new york

    #From what I can see in the docs the username is always first in the examples.
    #Split by the second underscore.

    #No valid country ISO codes should be longer than 1 word i.e no underscore.
    #Cities we need to append all parts after the city word until either the end of the input
    #OR
    #Until we hit the c keyword to indicate a country.

    userParts = request.username.split("_")

    if len(userParts) < 2:
        return JSONResponse(
            status_code=400, 
            content={
                "internal_error_code": 1007,
                "error_message": "Invalid username."}
        )

    name = f"{userParts[0]}_{userParts[1]}"

    country = None
    city = None
    cityParts = []

    totParts = len(userParts)

    for i in range(2, totParts):

        if userParts[i] == "c" and (i+1) < totParts:
            if userParts[i+1] == "c":
                return JSONResponse(
                    status_code=400, 
                    content={
                        "internal_error_code": 1006,
                        "error_message": "Invalid username."}
                )
            if userParts[i+1] == "city":
                return JSONResponse(
                    status_code=400, 
                    content={
                        "internal_error_code": 1005,
                        "error_message": "Invalid username."}
                )
            country = userParts[i+1]

        elif userParts[i] == "city" and i + 1 < totParts:
            for j in range(i+1, totParts):
                if userParts[j] == "city":
                    return JSONResponse(
                        status_code=400, 
                        content={
                            "internal_error_code": 1004,
                            "error_message": "Invalid username."}
                    )
                if userParts[j] == "c":
                    if not cityParts:
                        return JSONResponse(
                            status_code=400, 
                            content={
                                "internal_error_code": 1003,
                                "error_message": "Invalid username."}
                        )
                    break
                cityParts.append(userParts[j])
    if cityParts:
        city = "_".join(cityParts)

    #2. Query DB

    query = select(ResidentialProxyUser).where(
        ResidentialProxyUser.proxy_user_id == name
        )
    user = db.exec(query).first()

    #3. Check if we have a match

    if not user:
        return JSONResponse(
            status_code=401,
            content={
                "internal_error_code": 1002,
                "error_message": "User not found."}
        )
    if user.proxy_user_password != request.password:
        return JSONResponse(
            status_code=401,
            content={
                "internal_error_code": 1001,
                "error_message": "Invalid password."}
        )
    
    #4. If it passes the checks then send the formatted context

    return JSONResponse(
        status_code=200,
        content={
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
    )