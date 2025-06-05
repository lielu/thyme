#!/bin/bash

# Create backgrounds directory if it doesn't exist
mkdir -p backgrounds

# Change to backgrounds directory
cd backgrounds

# Download today's Bing wallpaper
BACKGROUND_META=$(curl 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US')
FILENAME=$(echo $BACKGROUND_META | jq -r '.images[0].urlbase' | sed s/.*=//).jpg
curl -o "$FILENAME" "https://bing.com$(echo $BACKGROUND_META | jq -r '.images[0].url')"

# Keep only the 7 most recent images
ls -t *.jpg | tail -n +8 | xargs rm -f 2>/dev/null 