# Docker image for the app 
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN pip install -r app/requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501"]