FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ssh \
    vim \
    tesseract-ocr

# Set the working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

RUN mkdir /run/sshd && \
    useradd -m workshop && \
    echo "workshop:password" | chpasswd && \
    echo "set encoding=utf-8" > "/home/workshop/.vimrc" && \
    chown -R workshop:workshop /app

# Create start script
RUN echo '#!/bin/bash' > /start.sh && \
    echo '/usr/sbin/sshd -D &' >> /start.sh && \
    echo 'su workshop' >> /start.sh && \
    echo 'flask run' >> /start.sh && \
    chmod +x /start.sh
    
# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5002

ENV OLLAMA_BASE_URL=http://ollama:11434
ENV EE_HOSTNAME=couchbase
ENV CB_USERNAME=admin
ENV CB_PASSWORD=workshop
    
EXPOSE 22

# Use the start script as the entry point
CMD ["/start.sh"]