# install utils
sudo apt-get update
sudo apt-get install -y git vim curl wget unzip zip gnupg lsb-release ca-certificates

# install docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.26.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# clone repo
sudo git clone https://github.com/nagataaaas/nagata.pro.git app
cd app || exit

# docker
sudo docker-compose up --build -d

# update letsencrypt
# docker run --rm -p 443:443 -p 80:80 --name letsencrypt -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" certbot/certbot certonly -n -m "nagata@mail.nagata.pro" -d mail.nagata.pro
# docker run --rm -p 443:443 -p 80:80 --name letsencrypt -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" certbot/certbot certonly -n -m "nagata@mail.nagata.pro" -d nagata.pro                    --standalone --agree-tos