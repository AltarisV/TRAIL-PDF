FROM python:3.11

WORKDIR /usr/src/app

# Install Poppler
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7777

CMD ["python", "./app.py"]
