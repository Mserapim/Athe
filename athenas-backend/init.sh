#!/bin/bash

COMPOSE_DIR="compose.d"

if [ -z "$ENVBASE" ]; then
  echo 'Erro na chamada! Execute o script correto de acordo com o ambiente!'
  echo '# init-mpmt-master.sh - produção'
  echo '# init-unstable.sh - homologacao'
  echo '# init-dev.sh - desenvolvimento'
  exit 0
fi


if [ -z "$USER_ID" ]; then
  USER_ID=$(id -u)
fi

if [ -z "$STACKNAME" ]; then
  STACKNAME='dev'
fi

if [ -z "$BRANCH" ]; then
  BRANCH='unstable'
fi

if [ -z "$HTTP_PORT" ]; then
  HTTP_PORT='8000'
fi

if [ -z "$FLOWER_PORT" ]; then
  FLOWER_PORT=$(($HTTP_PORT + 1))
fi

if [ -z "$HTTPS_PORT" ]; then
  HTTPS_PORT='8443'
fi

if [ -z "$IMGHUB_REPO" ]; then
  IMGHUB_REPO='registry.mpmt.mp.br/mpmt'
fi

if [ -z $PROXY_HOST ]; then
  PROXY_HOST="athenas.mpmt.mp.br"
fi

if [ $# -gt 0 ]; then
  if [ $1 == "help" ]; then
    echo ""
    echo "Modo de uso:"
    echo "  $0 [stackname] (envbase)"
    echo ""
    echo "Para envbase verifique as opções em compose.d"
    echo ""
    exit 0
  fi  
fi

if [ ! -f "${COMPOSE_DIR}/${ENVBASE}.yml" ]; then
  echo "O arquivo ${COMPOSE_DIR}/${ENVBASE}.yml não foi encontrado"
  echo "O deploy foi encerrado."
  exit 1
fi

HIGHLIGHT='\033[1;33m'
RESET='\033[0m'

echo -e "[ Resumo ]"
echo -e "${HIGHLIGHT}IMGHUB_REPO${RESET} .: $IMGHUB_REPO"
echo -e "${HIGHLIGHT}PROXY_HOST${RESET} ..: $PROXY_HOST"
echo -e "${HIGHLIGHT}ENVBASE${RESET} .....: $ENVBASE"
echo -e "${HIGHLIGHT}GITLAB_HOST${RESET} .: $GITLAB_HOST"
echo -e "${HIGHLIGHT}GITLAB_GROUP${RESET} : $GITLAB_GROUP"
echo -e "${HIGHLIGHT}STACKNAME${RESET} ...: $STACKNAME"
echo -e "${HIGHLIGHT}BRANCH${RESET} ......: $BRANCH"
echo -e "${HIGHLIGHT}HTTP_PORT${RESET} ...: $HTTP_PORT"
echo -e "${HIGHLIGHT}HTTPS_PORT${RESET} ..: $HTTPS_PORT"
echo -e "${HIGHLIGHT}FLOWER_PORT${RESET} .: $FLOWER_PORT"
echo -e "${HIGHLIGHT}USER_ID${RESET} .....: $USER_ID"
echo

if [[ "$ENVBASE" == *dev ]]; then
  if [ ! -d src ]; then
    if [ -f token ]; then
      TOKEN=$(cat token)
      git clone https://oauth:${TOKEN}@${GITLAB_HOST}/${GITLAB_GROUP}/athenas.git src
    else
      echo ""
      echo "Não foi possivel encontrar o arquivo com token de acesso do gitlab"
      echo "Este token pode ser criada no seguinte endereço:"
      echo ""
      echo "  https://${GITLAB_HOST}/profile/personal_access_tokens"
      echo ""
      echo "A chave deve ter no minimo acesso de leitura e deve ser gravada"
      echo "em um arquivo \"token\" junto com este script."
      echo ""
      exit 1
    fi
  fi
else
  echo ""
  echo "Rodando o sistema sem o diretório SRC"
  echo ""
fi

volumes="db mongo logs storage etc cache redis"

for volume in $(echo $volumes)
do
  if [ ! -d "volumes/${volume}" ]; then
    mkdir -p "volumes/${volume}"
  fi
done

if [ ! -d "volumes/htdocs" ]; then
  wget https://tools.mpmt.mp.br/files/athenas/js-vol.tar.gz
  mkdir -p volumes/htdocs
  tar xf js-vol.tar.gz --strip-components=1 -C volumes/htdocs
  rm js-vol.tar.gz
fi

if [ ! -f "config.d/${ENVBASE}.json" ]; then
  echo "Será gerada uma SECRET_KEY nova"
  cat > "config.d/${ENVBASE}.json" <<EOF
{
  "SECRET_KEY": "$(openssl rand 128 | base64 -w0)"
}
EOF
fi

if [ ! -f "redis.conf" ]; then
  cat > redis.conf <<EOF
requirepass secr3t
tcp-keepalive 0

save 900 1
save 300 10
save 60 10000

rdbcompression no
rdbchecksum no

appendonly no
EOF
fi

if [ ! -f "volumes/etc/rabbitmq/rabbitmq.conf" ]; then
  mkdir -p volumes/etc/rabbitmq
  cat > volumes/etc/rabbitmq/rabbitmq.conf <<EOF
default_vhost = default
default_user = admin
default_pass = secr3t
vm_memory_high_watermark.relative = 0.9

EOF
fi

if [ ! -f $HOME/.pgpass ]; then
  cat > $HOME/.pgpass <<EOF
127.0.0.1:5432:*:postgres:123
EOF
fi

chmod 0600 $HOME/.pgpass

#docker stack rm ${STACKNAME}
#docker node ls --format '{{.Hostname}}' | xargs -I {} ssh -p 2280 {} "docker images --filter "dangling=true" -q | xargs docker rmi"
#docker node ls --format '{{.Hostname}}' | xargs -I {} ssh -p 2280 {} "docker rmi -f ${IMGHUB_REPO}/mpmt/athenas:${BRANCH}"

ENVBASE=$ENVBASE \
BRANCH=$BRANCH \
HTTP_PORT=$HTTP_PORT \
IMGHUB_REPO=$IMGHUB_REPO \
HTTPS_PORT=$HTTPS_PORT \
FLOWER_PORT=$FLOWER_PORT \
USER_ID=$USER_ID \
  docker stack deploy --with-registry-auth -c ${COMPOSE_DIR}/${ENVBASE}.yml ${STACKNAME}
