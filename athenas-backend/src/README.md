Base de conhecimento
===

* [Python 2to3 utilitário](https://docs.python.org/3.7/library/2to3.html)
* [Documentação Python 3.7](https://docs.python.org/3.7/)
* [Documentação Python 3.9](https://docs.python.org/3.9/)

# Padrões de Desenvolvimento

## Estrutura do Módulo

### Organização de Diretórios

Estrutura básica do módulo:

```
meu_modulo/
├── __init__.py
├── apps.py
├── models.py
├── urls.py
├── tasks.py
├── const.py
├── utils.py
│
├── migrations/        # Migrations
├── management/        # Comandos Django
├── fixtures/          # Dados iniciais
├── notificacoes/      # Notificações
├── apiv2/             # API v2
├── scripts/           # Utilitários
├── templates/         # Templates
```

## Padronização de APIs

### Filtros de Ranges de Datas

Seguir o seguinte modelo:

- `solicitacao_inicio_em`
- `solicitacao_fim_em`

### Parâmetros (query_params)

#### Relacionamento

- **Único**:
```json
"categoria": number
```

- **Múltiplos**:
```json
"categorias[]": number[]
```

#### Choice

- **Único**:
```json
"categoria_funcional": string | number
```

- **Múltiplos**:
```json
"categoria_funcionais[]": string | number[]
```

### Retorno da Listagem

#### Relacionamentos

- **Único**:
```json
"categoria": {
    "id": 1515,
    "display": "Categoria Exemplo"
}
```

- **Múltiplos**:
```json
"categorias": [
    {
        "id": 1515,
        "display": "Categoria Exemplo 1"
    },
    {
        "id": 1516,
        "display": "Categoria Exemplo 2"
    }
]
```

#### Choices

- **Único**:
```json
"categoria_funcional": {
    "valor": "label1",
    "display": "Descrição do Label 1"
}
```

- **Múltiplos**:
```json
"categoria_funcionais": [
    {
        "valor": "label1",
        "display": "Descrição do Label 1"
    },
    {
        "valor": "label2",
        "display": "Descrição do Label 2"
    }
]
```

## Padrão de Resposta da API de Listagem

```json
{
    "total": 3,
    "page": 1,
    "per_page": 3,
    "navigation": {
        "next": null,
        "previous": null
    },
    "results": []
}
```

## Padrão de Rotas da API

### Listagem (Plural)

- `GET /usuarios/` → Retorna a lista de usuários
- `GET /pedidos/` → Retorna a lista de pedidos

### Registro Único (Singular)

- `GET /usuario/?id=123` → Retorna um único usuário
- `GET /pedido/?id=456` → Retorna um único pedido

### Ações Específicas (Verbo no Final)

- `POST /usuario/criar/` → Cria um novo usuário
- `POST /usuario/editar/?id=123` → Edita um usuário
- `POST /usuario/apagar/?id=123` → Apaga um usuário
- `POST /pedido/cancelar/?id=456` → Cancela um pedido