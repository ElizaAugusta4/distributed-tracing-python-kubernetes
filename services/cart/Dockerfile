FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1
RUN adduser --disabled-password --gecos "" appuser
WORKDIR /app
COPY cart/app.py .
COPY cart/requirements.txt .
COPY common ./common
RUN pip install --no-cache-dir -r requirements.txt \
	&& chown -R appuser:appuser /app
USER appuser
EXPOSE 5001
CMD ["python", "app.py"]
