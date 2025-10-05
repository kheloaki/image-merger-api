"""
Image Merger API
FastAPI service for merging model and product images
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import base64
import io
import uuid
import requests
from datetime import datetime
from pathlib import Path
import shutil
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Image Merger API",
    description="Merge model and product images side by side",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and outputs
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files to serve merged images
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# Pydantic models for JSON requests
class ImageMergeRequest(BaseModel):
    model_image: str  # Image URL or base64 encoded image
    product_image: str  # Image URL or base64 encoded image
    target_height: Optional[int] = 1200
    output_format: Optional[str] = "jpg"
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_image": "https://example.com/model.jpg",
                "product_image": "https://example.com/product.png",
                "target_height": 1200,
                "output_format": "jpg"
            }
        }


def merge_images_func(model_img_path: str, product_img_path: str, 
                      output_path: str, target_height: int = 1200):
    """
    Merge two images side by side with maximum quality
    """
    try:
        # Load images
        model_img = Image.open(model_img_path)
        product_img = Image.open(product_img_path)
        
        # Handle transparent backgrounds properly
        if model_img.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', model_img.size, (255, 255, 255))
            if model_img.mode == 'RGBA':
                background.paste(model_img, mask=model_img.split()[-1])
            else:
                background.paste(model_img)
            model_img = background
        elif model_img.mode != 'RGB':
            model_img = model_img.convert('RGB')
            
        if product_img.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', product_img.size, (255, 255, 255))
            if product_img.mode == 'RGBA':
                background.paste(product_img, mask=product_img.split()[-1])
            else:
                background.paste(product_img)
            product_img = background
        elif product_img.mode != 'RGB':
            product_img = product_img.convert('RGB')
        
        # Resize model image to target height, keep product at original size
        model_aspect = model_img.width / model_img.height
        model_new_width = int(target_height * model_aspect)
        
        model_img_resized = model_img.resize(
            (model_new_width, target_height), 
            Image.Resampling.LANCZOS
        )
        
        # Keep product image at its original size
        product_img_resized = product_img
        product_width = product_img.width
        product_height = product_img.height
        
        # Use the maximum height between model and product
        final_height = max(target_height, product_height)
        
        # Create merged image with enough space for both
        total_width = model_new_width + product_width
        merged_img = Image.new('RGB', (total_width, final_height), (255, 255, 255))
        
        # Paste model image on the left (centered vertically if needed)
        model_y_offset = (final_height - target_height) // 2
        merged_img.paste(model_img_resized, (0, model_y_offset))
        
        # Paste product image on the right (centered vertically if needed)
        product_y_offset = (final_height - product_height) // 2
        merged_img.paste(product_img_resized, (model_new_width, product_y_offset))
        
        # Save with maximum quality
        file_ext = output_path.lower().split('.')[-1]
        if file_ext in ['jpg', 'jpeg']:
            merged_img.save(output_path, quality=100, optimize=True, subsampling=0)
        elif file_ext == 'png':
            merged_img.save(output_path, optimize=True, compress_level=9)
        else:
            merged_img.save(output_path, quality=100)
        
        return True, total_width, final_height
    
    except Exception as e:
        return False, 0, 0, str(e)


def load_image_from_source(image_source: str) -> Image.Image:
    """
    Load image from URL or base64 string
    Supports both URLs and base64 encoded images
    """
    try:
        # Check if it's a URL
        if image_source.startswith(('http://', 'https://')):
            # Download image from URL
            response = requests.get(image_source, timeout=30)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
        elif image_source.startswith('data:'):
            # Base64 data URL
            base64_string = image_source.split(',')[1]
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
        else:
            # Raw base64 string
            image_data = base64.b64decode(image_source)
            image = Image.open(io.BytesIO(image_data))
        
        return image
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image from URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Image Merger API",
        "version": "1.0.0",
        "endpoints": {
            "POST /merge": "Merge two images (multipart/form-data)",
            "POST /merge-json": "Merge two images (JSON with base64)",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/merge")
async def merge_images_endpoint(
    model_image: UploadFile = File(..., description="Model/Person image"),
    product_image: UploadFile = File(..., description="Product image"),
    target_height: int = Form(1200, description="Target height in pixels"),
    output_format: str = Form("jpg", description="Output format: jpg or png")
):
    """
    Merge two images side by side
    
    - **model_image**: The model/person image (left side)
    - **product_image**: The product image (right side)
    - **target_height**: Target height in pixels (default: 1200)
    - **output_format**: Output format - jpg or png (default: jpg)
    
    Returns a JSON with the URL to the merged image
    """
    
    # Validate output format
    if output_format not in ['jpg', 'jpeg', 'png']:
        raise HTTPException(status_code=400, detail="output_format must be 'jpg' or 'png'")
    
    # Validate target height
    if target_height < 100 or target_height > 5000:
        raise HTTPException(status_code=400, detail="target_height must be between 100 and 5000")
    
    # Generate unique filenames
    unique_id = str(uuid.uuid4())
    
    try:
        # Save uploaded files temporarily
        model_temp_path = UPLOAD_DIR / f"{unique_id}_model_{model_image.filename}"
        product_temp_path = UPLOAD_DIR / f"{unique_id}_product_{product_image.filename}"
        
        with open(model_temp_path, "wb") as buffer:
            shutil.copyfileobj(model_image.file, buffer)
        
        with open(product_temp_path, "wb") as buffer:
            shutil.copyfileobj(product_image.file, buffer)
        
        # Generate output filename
        output_filename = f"merged_{unique_id}.{output_format}"
        output_path = OUTPUT_DIR / output_filename
        
        # Merge images
        result = merge_images_func(
            str(model_temp_path),
            str(product_temp_path),
            str(output_path),
            target_height
        )
        
        # Clean up temporary files
        model_temp_path.unlink(missing_ok=True)
        product_temp_path.unlink(missing_ok=True)
        
        if result[0]:
            # Get the base URL - use Railway URL for production
            base_url = "https://image-merger-api-production.up.railway.app"
            
            return JSONResponse({
                "success": True,
                "message": "Images merged successfully",
                "output": {
                    "url": f"{base_url}/outputs/{output_filename}",
                    "filename": output_filename,
                    "dimensions": {
                        "width": result[1],
                        "height": result[2]
                    },
                    "format": output_format.upper()
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        else:
            raise HTTPException(status_code=500, detail=f"Failed to merge images: {result[3]}")
    
    except Exception as e:
        # Clean up on error
        if 'model_temp_path' in locals():
            Path(model_temp_path).unlink(missing_ok=True)
        if 'product_temp_path' in locals():
            Path(product_temp_path).unlink(missing_ok=True)
        
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")


@app.post("/merge-json")
async def merge_images_json(request: ImageMergeRequest):
    """
    Merge two images using JSON request with image URLs or base64 data
    
    - **model_image**: Image URL or base64 encoded model/person image (left side)
    - **product_image**: Image URL or base64 encoded product image (right side)  
    - **target_height**: Target height in pixels (default: 1200)
    - **output_format**: Output format - jpg or png (default: jpg)
    
    Returns a JSON with the URL to the merged image
    """
    
    # Validate output format
    if request.output_format not in ['jpg', 'jpeg', 'png']:
        raise HTTPException(status_code=400, detail="output_format must be 'jpg' or 'png'")
    
    # Validate target height
    if request.target_height < 100 or request.target_height > 5000:
        raise HTTPException(status_code=400, detail="target_height must be between 100 and 5000")
    
    # Generate unique filename
    unique_id = str(uuid.uuid4())
    output_filename = f"merged_{unique_id}.{request.output_format}"
    output_path = OUTPUT_DIR / output_filename
    
    try:
        # Load images from URLs or base64
        model_img = load_image_from_source(request.model_image)
        product_img = load_image_from_source(request.product_image)
        
        # Handle transparent backgrounds properly
        if model_img.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', model_img.size, (255, 255, 255))
            if model_img.mode == 'RGBA':
                background.paste(model_img, mask=model_img.split()[-1])
            else:
                background.paste(model_img)
            model_img = background
        elif model_img.mode != 'RGB':
            model_img = model_img.convert('RGB')
            
        if product_img.mode in ('RGBA', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', product_img.size, (255, 255, 255))
            if product_img.mode == 'RGBA':
                background.paste(product_img, mask=product_img.split()[-1])
            else:
                background.paste(product_img)
            product_img = background
        elif product_img.mode != 'RGB':
            product_img = product_img.convert('RGB')
        
        # Resize model image to target height, keep product at original size
        model_aspect = model_img.width / model_img.height
        model_new_width = int(request.target_height * model_aspect)
        
        model_img_resized = model_img.resize(
            (model_new_width, request.target_height), 
            Image.Resampling.LANCZOS
        )
        
        # Keep product image at its original size
        product_img_resized = product_img
        product_width = product_img.width
        product_height = product_img.height
        
        # Use the maximum height between model and product
        final_height = max(request.target_height, product_height)
        
        # Create merged image with enough space for both
        total_width = model_new_width + product_width
        merged_img = Image.new('RGB', (total_width, final_height), (255, 255, 255))
        
        # Paste model image on the left (centered vertically if needed)
        model_y_offset = (final_height - request.target_height) // 2
        merged_img.paste(model_img_resized, (0, model_y_offset))
        
        # Paste product image on the right (centered vertically if needed)
        product_y_offset = (final_height - product_height) // 2
        merged_img.paste(product_img_resized, (model_new_width, product_y_offset))
        
        # Save with maximum quality
        if request.output_format in ['jpg', 'jpeg']:
            merged_img.save(str(output_path), quality=100, optimize=True, subsampling=0)
        elif request.output_format == 'png':
            merged_img.save(str(output_path), optimize=True, compress_level=9)
        else:
            merged_img.save(str(output_path), quality=100)
        
        # Get the base URL - use Railway URL for production, localhost for development
        base_url = "https://image-merger-api-production.up.railway.app"
        
        return JSONResponse({
            "success": True,
            "message": "Images merged successfully",
            "output": {
                "url": f"{base_url}/outputs/{output_filename}",
                "filename": output_filename,
                "dimensions": {
                    "width": total_width,
                    "height": final_height
                },
                "format": request.output_format.upper()
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")


@app.get("/outputs/{filename}")
async def get_output_image(filename: str):
    """Serve merged output images"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(file_path)


@app.delete("/cleanup")
async def cleanup_old_files(max_age_hours: int = 24):
    """
    Clean up old files (for maintenance)
    Removes files older than max_age_hours
    """
    try:
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleaned_uploads = 0
        cleaned_outputs = 0
        
        # Clean uploads
        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_uploads += 1
        
        # Clean outputs
        for file_path in OUTPUT_DIR.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_outputs += 1
        
        return {
            "success": True,
            "cleaned_uploads": cleaned_uploads,
            "cleaned_outputs": cleaned_outputs
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

