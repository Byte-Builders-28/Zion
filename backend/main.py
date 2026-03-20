import sys
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from db.store import init_chain_table
from routes import dashboard_api, events, simulate, anomalies
from routes.chain_routes import router as chain_router

from middleware.interceptor import interceptor


@asynccontextmanager
async def lifespan(app):
    init_chain_table()
    print("[DB] chain_log table ready")
    yield


app = FastAPI(title="Zion", lifespan=lifespan)
app.middleware("http")(interceptor)

# Routers

app.include_router(dashboard_api.router)
app.include_router(events.router)
app.include_router(simulate.router)
app.include_router(anomalies.router)
app.include_router(chain_router)


@app.get("/")
def root():
    return {"msg": "Zion API running"}


@app.api_route("/test", methods=["GET", "POST"])
def test():
    return {"msg": "hit"}


@app.post("/login")
def login(creds: dict):
    # Always fail login for attack simulation to trigger 401s
    if creds.get("password") == "correct_password":
        return {"msg": "success"}
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=401, content={"msg": "Unauthorized"})


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
