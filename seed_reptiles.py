#!/usr/bin/env python
"""
Seed script to populate the species_profiles collection with reptile species and their optimal habitat variables.
Run this once to populate your MongoDB with species profile data.
"""

from pymongo import MongoClient
from datetime import datetime

# Compatibility fix for older pymongo versions
try:
    from collections import MutableMapping
except ImportError:
    import collections.abc as _abc
    import collections
    collections.MutableMapping = _abc.MutableMapping

# MongoDB connection
MONGO_URI = "mongodb://mongo:mongo@localhost:27017/?authSource=admin"
MONGO_DB = "tanks_db"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
species_col = db["species_profiles"]

# Species profile data with optimum habitat variables
species_profiles = [
    {
        "species_name": "Leopard Gecko",
        "cool_temp": 26.0,
        "hot_temp": 32.0,
        "basking_temp": 35.0,
        "humidity": 40.0,
        "daylight_hours": 12,
        "basking_duration_minutes": 60,
        "requires_basking": True,
        "feed_interval_days": 2,
        "description": "A popular beginner-friendly gecko species. Prefers temperatures with a cool side around 26°C and a warm side around 32°C. Requires regular feeding and proper humidity levels.",
        "created_at": datetime.utcnow()
    },
    {
        "species_name": "Bearded Dragon",
        "cool_temp": 26.0,
        "hot_temp": 38.0,
        "basking_temp": 40.0,
        "humidity": 30.0,
        "daylight_hours": 12,
        "basking_duration_minutes": 120,
        "requires_basking": True,
        "feed_interval_days": 1,
        "description": "A popular medium-sized reptile requiring high basking temperatures and daily feeding. Known for their docile temperament and impressive spiky appearance.",
        "created_at": datetime.utcnow()
    },
    {
        "species_name": "Crested Gecko",
        "cool_temp": 20.0,
        "hot_temp": 25.0,
        "basking_temp": 26.0,
        "humidity": 80.0,
        "daylight_hours": 12,
        "basking_duration_minutes": 30,
        "requires_basking": False,
        "feed_interval_days": 2,
        "description": "A delicate arboreal gecko requiring high humidity and cooler temperatures. No basking required. Feeds primarily on prepared gecko diets and fruit.",
        "created_at": datetime.utcnow()
    }
]

def seed_species_profiles():
    """Insert species profile data into the database."""
    try:
        # Clear existing data (optional - comment out if you want to keep existing records)
        # species_col.delete_many({})

        # Insert new data
        result = species_col.insert_many(species_profiles)
        print(f"✓ Successfully inserted {len(result.inserted_ids)} species profiles into the database")

        # Display inserted species
        print("\nInserted species profiles:")
        for profile in species_col.find({}).sort("_id", -1).limit(len(species_profiles)):
            print(f"\n  Species: {profile['species_name']}")
            print(f"  Cool Temp: {profile['cool_temp']}°C")
            print(f"  Hot Temp: {profile['hot_temp']}°C")
            print(f"  Basking Temp: {profile['basking_temp']}°C")
            print(f"  Humidity: {profile['humidity']}%")
            print(f"  Feed Interval: Every {profile['feed_interval_days']} day(s)")
            print(f"  Requires Basking: {profile['requires_basking']}")
            if profile.get('description'):
                print(f"  Description: {profile['description']}")

    except Exception as e:
        print(f"✗ Error seeding species profiles: {e}")
        raise

if __name__ == "__main__":
    print("Seeding species profiles database...")
    seed_species_profiles()
    print("\n✓ Database seeding complete!")

