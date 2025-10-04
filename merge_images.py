#!/usr/bin/env python3
"""
Image Merger Script
Combines a model image and a product image side by side
"""

from PIL import Image
import sys
import os


def merge_images(model_image_path, product_image_path, output_path="merged_output.jpg", 
                 split_ratio=0.6, target_height=None, background_color=(255, 255, 255)):
    """
    Merge model and product images side by side.
    
    Args:
        model_image_path: Path to the model/person image
        product_image_path: Path to the product image
        output_path: Path where the merged image will be saved
        split_ratio: Ratio of width for model image (0-1). Default 0.6 means 60% for model, 40% for product
        target_height: Target height for the output image. If None, uses the max height of input images
        background_color: RGB tuple for background color (default white)
    """
    
    # Load images
    try:
        model_img = Image.open(model_image_path)
        product_img = Image.open(product_image_path)
    except Exception as e:
        print(f"Error loading images: {e}")
        return False
    
    # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
    if model_img.mode != 'RGB':
        model_img = model_img.convert('RGB')
    if product_img.mode != 'RGB':
        product_img = product_img.convert('RGB')
    
    # Determine target height
    if target_height is None:
        target_height = max(model_img.height, product_img.height)
    
    # Calculate aspect ratios and resize images to match target height
    model_aspect = model_img.width / model_img.height
    product_aspect = product_img.width / product_img.height
    
    model_new_width = int(target_height * model_aspect)
    product_new_width = int(target_height * product_aspect)
    
    model_img_resized = model_img.resize((model_new_width, target_height), Image.Resampling.LANCZOS)
    product_img_resized = product_img.resize((product_new_width, target_height), Image.Resampling.LANCZOS)
    
    # Calculate final canvas width
    total_width = model_new_width + product_new_width
    
    # Create new image with background
    merged_img = Image.new('RGB', (total_width, target_height), background_color)
    
    # Paste images side by side
    merged_img.paste(model_img_resized, (0, 0))
    merged_img.paste(product_img_resized, (model_new_width, 0))
    
    # Save the result with maximum quality
    try:
        # Determine save parameters based on file extension
        file_ext = output_path.lower().split('.')[-1]
        
        if file_ext in ['jpg', 'jpeg']:
            # Maximum JPEG quality with optimization
            merged_img.save(output_path, quality=100, optimize=True, subsampling=0)
        elif file_ext == 'png':
            # PNG is lossless by default, use maximum compression
            merged_img.save(output_path, optimize=True, compress_level=9)
        else:
            # Default high quality save
            merged_img.save(output_path, quality=100)
            
        print(f"✓ Merged image saved successfully to: {output_path}")
        print(f"  Output size: {total_width}x{target_height}")
        print(f"  Format: {file_ext.upper()} (Maximum Quality)")
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def main():
    """Main function to handle command line usage"""
    
    if len(sys.argv) < 3:
        print("Usage: python merge_images.py <model_image> <product_image> [output_path] [target_height]")
        print("\nExample:")
        print("  python merge_images.py model.jpg product.png output.jpg 1200")
        print("\nArguments:")
        print("  model_image    - Path to the model/person image")
        print("  product_image  - Path to the product image")
        print("  output_path    - (Optional) Output file path (default: merged_output.jpg)")
        print("  target_height  - (Optional) Target height in pixels (default: max of input heights)")
        sys.exit(1)
    
    model_path = sys.argv[1]
    product_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else "merged_output.jpg"
    target_height = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    # Check if input files exist
    if not os.path.exists(model_path):
        print(f"Error: Model image not found: {model_path}")
        sys.exit(1)
    
    if not os.path.exists(product_path):
        print(f"Error: Product image not found: {product_path}")
        sys.exit(1)
    
    print(f"Merging images...")
    print(f"  Model: {model_path}")
    print(f"  Product: {product_path}")
    
    success = merge_images(model_path, product_path, output_path, target_height=target_height)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()

