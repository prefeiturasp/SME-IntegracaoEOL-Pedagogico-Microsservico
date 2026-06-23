# SME-IntegracaoEOL-Pedagogico-Microsservico

Microsserviço do domínio Pedagógico (Turmas, Componentes, Território do Saber, Atribuição) SME-SP.

---

## Estrutura dos Apps

| App | Responsabilidade | Prefixo API |
|-----|-----------------|-------------|
| `apps.turmas` | Turmas, sincronizações institucionais, itinerários | `/api/v1/pedagogico/turmas/` |
| `apps.componentes_curriculares` | Componentes Curriculares, Território do Saber, Atribuições | `/api/v1/pedagogico/componentes-curriculares/` |
| `apps.core` | Autenticação por API key | — |

### Modelos ETL Cobertos:

- **turmas**: `Turma` (`managed=False`), `TurmaItinerarioEnsinoMedio` (fixture local)
- **componentes_curriculares**: `ComponenteCurricular`, `ComponenteTurma`, `AtribuicaoComponente`, `GradeComponenteCurricular`, `ComponenteCurricularHierarquia`, `AgrupamentoAtribuicaoTerritorioSaber`

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

## Executar Testes com Docker

Para rodar a suíte completa de testes e gerar o relatório de cobertura:

```bash
./scripts/executar_testes_docker.sh
```

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
| `/pedagogico/api/v1/docs/` | Swagger UI interativo |
| `/pedagogico/api/v1/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints Implementados

### Turmas

| ID | Método | Path | Descrição |
|----|--------|------|-----------|
| T01 | POST | `/api/v1/pedagogico/turmas/turmas-regulares/` | Filtrar turmas regulares por lista de códigos |
| T02 | POST | `/api/v1/pedagogico/turmas/turmas-programa/` | Filtrar turmas programa por lista de códigos |
| T03 | POST | `/api/v1/pedagogico/turmas/listar-turmas/` | Listar turmas por lista de códigos (sem filtro de tipo) |
| T04 | GET | `/api/v1/pedagogico/turmas/{codigoTurma}/dados/` | Dados cadastrais de uma turma |
| T05 | GET | `/api/v1/pedagogico/turmas/ues/{ueCodigo}/turmas/{turmaCodigo}/sincronizacoes-institucionais/` | Sincronizações institucionais de uma turma por UE |
| T06 | GET | `/api/v1/pedagogico/turmas/ue/{ueCodigo}/sincronizacoes-institucionais/anosLetivos/` | Códigos de turma da UE (tipo_turma <> 4), filtráveis por `anos_letivos_vigente`; ausente/vazio lista todos da UE, `0` retorna `[]` |
| T07 | GET | `/api/v1/pedagogico/turmas/anos-letivos/{anoLetivo}/professor/{professorRf}/turmas-historicas-geral/` | Turmas do professor por ano letivo com atribuição válida. Resposta no contrato legado de 7 campos (`ano`, `ano_letivo`, `codigo`, `modalidade`, `codigo_modalidade`, `nome_turma`, `semestre`); sem resultado retorna `200 []` |
| T08 | GET | `/api/v1/pedagogico/turmas/itinerario/ensino-medio/` | Itinerários do Ensino Médio (fixture local) |

### Componentes Curriculares

| ID | Método | Path | Descrição |
|----|--------|------|-----------|
| CC01 | GET | `/api/v1/pedagogico/componentes-curriculares/funcionarios/{login}/` | Listar Componentes Curriculares por Funcionário |
| CC02 | GET | `/api/v1/pedagogico/componentes-curriculares/anos/{anoTurma}/regencia/` | Listar Componentes de Regência por Ano de Turma |
| CC03 | GET | `/api/v1/pedagogico/componentes-curriculares/turmas/{codigoTurma}/pap/` | Verificar Componente PAP em Turma |
| CC04 | GET | `/api/v1/pedagogico/componentes-curriculares/ues/{ueId}/modalidades/{modalidade}/anos/{anoLetivo}/` | Listar Componentes Curriculares por UE, Modalidade e Ano |
| CC05 | GET | `/api/v1/pedagogico/componentes-curriculares/ues/{ueId}/modalidades/{modalidade}/anos/{anoLetivo}/turmas-programa/` | Listar Componentes de Turmas Programa |
| CC06 | GET | `/api/v1/pedagogico/componentes-curriculares/ues/{ueId}/turmas/` | Listar Componentes Simplificados por UE e Turmas |
| CC07 | GET | `/api/v1/pedagogico/componentes-curriculares/turmas/` | Listar Componentes para Planejamento por Lista de Turmas |
| CC08 | GET | `/api/v1/pedagogico/componentes-curriculares/turmas/brutos/` | Listar Componentes de Turmas sem Pós-processamento |
| CC09 | GET | `/api/v1/pedagogico/componentes-curriculares/` | Listar Catálogo Completo de Componentes Curriculares |
| CC10 | GET | `/api/v1/pedagogico/componentes-curriculares/turmas/vigencia/` | Obter Vigência de Componentes por Turma e UE |
| CC11 | GET | `/api/v1/pedagogico/componentes-curriculares/grade-curricular/{anoLetivo}/` | Listar Grade Curricular por Ano Letivo |
| CC12 | GET | `/api/v1/pedagogico/componentes-curriculares/turmas/{codigoTurma}/sem-atribuicao/` | Listar Componentes Sem Atribuição em uma Turma |
| CC13 | GET | `/api/v1/pedagogico/componentes-curriculares/{codigoComponente}/territorio-saber/agrupamentos-correlacionados/` | Obter Agrupamentos Correlacionados por `cod_agrupamento` |
| CC14 | POST | `/api/v1/pedagogico/componentes-curriculares/territorio-saber/agrupamentos-correlacionados/` | Obter Agrupamentos Correlacionados em Lote por `cod_agrupamento` |
| CC15 | POST | `/api/v1/pedagogico/componentes-curriculares/territorio-saber/agrupamentos/` | Obter Agrupamentos de Território do Saber por `cod_agrupamento` |

---

## Referências
