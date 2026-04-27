# SME-IntegracaoEOL-Pedagogico-Microsservico

Microsserviço do domínio Pedagógico (Turmas, Componentes, Território do Saber, Atribuição) SME-SP.

---

## Estrutura dos Apps

| App | Responsabilidade | Endpoints | Prefixo API |
|-----|-----------------|-----------|-------------|
| `apps.componentes_curriculares` | Componentes Curriculares | — | `/api/componentes-curriculares/` |
| `apps.core` | Autenticação por API key, dados mock compartilhados | — | — |

### Modelos ETL Cobertos:

- **componentes_curriculares**: `ComponenteCurricular`, `TerritorioDoSaber`, `Atribuicao`

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (para rodar via container)

---

## Rodar localmente (sem Docker)

```bash
# 1. Copiar o .env
cp .env.example .env

# 2. Instalar dependências
pip install -r requirements/local.txt

# 3. Rodar o servidor
python manage.py runserver 0.0.0.0:8001
```

Acesse em: http://localhost:8001/api/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:8001/api/docs/

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key` com o valor configurado em `API_KEY` (`.env`).

Valor padrão em desenvolvimento: `dev-key-default`

```bash
curl -H "X-API-Key: dev-key-default" http://localhost:8001/api/componentes-curriculares/
```

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints Implementados

### Componentes Curriculares

| ID | Método | Path | Descrição |
|----|--------|------|-----------|
| CC01 | GET | `/api/componentes-curriculares/funcionarios/{login}/` | Listar Componentes Curriculares por Funcionário |
| CC02 | GET | `/api/componentes-curriculares/anos/{anoTurma}/regencia/` | Listar Componentes de Regência por Ano de Turma |
| CC03 | GET | `/api/componentes-curriculares/turmas/{codigoTurma}/pap/` | Verificar Componente PAP em Turma |
| CC04 | GET | `/api/componentes-curriculares/ues/{ueId}/modalidades/{modalidade}/anos/{anoLetivo}/` | Listar Componentes Curriculares por UE, Modalidade e Ano |
| CC05 | GET | `/api/componentes-curriculares/ues/{ueId}/modalidades/{modalidade}/anos/{anoLetivo}/turmas-programa/` | Listar Componentes de Turmas Programa |
| CC06 | GET | `/api/componentes-curriculares/ues/{ueId}/turmas/` | Listar Componentes Simplificados por UE e Turmas |
| CC07 | GET | `/api/componentes-curriculares/turmas/` | Listar Componentes para Planejamento por Lista de Turmas |
| CC08 | GET | `/api/componentes-curriculares/turmas/brutos/` | Listar Componentes de Turmas sem Pós-processamento |
| CC09 | GET | `/api/componentes-curriculares/` | Listar Catálogo Completo de Componentes Curriculares |
| CC10 | GET | `/api/componentes-curriculares/turmas/vigencia/` | Obter Vigência de Componentes por Turma e UE |
| CC11 | GET | `/api/componentes-curriculares/grade-curricular/{anoLetivo}/` | Listar Grade Curricular por Ano Letivo |
| CC12 | GET | `/api/componentes-curriculares/turmas/{codigoTurma}/sem-atribuicao/` | Listar Componentes Sem Atribuição em uma Turma |
| CC13 | GET | `/api/componentes-curriculares/{codigoComponente}/territorio-saber/agrupamentos-correlacionados/` | Obter Agrupamentos Correlacionados por Componente |
| CC14 | POST | `/api/componentes-curriculares/territorio-saber/agrupamentos-correlacionados/` | Obter Agrupamentos Correlacionados em Lote |
| CC15 | POST | `/api/componentes-curriculares/territorio-saber/agrupamentos/` | Obter Agrupamentos de Território do Saber por IDs |

---

## Referências
