# Fuse - Admin template and Starter project for Angular

This project was generated with [Angular CLI](https://github.com/angular/angular-cli)

## Preparando o ambiente de desenvolvimento do Athenas Frontend

#### Instale o Git

-   **[Git download](https://git-scm.com/download/win)**

#### Instale o Node.js

-   **[Node.js download](https://nodejs.org/en/download)**

**Após instalar reinicie o vscode**

#### Clone o projeto direto na máquina windows:

-   **[athenas-frontend](https://gitlab.mpmt.mp.br/area-meio/athenas-frontend)**

#### Configure o arquivo hosts

-   Adicione a configuração no arquivo **hosts** em: C:\Windows\System32\drivers\etc **(abrir como administrador)**:

```bash
10.2.5.xxx(ip athenas dev)      localapi.mpmt.mp.br
172.16.20.xxx(ip máquina windows)    local.mpmt.mp.br
```

#### Configure o arquivo proxy.conf.json

-   Configure o ip do seu sistema **Athenas Dev** no **target** do arquivo: **athenas-frontend/proxy.conf.json**, exemplo:

```bash
"target": "http://10.2.5.123:8000/athenas/api/v2",
```

#### Configure o arquivo environment.ts

-   Configure o ip da sua máquina **Windows** no **remote** do arquivo: **athenas-frontend/src/environments/environment.ts**, exemplo:

```bash
remote: '172.16.20.123',
```

**Derrube o Athenas e reinicie a máquina Windows para aplicar as configurações**

#### Instale e inicie o projeto

-   Na pasta inicial do projeto (**athenas-frontend/**), execute o comando:

```bash
npm install
```

-   Suba o sistema com o comando:

```bash
npm start ou
nohup npm start > server.log 2>&1 &
```

Opção de criar uma sessão do terminal que fica em segundo plano:

comando para criar uma nova sessão do terminal

```bash
tmux new -s front_athenas
```

comando para acessar uma sessão do terminal 

```bash
tmux attach -t front_athenas
```

comando para subir o sistema salvando os logs em um arquivo

```bash
npm start > server.log 2>&1 &
```

-   Se as configurações estiverem corretas o sistema estará acessível no link: https://local.mpmt.mp.br:4200/

## Rodando o Storybook

Para rodar o Storybook localmente, execute o seguinte comando na raiz do projeto:

```bash
npm run storybook
```

Isso iniciará o Storybook em `http://localhost:6006/`.


## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.





ATS-6802 - 
Adicionar tag de ambiente
personalizaçãod do modal
Ocultar conteudo expandido
