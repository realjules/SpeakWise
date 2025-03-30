# Use a smaller base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies efficiently
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Use exec form to ensure proper signal handling
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
