# DevShowcase API

Backend REST da plataforma DevShowcase, desenvolvido com Python, FastAPI, SQLAlchemy e SQLite.

## Requisitos

- Python 3.11 ou superior
- Postman (para executar a coleção fornecida)

## Executar localmente

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

A aplicação cria o banco relacional `devshowcase.db` ao iniciar. Para usar outro banco compatível com SQLAlchemy, configure a variável `DATABASE_URL` antes de iniciar.

- Documentação interativa: http://127.0.0.1:8000/docs
- Verificação de saúde: http://127.0.0.1:8000/

## Modelo relacional

- **Profile 1:N Project**: cada projeto pertence a um perfil.
- **Project N:N Technology**: a tabela de associação `project_technologies` liga projetos e tecnologias.
- **Project 1:N Feedback**: cada opinião pertence a um projeto.

As entidades e seus relacionamentos ficam em `app/models.py`. Os DTOs de entrada e saída, incluindo validação de campos obrigatórios e URLs HTTP/HTTPS, estão em `app/schemas.py`.

## Endpoints da etapa

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/profiles` | Cadastra perfil |
| GET | `/api/profiles/{id}` | Busca perfil e seus projetos |
| POST | `/api/technologies` | Cadastra tecnologia |
| GET | `/api/technologies` | Lista tecnologias |
| POST | `/api/projects` | Cadastra projeto com perfil e tecnologias |
| GET | `/api/projects` | Lista projetos com tecnologias e opiniões |

A API responde com **201** ao criar recursos, **404** quando o perfil ou tecnologia referenciado não existe, **409** para tecnologia duplicada e **422** para dados inválidos.

## Executar os testes

```powershell
python -m pytest
```

## Demonstração no Postman

Importe `postman/DevShowcase_API.postman_collection.json` e mantenha a API em execução. Execute as requisições da coleção em sequência: ela salva os IDs criados e os reutiliza nas buscas e no cadastro do projeto. A coleção também inclui exemplos de validação.

Na gravação, mostre a execução de cada requisição e a resposta retornada. O GET do perfil mostra o perfil com seus projetos; o GET de projetos mostra as tecnologias associadas.

## Repositório e vídeo

Para concluir o PDF de entrega, inclua o link público do repositório GitHub e o link do vídeo não listado no YouTube. O vídeo e os links finais dependem das contas e gravação do grupo.
