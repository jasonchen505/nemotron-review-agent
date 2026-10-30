FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY review_agent ./review_agent
COPY app.py .env.example ./
EXPOSE 7860
CMD ["python", "app.py"]
