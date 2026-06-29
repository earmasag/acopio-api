from fastapi import Depends, HTTPException, status, Header
from app.core.config import settings

def verify_admin_secret(x_admin_secret: str = Header(...)):
    if x_admin_secret != settings.ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin secret"
        )
    return True
