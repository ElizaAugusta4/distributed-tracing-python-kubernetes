FROM python:3.11-slim
WORKDIR /app
COPY catalog/app.py .
COPY catalog/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
