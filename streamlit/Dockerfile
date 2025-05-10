FROM python:3.10-slim

# Set environment variables
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
EXPOSE 8501

# Set working directory
WORKDIR /app


COPY ./streamlit/requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit app code
COPY streamlit/main.py .

# Run Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]