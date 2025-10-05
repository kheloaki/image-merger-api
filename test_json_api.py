#!/usr/bin/env python3
"""
Test script for Image Merger API JSON endpoint
"""

import requests
import base64
import sys
import os
from pathlib import Path

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/{image_path.suffix[1:]};base64,{encoded_string}"

def test_json_api(base_url, model_image_path, product_image_path, 
                  target_height=1200, output_format="jpg"):
    """
    Test the JSON merge API endpoint
    """
    
    print(f"\n{'='*60}")
    print(f"Testing Image Merger API (JSON)")
    print(f"{'='*60}")
    print(f"Base URL: {base_url}")
    print(f"Model Image: {model_image_path}")
    print(f"Product Image: {product_image_path}")
    print(f"Target Height: {target_height}px")
    print(f"Output Format: {output_format}")
    print(f"{'='*60}\n")
    
    # Check if files exist
    if not os.path.exists(model_image_path):
        print(f"❌ Error: Model image not found: {model_image_path}")
        return False
    
    if not os.path.exists(product_image_path):
        print(f"❌ Error: Product image not found: {product_image_path}")
        return False
    
    try:
        # Test health endpoint
        print("1️⃣  Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print(f"   ✅ Health check passed: {health_response.json()}")
        else:
            print(f"   ⚠️  Health check returned: {health_response.status_code}")
        
        # Convert images to base64
        print("\n2️⃣  Converting images to base64...")
        model_base64 = image_to_base64(Path(model_image_path))
        product_base64 = image_to_base64(Path(product_image_path))
        print(f"   ✅ Model image converted ({len(model_base64)} chars)")
        print(f"   ✅ Product image converted ({len(product_base64)} chars)")
        
        # Test JSON merge endpoint
        print("\n3️⃣  Testing JSON merge endpoint...")
        
        payload = {
            "model_image": model_base64,
            "product_image": product_base64,
            "target_height": target_height,
            "output_format": output_format
        }
        
        print("   📤 Sending JSON request...")
        response = requests.post(f"{base_url}/merge-json", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Merge successful!")
            print(f"\n📊 Result:")
            print(f"   - Success: {result['success']}")
            print(f"   - Message: {result['message']}")
            print(f"   - Filename: {result['output']['filename']}")
            print(f"   - Dimensions: {result['output']['dimensions']['width']}x{result['output']['dimensions']['height']}")
            print(f"   - Format: {result['output']['format']}")
            print(f"\n🔗 Merged Image URL:")
            print(f"   {base_url}{result['output']['url']}")
            print(f"\n💡 You can access this URL in your browser or download it.")
            
            return True
        else:
            print(f"   ❌ Merge failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {base_url}")
        print(f"   Make sure the API server is running.")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main function"""
    
    # Default values
    base_url = "http://localhost:8000"
    
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python test_json_api.py <model_image> <product_image> [base_url] [height] [format]")
        print("\nExample (local):")
        print("  python test_json_api.py model.jpg product.png")
        print("\nExample (Railway):")
        print("  python test_json_api.py model.jpg product.png https://your-app.railway.app 1200 jpg")
        print("\nTrying with default images in current directory...")
        
        # Try to find images in current directory
        current_files = list(Path(".").glob("*.jpg")) + list(Path(".").glob("*.png"))
        
        if len(current_files) >= 2:
            model_image = str(current_files[0])
            product_image = str(current_files[1])
            print(f"\n📸 Found images: {model_image}, {product_image}")
        else:
            print("\n❌ No images found. Please provide image paths.")
            sys.exit(1)
    else:
        model_image = sys.argv[1]
        product_image = sys.argv[2]
        
        if len(sys.argv) > 3:
            base_url = sys.argv[3]
        
        target_height = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
        output_format = sys.argv[5] if len(sys.argv) > 5 else "jpg"
    
    # Run test
    success = test_json_api(
        base_url=base_url,
        model_image_path=model_image,
        product_image_path=product_image,
        target_height=target_height if 'target_height' in locals() else 1200,
        output_format=output_format if 'output_format' in locals() else "jpg"
    )
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Tests failed")
        print(f"{'='*60}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
