from fastapi import FastAPI


def start_server(app: FastAPI):
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
