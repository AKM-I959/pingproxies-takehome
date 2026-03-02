from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, Field, select, func
from typing import Optional, Dict, Any
from decimal import Decimal
from database import get_db

router = APIRouter()

class Route(BaseModel):
    context: Dict[str, Any]
    protocol: str

class ResidentialProxy(SQLModel, table=True):
    __tablename__ = "residential_proxy"
    residential_proxy_id: Optional[int] = Field(default=None, primary_key=True)
    residential_proxy_ip_address_v4: str
    residential_proxy_port: int
    country_id: str
    city_id: str
    residential_proxy_supported_protocol: str

#Routing Logic:
#
#  1.  If an exact country + city match exists, return it
#  2.  If no city match, fallback to any proxy in that country
#  3.  If no country match, return error
#  4.  If no routing parameters specified, select a random proxy
#  5.  All results need to support the chosen protocol -> Check this first

@router.post("/route")
def route_proxy(request: Route, db: Session = Depends(get_db)):

    # 1. Parse request

    auth = request.context.get("auth_service", {})
    res = auth.get("residential_params", {})

    country = res.get("country")
    city = res.get("city")
    protocol = request.protocol

    # 2. Query DB --> note. protocol must always match

    query = select(ResidentialProxy).where(
        ResidentialProxy.residential_proxy_supported_protocol == protocol
        )
    
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
                content={
                    "internal_error_code": 3400, 
                    "error_message": "No proxy found for this country."
                }
            )
    
    # 3.3 No country or city given

    if not proxy and not country:
        proxy = db.exec(query.order_by(func.random())).first()

    # 3.4 No proxies for the specified protocol
    
    if not proxy:
        return JSONResponse(
            status_code=404,
            content={
                "internal_error_code": 3401, 
                "error_message": f"No available proxies for the {protocol} protocol."
            }
        )
    
    # 4. By now we will have a proxy

    return JSONResponse(
        status_code=200,
        content={
            "context": {
                "auth_service": auth,
                "route_service": {
                    "proxy_addr": {
                        "ip": proxy.residential_proxy_ip_address_v4,
                        "port": proxy.residential_proxy_port
                    },
                    "protocol": protocol
                }
            },
            "proxy_addr": {
                "ip": proxy.residential_proxy_ip_address_v4,
                "port": proxy.residential_proxy_port
            }
        }
    )