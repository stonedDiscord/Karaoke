import os
import struct
import string
import numpy as np
from PIL import Image
import logging
from collections import defaultdict
import string

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_NoneType = type(None)

def keeper(keep):
    table = defaultdict(_NoneType)
    table.update({ord(c): c for c in keep})
    return table

digit_keeper = keeper(string.digits)

def extract_images(input_file, output_dir):
    # Check if output directory exists, if not create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'rb') as f:
        # Read the number of images from offset 0x18
        f.seek(0x18)
        num_images = struct.unpack('<H', f.read(2))[0]
        logger.info(f'Number of images: {num_images}')

        # Read the table of offsets starting from offset 0x28
        f.seek(0x28)
        offsets = struct.unpack('I' * num_images, f.read(4 * num_images))

        # Read each image using the offsets
        for i, offset in enumerate(offsets):
            if offset == 0:
                logger.warning(f'Skipping image {i} with offset 0')
                continue  # Skip if offset is 0

            logger.info(f'Processing image {i}, offset: {offset:08X}')

            f.seek(offset)  # Move to the start of the image data

            # Read the width and height of the image (each is a single byte)
            image_width, image_height = struct.unpack('BB', f.read(2))
            logger.info(f'Image dimensions: {image_width}x{image_height}')

            # Calculate the size of the image data
            image_size_bytes = (image_width * image_height) // 2  # 4-bit grayscale, 2 pixels per byte

            # Skip 3 junk bytes
            f.seek(3, os.SEEK_CUR)

            # Read the image data
            image_data = f.read(image_size_bytes)

            # Process image data to extract 4-bit grayscale values for each pixel
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            pixels = np.unpackbits(image_array).reshape(-1, 4)
            # Convert the 4-bit pixels to 8-bit (0-255 range)
            image_array = pixels.dot(2**np.arange(4)[::-1]) * 17

            # Reshape the image data to match the image size
            image_array = image_array[:image_width * image_height].reshape((image_height, image_width))

            # Convert the numpy array to a PIL image
            image = Image.fromarray(image_array.astype(np.uint8))

            # Save the image as PNG
            image_path = os.path.join(output_dir, f'image_{i}.png')
            image.save(image_path)
            logger.info(f'Saved image {i} to {image_path}')

    return output_dir

def update_file(input_file, modified_images_dir):
    # Read modified images from the directory
    modified_images = sorted(os.listdir(modified_images_dir), key=lambda x: int(x.split('_')[1].split('.')[0]))
    with open(input_file, 'r+b') as f:
        # Read the number of images from offset 0x18
        f.seek(0x18)
        num_images = struct.unpack('<H', f.read(2))[0]
        logger.info(f'Number of images: {num_images}')

        # Read the table of offsets starting from offset 0x28
        f.seek(0x28)
        offsets = struct.unpack('I' * num_images, f.read(4 * num_images))

        for image_file in modified_images:
            image_path = os.path.join(modified_images_dir, image_file)
            image_number = int(image_file.translate(digit_keeper))
            logger.info(f'Updating image #{image_number} {image_path}')

            # Open the modified image
            image = Image.open(image_path).convert('L')  # Convert to 8-bit grayscale
            image_width, image_height = image.size

            # Convert the 8-bit grayscale image to 4-bit grayscale
            img_np = np.array(image) // 16  # Integer division to scale 0-255 range to 0-15 range
    
            # Ensure the values are in 0-15 range (4-bit)
            img_np = np.clip(img_np, 0, 15).astype(np.uint8)
            
            # Pack the 4-bit values into bytes
            packed_bytes = []
            
            for y in range(image_height):
                for x in range(0, image_width, 2):
                    if x + 1 < image_width:
                        # Combine two 4-bit values into one byte
                        packed_byte = (img_np[y, x] << 4) | img_np[y, x + 1]
                    else:
                        # If the width is odd, pad with a 0 for the last byte
                        packed_byte = img_np[y, x] << 4
                    packed_bytes.append(packed_byte)
            
            # Convert to bytearray for writing to file
            packed_bytes = bytearray(packed_bytes)
    
            # Move to the start of the image data
            f.seek(offsets[image_number])

            # Read the width and height of the image (each is a single byte)
            original_width, original_height = struct.unpack('BB', f.read(2))

            # Check if this image matches the modified image
            if original_width == image_width and original_height == image_height:
                # Skip 3 junk bytes
                f.seek(3, os.SEEK_CUR)

                # Write the modified image data to the file
                f.write(packed_bytes)
                logger.info(f'Updated image #{image_number}')

input_file = '115.74'
output_dir = input_file+'_extract'

# Extract images from the input file
modified_images_dir = extract_images(input_file, output_dir)

# Update the input file with modified images
update_file(input_file, modified_images_dir)