from __future__ import annotations

from authlib.integrations.starlette_client import OAuth  # type: ignore[import-untyped]
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from mathwizard.settings import get_settings


class NotAuthenticatedException(Exception):
    pass


def _get_oauth() -> OAuth:
    settings = get_settings()
    oauth = OAuth()
    issuer = f"https://cognito-idp.{settings.cognito_region}.amazonaws.com/{settings.cognito_user_pool_id}"
    oauth.register(
        name="cognito",
        client_id=settings.cognito_client_id,
        client_secret=settings.cognito_client_secret,
        server_metadata_url=f"{issuer}/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email"},
    )
    return oauth


def require_authentication(request: Request) -> bool:
    if request.session.get("user") is None:
        raise NotAuthenticatedException()
    return True


router = APIRouter(tags=["auth"])
_settings = get_settings()
_oauth = _get_oauth()


@router.get("/login", response_model=None)
async def login(request: Request) -> RedirectResponse:
    return await _oauth.cognito.authorize_redirect(request, _settings.cognito_redirect_uri)


@router.get("/callback")
async def callback(request: Request) -> RedirectResponse:
    try:
        token = await _oauth.cognito.authorize_access_token(request)
        user_info = token.get("userinfo")
        if user_info:
            request.session["user"] = dict(user_info)
        return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return RedirectResponse(url="/login?error=auth_failed", status_code=303)


@router.get("/logout")
@router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    request.session.clear()
    logout_uri = _settings.cognito_redirect_uri.replace("/callback", "/")
    cognito_logout_url = (
        f"https://{_settings.cognito_domain}/logout"
        f"?client_id={_settings.cognito_client_id}"
        f"&logout_uri={logout_uri}"
    )
    return RedirectResponse(url=cognito_logout_url, status_code=303)
