# Image Merger Script

A Python script to merge model/person images with product images side by side.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install Pillow directly:
```bash
pip install Pillow
```

## Usage

### Basic Usage
```bash
python merge_images.py model.jpg product.png
```

This will create a `merged_output.jpg` file with both images combined.

### Custom Output Path
```bash
python merge_images.py model.jpg product.png output.jpg
```

### Specify Target Height
```bash
python merge_images.py model.jpg product.png output.jpg 1200
```

This will resize the output to 1200 pixels in height while maintaining aspect ratios.

## Parameters

- `model_image` (required) - Path to the model/person image
- `product_image` (required) - Path to the product image  
- `output_path` (optional) - Output file path (default: `merged_output.jpg`)
- `target_height` (optional) - Target height in pixels (default: maximum height of input images)

## Example

```bash
python merge_images.py woman_in_suit.jpg argan_oil_bottle.png final_result.jpg 1080
```

## Features

- Automatically maintains aspect ratios of both images
- Resizes images to match heights
- Supports various image formats (JPG, PNG, etc.)
- High-quality output with anti-aliasing
- Places model image on left, product on right

## Notes

- Images are automatically converted to RGB format if needed
- The script preserves image quality using LANCZOS resampling
- Output is saved as JPEG with 95% quality

