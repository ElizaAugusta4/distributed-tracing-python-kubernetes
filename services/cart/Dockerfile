FROM python:3.11-slim
WORKDIR /app
COPY cart/app.py .
COPY cart/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5001
CMD ["python", "app.py"]
