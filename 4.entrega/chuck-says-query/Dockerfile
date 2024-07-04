FROM python:3.9-slim

WORKDIR /app

RUN pip install fastapi uvicorn motor

COPY app.py .
COPY config.properties /config/config.properties

# Command to run the FastAPI application
CMD ["python", "app.py"]