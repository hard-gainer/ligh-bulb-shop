FROM python:3.12-slim

WORKDIR /app

COPY order_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY order_service/ ./order_service/
COPY auth_service/ ./auth_service/

EXPOSE 8000

CMD ["uvicorn", "order_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
