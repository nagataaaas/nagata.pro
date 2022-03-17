FROM python:3.9.0-slim

ENV PYTHONBUFFERED 1

# install chrome
RUN apt-get update
RUN apt-get install -y wget unzip gnupg net-tools --no-install-recommends

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
wget https://dl.google.com/linux/deb/pool/main/g/google-chrome-unstable/google-chrome-unstable_93.0.4577.18-1_amd64.deb && \
apt-get install -y -f ./google-chrome-unstable_93.0.4577.18-1_amd64.deb --no-install-recommends

ADD https://chromedriver.storage.googleapis.com/93.0.4577.15/chromedriver_linux64.zip /opt/chrome/
RUN cd /opt/chrome/ && \
unzip chromedriver_linux64.zip
ENV PATH /opt/chrome/:$PATH

RUN pip install --upgrade pip
# RUN each time below
# ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /dev/null
ADD ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt
ADD ./ /api
WORKDIR /api