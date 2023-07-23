from PIL import Image
from typing import Union
from io import BytesIO

s = 16

def calculate_hash(image_path: Union[str, bytes, BytesIO]) -> str:
    # Open image using PIL
    image = Image.open(image_path)
    
    # Resize image to a fixed size (e.g., 8x8 pixels)
    image = image.resize((s, s), Image.LANCZOS)
    
    # Convert image to grayscale
    image = image.convert('L')
    
    # Calculate average pixel value
    average_pixel = sum(image.getdata()) / (s ** 2)
    
    # Generate binary hash
    hash_value = ''.join(['1' if pixel >= average_pixel else '0' for pixel in image.getdata()])
    
    return hash_value

def hamming_distance(hash1: str, hash2: str) -> float:
    # Calculate the Hamming distance between two hashes
    return sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
