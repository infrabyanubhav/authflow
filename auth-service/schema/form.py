from pydantic import BaseModel


class SignUpForm(BaseModel):
    email: str
    password: str


class SignInForm(BaseModel):
    email: str
    password: str


class ForgotPasswordForm(BaseModel):
    email: str


class ResetPasswordForm(BaseModel):
    password: str
    confirm_password: str
