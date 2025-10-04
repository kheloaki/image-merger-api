# 🚀 Image Merger API

A FastAPI web service for merging model and product images side by side with maximum quality.

## 📋 Features

- ✅ RESTful API endpoint for image merging
- ✅ Maximum quality output (100% JPEG or lossless PNG)
- ✅ Configurable output height
- ✅ CORS enabled for cross-origin requests
- ✅ Health check endpoint
- ✅ Automatic file cleanup
- ✅ Railway deployment ready

## 🛠️ Local Development

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
# or
uvicorn app:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Test Locally

```bash
# Test with curl
curl -X POST "http://localhost:8000/merge" \
  -F "model_image=@model.jpg" \
  -F "product_image=@product.png" \
  -F "target_height=1200" \
  -F "output_format=jpg"
```

## 🌐 API Endpoints

### `GET /`
Root endpoint with API information

**Response:**
```json
{
  "message": "Image Merger API",
  "version": "1.0.0",
  "endpoints": {
    "POST /merge": "Merge two images",
    "GET /health": "Health check"
  }
}
```

### `POST /merge`
Merge two images side by side

**Parameters:**
- `model_image` (file, required) - Model/person image (left side)
- `product_image` (file, required) - Product image (right side)
- `target_height` (int, optional) - Target height in pixels (default: 1200, range: 100-5000)
- `output_format` (string, optional) - Output format: "jpg" or "png" (default: "jpg")

**Example Request (cURL):**
```bash
curl -X POST "https://your-app.railway.app/merge" \
  -F "model_image=@/path/to/model.jpg" \
  -F "product_image=@/path/to/product.png" \
  -F "target_height=1200" \
  -F "output_format=jpg"
```

**Example Request (Python):**
```python
import requests

url = "https://your-app.railway.app/merge"

files = {
    'model_image': open('model.jpg', 'rb'),
    'product_image': open('product.png', 'rb')
}

data = {
    'target_height': 1200,
    'output_format': 'jpg'
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Example Request (JavaScript/Fetch):**
```javascript
const formData = new FormData();
formData.append('model_image', modelImageFile);
formData.append('product_image', productImageFile);
formData.append('target_height', '1200');
formData.append('output_format', 'jpg');

fetch('https://your-app.railway.app/merge', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Success Response:**
```json
{
  "success": true,
  "message": "Images merged successfully",
  "output": {
    "url": "/outputs/merged_abc123.jpg",
    "filename": "merged_abc123.jpg",
    "dimensions": {
      "width": 3000,
      "height": 1200
    },
    "format": "JPG"
  },
  "timestamp": "2025-10-04T23:45:00.123456"
}
```

**Access the merged image:**
```
https://your-app.railway.app/outputs/merged_abc123.jpg
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-04T23:45:00.123456"
}
```

### `GET /outputs/{filename}`
Get a merged image by filename

**Example:**
```
https://your-app.railway.app/outputs/merged_abc123.jpg
```

### `DELETE /cleanup`
Clean up old files (maintenance endpoint)

**Parameters:**
- `max_age_hours` (int, optional) - Remove files older than this (default: 24)

**Example:**
```bash
curl -X DELETE "https://your-app.railway.app/cleanup?max_age_hours=24"
```

## 🚂 Deploy to Railway

### Quick Deploy

1. **Push to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/image-merger-api.git
git push -u origin main
```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect the configuration and deploy!

### Environment Variables (Optional)

No environment variables are required, but you can add:
- `PORT` - Server port (Railway sets this automatically)

### Railway Configuration

The app includes:
- ✅ `Procfile` - Deployment command
- ✅ `railway.json` - Railway-specific config
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Dependencies

## 📊 API Documentation

Once deployed, visit these URLs for interactive documentation:

- **Swagger UI:** `https://your-app.railway.app/docs`
- **ReDoc:** `https://your-app.railway.app/redoc`

## 🔧 Configuration

### Adjust Image Quality

Edit `app.py` line 71-75 to adjust quality settings:

```python
# Maximum quality JPEG
merged_img.save(output_path, quality=100, optimize=True, subsampling=0)

# Or lossless PNG
merged_img.save(output_path, optimize=True, compress_level=9)
```

### Adjust File Storage

The app stores files in:
- `uploads/` - Temporary uploaded files
- `outputs/` - Merged output images

For production with persistent storage, consider:
- AWS S3
- Cloudinary
- Railway Volumes

## 🧪 Testing

### Test Script Included

```bash
python test_api.py
```

### Manual Testing with Postman

1. Create a new POST request to `https://your-app.railway.app/merge`
2. Select "Body" → "form-data"
3. Add key `model_image` (type: File)
4. Add key `product_image` (type: File)
5. Add key `target_height` (type: Text) = `1200`
6. Add key `output_format` (type: Text) = `jpg`
7. Send request

## 📝 Response Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Image not found
- `500` - Server error

## 🛡️ Rate Limiting

For production, consider adding rate limiting:
```bash
pip install slowapi
```

## 📞 Support

For issues or questions, check:
- Interactive docs: `/docs`
- Health check: `/health`

## 📄 License

MIT License

