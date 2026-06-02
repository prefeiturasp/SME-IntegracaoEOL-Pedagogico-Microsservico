# language: pt

Funcionalidade: Componentes de regência por ano de turma
  Como consumidor da API
  Quero consultar componentes de regência por ano
  Para garantir que a API retorna sucesso

  Cenário: Consultar regência sem API Key deve retornar 403
    Dado que possuo acesso à API de componentes de regência
    Quando envio uma requisição GET para listar regência sem autenticação
    Então o status da resposta de regência deve ser 403