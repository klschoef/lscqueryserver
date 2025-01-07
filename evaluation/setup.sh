#!/bin/bash

# Load environment variables
if [ -f ./.env ]; then
    export $(cat ./.env | grep -v '^#' | awk '/=/ {print $1}')
else
    echo "Error: .env file not found."
    exit 1
fi

# Define absolute paths
PROJECT_DIR="$(pwd)"
VENV_PATH="$PROJECT_DIR/$VENV_NAME"
SHARED_LIB_PATH="$(cd "$PROJECT_DIR/$SHARED_LIB_PATH" && pwd)"

# Create the virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_PATH"

echo "Installing required packages..."
# Activate the virtual environment
source "$VENV_PATH/bin/activate"
pip3 install -r docker/python/requirements.txt

echo "Creating symbolic link for shared library ..."
# Determine the Python version in the venv to find the correct path for site-packages
PYTHON_VERSION=$(python -c "import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES_PATH="$VENV_PATH/lib/$PYTHON_VERSION/site-packages"

# Create a symbolic link
ln -sf "$SHARED_LIB_PATH" "$SITE_PACKAGES_PATH/lsc_shared"
deactivate

echo "Virtual environment and symbolic link have been successfully created."
echo "To activate the virtual environment, run 'source $VENV_NAME/bin/activate'."
