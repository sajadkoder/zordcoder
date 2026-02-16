#!/bin/bash
# Zord Coder v1 - Git Push Script
# Run this script after cloning to push to your GitHub repository

echo "Pushing Zord Coder v1 to GitHub..."
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) not installed"
    echo ""
    echo "Install instructions:"
    echo "  Windows: winget install gh"
    echo "  Mac: brew install gh"
    echo "  Linux: sudo apt install gh"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "GitHub authentication required. Run: gh auth login"
    exit 1
fi

# Create repository
REPO_NAME="zordcoder"
echo "Creating repository: $REPO_NAME"

gh repo create "$REPO_NAME" --public --source=. --push

echo ""
echo "Done! Repository pushed to: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
