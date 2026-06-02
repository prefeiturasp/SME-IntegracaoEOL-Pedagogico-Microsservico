# language: pt

Funcionalidade: Validar componente PAP por turma e funcionário
  Como consumidor da API
  Quero validar componente PAP
  Para garantir que a API retorna sucesso

  Cenário: Validar componente PAP com sucesso
    Dado que possuo acesso à API de validação PAP
    Quando envio uma requisição GET para validar componente PAP
    Então a API de PAP deve responder com sucesso

  Cenário: Validar que o retorno da validação PAP é booleano
    Dado que possuo acesso à API de validação PAP
    Quando envio uma requisição GET para validar componente PAP
    Então a API de PAP deve responder com sucesso
    E o retorno da validação PAP deve ser booleano

  Cenário: Validar PAP sem API Key deve retornar 403
    Dado que possuo acesso à API de validação PAP
    Quando envio uma requisição GET para validar PAP sem autenticação
    Então o status da resposta de validação PAP deve ser 403