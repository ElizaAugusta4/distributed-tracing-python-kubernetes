FROM python:3.11-slim
WORKDIR /app
COPY order/app.py .
COPY order/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5002
CMD ["python", "app.py"]
