#!/bin/bash
# Copy portfolio-template directory to src before building
cp -r ../portfolio-template ./src/
# Run SAM build
sam build
# Clean up the copied template (optional)
rm -rf ./src/portfolio-template