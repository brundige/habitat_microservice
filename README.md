# 🦎 Tank Simulator - Reptile Habitat Management System

A FastAPI-based microservice for monitoring and managing reptile tank environments with real-time sensor data collection and species-specific habitat optimization profiles.

## 📋 Features

- **Real-time Sensor Monitoring**: Continuously collect temperature, humidity, and light sensor data
- **Species Profiles**: Pre-configured optimal habitat parameters for Leopard Geckos, Bearded Dragons, and Crested Geckos
- **MongoDB Integration**: Persistent data storage for sensor readings and species profiles
- **RESTful API**: Complete CRUD operations for managing sensor data and species profiles
- **Docker Deployment**: Fully containerized with Docker Compose for easy deployment
- **Smart Powerstrip Control**: Kasa smart plug integration for habitat automation (optional)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- MongoDB (runs in Docker)

### Setup & Run

1. **Clone and navigate to the project:**
```bash
cd /Users/chris/PycharmProjects/tank_simulator
```

2. **Start services with Docker Compose:**
```bash
docker-compose up -d
```

3. **Seed the database with species profiles:**
```bash
python seed_reptiles.py
```

4. **Access the API:**
- API Base URL: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- MongoDB: `localhost:27017`

## 📚 API Documentation

### Species Profiles

**Create a species profile:**
```bash
POST /api/species-profiles
Content-Type: application/json

{
  "species_name": "Bearded Dragon",
  "cool_temp": 26.0,
  "hot_temp": 38.0,
  "basking_temp": 40.0,
  "humidity": 30.0,
  "daylight_hours": 12,
  "basking_duration_minutes": 120,
  "requires_basking": true,
  "feed_interval_days": 1,
  "description": "A popular medium-sized reptile..."
}
```

**Get all species profiles:**
```bash
GET /api/species-profiles
```

**Get profile by name:**
```bash
GET /api/species-profiles/name/Leopard%20Gecko
```

**Get profile by ID:**
```bash
GET /api/species-profiles/{profile_id}
```

**Update a profile:**
```bash
PUT /api/species-profiles/{profile_id}
Content-Type: application/json

{
  "cool_temp": 25.0,
  "hot_temp": 31.0
}
```

**Delete a profile:**
```bash
DELETE /api/species-profiles/{profile_id}
```

### Sensor Readings

**Get readings for a tank:**
```bash
GET /api/readings/{tank_id}
```

**Post a sensor reading:**
```bash
POST /api/readings
Content-Type: application/json

{
  "id": 1,
  "temp": 28.5,
  "humidity": 45.0,
  "light": true
}
```

## 🗄️ Database Collections

### `sensor_readings`
Stores real-time temperature, humidity, and light readings from each tank.

```json
{
  "_id": ObjectId,
  "tank_id": 1,
  "temp": 28.5,
  "humidity": 45.2,
  "light": true,
  "timestamp": "2026-01-07T12:34:56Z"
}
```

### `species_profiles`
Stores species-specific optimal habitat parameters.

```json
{
  "_id": ObjectId,
  "species_name": "Leopard Gecko",
  "cool_temp": 26.0,
  "hot_temp": 32.0,
  "basking_temp": 35.0,
  "humidity": 40.0,
  "daylight_hours": 12,
  "basking_duration_minutes": 60,
  "requires_basking": true,
  "feed_interval_days": 2,
  "description": "...",
  "created_at": "2026-01-07T12:00:00Z"
}
```

## 🔌 Configuration

Environment variables (set in `.env` or `docker-compose.yml`):

```env
# MongoDB
MONGO_URI=mongodb://mongo:mongo@localhost:27017/?authSource=admin
MONGO_DB=tanks_db
MONGO_COLLECTION=sensor_readings

# Server
SERVER_API_URL=http://localhost:8000/api/readings
ENVIRONMENT=development

# Smart Plug (optional)
KASA_DEVICE_IP=192.168.0.109
KASA_USERNAME=your_kasa_username
KASA_PASSWORD=your_kasa_password
```

## 📊 Project Structure

```
tank_simulator/
├── server/
│   ├── app.py                 # FastAPI application
│   ├── sensor_interface.py    # Sensor polling loop
│   ├── powerstrip_interface.py # Kasa smart plug integration
│   ├── static/                # JavaScript frontend
│   └── templates/             # HTML templates
├── models/
│   ├── reptile.py            # Reptile and ReptileProfile classes
│   └── tank.py               # Tank simulation model
├── controller/
│   └── tank_controller.py     # Tank control logic
├── DB_generator.py            # Database seeding script
├── seed_reptiles.py          # Species profiles seeding script
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-container orchestration
└── README.md                  # This file
```

## 🛠️ Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Locally (without Docker)
```bash
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
```

### View MongoDB Data
Use MongoDB Compass to connect:
```
Connection String: mongodb://mongo:mongo@localhost:27017/?authSource=admin
```

## 📦 Pre-seeded Species Profiles

| Species | Cool Temp | Hot Temp | Basking | Humidity | Feed Interval |
|---------|-----------|----------|---------|----------|---------------|
| Leopard Gecko | 26°C | 32°C | 35°C | 40% | Every 2 days |
| Bearded Dragon | 26°C | 38°C | 40°C | 30% | Daily |
| Crested Gecko | 20°C | 25°C | 26°C | 80% | Every 2 days |

## 🐳 Docker Commands

**Start services:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f app    # App logs
docker-compose logs -f mongo  # MongoDB logs
```

**Stop services:**
```bash
docker-compose down
```

**Rebuild containers:**
```bash
docker-compose up -d --build
```

## 🔧 Troubleshooting

### MongoDB Connection Error
Make sure MongoDB container is running:
```bash
docker-compose ps
```

### Sensor Data Not Appearing
Check if sensor polling is running:
```bash
docker-compose logs app | grep "Sensor polling"
```

### Port Already in Use
Change the port in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Last Updated:** January 2026  
**Python Version:** 3.11+  
**Framework:** FastAPI 0.128.0  
**Database:** MongoDB 7.0

