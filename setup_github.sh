#!/bin/bash
# Quick setup script for fusion-benchmark GitHub repository
# This script helps you quickly initialize and push to GitHub

set -e  # Exit on error

echo "========================================"
echo "Fusion Benchmark GitHub Setup Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current directory
REPO_DIR=$(pwd)
echo -e "${GREEN}Repository directory: $REPO_DIR${NC}"
echo ""

# Step 1: Check if git is initialized
echo "Step 1: Checking Git initialization..."
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Initializing Git repository...${NC}"
    git init
    echo -e "${GREEN}✓ Git repository initialized${NC}"
else
    echo -e "${GREEN}✓ Git repository already initialized${NC}"
fi
echo ""

# Step 2: Get GitHub username
echo "Step 2: GitHub Configuration"
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your email: " USER_EMAIL
read -p "Enter repository name [fusion-benchmark]: " REPO_NAME
REPO_NAME=${REPO_NAME:-fusion-benchmark}
echo ""

# Step 3: Update placeholders in files
echo "Step 3: Updating placeholders..."
echo -e "${YELLOW}Replacing YOUR_USERNAME with $GITHUB_USER...${NC}"
find . -name "*.md" -type f -exec sed -i "s/YOUR_USERNAME/$GITHUB_USER/g" {} +

echo -e "${YELLOW}Replacing YOUR_EMAIL with $USER_EMAIL...${NC}"
find . -name "*.md" -type f -exec sed -i "s/YOUR_EMAIL/$USER_EMAIL/g" {} +

echo -e "${GREEN}✓ Placeholders updated${NC}"
echo ""

# Step 4: Add all files
echo "Step 4: Adding files to Git..."
git add .
echo -e "${GREEN}✓ Files added${NC}"
echo ""

# Step 5: Create initial commit
echo "Step 5: Creating initial commit..."
git commit -m "Initial commit: Fusion detection benchmark with Docker containers and analysis scripts

- 9 Docker containers for fusion detection tools
- 12 Python analysis scripts
- Complete documentation (README, WIKI, guides)
- 40 simulated datasets described
- 17 real datasets described
- FusionSimulatorToolkit-style documentation"

echo -e "${GREEN}✓ Initial commit created${NC}"
echo ""

# Step 6: Set up remote
echo "Step 6: Setting up GitHub remote..."
REMOTE_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo -e "${YELLOW}Remote URL: $REMOTE_URL${NC}"

if git remote | grep -q "origin"; then
    echo -e "${YELLOW}Updating existing remote...${NC}"
    git remote set-url origin $REMOTE_URL
else
    echo -e "${YELLOW}Adding new remote...${NC}"
    git remote add origin $REMOTE_URL
fi
echo -e "${GREEN}✓ Remote configured${NC}"
echo ""

# Step 7: Instructions for creating GitHub repository
echo "========================================"
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "========================================"
echo ""
echo "1. Create GitHub repository:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: Comprehensive benchmark of fusion detection tools for long-read RNA-seq"
echo "   - Choose Public or Private"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo "   - Click 'Create repository'"
echo ""
echo "2. Push to GitHub:"
echo "   Run these commands:"
echo "   ${GREEN}git branch -M main${NC}"
echo "   ${GREEN}git push -u origin main${NC}"
echo ""
echo "3. Upload datasets to cloud storage:"
echo "   See UPLOAD_GUIDE.md for detailed instructions"
echo ""
echo "4. Update data download links:"
echo "   - data_links/SIMULATED_DATA.md"
echo "   - data_links/REAL_DATA.md"
echo "   - README.md"
echo ""
echo "5. Create a release:"
echo "   - Go to: https://github.com/$GITHUB_USER/$REPO_NAME/releases/new"
echo "   - Tag: v1.0.0"
echo "   - Title: Fusion Detection Benchmark v1.0.0"
echo "   - See UPLOAD_GUIDE.md for release notes template"
echo ""
echo "========================================"
echo -e "${GREEN}Setup complete!${NC}"
echo "========================================"
echo ""
echo "Repository is ready to push to GitHub."
echo "Run: git push -u origin main"
echo ""
