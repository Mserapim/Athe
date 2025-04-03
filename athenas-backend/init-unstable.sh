#!/bin/bash


export BRANCH="unstable"
export STACKNAME=ath_$BRANCH
export ENVBASE="branched-unstable"
export HTTP_PORT=8000
export HTTPS_PORT=8443
export PROXY_HOST="athenas-hom.mpmt.mp.br"


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
