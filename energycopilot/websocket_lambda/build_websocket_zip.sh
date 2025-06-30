#!/bin/bash
set -e

echo "install to temp folder..."
mkdir -p build
pip install -r requirements.txt -t build/

echo "copy..."
cp websocket_handler.py build/

echo "zip to websocket_handler.zip..."
cd build
zip -r ../websocket_handler.zip .
cd ..
rm -rf build

echo "completed：websocket_handler.zip"

