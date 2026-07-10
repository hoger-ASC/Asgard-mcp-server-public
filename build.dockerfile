FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt
  RUN pip install --no-cache-dir -r requirements.txt

  COPY server.py chat_server.py ./
  COPY static ./static

  EXPOSE 8765
  EXPOSE 8000
