# Guia de Estilo para Black Formatter no Python

## Introdução

Este documento define as diretrizes de formatação de código Python utilizando o Black, um formatador de código que preza por consistência e padronização.

## Instalação

Para instalar o Black, utilize o pip:

```bash
pip install black
```

## Regras de Formatação

### Comprimento da Linha

O padrão é 88 caracteres por linha. Isso pode ser alterado na configuração para valores como 79 (PEP 8) ou 100.

### Aspas

Black converte todas as aspas para aspas duplas por padrão:

#### Antes

```python
x = 'teste'
```

#### Depois

```python
x = "teste"
```

Se preferir manter as aspas como estão, use `--skip-string-normalization`.

### Espaçamento e Indentação

A indentação é de 4 espaços, conforme a PEP 8.

### Quebra de Linhas e Chaves

Black quebra linhas automaticamente para manter a legibilidade:

#### Antes

```python
def funcao(parametro1, parametro2, parametro3, parametro4): pass
```

#### Depois

```python
def funcao(
    parametro1,
    parametro2,
    parametro3,
    parametro4,
):
    pass
```

### Uso de Parênteses

Black adiciona parênteses extras para evitar ambiguidades e melhorar a legibilidade:

#### Antes

```python
resultado = x + y * z - w
```

#### Depois

```python
resultado = x + (y * z) - w
```

## Execução

Para formatar um arquivo ou diretório, use:

```bash
black meu_arquivo.py
black meu_diretorio/
```

Para verificar arquivos sem modificar:

```bash
black --check meu_diretorio/
```

## Integração com Git

Para evitar commits de código sem formatação, configure um pre-commit hook:

```bash
pip install pre-commit
pre-commit install
```

## Conclusão

O Black simplifica a manutenção do código e evita discussões sobre estilo. A adoção desse formatador garante consistência e melhora a legibilidade do projeto.