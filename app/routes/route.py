from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel import Session, select, func
from database import get_db
from models import (
    RouteRequest, 
    RouteResponse, 
    ResidentialProxy, 
    ErrorResponse, 
    FullContext, 
    RouteServiceContext, 
    ProxyAddr
)

router = APIRouter()
#Routing Logic:
#
#  1.  If an exact country + city match exists, return it
#  2.  If no city match, fallback to any proxy in that country
#  3.  If no country match, return error
#  4.  If no routing parameters specified, select a random proxy
#  5.  All results need to support the chosen protocol -> Check this first

#TODO replace Route model with multiple nested models that better represent the nested JSON it expects. Currently this would allow
# pretty much any JSON. In its current state it will throw an error 442. Also would then provide better docs.

@router.post("/route",
            response_model=RouteResponse,
            responses={
                404: {"model": ErrorResponse}
            })
def route_proxy(request: RouteRequest, db: Session = Depends(get_db)):

    # 1. Parse request

    res = request.context.auth_service.residential_params

    country = res.country
    city = res.city

    # 2. Query DB --> note. protocol must always match

    query = select(ResidentialProxy).where(
        ResidentialProxy.residential_proxy_supported_protocol == request.protocol
        ).order_by(func.random()) # Added random here so it applies to all requests. Means two requests with the same city or country can get different proxies (if they exist)
    
    # 3. Work our way through the routing logic

    proxy = None

    if country and city:
        proxy = db.exec(query.where(
            ResidentialProxy.country_id == country,
            ResidentialProxy.city_id == city
        )).first()
    
    # 3.1 If we didnt get a match but have a country

    if not proxy and country:
        proxy = db.exec(query.where(
            ResidentialProxy.country_id == country
        )).first()

        # 3.2 If we still have no proxy for the specified country, give an error

        if not proxy:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    internal_error_code=3400, 
                    error_message="no proxy found for country"
                ).model_dump()
            )
    
    # 3.3 No country or city given --> This does assume that a protocol is always specified.

    if not proxy and not country:
        proxy = db.exec(query).first()

    # 3.4 No proxies for the specified protocol
    
    if not proxy:
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                internal_error_code=3401,
                error_message=f"No available proxies for the {request.protocol} protocol"
            ).model_dump()
        )
    
    # 4. By now we will have a proxy

    proxy_address = ProxyAddr(
        ip=proxy.residential_proxy_ip_address_v4,
        port=proxy.residential_proxy_port
    )

    return RouteResponse(
        context=FullContext(
            auth_service=request.context.auth_service,
            route_service=RouteServiceContext(
                proxy_addr=proxy_address,
                protocol=request.protocol
            )
        ),
        proxy_addr=proxy_address
    )