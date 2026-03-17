from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session,select
from database import get_db
from models import (
    AuthRequest,
    AuthResponse,
    ResidentialProxyUser,
    FullContext,
    AuthServiceContext,
    ResidentialParams,
    ErrorResponse,
)

router = APIRouter()

def parse_request(request: AuthRequest):
    userParts = request.username.split("_")

    if len(userParts) < 2:
        return JSONResponse(
            status_code=400, 
            content=ErrorResponse(
                internal_error_code=1002,
                error_message="Invalid username."
            ).model_dump()
        )
    
    name = f"{userParts[0]}_{userParts[1]}"

    country = None
    city = None

    buffer = []

    for i in range(len(userParts) -1, 1, -1):
        part = userParts[i]

        if(part == "city" and buffer):
            city = "_".join(reversed(buffer))
            buffer = []
        elif(part == "c" and buffer):
            country = "_".join(reversed(buffer))
            buffer = []
        else:
            buffer.append(part)
    
    return {
        "name": name,
        "res_params": ResidentialParams(
            country = country,
            city = city
        )
    }

@router.post(
        "/auth",
        response_model=AuthResponse,
        response_model_exclude_none=True,
        responses={
            400: {"model": ErrorResponse},
            401: {"model": ErrorResponse}
        })
def auth_user(
    request: AuthRequest,
    db: Session = Depends(get_db),
    parsedRequest: dict = Depends(parse_request)    
):

    name = parsedRequest["name"]
    res_params = parsedRequest["res_params"]

    user = db.exec(
        select(ResidentialProxyUser).
        where(ResidentialProxyUser.proxy_user_id == name)
    ).first()

    if not user:
        return JSONResponse(
            status_code=401, 
            content=ErrorResponse(
                internal_error_code=1002,
                error_message="User not found."
            ).model_dump()
        )
    if user.proxy_user_password != request.password:
        return JSONResponse(
            status_code=401, 
            content=ErrorResponse(
                internal_error_code=1001,
                error_message="Invalid password."
            ).model_dump()
        )

    return AuthResponse(
        context=FullContext(
            auth_service=AuthServiceContext(
                proxy_user_id=user.proxy_user_id,
                available_bandwidth=user.proxy_user_available_bandwidth,
                residential_params=res_params
            )
        ),
        available_bandwidth=user.proxy_user_available_bandwidth
    )