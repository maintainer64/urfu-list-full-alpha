FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /opt/app
COPY requirements.txt /opt/app/requirements.txt
RUN pip3 install \
   --upgrade pip -r requirements.txt
COPY . .
RUN find . -name __pycache__ -type d -exec rm -rv {} +
ENV TZ=UTC
