# Use the official Python image as the base image
FROM python:3-alpine AS builder

# Set the working directory to /app
WORKDIR /app

RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2
FROM python:3-alpine AS runner

WORKDIR /app

COPY --from=builder /app/venv venv
COPY app.py app.py

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app/app.py

EXPOSE 8000

CMD ["gunicorn", "--bind" , ":8080", "--workers", "2", "app:app"]