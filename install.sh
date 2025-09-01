#! /bin/bash



environment=$1

set -e

echo "error" >>traceback.txt

sudo apt install -y python3-pip docker.io docker-compose

cd auth-service
sudo chmod +x migrate.sh && ./migrate.sh







if [ "$environment" == "development" ]; then

cat <<EOF > docker-compose.yml
version: '3.8'

env-file:
    - .env.development

EOF
fi

if [ "$environment" == "production" ]; then

cat <<EOF > docker-compose.yml
version: '3.8'

env-file:
  - .env.production

EOF
fi

docker-compose up -d








cd auth-service