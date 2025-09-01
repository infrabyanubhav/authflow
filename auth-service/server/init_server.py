import os
from datetime import datetime

import tabulate as tb
from api.v1.routes.health.__int__ import router as health_router
from api.v1.routes.simple_auth import router as simple_auth_router
from api.v1.routes.welcome import router as welcome_router
from config.init_config import api_config, secrets_config, server_config
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from key_store.generate_secrets import generate_key
from service.logs.logger import logger
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

"""
This file is used to initialize the server
The project is built with FastAPI and Starlette,
app: FastAPI is the main application object
config: init_config.py is the configuration file
api: v1/routes: simple_auth.py is the router for the simple auth routes
api: v1/routes: welcome.py is the router for the welcome routes
key_store: generate_secrets.py is the file that generates the secrets for the application
service: logs: logger.py is the file that logs the application
"""


print("Loading server config from path", " /config/init_config.py")


app = FastAPI(**server_config)


generate_key()

# Add session middleware for OAuth state management and static files
app.add_middleware(SessionMiddleware, secret_key=secrets_config["session_secret_key"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(simple_auth_router, prefix=api_config["prefix"] + "/simple_auth")

app.include_router(welcome_router, prefix="/session-success")

app.include_router(health_router)

list_of_routes = []

for route in app.routes:

    list_of_routes.append((route.path, route.name))

table = tb.tabulate(
    list_of_routes, headers=["Path", "Name"], tablefmt="grid", showindex=True
)

print(table)


logger.info("--------------------------------")
logger.info(
    "Welcome to AuthFlow Service, A secure and fast auth service for you made by developer for developers"
)
logger.info("--------------------------------")
logger.info(
    "Server was started at port 8000 on 0.0.0.0 at %s by %s",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    os.getlogin(),
)
