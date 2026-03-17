from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import BaseModel

# ----- Database Tables -----

class ResidentialProxyUser(SQLModel, table=True):
    __tablename__ = "residential_proxy_user"
    id: Optional[int] = Field(default=None, primary_key=True)
    proxy_user_id: str = Field(unique=True, index=True)
    proxy_user_password: str
    proxy_user_available_bandwidth: int

class ResidentialProxy(SQLModel, table=True):
    __tablename__ = "residential_proxy"
    residential_proxy_id: Optional[int] = Field(default=None, primary_key=True)
    residential_proxy_ip_address_v4: str
    residential_proxy_port: int
    country_id: str
    city_id: str
    residential_proxy_supported_protocol: str

# ----- Reused Models -----

class ResidentialParams(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None

class AuthServiceContext(BaseModel):
    proxy_user_id: str
    available_bandwidth: int
    residential_params: ResidentialParams

class RequestContext(BaseModel):
    auth_service: AuthServiceContext

class ProxyAddr(BaseModel):
    ip: str
    port: int

class RouteServiceContext(BaseModel):
    proxy_addr: ProxyAddr
    protocol: str

class FullContext(BaseModel):
    auth_service: AuthServiceContext
    route_service: Optional[RouteServiceContext] = None

class ErrorResponse(BaseModel):
    internal_error_code: int
    error_message: str

# -------------------------

# --------- Auth ---------

# Requests

class AuthRequest(BaseModel):
    username: str
    password: str

# Responses

class AuthResponse(BaseModel):
    context: FullContext
    available_bandwidth: int

# -------------------------------

# --------- Route Requests & Responses ---------

# Requests

class RouteRequest(BaseModel):
    context: RequestContext
    protocol: str

# Responses

class RouteResponse(BaseModel):
    context: FullContext
    proxy_addr: ProxyAddr

# --------------------------------