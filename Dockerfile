FROM python:3.11-slim

# Don't buffer logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system packages needed for numpy/pandas/scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt --prefer-binary

# Copy project files
COPY . .

# Start the app (Render provides $PORT)
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000}"]
