from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.routers import auth, users, cards, bills, payments, entities, simulations, connect
from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token

# Create FastAPI app
app = FastAPI(
    title="AgentPay API",
    description="AI-powered bill payment automation backend",
    version="1.0.0"
)

# CORS configuration - allow both common frontend ports
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(connect.router, prefix="/api/connect", tags=["bank-connection"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(cards.router, prefix="/api/cards", tags=["cards"])
app.include_router(bills.router, prefix="/api/bills", tags=["bills"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(simulations.router, prefix="/api/simulations", tags=["simulations"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AgentPay API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test Supabase connection
        supabase = get_supabase_client()
        # Simple query to test connection
        result = supabase.table("users").select("count").execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from Supabase JWT token"""
    try:
        token = credentials.credentials
        user_data = verify_supabase_token(token)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
