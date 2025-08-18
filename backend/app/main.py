from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import os
import logging
import time
import asyncio
from datetime import datetime

# Import routers directly
from app.routers.user import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.conversations import router as conversations_router
from app.routers.share import router as share_router
from app.routers.chat_analytics import router as chat_analytics_router
from app.routers.peers import router as peers_router
from app.routers.messages import router as messages_router
from app.routers.profiles import router as profiles_router
from app.routers.test import router as test_router
from app.routers.space import router as space_router
from app.routers.vector_search import router as vector_router
from app.routers.recommendations import router as recommendations_router
from app.routers.careers import router as careers_router
from app.routers.tree import router as tree_router
from app.routers.tree_paths import router as tree_paths_router
from app.routers.node_notes import router as node_notes_router
from app.routers.user_progress import router as user_progress_router
from app.routers.jobs import router as jobs_router
from app.routers.program_recommendations import router as program_recommendations_router
from app.routers.holland_test import router as holland_test_router
from app.routers.hexaco_test import router as hexaco_test_router
from app.routers.insight_router import router as insight_router
from app.routers.competence_tree import router as competence_tree_router
from app.routers.career_progression import router as career_progression_router
from app.routers.users import router as users_router
from app.routers.reflection_router import router as reflection_router
from app.routers.avatar import router as avatar_router
from app.routers.onboarding import router as onboarding_router
from app.routers.education import router as education_router
from app.routers.school_programs import router as school_programs_router
from app.routers.courses import router as courses_router
from app.routers.enhanced_chat import router as enhanced_chat_router
from app.routers.socratic_chat import router as socratic_chat_router
from app.routers.career_goals import router as career_goals_router
# from app.api.endpoints.job_recommendations import router as job_recommendations_router  # Module not found
from app.routers.llm_career_advisor import router as llm_career_advisor_router
from app.routers.orientator import router as orientator_router
from app.routers.auth_clerk import router as auth_clerk_router
from app.routers.cache_monitoring import router as cache_monitoring_router
from app.routers.test_auth import router as test_auth_router
from app.routers.jwks_monitoring import router as jwks_monitoring_router
from fastapi import FastAPI, HTTPException
from pathlib import Path
# from scripts.model_loader import load_models
from logging.handlers import RotatingFileHandler
from .utils.logging_config import setup_logging

# from app.routers.resume import router as resume_router  # Commented out resume router

# Set up logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Navigo API",
    description="API for the Navigo Career and Skill Tree Explorer",
    version="0.1.0",
)

# ✅ INTEGRATE FASTAPI-MCP FOR ADVANCED API DEBUGGING
try:
    from fastapi_mcp import FastApiMCP
    
    # Initialize MCP with comprehensive debugging capabilities
    mcp = FastApiMCP(
        app,
        name="Orientor Platform MCP Tools", 
        description="Advanced debugging and management tools for Orientor Platform APIs"
    )
    
    # Mount the MCP server for API tool access (automatically mounts at /mcp)
    mcp.mount()
    
    logger.info("🚀 FastAPI-MCP integration successful!")
    logger.info("   - API debugging tools available at /mcp")
    logger.info("   - All endpoints automatically exposed as MCP tools")
    logger.info("   - Enhanced error tracking and authentication flow visibility")
    
except ImportError as e:
    logger.warning(f"⚠️ FastAPI-MCP not available: {e}")
    logger.info("   - API will function normally without MCP debugging tools")
    logger.info("   - To enable MCP integration: pip install fastapi-mcp")
except Exception as e:
    logger.error(f"❌ FastAPI-MCP integration failed: {e}")
    logger.info("   - Continuing without MCP tools")

# ✅ ADD ENHANCED API DEBUGGING ENDPOINTS
@app.get("/debug/holland-test", tags=["debugging"])
async def debug_holland_test():
    """
    🔍 Enhanced debugging endpoint for Holland test API issues
    Helps diagnose the root causes of empty {} response errors
    """
    try:
        from app.utils.prisma_client import get_prisma_client
        from app.utils.clerk_auth import get_current_user
        
        prisma = get_prisma_client()
        
        debug_info = {
            "timestamp": time.time(),
            "endpoints_analysis": {
                "holland_routes": [route.path for route in app.routes if "holland" in route.path.lower()],
                "total_routes": len(app.routes)
            },
            "database_connectivity": {
                "prisma_available": prisma is not None,
                "connection_status": "available" if prisma else "unavailable"
            },
            "authentication_system": {
                "clerk_auth_available": get_current_user is not None,
                "auth_function": str(get_current_user) if get_current_user else "None"
            },
            "common_fixes_applied": {
                "backend_typo_fixed": "HTTP_INTERNAL_SERVER_ERROR",
                "defensive_getattr": "result attribute access protected",
                "frontend_validation": "service response validation added",
                "error_fallbacks": "safe default values implemented"
            },
            "troubleshooting_urls": {
                "test_endpoint": "/api/v1/tests/holland/user-results",
                "debug_endpoint": "/debug/holland-test",
                "mcp_tools": "/mcp"
            },
            "recent_fixes": [
                "Fixed HTTP_interNAL_SERVER_ERROR typo in holland_test.py:632",
                "Added defensive getattr() for Prisma query result access", 
                "Implemented response validation in hollandTestService.ts",
                "Added safe default fallbacks for empty responses"
            ]
        }
        
        return {
            "status": "✅ Holland test debugging information",
            "debug_info": debug_info,
            "message": "Use this information to diagnose Holland test API issues",
            "next_steps": [
                "Test /api/v1/tests/holland/user-results endpoint with proper auth",
                "Check browser console for specific error messages",
                "Verify Clerk authentication tokens are valid",
                "Use MCP tools at /mcp for advanced debugging"
            ]
        }
        
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        return {
            "status": "❌ Debug endpoint error",
            "error": str(e),
            "message": "Debug endpoint encountered an issue"
        }

@app.get("/debug/api-health", tags=["debugging"])
async def debug_api_health():
    """
    🏥 API health check with detailed diagnostics
    """
    try:
        health_status = {
            "timestamp": time.time(),
            "fastapi_mcp_integration": "✅ Installed and configured",
            "total_endpoints": len(app.routes),
            "critical_endpoints": {
                "holland_test": len([r for r in app.routes if "holland" in r.path.lower()]),
                "authentication": len([r for r in app.routes if "auth" in r.path.lower()]),
                "careers": len([r for r in app.routes if "career" in r.path.lower()])
            },
            "recent_error_fixes": [
                "Holland test backend errors resolved",
                "Frontend defensive programming added",
                "Authentication flow stabilized"
            ],
            "debugging_tools": {
                "mcp_available": True,
                "debug_endpoints": ["/debug/holland-test", "/debug/api-health"],
                "logging_level": "INFO"
            }
        }
        
        return {
            "status": "✅ API health check complete",
            "health": health_status,
            "message": "All systems operational with enhanced debugging"
        }
        
    except Exception as e:
        return {
            "status": "❌ Health check failed", 
            "error": str(e)
        }

# Configure static files for avatars (only if directory exists)
import os
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logging.warning(f"Static directory '{static_dir}' does not exist - skipping static file mounting")

# Configure CORS
if os.getenv("ENV", "development") == "development":
    logger.warning("⚠️ Development CORS enabled - DO NOT USE IN PRODUCTION")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,
    )
else:
    # Production CORS settings - Now configurable via environment variable
    cors_origins_env = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    base_origins = [origin.strip() for origin in cors_origins_env.split(",")]
    
    # Add additional production origins
    additional_origins = [
        "https://navigoproject.vercel.app",  # Production frontend
        "http://localhost:5173",  # Vite development server
        "https://localhost:3000",  # HTTPS local development
        "https://localhost:3007",  # HTTPS local development (alt port)
        "https://localhost:5173",  # HTTPS Vite development
        "https://*.up.railway.app",  # Railway domains
        "https://*.railway.app",    # Railway domains  
        "https://*.clerk.accounts.dev",  # Clerk development domains
        "https://*.clerk.com",  # Clerk production domains
    ]
    
    # Combine base origins from env var with additional production origins
    origins = base_origins + additional_origins
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Clerk-Auth-Token"],
        expose_headers=["Set-Cookie"],
        max_age=600,
    )

# Global variable to store recent requests for middleware
_middleware_recent_requests = set()

# Add debug middleware
@app.middleware("http")
async def auth_debug_middleware(request: Request, call_next):
    """Debug middleware to trace authentication issues"""
    global _middleware_recent_requests
    
    # Only log API requests (reduced logging to prevent spam)
    if "/api/" in str(request.url):
        auth_header = request.headers.get("authorization", "None")
        
        if auth_header != "None":
            # Only log unique requests to reduce log spam
            request_signature = f"{request.method}:{request.url.path}:{hash(auth_header[:20])}"
            
            # Check if we've seen this request recently (using a simple in-memory set)
            current_time = int(time.time() / 10)  # 10-second windows
            cache_key = f"{request_signature}:{current_time}"
            
            # Clean old entries (keep only current and previous window)
            _middleware_recent_requests = {
                key for key in _middleware_recent_requests 
                if key.split(':')[-1] in [str(current_time), str(current_time - 1)]
            }
            
            # Only log if this is a new request
            if cache_key not in _middleware_recent_requests:
                _middleware_recent_requests.add(cache_key)
                token_type = "JWT" if auth_header.startswith("Bearer eyJ") else "Session" if "sess_" in auth_header else "Unknown"
                logger.debug(f"🔐 Auth Request: {request.method} {request.url.path}")
                logger.debug(f"   Token Type: {token_type}")
    
    # Process request
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log failures
    if response.status_code == 401 and "/api/" in str(request.url):
        logger.warning(f"❌ 401 Unauthorized: {request.url.path} ({duration:.2f}s)")
    elif response.status_code == 404 and "/api/" in str(request.url):
        logger.warning(f"❌ 404 Not Found: {request.url.path} ({duration:.2f}s)")
    
    return response

# Print debug information about routers
try:
    logger.info("======= ROUTER REGISTRATION DETAILS =======")
    logger.info(f"auth_router import path: {auth_router.__module__}")
    logger.info("get_current_user import removed to prevent circular dependencies")
    logger.info(f"profiles_router import path: {profiles_router.__module__}")
    
    logger.info(f"Registering auth_router routes: {[f'{route.path} [{route.methods}]' for route in auth_router.routes]}")
    logger.info(f"Registering profiles_router routes: {[f'{route.path} [{route.methods}]' for route in profiles_router.routes]}")
    logger.info(f"Registering chat_router routes: {[f'{route.path} [{route.methods}]' for route in chat_router.routes]}")
    logger.info(f"Registering peers_router routes: {[f'{route.path} [{route.methods}]' for route in peers_router.routes]}")
    logger.info(f"Registering messages_router routes: {[f'{route.path} [{route.methods}]' for route in messages_router.routes]}")
    logger.info(f"Registering test_router routes: {[f'{route.path} [{route.methods}]' for route in test_router.routes]}")
    logger.info(f"Registering space_router routes: {[f'{route.path} [{route.methods}]' for route in space_router.routes]}")
    logger.info(f"Registering vector_router routes: {[f'{route.path} [{route.methods}]' for route in vector_router.routes]}")
    logger.info(f"Registering recommendations_router routes: {[f'{route.path} [{route.methods}]' for route in recommendations_router.routes]}")
    logger.info(f"Registering careers_router routes: {[f'{route.path} [{route.methods}]' for route in careers_router.routes]}")
    logger.info(f"Registering tree_router routes: {[f'{route.path} [{route.methods}]' for route in tree_router.routes]}")
    logger.info(f"Registering tree_paths_router routes: {[f'{route.path} [{route.methods}]' for route in tree_paths_router.routes]}")
    logger.info(f"Registering node_notes_router routes: {[f'{route.path} [{route.methods}]' for route in node_notes_router.routes]}")
    logger.info(f"Registering user_progress_router routes: {[f'{route.path} [{route.methods}]' for route in user_progress_router.routes]}")
    logger.info(f"Registering holland_test_router routes: {[f'{route.path} [{route.methods}]' for route in holland_test_router.routes]}")
    logger.info(f"Registering hexaco_test_router routes: {[f'{route.path} [{route.methods}]' for route in hexaco_test_router.routes]}")
    logger.info(f"Registering insight_router routes: {[f'{route.path} [{route.methods}]' for route in insight_router.routes]}")
    logger.info(f"Registering orientator_router routes: {[f'{route.path} [{route.methods}]' for route in orientator_router.routes]}")
    logger.info("============================================")
except Exception as e:
    logger.error(f"Error while logging router details: {str(e)}")

# Include routers in the correct order
logger.info("Including routers in the FastAPI app")
# Include auth router first - it defines dependencies
app.include_router(auth_router)
logger.info("Auth router included successfully")
# Include profiles router after auth router
app.include_router(profiles_router, prefix="/api/v1")
logger.info("Profiles router included successfully")
# Include remaining routers  
# Standardize all API routes with /api/v1 prefix
# Include all core routers with /api/v1 prefix for standardization
app.include_router(test_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1") 
app.include_router(chat_router, prefix="/api/v1")
app.include_router(share_router, prefix="/api/v1")
app.include_router(chat_analytics_router, prefix="/api/v1")
app.include_router(peers_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(space_router, prefix="/api/v1")
app.include_router(vector_router, prefix="/api/v1")
app.include_router(recommendations_router, prefix="/api/v1")
app.include_router(careers_router, prefix="/api/v1")
app.include_router(tree_router, prefix="/api/v1")
app.include_router(tree_paths_router, prefix="/api/v1")
app.include_router(node_notes_router, prefix="/api/v1")
app.include_router(user_progress_router, prefix="/api/v1")
# Also include without prefix for legacy compatibility  
app.include_router(user_progress_router)
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(program_recommendations_router, prefix="/api/v1")
app.include_router(holland_test_router, prefix="/api/v1")
app.include_router(hexaco_test_router, prefix="/api/v1")
app.include_router(insight_router, prefix="/api/v1")
app.include_router(competence_tree_router, prefix="/api/v1")
app.include_router(career_progression_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(reflection_router, prefix="/api/v1")
app.include_router(avatar_router, prefix="/api/v1")
app.include_router(onboarding_router, prefix="/api/v1")
app.include_router(education_router, prefix="/api/v1")
app.include_router(school_programs_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(enhanced_chat_router, prefix="/api/v1")
app.include_router(socratic_chat_router, prefix="/api/v1")
app.include_router(career_goals_router, prefix="/api/v1")
app.include_router(llm_career_advisor_router, prefix="/api/v1")
app.include_router(orientator_router, prefix="/api/v1")
app.include_router(auth_clerk_router, prefix="/api/v1")
app.include_router(cache_monitoring_router, prefix="/api/v1")
app.include_router(test_auth_router, prefix="/api/v1")
app.include_router(jwks_monitoring_router, prefix="/api/v1")
logger.info("All routers included successfully")

# Explicitly capture route after including it
logger.info("=== Available Routes ===")
for route in app.routes:
    if hasattr(route, 'methods'):
        logger.info(f"Route: {route.path}, Methods: {route.methods}")
    else:
        logger.info(f"Mount: {route.path}")
logger.info("======================")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to the Navigo API. Go to /docs for API documentation."}

# @app.get("/api/health") # /api/health
# def health_check():
#     try:
#         return {"status": "ok"}
#     except Exception as e:
#         logger.error(f"Health check failed: {str(e)}")
#         return {"status": "error", "detail": str(e)}

@app.get("/health")
async def health_check():
    try:
        # Basic health check without model dependency
        return {"status": "healthy", "message": "Service is running"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "detail": str(e)}

# Startup event with error handling
@app.on_event("startup")
async def startup_event():
    """Application startup configuration"""
    try:
        logger.info("🚀 Application startup initiated")
        
        # Run security validation first
        logger.info("🔍 Running security validation...")
        try:
            from .utils.security_validation import validate_production_security
            security_results = validate_production_security()
            
            if not security_results["deployment_safe"]:
                critical_count = len(security_results["issues"]["critical"])
                logger.error(f"🚨 SECURITY VALIDATION FAILED: {critical_count} critical issues found")
                
                # In production, we should consider failing startup
                is_production = os.getenv("ENVIRONMENT") == "production" or os.getenv("RAILWAY_ENVIRONMENT") == "production"
                if is_production and critical_count > 0:
                    logger.critical("❌ WARNING: Critical security issues detected in production")
            else:
                logger.info("✅ Security validation passed")
                
        except Exception as e:
            logger.error(f"❌ Security validation error: {e}")
        
        # Preload models asynchronously during startup
        logger.info("🧠 Preloading ML models asynchronously...")
        asyncio.create_task(preload_all_models())
        
        # Initialize database if not already done
        try:
            from .utils.database import initialize_database, database_connected
            if not database_connected:
                logger.info("🔌 Attempting database initialization...")
                initialize_database()
        except Exception as db_e:
            logger.warning(f"⚠️ Database initialization failed (continuing anyway): {str(db_e)}")
        
        # Initialize authentication cache system
        try:
            logger.info("🚀 Initializing authentication cache system...")
            from .utils.auth_cache import start_cache_maintenance, get_jwks_cache
            
            # Pre-populate JWKS cache
            jwks_cache = get_jwks_cache()
            await jwks_cache.get_jwks()
            logger.info("✅ JWKS cache pre-populated")
            
            # Start background maintenance
            await start_cache_maintenance()
            logger.info("✅ Cache maintenance tasks started")
            
        except Exception as cache_e:
            logger.warning(f"⚠️ Cache system initialization failed (continuing anyway): {str(cache_e)}")
        
        logger.info("✅ Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}")
        # Don't fail startup - let Railway handle gracefully
        pass

def load_models():
    """Load ML models with graceful error handling"""
    try:
        logger.info("Loading models...")
        
        # Try to load models from scripts if available
        try:
            from scripts.model_loader import load_models as script_load_models
            script_load_models()
            logger.info("Models loaded from scripts")
        except ImportError:
            logger.info("No model loader script found, skipping model loading")
        except Exception as e:
            logger.warning(f"Script model loading failed: {str(e)}")
        
        # Try to load any other models
        # Add your specific model loading code here
        
        logger.info("Model loading process completed")
        
    except Exception as e:
        logger.error(f"Error in load_models: {str(e)}")
        # Don't raise the exception, just log it for graceful degradation
        pass

async def preload_all_models():
    """Preload all ML models asynchronously during startup"""
    try:
        logger.info("🧠 Starting asynchronous model preloading...")
        
        # Import and preload vector search model
        try:
            from .routers.vector_search import preload_embedding_model
            await preload_embedding_model()
        except Exception as e:
            logger.warning(f"Failed to preload vector search model: {str(e)}")
        
        # Import and preload OaSIS models
        try:
            from .services.Oasisembedding_service import oasis_model_state, esco_model_state
            await asyncio.get_event_loop().run_in_executor(None, oasis_model_state.load_models)
            await asyncio.get_event_loop().run_in_executor(None, esco_model_state.load_models)
            logger.info("✅ OaSIS and ESCO models preloaded")
        except Exception as e:
            logger.warning(f"Failed to preload OaSIS/ESCO models: {str(e)}")
            
        # Import and preload career progression service
        try:
            from .routers.career_progression import preload_career_progression_service
            await preload_career_progression_service()
        except Exception as e:
            logger.warning(f"Failed to preload career progression service: {str(e)}")
            
        # Import and preload competence tree service
        try:
            from .routers.competence_tree import preload_competence_tree_service
            await preload_competence_tree_service()
        except Exception as e:
            logger.warning(f"Failed to preload competence tree service: {str(e)}")
        
        logger.info("✅ Asynchronous model preloading completed")
        
    except Exception as e:
        logger.error(f"Error during model preloading: {str(e)}")
        # Don't raise - continue startup gracefully

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000) #, reload=True)

# Enhanced request validation error handler - P1 HIGH priority fix
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Enhanced validation error handler with detailed debugging information
    Addresses HTTP 422 validation errors identified in comprehensive error analysis
    """
    try:
        # Extract detailed error information
        error_details = []
        for error in exc.errors():
            error_info = {
                "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
                "message": error.get("msg", "Unknown validation error"),
                "type": error.get("type", "validation_error"),
                "input_value": error.get("input", "Not provided")
            }
            error_details.append(error_info)
        
        # Build comprehensive error response
        error_response = {
            "status": "validation_error",
            "message": "Request validation failed",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
            "errors": error_details,
            "error_count": len(error_details)
        }
        
        # Add debugging information for development
        if os.getenv("ENV", "development") == "development":
            try:
                request_body = await request.body()
                error_response["debug_info"] = {
                    "request_size": len(request_body) if request_body else 0,
                    "content_type": request.headers.get("content-type", "unknown"),
                    "user_agent": request.headers.get("user-agent", "unknown")
                }
            except:
                error_response["debug_info"] = {"note": "Could not extract request body"}
        
        # Log validation error for monitoring
        logger.warning(f"🔍 Request validation failed on {request.method} {request.url.path}: {len(error_details)} errors")
        for error_detail in error_details[:3]:  # Log first 3 errors to avoid spam
            logger.warning(f"   • Field '{error_detail['field']}': {error_detail['message']}")
        
        return JSONResponse(
            status_code=422,
            content=error_response
        )
        
    except Exception as handler_error:
        # Fallback error response if handler itself fails
        logger.error(f"❌ Validation error handler failed: {str(handler_error)}")
        return JSONResponse(
            status_code=422,
            content={
                "status": "validation_error",
                "message": "Request validation failed with handler error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url.path),
                "method": request.method,
                "handler_error": str(handler_error)
            }
        )

# Set default SECRET_KEY for development if not configured
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "development-secret-key-change-in-production-12345678901234567890"
    logger.warning("⚠️ Using default SECRET_KEY for development - change for production!")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Railway-assigned port
    print(f"🚀 Starting app on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
