FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

ADD . /ICT3102-Grp4
WORKDIR /ICT3102-Grp4

EXPOSE 5000

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

COPY . /ICT3102-Grp4

#CMD [ "python3", "app.py" ]

CMD pkill gunicorn && gunicorn -w 4 -b 0.0.0.0:5000 app:app --daemon


