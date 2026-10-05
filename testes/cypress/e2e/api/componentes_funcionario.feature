# language: pt

Funcionalidade: Componentes curriculares por funcionário e perfil
  Como consumidor da API
  Quero consultar componentes curriculares por funcionário e perfil
  Para garantir que a API retorna os dados corretamente

  Cenário: Listar componentes curriculares por funcionário e perfil com sucesso
    Dado que possuo acesso à API de componentes curriculares por funcionário e perfil
    Quando envio uma requisição GET para consultar componentes curriculares do funcionário
    Então a API deve responder com sucesso

  Cenário: Consultar componentes sem API Key deve retornar 403
    Dado que possuo acesso à API de componentes curriculares por funcionário e perfil
    Quando envio uma requisição GET para componentes do funcionário sem autenticação
    Então o status da resposta de funcionário deve ser 403

  Cenário: Consultar componentes com login inexistente deve retornar 200 ou 204
    Dado que possuo acesso à API de componentes curriculares por funcionário e perfil
    Quando envio uma requisição GET para componentes de um login inexistente
    Então a resposta de login inexistente deve ser 200 ou 204