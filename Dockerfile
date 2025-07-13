# Docker image for the app 
FROM python:3.11-slim

WORKDIR /app
COPY . /app
RUN pip install -r app/requirements.txt

EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501"]