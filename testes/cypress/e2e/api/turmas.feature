# language: pt
Funcionalidade: Consultar turmas pedagógicas
  Como consumidor da API
  Quero consultar dados de turmas
  Para garantir que a API retorna dados válidos

  Cenário: Listar turmas regulares via POST com sucesso
    Dado que possuo acesso à API de turmas regulares
    Quando envio uma requisição POST para listar turmas regulares
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de turmas regulares

  Cenário: Listar turmas programa via POST com sucesso
    Dado que possuo acesso à API de turmas programa via POST
    Quando envio uma requisição POST para listar turmas programa
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de turmas programa

  Cenário: Listar turmas via POST com sucesso
    Dado que possuo acesso à API de listar turmas
    Quando envio uma requisição POST para listar turmas
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de turmas

  Cenário: Consultar dados de uma turma com sucesso
    Dado que possuo acesso à API de dados de turma
    Quando envio uma requisição GET para consultar dados da turma
    Então o status da resposta de turmas deve ser 200
    E o retorno deve conter dados da turma

  Cenário: Consultar sincronizações institucionais de uma turma com sucesso
    Dado que possuo acesso à API de sincronizações institucionais de turma
    Quando envio uma requisição GET para listar sincronizações da turma
    Então a resposta de sincronizações deve ser válida

  Cenário: Consultar anos letivos da UE com sucesso
    Dado que possuo acesso à API de anos letivos da UE
    Quando envio uma requisição GET para listar anos letivos da UE
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de anos letivos

  Cenário: Consultar turmas históricas de professor com sucesso
    Dado que possuo acesso à API de turmas históricas do professor
    Quando envio uma requisição GET para listar turmas históricas do professor
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de turmas históricas

  Cenário: Consultar itinerário do ensino médio com sucesso
    Dado que possuo acesso à API de itinerário do ensino médio
    Quando envio uma requisição GET para listar itinerário do ensino médio
    Então o status da resposta de turmas deve ser 200
    E o retorno deve ser uma lista de itinerários

  Cenário: Acessar dados de turma inexistente deve retornar 404
    Dado que possuo acesso à API de dados de turma
    Quando envio uma requisição GET para consultar dados de uma turma inexistente
    Então o status da resposta de turmas deve ser 404

  Cenário: Acessar turmas regulares sem API Key deve retornar 403
    Dado que possuo acesso à API de turmas regulares
    Quando envio uma requisição POST para listar turmas regulares sem autenticação
    Então o status da resposta de turmas deve ser 401 ou 403
