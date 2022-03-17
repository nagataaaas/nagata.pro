#!/bin/sh
cd /
if hugo new site hugo -f yml; then
  echo "created hugo site"
  cd /hugo || exit
  mv /themes /hugo/
  echo theme: "PaperMod" >> config.yml
else
  echo "site is already exist"
  cd /hugo || exit
fi

wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >  /hugo/static/github_repos.json
echo cron starting
cron -f &
echo cron started
hugo server --bind 0.0.0.0 --port 80