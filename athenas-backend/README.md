## Preparando o ambiente de desenvolvimento do Athenas

#### Pré-requisitos
Primeiramente, você precisa ter uma conta no GitLab do MP MT:
**[Repositório GitLab MPMT](https://gitlab.mpmt.mp.br/)**.

Os repositório necessários para desenvolvimento que você precisará ser incluído são:

- **[athenas-project](https://gitlab.mpmt.mp.br/mpmt/athenas-project/)**
- **[athenas](https://gitlab.mpmt.mp.br/mpmt/athenas/)**

#### Token GitLab

Crie um diretório no home do seu usuário para armazenar todos os arquivos que vamos baixar relacionados ao ambiente de desenvolvimento:

```bash
mkdir ~/athenas
cd ~/athenas
```

Você precisará criar um token de acesso pessoal de modo que consiga usar o Git sem precisar fornecer usuário e senha toda vez que precisar fazer um push do repositório. É com esse token que você irá se autenticar junto ao GitLab do MP MT, para que consiga clonar os repositórios e versionar o projeto. Além disso o toekn é necessário para fazer o build do sistema.

Para criar um token siga os seguintes passos:

- Faça login no GitLab do MP MT.
- Clique na sua foto de perfil.
- Clique em **Preferences**.
- Na barra de navegação à esquerda clique em **Access Tokens**.
- No campo **Token Name** forneça um nome para o token.
- No campo **Expiration Date** remova a data de expiração, deixando o campo em branco (vazio).
- Em **Select Scopes** marque as opções **read_repository** e **write_repository**.
- Clique no botão **Create personal access token**.

O token, que é uma string de caracteres embaralhados, aparecerá próximo ao topo da página. Copie-o para um arquivo chamado ```token``` e salve o arquivo na pasta ```~/athenas```.

Obs.:
- copie o token neste momento, pois você não terá outra oportunidade de fazer isso.
- Lembre-se, assim como uma senha ou uma chave privada, esse token é pessoal e intransferível.

#### Instalando pacotes básicos

```bash
apt update
apt install curl git -y
```

#### Instalando o Docker

Instale o Docker Engine Community:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

Verifique se foi instalado corretamente:

```bash
docker -v
service docker status
```

Finalmente, estamos prontos para inicializar o glorioso Swarm. Para isto, execute:

```bash
docker swarm init
```

Podemos verificar se o Swarm foi realmente inicializado:

```bash
docker info | grep -i swarm
```

Se tudo correu bem, a saída do comando acima deverá conter a linha seguinte:

```bash
Swarm: active
```

#### Variáveis de ambiente

Os arquivos de configurações da variáveis de ambiente estão na pasta ```athenas-project/config.d```. Cada ambiente tem o seu arquivo específico de configuração, ambientes de Produção, Homologação, Develop e Desenvolvimento Local.
O arquivo do ambiente de desenvolvimento é o ```imp_dev.json```

Variáveis com dados sensíveis, como senhas, são armazenadas utilizando a funcionalidade 'secret' do docker.
Para configurar basta utilizar os comandos do ```docker secret```.

A lista abaixo estão as configurações das variáveis essenciais para subir o projeto.

Para a varável de ambiente de conexão ao banco de dados (DATABASE_DEFAULT) é necessário configurar o valor correto da sercret 'bd_athenas'.

Configurando a conexão ao banco de dados local, com a camada 'db' da stack configurada.

```
DATABASE_DEFAULT: echo "postgres://postgres:123@db/athenas01" | docker secret create bd_athenas -
```

Configurando a conexão ao banco de dados remoto, onde localmente não há a camada 'db' na stack e o database fica em um servidor remoto.
Obs.: é necessário alterar o nome do database (athenas_206) com referência do final do IP da maquina de desenvolvimento que está sendo configurada.

```
DATABASE_DEFAULT: echo "postgres://athenas:MPMT159357athenas@athenas-bd-dev.sede.mpe/athenas_206" | docker secret create bd_athenas -
```

E abaixo estão as configurações das variáveis que não há a nessencidade de configurar o valor correto, mas é necessário setá-las ao menos com valor vazio. Obs: algumas funcionalidades do sistema só funcionam corretamente configurando o valor correto da variável.

```
CROWD_USERNAME: echo "" | docker secret create crowd_username -
CROWD_PASSWORD: echo "" | docker secret create crowd_password -
CROWD_TOKEN: echo "" | docker secret create crowd_token -
LDAP_ADMIN_USER_DN: echo "" | docker secret create ldap_admin_user_dn -
LDAP_ADMIN_PASSWD: echo "" | docker secret create ldap_admin_passwd -
JASPER_SERVER_USERNAME: echo "" | docker secret create jasper_server_username -
JASPER_SERVER_PASSWORD: echo "" | docker secret create jasper_server_password -
DATABASE_PLANTOES_USER: echo "" | docker secret create database_plantoes_user -
DATABASE_PLANTOES_PASSWORD: echo "" | docker secret create database_plantoes_password -
DATABASE_SISDIAS_USER: echo "" | docker secret create database_sisdias_user -
DATABASE_SISDIAS_PASSWORD: echo "" | docker secret create database_sisdias_password -
DATABASE_FOLHAPONTO_USER: echo "" | docker secret create database_folhaponto_user -
DATABASE_FOLHAPONTO_PASSWORD: echo "" | docker secret create database_folhaponto_password -
DATABASE_SIAP_USER: echo "" | docker secret create database_siap_user -
DATABASE_SIAP_PASSWORD: echo "" | docker secret create database_siap_password -
HERMES_TOKEN: echo "" | docker secret create hermes_token -
CROWD_APP_PASSWD: echo "" | docker secret create crowd_app_passwd -
TOKEN_API_NOMEACAO_RESIDENTES: echo "" | docker secret create token_api_nomeacao_residentes -
JWT_SECRET_KEY: echo "" | docker secret create jwt_secret_key -
TOKEN_API_DAA_TRANSP_DIST: echo "" | docker secret create token_api_daa_transp_dist -
HERMES_TOKEN_RELATORIOS echo "" | docker secret create hermes_token_relatorios -
HERMES_TOKEN_EMAIL_PESSOAL echo "" | docker secret create hermes_token_email_pessoal -
HERMES_TOKEN_PROCESSAMENTOS echo "" | docker secret create hermes_token_processamentos -
TOKEN_API_PLANTOES echo "" | docker secret create token_api_plantoes -
TOKEN_SISDIAS: echo "" | docker secret create token_sisdias -
```

#### Fazendo o deploy

Agora vamos baixar o repositório que contém os scripts para instalação do Athenas, e para isso precisaremos do token gerado pelo GitLab, conforme já instruído no início deste tutorial:

```bash
cd ~/athenas
git clone https://oauth:COLE-AQUI-SEU-TOKEN@gitlab.mpmt.mp.br/area-meio/athenas-project.git
```

Copie o arquivo ```token``` para o mesmo diretório do script ```init.sh```, dentro da pasta ```athenas-project/```. Esse mesmo token será utilizado pelo script para baixar o código-fonte do Athenas:

```bash
cd ~/athenas/athenas-project
cp ../token ./
```

O projeto Athenas tem arquivos específicos de configurações para cada ambiente: produção, homologação e desenvolvimento.
Para subir o projeto em ambiente de desenvolvimento é só executar o arquivo ```init-dev.sh```.


```bash
cd ~/athenas/athenas-project
./init-dev.sh
```

O projeto utiliza o swarm e os services para subir todas as camadas da stack, para monitor se as camadas subiram corretamente utilize o comendo abaixo:

```bash
cd ~/athenas/athenas-project
docker service ls
```

Na listagem,  todos os services deverão estar com o status ```1/1```. Na primeira vez que for subir o sistema os services não subirão corretamente, pois ainda não há database e consequentemente não há dados.

#### Preparando o banco de dados

Após subir a aplicação é necessário criar um database e realizar um restore no banco de dados de desenvolvimento.
Esse processo deverá ser feito utilizando o PgAdmin.


#### Testando

Por fim, basta acessar o Athenas na url utilizando o IP da maquina de desenvolvimento, por exemplo **http://10.2.5.199:8000**.

#### Derrubar o sistema (stack do athenas)

Quando precisar derrubar toda a stack do projeto Athenas, todas as camadas, pesquise o nome da stack e execute o comando para remover a stack. Siga os comandos abaixo:

```bash
docker stack ls
docker stack rm ath_dev
```

E para subir o projeto novamente é só rodar o arquivo ```init-dev.sh```:

```bash
./init-dev.sh
```

#### Debugar

Para acessar o container do Athenas e poder acessar o shell do python, rode o comando abaixo para entrar no container do service ```ath_dev_worker```:

```bash
docker exec -it $(docker ps -f "name=ath_dev_worker" -f "status=running" --format {{.ID}} -l) busybox.py shell
```

Dentro deste container você conseguirá executar todos os comandos do django necessários para desenvolvimento, como por exemplo o ```makemigrations``` e o ```migrate```

E para acessar o shell do Django rode:

```bash
./manage.py shell
```
#### Para subir o Registry localmente

Estando na pasta raiz do projeto, acesse a pasta 'compose.d' e instale um repositório (registry) de imagens no ambiente local de desenvolvimento:

```bash
cd ./compose.d/
docker stack deploy -c local-registry.yml local-registry
```


#### Bom desenvolvimento

Por enquanto é isso! :)
