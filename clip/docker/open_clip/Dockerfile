# Dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV PYTORCH_ENABLE_MPS_FALLBACK=1

CMD [ "python", "server.py"]