"""Esquemas del jwt"""

from pydantic import BaseModel


class Token(BaseModel):
    """Esquema que define la estructura del token"""
    access_token: str
    token_type: str
