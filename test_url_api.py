#!/usr/bin/env python3
"""
Test script for Image Merger API with URL-based requests
"""

import requests
import sys
import os
from pathlib import Path

def test_url_api(base_url, model_image_url, product_image_url, 
                 target_height=1200, output_format="jpg"):
    """
    Test the JSON merge API endpoint with image URLs
    """
    
    print(f"\n{'='*60}")
    print(f"Testing Image Merger API (URL-based)")
    print(f"{'='*60}")
    print(f"Base URL: {base_url}")
    print(f"Model Image URL: {model_image_url}")
    print(f"Product Image URL: {product_image_url}")
    print(f"Target Height: {target_height}px")
    print(f"Output Format: {output_format}")
    print(f"{'='*60}\n")
    
    try:
        # Test health endpoint
        print("1️⃣  Testing health endpoint...")
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print(f"   ✅ Health check passed: {health_response.json()}")
        else:
            print(f"   ⚠️  Health check returned: {health_response.status_code}")
        
        # Test JSON merge endpoint with URLs
        print("\n2️⃣  Testing JSON merge endpoint with URLs...")
        
        payload = {
            "model_image": model_image_url,
            "product_image": product_image_url,
            "target_height": target_height,
            "output_format": output_format
        }
        
        print("   📤 Sending JSON request with image URLs...")
        print(f"   📸 Model URL: {model_image_url}")
        print(f"   📸 Product URL: {product_image_url}")
        
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
            print(f"   {result['output']['url']}")
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
        print("Usage: python test_url_api.py <model_image_url> <product_image_url> [base_url] [height] [format]")
        print("\nExample (local):")
        print("  python test_url_api.py https://example.com/model.jpg https://example.com/product.png")
        print("\nExample (Railway):")
        print("  python test_url_api.py https://example.com/model.jpg https://example.com/product.png https://your-app.railway.app 1200 jpg")
        print("\nExample with sample URLs:")
        print("  python test_url_api.py https://picsum.photos/800/1200 https://picsum.photos/400/1200")
        sys.exit(1)
    else:
        model_image_url = sys.argv[1]
        product_image_url = sys.argv[2]
        
        if len(sys.argv) > 3:
            base_url = sys.argv[3]
        
        target_height = int(sys.argv[4]) if len(sys.argv) > 4 else 1200
        output_format = sys.argv[5] if len(sys.argv) > 5 else "jpg"
    
    # Run test
    success = test_url_api(
        base_url=base_url,
        model_image_url=model_image_url,
        product_image_url=product_image_url,
        target_height=target_height,
        output_format=output_format
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
