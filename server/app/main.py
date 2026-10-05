import math

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import dashboard, inventory, orders, planning, purchase_orders, reports, spending

app = FastAPI(title="Factory Inventory Management System")


def _json_safe(value):
    """Replace NaN/Infinity (which strict JSON can't encode) with their string form."""
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 422 errors echo the rejected input; if that was NaN/Infinity, the default response
    # can't be serialised and FastAPI would answer 500. Otherwise the response is unchanged.
    try:
        return await request_validation_exception_handler(request, exc)
    except ValueError:
        return JSONResponse(status_code=422,
                            content={"detail": _json_safe(jsonable_encoder(exc.errors()))})

# CORS middleware (demo only: allows every origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Factory Inventory Management System API", "version": "1.0.0"}


for module in (inventory, orders, planning, purchase_orders, dashboard, spending, reports):
    app.include_router(module.router)
