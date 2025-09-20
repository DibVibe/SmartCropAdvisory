# 📱 SmartCropAdvisory API - Postman Endpoints Guide

## 🔑 Authentication
All requests require this header:
```
Authorization: Bearer 45fd4973d7ca3abf595d90f7c6940dc534c9b967b3b0dd32d0f14adf4420bc73
```

## 🌾 Available Endpoints

### 1️⃣ Crop Management
```http
GET http://localhost:8000/api/v1/crop/crops/
```
- **Purpose:** List all available crops
- **Method:** GET
- **Headers:** Authorization Bearer token
- **Response:** List of crops with details

```http
GET http://localhost:8000/api/v1/crop/crops/{crop_id}/
```
- **Purpose:** Get details of a specific crop
- **Method:** GET
- **Example:** `GET /api/v1/crop/crops/1/`

### 2️⃣ Yield Prediction (What you tried before)
```http
POST http://localhost:8000/api/v1/crop/predict-yield/
```
- **Purpose:** Predict crop yield for given conditions
- **Method:** POST
- **Headers:** 
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`
- **Body Example:**
```json
{
  "field_id": "test_field_123",
  "crop_id": "wheat",
  "environmental_data": {
    "temperature": 25,
    "rainfall": 800,
    "humidity": 70,
    "soil_ph": 6.5
  }
}
```

### 3️⃣ Crop Recommendations
```http
POST http://localhost:8000/api/v1/crop/recommend-crops/
```
- **Purpose:** Get crop recommendations based on soil conditions
- **Method:** POST
- **Body Example:**
```json
{
  "soil_ph": 6.5,
  "soil_nitrogen": 60,
  "soil_phosphorus": 40,
  "soil_potassium": 80,
  "rainfall_mm": 800,
  "temperature_avg": 25,
  "humidity": 65
}
```

### 4️⃣ Disease Detection
```http
POST http://localhost:8000/api/v1/crop/detect-disease/
```
- **Purpose:** Detect diseases from crop images
- **Method:** POST
- **Body:** Multipart form with image file

### 5️⃣ Field Analysis
```http
POST http://localhost:8000/api/v1/crop/fields/{field_id}/analyze/
```
- **Purpose:** Analyze a specific field
- **Method:** POST
- **Example:** `POST /api/v1/crop/fields/1/analyze/`

### 6️⃣ Farming Tips
```http
GET http://localhost:8000/api/v1/crop/farming-tips/
```
- **Purpose:** Get farming tips and advice
- **Method:** GET

```http
GET http://localhost:8000/api/v1/crop/farming-tips/daily/
```
- **Purpose:** Get daily farming tip
- **Method:** GET

## ❌ What Doesn't Exist
- ~~`/crop/analysis/`~~ ← This endpoint doesn't exist
- ~~`/crop/analyze/`~~ ← This doesn't exist either

## 🎯 Quick Fix for Your Current Request

Instead of:
```
GET /crop/analysis/?test_crop_id&include_images=true
```

Try one of these:

**Option 1: List crops**
```http
GET http://localhost:8000/api/v1/crop/crops/
Authorization: Bearer 45fd4973d7ca3abf595d90f7c6940dc534c9b967b3b0dd32d0f14adf4420bc73
```

**Option 2: Get crop recommendations**
```http
POST http://localhost:8000/api/v1/crop/recommend-crops/
Authorization: Bearer 45fd4973d7ca3abf595d90f7c6940dc534c9b967b3b0dd32d0f14adf4420bc73
Content-Type: application/json

{
  "soil_ph": 6.5,
  "soil_nitrogen": 60,
  "soil_phosphorus": 40,
  "soil_potassium": 80
}
```

**Option 3: Predict yield**
```http
POST http://localhost:8000/api/v1/crop/predict-yield/
Authorization: Bearer 45fd4973d7ca3abf595d90f7c6940dc534c9b967b3b0dd32d0f14adf4420bc73
Content-Type: application/json

{
  "field_id": "test_field",
  "crop_id": "wheat",
  "environmental_data": {
    "temperature": 25,
    "rainfall": 800
  }
}
```

## 🔧 Testing Tips

1. **Start Simple:** Try `GET /api/v1/crop/crops/` first
2. **Check Headers:** Make sure Authorization header is set
3. **Use POST for Complex Operations:** Most analysis endpoints expect POST with JSON data
4. **Check Response:** Look for helpful error messages in the response body

## 🌐 Base URL Structure
```
http://localhost:8000/api/v1/crop/{endpoint}/
```

All crop-related endpoints start with `/api/v1/crop/`
