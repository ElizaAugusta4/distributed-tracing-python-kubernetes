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
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "1", "--threads", "4", "--timeout", "60", "--graceful-timeout", "30", "--worker-tmp-dir", "/tmp", "--no-control-socket", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:app"]
