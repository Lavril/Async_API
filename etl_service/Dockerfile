FROM python:3.12

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.txt
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY ./ ./
RUN chmod +x ./main.py

CMD ["python", "/opt/app/main.py"]
