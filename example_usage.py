#!/usr/bin/env python3
"""
Example usage of the merge_images module
"""

from merge_images import merge_images

# Example 1: Basic usage
print("Example 1: Basic merge")
merge_images(
    model_image_path="model.jpg",
    product_image_path="product.png",
    output_path="result.jpg"
)

# Example 2: With custom height
print("\nExample 2: Custom height")
merge_images(
    model_image_path="model.jpg",
    product_image_path="product.png",
    output_path="result_1200.jpg",
    target_height=1200
)

# Example 3: With custom background color (if needed)
print("\nExample 3: Custom background")
merge_images(
    model_image_path="model.jpg",
    product_image_path="product.png",
    output_path="result_custom_bg.jpg",
    background_color=(240, 240, 240)  # Light gray
)

