#!/bin/bash
# Convert Iphone photo to normal format (*.HEIC to *.jpg)
# move original files in "original_heic" folder

mkdir -p original_heic

for file in *.HEIC
  do
  heif-convert $file $file.jpg
  if [ $? -eq 0 ]; then
    mv $file original_heic/
  fi
done

echo "If you see *.HEIC in dir, use https://freetoolonline.com/heic-to-jpg.html"
