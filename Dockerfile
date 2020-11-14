FROM ubuntu:18.04
COPY . /app
RUN make /app
CMD python /app/app.py

FROM python:3
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/