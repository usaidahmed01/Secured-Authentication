from pydantic import BaseModel


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenExchangeResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class StandardActionResponse(BaseModel):
    detail: str