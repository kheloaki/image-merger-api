# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Prepare Your Repository

1. **Initialize Git (if not already done):**
```bash
git init
git add .
git commit -m "Initial commit: Image Merger API"
```

2. **Push to GitHub:**
```bash
# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/image-merger-api.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Select your `image-merger-api` repository
5. Railway will automatically detect the configuration and deploy!

### Step 3: Access Your API

Once deployed, Railway will provide you with a URL like:
```
https://your-app-name.railway.app
```

### Step 4: Test Your Deployed API

**Option 1: Using the test script**
```bash
python3 test_api.py model.jpg product.png https://your-app-name.railway.app
```

**Option 2: Using cURL**
```bash
curl -X POST "https://your-app-name.railway.app/merge" \
  -F "model_image=@model.jpg" \
  -F "product_image=@product.png" \
  -F "target_height=1200" \
  -F "output_format=jpg"
```

**Option 3: Open the test page**
- Open `test_page.html` in your browser
- Change the API URL to your Railway URL
- Upload images and test!

---

## 🔧 Configuration Files Included

✅ **Procfile** - Tells Railway how to start your app
✅ **railway.json** - Railway-specific configuration
✅ **runtime.txt** - Specifies Python version
✅ **requirements.txt** - All dependencies

---

## 📊 API Endpoints

### Base URL
```
https://your-app-name.railway.app
```

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/merge` | Merge two images |
| GET | `/outputs/{filename}` | Get merged image |
| GET | `/docs` | Interactive API docs (Swagger) |
| GET | `/redoc` | Alternative docs (ReDoc) |

---

## 💡 Example Usage

### Python
```python
import requests

url = "https://your-app-name.railway.app/merge"

files = {
    'model_image': open('model.jpg', 'rb'),
    'product_image': open('product.png', 'rb')
}

data = {
    'target_height': 1200,
    'output_format': 'jpg'
}

response = requests.post(url, files=files, data=data)
result = response.json()

if result['success']:
    image_url = f"https://your-app-name.railway.app{result['output']['url']}"
    print(f"Merged image: {image_url}")
```

### JavaScript/Node.js
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('model_image', fs.createReadStream('model.jpg'));
form.append('product_image', fs.createReadStream('product.png'));
form.append('target_height', '1200');
form.append('output_format', 'jpg');

axios.post('https://your-app-name.railway.app/merge', form, {
  headers: form.getHeaders()
})
.then(response => {
  const imageUrl = `https://your-app-name.railway.app${response.data.output.url}`;
  console.log('Merged image:', imageUrl);
})
.catch(error => console.error(error));
```

### cURL
```bash
curl -X POST "https://your-app-name.railway.app/merge" \
  -F "model_image=@/path/to/model.jpg" \
  -F "product_image=@/path/to/product.png" \
  -F "target_height=1200" \
  -F "output_format=jpg"
```

---

## 🛠️ Local Testing Before Deploy

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
python3 app.py
# or
uvicorn app:app --reload

# Server will run at http://localhost:8000
```

Test endpoints:
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- Test page: Open `test_page.html` in browser

---

## 🔒 Production Considerations

### 1. File Storage
- Current setup stores files locally (ephemeral on Railway)
- For production, consider:
  - **AWS S3** - Scalable cloud storage
  - **Cloudinary** - Image-specific CDN
  - **Railway Volumes** - Persistent storage

### 2. Rate Limiting
Add rate limiting to prevent abuse:
```bash
pip install slowapi
```

### 3. Authentication
Add API key authentication if needed:
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=401)
```

### 4. File Cleanup
Set up automatic cleanup:
```bash
# Call cleanup endpoint daily
curl -X DELETE "https://your-app-name.railway.app/cleanup?max_age_hours=24"
```

---

## 📈 Monitoring

Railway provides:
- ✅ Automatic HTTPS
- ✅ Environment variables
- ✅ Logs viewing
- ✅ Metrics dashboard
- ✅ Auto-deployments on git push

Access logs in Railway dashboard to monitor API usage.

---

## 🆘 Troubleshooting

### API not responding
- Check Railway logs in the dashboard
- Verify the build succeeded
- Test health endpoint: `/health`

### Images not merging
- Check file size limits (Railway default: 100MB)
- Verify image formats are supported
- Check logs for detailed errors

### Slow performance
- Consider upgrading Railway plan
- Optimize image sizes before upload
- Add caching for frequently merged images

---

## 📞 Support

- **Interactive Docs**: https://your-app-name.railway.app/docs
- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Deployment successful
- [ ] Health endpoint working
- [ ] Test merge with sample images
- [ ] Update URLs in client applications
- [ ] Set up monitoring/alerts
- [ ] Configure file cleanup schedule
- [ ] (Optional) Add custom domain
- [ ] (Optional) Set up authentication

---

**Your API is now ready to use! 🎉**

