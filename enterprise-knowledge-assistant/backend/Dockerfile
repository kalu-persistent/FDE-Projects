FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy Zscaler certificate
COPY zscaler.crt /usr/local/share/ca-certificates/zscaler.crt

# Update Linux CA bundle
RUN update-ca-certificates

# Python SSL configuration
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]