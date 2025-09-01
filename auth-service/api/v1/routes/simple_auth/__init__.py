from auth.simple_auth import SimpleAuth
from controllers.session_controller import SessionController
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from schema.auth_input import AuthInput
from schema.form import ForgotPasswordForm, ResetPasswordForm, SignInForm, SignUpForm
from service.logs.logger import logger
from service.ui.ui import render_template
from config.cookie_config import set_cookie, delete_cookie  
from config.init_config import api_config


router = APIRouter()


@router.get("/")
async def login():
    """Login page endpoint that renders the authentication form."""
    logger.info("Login endpoint called")
    return HTMLResponse(content=render_template("login.html", prefix=api_config.get("prefix")))


@router.post("/signup")
async def auth(request: Request, signup_form: SignUpForm = Form(...)):
    """User registration endpoint that creates new accounts."""
    logger.info("Signup endpoint called")
    password = str(signup_form.password)
    email = str(signup_form.email).lower()
    validated_input = AuthInput(email=email, password=password)
    if validated_input is None:
        return {
            "success": False,
            "message": "Invalid email or password",
            "error": "  To make your password strong, it should be at least 12 characters long and contain at least one uppercase letter, one lowercase letter, and one number.",
        }
    simple_auth = SimpleAuth(request=request)
    response = await simple_auth.sign_up(
        email=validated_input.email, password=validated_input.password
    )

    if response.get("success"):
        set_cookie(response, session_id=response.get("data").get("session_id"))
    else:
        return response

    return HTMLResponse(
        content=render_template("link_send.html", email=validated_input.email, prefix=api_config.get("prefix"))
    )


@router.post("/signin")
async def signin(request: Request, signin_form: SignInForm = Form(...)):
    """User authentication endpoint that validates credentials and creates sessions."""
    email = str(signin_form.email)
    password = str(signin_form.password)
    validated_input = AuthInput(email=email, password=password)
    if validated_input is None:
        return {
            "success": False,
            "message": "Invalid email or password",
            "error": "Invalid email or password! Please enter a valid email and password.",
        }
    simple_auth = SimpleAuth(request=request)
    response_data = await simple_auth.sign_in(
        email=validated_input.email, password=validated_input.password
    )
    new_response = None
    logger.info("Signin endpoint called")
    logger.info(response_data)
    if response_data.get("success") and response_data.get("data").get("session").get("session_id"):
        new_response = RedirectResponse(url=api_config.get("verify_url"),status_code=302)
        new_response.set_cookie(key="session_id", value=response_data.get("data").get("session").get("session_id"))
          
    else:
            return response_data
    logger.info("Signin endpoint called")
    
    return new_response



@router.get("/logout")
async def logout(request: Request):
    """User logout endpoint that terminates active sessions."""
    logger.info("Logout endpoint called")
    session_controller = SessionController()
    delete_cookie(request)
    response = await session_controller.delete_session(request=request)
    return {"message": "Logged out successfully"}


@router.get("/forgot-password")
async def forgot_password_email_link():
    """Forgot password page endpoint that renders the password reset form."""
    logger.info("Forgot password email link endpoint called")
    return HTMLResponse(content=render_template("reset_password.html", prefix=api_config.get("prefix")))


@router.post("/forgot-password/email-link")
async def forgot_password(
    request: Request, forgot_password_form: ForgotPasswordForm = Form(...)
):
    """Password reset email endpoint that sends recovery links."""
    logger.info(
        "Forgot password endpoint called for email: {}".format(
            forgot_password_form.email
        )
    )
    simple_auth = SimpleAuth(request=request)
    response = await simple_auth.forgot_password(email=forgot_password_form.email)

    logger.info(
        "Forgot password endpoint called for email: {}".format(
            forgot_password_form.email
        )
    )

    return HTMLResponse(
        content=render_template("link_send.html", email=forgot_password_form.email, prefix=api_config.get("prefix"))
    )


@router.get("/reset-password")
async def reset_password_page():
    """Reset password page endpoint that renders the password update form."""
    logger.info("Reset password page endpoint called")
    return HTMLResponse(content=render_template("reset_password.html", prefix=api_config.get("prefix")))


@router.post("/update-password")
async def validate_reset_token(
    request: Request, reset_password_form: ResetPasswordForm = Form(...)
):
    """Password update endpoint that validates reset tokens and updates passwords."""
    logger.info("Validate reset token endpoint called")
    password = str(reset_password_form.password)
    simple_auth = SimpleAuth(request=request)
    response = await simple_auth.reset_password(password=password)
    return response
