"""Request body models for POST or PUT"""
from pydantic import BaseModel


class WithCsrfToken(BaseModel):
    """Request with CSRF token"""

    csrf_token: str


class CreateEpisodeRequest(BaseModel):
    """Create episode request form"""

    title: str
    status: str = "draft"
    edit_reservation: int = 0
    keep_editing: int = 0
    body: str
