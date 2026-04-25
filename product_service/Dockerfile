FROM python:3.12-slim

WORKDIR /app

COPY product_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY product_service/ ./product_service/
COPY auth_service/ ./auth_service/

EXPOSE 8000

CMD ["uvicorn", "product_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
