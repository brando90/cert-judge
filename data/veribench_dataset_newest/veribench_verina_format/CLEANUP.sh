#!/bin/bash
# Cleanup script to remove old src/ and scripts/ directories

cd /Users/srivatsavadaruru/Documents/projects/stanford/verina/veribench/veribench_dataset/veribench_verina_format

echo "Removing old src/ and scripts/ directories..."
rm -rf src/
rm -rf scripts/

echo "Cleanup complete!"
echo ""
echo "Remaining structure:"
ls -la
