FROM python:3.11-slim

WORKDIR /app

# dependencies আগে copy করো (Docker cache layer)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# backend app code copy
COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
