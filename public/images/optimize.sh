#!/bin/bash

mkdir -p optimized

for file in *.png; do
  magick "$file" \
    -resize '300x300>' \
    -strip \
    -define png:compression-level=9 \
    -define png:compression-filter=5 \
    -define png:compression-strategy=1 \
    -define png:exclude-chunk=all \
    "optimized/$file"
done

echo "✅ All PNGs optimized and resized (max 300px) to 'optimized/'"
