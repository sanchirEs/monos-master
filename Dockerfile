FROM python:3.6

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
ADD . .
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app/


