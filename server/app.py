# File: server/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from typing import Optional
from datetime import datetime
import os
import logging

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required in production/Docker

# Import sensor interface for background polling
from server import sensor_interface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tanks-api")

# Config (loaded from environment variables or .env file)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:mongo@localhost:27017/?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "tanks_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "sensor_readings")

app = FastAPI(title="Reptillia API", version="1.0.0")

# Setup Jinja2 templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# Serve static files from server/static (for JS/CSS)
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# allow simple CORS for devices / debugging (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# Pydantic models for Species Profiles
class SpeciesProfile(BaseModel):
    species_name: str = Field(..., description="Species name (e.g., 'Leopard Gecko')")
    cool_temp: float = Field(..., description="Optimal cool temperature in Celsius")
    hot_temp: float = Field(..., description="Optimal hot temperature in Celsius")
    basking_temp: float = Field(..., description="Optimal basking temperature in Celsius")
    humidity: float = Field(..., description="Optimal humidity percentage")
    daylight_hours: int = Field(default=12, description="Hours of daylight needed")
    basking_duration_minutes: int = Field(default=60, description="Duration of basking in minutes")
    requires_basking: bool = Field(default=True, description="Whether species requires basking")
    feed_interval_days: int = Field(default=7, description="Feeding interval in days")
    description: str = Field(default="", description="Species description and care notes")

class SpeciesProfileUpdate(BaseModel):
    species_name: Optional[str] = None
    cool_temp: Optional[float] = None
    hot_temp: Optional[float] = None
    basking_temp: Optional[float] = None
    humidity: Optional[float] = None
    daylight_hours: Optional[int] = None
    basking_duration_minutes: Optional[int] = None
    requires_basking: Optional[bool] = None
    feed_interval_days: Optional[int] = None
    description: Optional[str] = None

# Pydantic model for incoming readings
class Reading(BaseModel):
    id: int = Field(..., description="Tank identifier")
    temp: float
    humidity: float
    light: bool
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


# powerstrip control module (renamed to powerstrip_interface)
try:
    import powerstrip_interface as powerstrip_module
except Exception:
    # try top-level import when running outside package
    import server.powerstrip_interface as powerstrip_module


# try to reference the PowerstripUnavailableError type if present on the module
PowerstripUnavailableError = getattr(powerstrip_module, "PowerstripUnavailableError", None)

# Mongo client placeholder
mongo_client: Optional[AsyncIOMotorClient] = None
collection = None
species_profiles_collection = None

@app.on_event("startup")
async def startup_db_client():
    global mongo_client, collection, species_profiles_collection
    mongo_client = AsyncIOMotorClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    species_profiles_collection = db["species_profiles"]
    logger.info("Connected to MongoDB - initialized sensor_readings and species_profiles collections")

@app.on_event("startup")
async def startup_powerstrip_interface():
    try:
        await powerstrip_module.initialize()
        logger.info("Powerstrip interface initialized")
    except Exception as e:
        logger.warning("Failed to initialize powerstrip interface: %s", str(e))
        # Don't fail startup if powerstrip is unavailable

@app.on_event("startup")
async def startup_sensor_polling():
    try:
        await sensor_interface.initialize()
        logger.info("Sensor polling initialized")
    except Exception as e:
        logger.warning("Failed to initialize sensor polling: %s", str(e))
        # Don't fail startup if sensor polling is unavailable

@app.on_event("shutdown")
async def shutdown_db_client():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")

@app.on_event("shutdown")
async def shutdown_sensor_polling():
    try:
        await sensor_interface.cleanup()
        logger.info("Sensor polling cleaned up")
    except Exception as e:
        logger.warning("Error during sensor polling cleanup: %s", str(e))

@app.post("/api/readings", status_code=201)
async def create_reading(reading: Reading):
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    doc = reading.dict()
    # Optionally rename `id` key to `tank_id` in DB:
    doc["tank_id"] = doc.pop("id")
    try:
        res = await collection.insert_one(doc)
        logger.info("Inserted reading for tank %s id=%s", doc["tank_id"], res.inserted_id)
        return {"inserted_id": str(res.inserted_id)}
    except Exception as e:
        logger.exception("Failed to insert reading")
        raise HTTPException(status_code=502, detail="Failed to persist reading")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("home.html", context)

@app.get("/api/readings/{tank_id}")
async def get_readings(tank_id: int):
    if collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        readings = await collection.find({"tank_id": tank_id}).to_list(length=None)
        # Convert ObjectId to string for JSON serialization
        for reading in readings:
            reading["_id"] = str(reading["_id"])
        return {"tank_id": tank_id, "readings": readings}
    except Exception as e:
        logger.exception("Failed to fetch readings")
        raise HTTPException(status_code=502, detail="Failed to fetch readings")


@app.get("/health", response_class=HTMLResponse)
async def health(request: Request):
    """Health check endpoint - returns API status as HTML view"""
    try:
        if mongo_client:
            # Ping MongoDB to verify connection
            await mongo_client.admin.command('ping')
            db_status = "connected"
        else:
            db_status = "disconnected"
    except Exception as e:
        logger.error("Health check failed: %s", str(e))
        db_status = "error"

    context = {
        "request": request,
        "status": "up",
        "service": "Reptillia API",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

    return templates.TemplateResponse("health.html", context)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 error page"""
    context = {
        "request": request,
        "error": "Not Found",
        "message": f"The requested path does not exist",
        "path": str(request.url.path)
    }
    return templates.TemplateResponse("404.html", context, status_code=404)


# ============================================
# SPECIES PROFILE MANAGEMENT ENDPOINTS
# ============================================

@app.post("/api/species-profiles", status_code=201)
async def create_species_profile(profile: SpeciesProfile):
    """Create a new species profile in the database."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        doc = profile.dict()
        doc["created_at"] = datetime.utcnow()
        result = await species_profiles_collection.insert_one(doc)
        logger.info("Created species profile for %s (ID: %s)", profile.species_name, result.inserted_id)
        return {"_id": str(result.inserted_id), **doc}
    except Exception as e:
        logger.exception("Failed to create species profile")
        raise HTTPException(status_code=502, detail="Failed to create species profile")


@app.get("/api/species-profiles")
async def list_species_profiles():
    """List all species profiles in the database."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        profiles = await species_profiles_collection.find({}).to_list(length=None)
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
        return {"profiles": profiles}
    except Exception as e:
        logger.exception("Failed to fetch species profiles")
        raise HTTPException(status_code=502, detail="Failed to fetch species profiles")


@app.get("/api/species-profiles/{profile_id}")
async def get_species_profile(profile_id: str):
    """Get a specific species profile by ID."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        from bson import ObjectId
        profile = await species_profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(status_code=404, detail="Species profile not found")
        profile["_id"] = str(profile["_id"])
        return profile
    except Exception as e:
        if "404" in str(e):
            raise
        logger.exception("Failed to fetch species profile")
        raise HTTPException(status_code=502, detail="Failed to fetch species profile")


@app.get("/api/species-profiles/name/{species_name}")
async def get_species_profile_by_name(species_name: str):
    """Get a species profile by species name."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        profile = await species_profiles_collection.find_one(
            {"species_name": {"$regex": species_name, "$options": "i"}}
        )
        if not profile:
            raise HTTPException(status_code=404, detail=f"Species profile for '{species_name}' not found")
        profile["_id"] = str(profile["_id"])
        return profile
    except Exception as e:
        if "404" in str(e):
            raise
        logger.exception("Failed to fetch species profile")
        raise HTTPException(status_code=502, detail="Failed to fetch species profile")


@app.put("/api/species-profiles/{profile_id}")
async def update_species_profile(profile_id: str, profile_update: SpeciesProfileUpdate):
    """Update a species profile."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        from bson import ObjectId
        update_data = {k: v for k, v in profile_update.dict().items() if v is not None}
        if not update_data:
            return {"message": "No fields to update"}

        result = await species_profiles_collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Species profile not found")
        logger.info("Updated species profile %s", profile_id)
        return {"message": "Species profile updated successfully"}
    except Exception as e:
        if "404" in str(e):
            raise
        logger.exception("Failed to update species profile")
        raise HTTPException(status_code=502, detail="Failed to update species profile")


@app.delete("/api/species-profiles/{profile_id}")
async def delete_species_profile(profile_id: str):
    """Delete a species profile from the database."""
    if species_profiles_collection is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    try:
        from bson import ObjectId
        result = await species_profiles_collection.delete_one({"_id": ObjectId(profile_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Species profile not found")
        logger.info("Deleted species profile %s", profile_id)
        return {"message": "Species profile deleted successfully"}
    except Exception as e:
        if "404" in str(e):
            raise
        logger.exception("Failed to delete species profile")
        raise HTTPException(status_code=502, detail="Failed to delete species profile")


#endpoints for powerstrip control

class OutletAction(BaseModel):
    action: str = Field(..., description="on, off, or toggle")


@app.get("/api/powerstrip/{index}")
async def read_outlet(index: int):
    try:
        state = await powerstrip_module.get_outlet_state(index)
        return {"index": index, "state": state}
    except Exception as e:
        # If the error indicates the powerstrip is unavailable, return 503
        if PowerstripUnavailableError and isinstance(e, PowerstripUnavailableError):
            logger.warning("Powerstrip unavailable when reading outlet %s: %s", index, str(e))
            raise HTTPException(status_code=503, detail="Powerstrip unreachable; please try again later")
        logger.exception("Failed to read outlet state")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/powerstrip/{index}")
async def control_outlet(index: int, action: OutletAction):
    try:
        result = await powerstrip_module.set_outlet_state(index, action.action)
        return {"index": index, "state": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if PowerstripUnavailableError and isinstance(e, PowerstripUnavailableError):
            logger.warning("Powerstrip unavailable when controlling outlet %s: %s", index, str(e))
            raise HTTPException(status_code=503, detail="Powerstrip unreachable; please try again later")
        logger.exception("Failed to control outlet")
        raise HTTPException(status_code=500, detail=str(e))
