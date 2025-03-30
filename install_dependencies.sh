#!/bin/bash
# Script to install the required dependencies for SpeakWise

echo "Installing SpeakWise dependencies..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install the browser-use package which is required by browser_agent
echo "Installing browser-use package..."
pip install browser-use

# Install other project requirements
echo "Installing project requirements..."
pip install -r requirements.txt

# Install additional packages needed for browser automation
echo "Installing additional dependencies..."
pip install langchain-openai

echo "Dependencies installed successfully!"
echo "You can now run the call-agent with: chainlit run call-agent/app.py"