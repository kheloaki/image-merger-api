"""
Image Merger API
FastAPI service for merging model and product images
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil

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


def merge_images_func(model_img_path: str, product_img_path: str, 
                      output_path: str, target_height: int = 1200):
    """
    Merge two images side by side with maximum quality
    """
    try:
        # Load images
        model_img = Image.open(model_img_path)
        product_img = Image.open(product_img_path)
        
        # Convert to RGB if necessary
        if model_img.mode != 'RGB':
            model_img = model_img.convert('RGB')
        if product_img.mode != 'RGB':
            product_img = product_img.convert('RGB')
        
        # Calculate aspect ratios and resize
        model_aspect = model_img.width / model_img.height
        product_aspect = product_img.width / product_img.height
        
        model_new_width = int(target_height * model_aspect)
        product_new_width = int(target_height * product_aspect)
        
        model_img_resized = model_img.resize(
            (model_new_width, target_height), 
            Image.Resampling.LANCZOS
        )
        product_img_resized = product_img.resize(
            (product_new_width, target_height), 
            Image.Resampling.LANCZOS
        )
        
        # Create merged image
        total_width = model_new_width + product_new_width
        merged_img = Image.new('RGB', (total_width, target_height), (255, 255, 255))
        
        # Paste images side by side
        merged_img.paste(model_img_resized, (0, 0))
        merged_img.paste(product_img_resized, (model_new_width, 0))
        
        # Save with maximum quality
        file_ext = output_path.lower().split('.')[-1]
        if file_ext in ['jpg', 'jpeg']:
            merged_img.save(output_path, quality=100, optimize=True, subsampling=0)
        elif file_ext == 'png':
            merged_img.save(output_path, optimize=True, compress_level=9)
        else:
            merged_img.save(output_path, quality=100)
        
        return True, total_width, target_height
    
    except Exception as e:
        return False, 0, 0, str(e)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Image Merger API",
        "version": "1.0.0",
        "endpoints": {
            "POST /merge": "Merge two images",
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
            # Get the base URL from the request
            # For Railway, this will automatically use the deployed URL
            return JSONResponse({
                "success": True,
                "message": "Images merged successfully",
                "output": {
                    "url": f"/outputs/{output_filename}",
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
    uvicorn.run(app, host="0.0.0.0", port=port)

