import sys
import uvicorn
from fastapi import FastAPI

from routes import dashboard_api, events

from middleware.interceptor import interceptor

app = FastAPI()

app.middleware("http")(interceptor)

# Routers

app.include_router(dashboard_api.router)
app.include_router(events.router)

@app.get("/")
def root():
    return {"msg": "Zion API running"}


@app.api_route("/test", methods=["GET", "POST"])
def test():
    return {"msg": "hit"}


def run():
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "debug"

    match mode:
        case "release":
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                reload=False
            )

        case _:

            uvicorn.run(
                "main:app",
                host="127.0.0.1",
                port=8000,
                reload=True
            )


if __name__ == "__main__":
    run()

