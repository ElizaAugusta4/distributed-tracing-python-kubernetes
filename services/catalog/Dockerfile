FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app
COPY catalog/app.py .
COPY catalog/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt \
	&& chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
CMD ["python", "app.py"]
