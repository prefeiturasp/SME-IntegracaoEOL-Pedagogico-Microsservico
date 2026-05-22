# language: pt

Funcionalidade: Componentes de regência por ano de turma
  Como consumidor da API
  Quero consultar componentes de regência por ano
  Para garantir que a API retorna sucesso

  Cenário: Listar componentes de regência com sucesso
    Dado que possuo acesso à API de componentes de regência
    Quando envio uma requisição GET para listar componentes de regência do ano 0
    Então a API deve responder com sucesso