FROM python:3.10-slim
WORKDIR /code
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt /code/app/requirements.txt
RUN apt-get update \
    && apt-get -y install libpq-dev swig vim gcc libssl-dev
RUN pip install --no-cache-dir --upgrade -r /code/app/requirements.txt
COPY . /code/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]