# 1. Stabilní Python 3.12 na odlehčeném Linuxu
FROM python:3.12-slim

WORKDIR /app

# 2. Seznam knihoven
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

# 3. Port 5000 pro Flask
EXPOSE 5000

# 4. Aplikace přes Gunicorn na portu 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]