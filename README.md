# Mangas Scrappers

Projeto em Python para extrair imagens de capitulos de manga a partir de URLs
publicas e salvar os arquivos localmente na estrutura:

```text
contents/<titulo do manga>/<capitulo>/<indice>.<extensao>
```

## Aviso

Este projeto e de uso didatico.

Ele tambem foi estruturado como exemplo pratico de SDD (Specification-Driven
Development) com Spec Kit, cobrindo o fluxo de especificacao, clarificacao,
planejamento, quebra em tarefas e implementacao orientada por artefatos.

Ele existe para estudo de:
- organizacao de um CLI pequeno em Python
- uso de SDD com Spec Kit
- extracao de dados HTML e consumo de APIs publicas
- estruturacao de arquivos e pipeline simples de download

Nao deve ser usado para contornar anuncios, mecanismos de monetizacao,
restricoes de acesso, autenticacao, anti-bot ou qualquer protecao de terceiros.
O escopo atual e limitado a conteudo publicamente acessivel ao usuario.

## Requisitos

- Python 3.12+
- Ambiente virtual Python

## Instalacao

```bash
python3 -m venv .venv
source .venv/bin/activate
.venv/bin/pip install -e .
```

## Uso

Extrair um capitulo:

```bash
.venv/bin/python -m src.cli.main extract-chapter "https://mangadex.org/chapter/<chapter-id>"
```

Extrair e salvar as imagens:

```bash
.venv/bin/python -m src.cli.main extract-chapter "https://mangadex.org/chapter/<chapter-id>" --save
```

Extrair varios capitulos a partir de um arquivo texto com 1 URL por linha:

```bash
.venv/bin/python -m src.cli.main extract-chapter "/caminho/para/chapters.txt" --file
```

Extrair varios capitulos e salvar as imagens:

```bash
.venv/bin/python -m src.cli.main extract-chapter "/caminho/para/chapters.txt" --file --save
```

Extrair todos os capitulos a partir de uma URL de title do MangaDex:

```bash
.venv/bin/python -m src.cli.main extract-title "https://mangadex.org/title/<title-id>/<slug>"
```

Extrair varios titles a partir de um arquivo texto com 1 URL de title por linha:

```bash
.venv/bin/python -m src.cli.main extract-title "/caminho/para/titles.txt" --file
```

Exemplo de `chapters.txt`:

```text
https://mangadex.org/chapter/<chapter-id-1>
https://mangadex.org/chapter/<chapter-id-2>
```

Exemplo de `titles.txt`:

```text
https://mangadex.org/title/<title-id-1>/<slug-1>
https://mangadex.org/title/<title-id-2>/<slug-2>
```

## Exemplo de saida

```text
contents/Release That Witch/02.Chapter 2/001.jpg
```

## Estrutura

```text
src/
specs/
contents/
```
