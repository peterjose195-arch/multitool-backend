from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from database import init_db
from modules.pdf_converter import router as pdf_router
from modules.price_tracker import router as tracker_router
from modules.lead_gen import router as lead_router

# Initialize database tables on startup
init_db()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Multi-Tool Platform API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount tool routers
app.include_router(pdf_router)
app.include_router(tracker_router)
app.include_router(lead_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "online"}
  
