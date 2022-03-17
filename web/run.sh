#!/bin/sh

cd /hugo || exit

if wget -O - "https://api.github.com/users/nagataaaas/repos?type=owner&sort=updated&per_page=100" --no-check-certificate >/github_repos.tmp; then
  cp /github_repos.tmp /hugo/static/github_repos.json
  /usr/local/bin/hugo -D -d /hugo/public
fi

rm /github_repos.tmp
