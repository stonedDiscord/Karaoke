#!/bin/bash

# Check if the required arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <csv_file> <image_folder>"
    exit 1
fi

csv_file="$1"
image_folder="$2"

# Check if the CSV file exists
if [ ! -f "$csv_file" ]; then
    echo "Error: CSV file '$csv_file' not found."
    exit 1
fi

# Check if the image folder exists
if [ ! -d "$image_folder" ]; then
    echo "Error: Image folder '$image_folder' not found."
    exit 1
fi

# Loop through each line in the CSV file
while IFS=, read -r file_number character; do
    # Check if the file exists in the image folder
    if [ -f "${image_folder}/image_${file_number}.png" ]; then
        # Draw the character on the image using ImageMagick
        convert "${image_folder}/image_${file_number}.png" -gravity south -fill white -stroke gray35 -strokewidth 2 -font Noto-Sans-Black -pointsize 26 -annotate +0-7 ${character} "${image_folder}/image_${file_number}.png"
        #convert "${image_folder}/image_${file_number}.png" -gravity south -fill white -stroke gray35 -strokewidth 2 -font Noto-Sans-Black -pointsize 14 -annotate +0-4 ${character} "${image_folder}/image_${file_number}.png"
        echo "Character '${character}' drawn on image_${file_number}.png"
    else
        echo "Warning: Image '${file_number}.jpg' not found in folder '${image_folder}'. Skipping."
    fi
done < "$csv_file"

echo "All images processed."
