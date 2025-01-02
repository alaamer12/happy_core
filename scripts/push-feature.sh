#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Function to check if we're on the holder branch
check_holder_branch() {
    current_branch=$(git branch --show-current)
    if [[ "$current_branch" != "holder" ]]; then
        print_error "You must be on the holder branch to create a new feature"
        print_warning "Current branch: $current_branch"
        print_warning "Please switch to holder branch first: git checkout holder"
        exit 1
    fi
}

# Function to validate feature name
validate_feature_name() {
    if [[ ! "$1" =~ ^[a-z0-9_]+$ ]]; then
        print_error "Feature name must contain only lowercase letters, numbers, and underscores"
        exit 1
    fi
}

# Function to check if the feature branch already exists
check_feature_branch() {
    if git show-ref --verify --quiet "refs/heads/features/$1"; then
        print_error "Feature branch features/$1 already exists"
        exit 1
    fi
}

# Check if git is initialized
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    print_error "Not a git repository"
    exit 1
fi

# Check if feature name is provided
if [ $# -eq 0 ]; then
    print_error "Please provide a feature name"
    echo "Usage: $0 <feature_name>"
    echo "Example: $0 create_auth"
    exit 1
fi

feature_name=$1

# Validate feature name
validate_feature_name "$feature_name"

# Make sure we're on holder branch
check_holder_branch

# Check if feature branch already exists
check_feature_branch "$feature_name"

# Make sure holder is up to date
print_warning "Updating holder branch..."
git pull origin holder

# Create and switch to new feature branch
feature_branch="features/$feature_name"
git checkout -b "$feature_branch"
if [ $? -eq 0 ]; then
    print_success "Created and switched to new feature branch: $feature_branch"
    print_warning "You can now start working on your feature"
    print_warning "When ready, commit your changes and run: git push -u origin $feature_branch"
    print_warning "Then create a pull request from $feature_branch to holder"
else
    print_error "Failed to create feature branch"
    exit 1
fi

# Instructions for next steps
echo
echo "Next steps:"
echo "1. Make your changes"
echo "2. git add <files>"
echo "3. git commit -m 'feat: your commit message'"
echo "4. git push -u origin $feature_branch"
echo "5. Create pull request to holder branch"
echo "6. After merge, run: git branch -D $feature_branch"