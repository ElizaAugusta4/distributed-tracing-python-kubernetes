FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app
COPY order/app.py .
COPY order/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt \
	&& chown -R appuser:appuser /app
USER appuser
EXPOSE 5002
CMD ["python", "app.py"]
