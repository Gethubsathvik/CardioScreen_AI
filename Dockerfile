FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m cardioscreen train
EXPOSE 8000
CMD ["python", "-m", "cardioscreen", "serve", "--host", "0.0.0.0"]
