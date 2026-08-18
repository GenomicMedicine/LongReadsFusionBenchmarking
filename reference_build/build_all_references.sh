#!/bin/bash
set -e

BASE_DIR=$(pwd)
echo "Starting Reference Build Pipeline for Long-read Fusion Benchmark..."
echo "WARNING: Building all references can take hours and consume >100GB of disk space."
sleep 3

echo "==================================="
echo "1. Building Common References"
echo "==================================="
cd "$BASE_DIR/common" && bash build_reference.sh

echo "==================================="
echo "2. Downloading CTAT-LR-Fusion Lib"
echo "==================================="
cd "$BASE_DIR/CTAT-LR-Fusion" && bash build_reference.sh

echo "==================================="
echo "3. Building pbfusion indices"
echo "==================================="
cd "$BASE_DIR/pbfusion" && bash build_reference.sh || echo "pbfusion index failed (Make sure Docker and pbmm2 are accessible)."

echo "==================================="
echo "4. Downloading JAFFAL env libs"
echo "==================================="
cd "$BASE_DIR/JAFFAL" && bash build_reference.sh || echo "JAFFAL scripts failed."

echo "==================================="
echo "5. Preparing genion inputs"
echo "==================================="
cd "$BASE_DIR/genion" && bash build_reference.sh

echo "==================================="
echo "All done! Check respective folders for index/ref outputs."
echo "==================================="
