@echo off
REM Script to install the required dependencies for SpeakWise

echo Installing SpeakWise dependencies...

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install the browser-use package which is required by browser_agent
echo Installing browser-use package...
pip install browser-use

REM Install other project requirements
echo Installing project requirements...
pip install -r requirements.txt

REM Install additional packages needed for browser automation
echo Installing additional dependencies...
pip install langchain-openai

echo Dependencies installed successfully!
echo You can now run the call-agent with: chainlit run call-agent/app.py