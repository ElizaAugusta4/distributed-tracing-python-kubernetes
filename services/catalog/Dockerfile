FROM python:3.11-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PIP_NO_CACHE_DIR=1
RUN addgroup --system --gid 10001 appuser \
	&& adduser --system --uid 10001 --ingroup appuser --home /home/appuser --disabled-password --gecos "" appuser
WORKDIR /app
COPY catalog/app.py .
COPY catalog/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt \
	&& chown -R 10001:10001 /app
USER 10001:10001
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "60", "--graceful-timeout", "30", "--worker-tmp-dir", "/tmp", "--no-control-socket", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "app:app"]
