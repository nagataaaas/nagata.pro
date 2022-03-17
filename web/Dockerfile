# install ubuntu 18.04
FROM ubuntu:18.04

# install hugo
RUN apt-get update
RUN apt-get install -y wget --no-install-recommends
RUN apt-get install cron

ENV HUGO_VERSION='0.94.2'
ENV HUGO_FILE="hugo_extended_${HUGO_VERSION}_Linux-64bit.deb"
ENV HUGO_URL = "https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/${HUGO_FILE}"

RUN wget $HUGO_URL --no-check-certificate || true
RUN dpkg -i $HUGO_FILE

ADD ./run.sh /run.sh
ADD ./themes /themes

# setting cron
# wget https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100 each minutes

RUN echo '* * * * * wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /hugo/static/github_repos.json' > /etc/cron.d/crontab
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/crontab

RUN /usr/bin/crontab /etc/cron.d/crontab