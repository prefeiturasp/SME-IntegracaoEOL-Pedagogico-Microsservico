# language: pt

Funcionalidade: Componentes curriculares por funcionário e perfil
  Como consumidor da API
  Quero consultar componentes curriculares por funcionário e perfil
  Para garantir que a API retorna os dados corretamente

  Cenário: Listar componentes curriculares por funcionário e perfil com sucesso
    Dado que possuo acesso à API de componentes curriculares por funcionário e perfil
    Quando envio uma requisição GET para consultar componentes curriculares do funcionário
    Então a API deve responder com sucesso