#!/bin/bash


export BRANCH="unstable"
export STACKNAME=ath_dev
export ENVBASE="imp_local_dev"
export HTTP_PORT=8000
export HTTPS_PORT=8443
export GITLAB_HOST="gitlab.mpmt.mp.br"  # Endereço GitLab do MP MT.
export GITLAB_GROUP="area-meio"  # Grupo do GitLab.
export IMGHUB_REPO="registry.mpmt.mp.br/mpmt"  # Endereço do repositório de imagens docker.
export PROXY_HOST="athenas-dev.mpmt.mp.br"

# Chamar a execução do outro script
./init.sh

# Verificar o código de saída do script chamado
retorno=$?

# Tratamento de erros
if [ $retorno -eq 0 ]; then
  echo "O script foi executado com sucesso!"
elif [ $retorno -eq 1 ]; then
  echo "Ocorreu um erro durante a execução do script."  
else
  echo "Erro desconhecido."
fi
