# language: pt
Funcionalidade: Listar componentes curriculares
  Como consumidor da API
  Quero consultar os componentes curriculares
  Para garantir que a API retorna dados válidos

  Cenário: Listar componentes curriculares com sucesso
    Dado que possuo acesso à API de componentes curriculares
    Quando envio uma requisição GET para listar componentes curriculares
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de componentes curriculares
    E cada item deve conter codigo e descricao

  Cenário: Listar agrupamentos correlacionados com sucesso
    Dado que possuo acesso à API de agrupamentos correlacionados
    Quando envio uma requisição GET para listar agrupamentos correlacionados
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de agrupamentos correlacionados
    E cada item deve conter codigo, descricao e territorio_saber

  Cenário: Validar estrutura do primeiro agrupamento
    Dado que possuo acesso à API de agrupamentos correlacionados
    Quando envio uma requisição GET para listar agrupamentos correlacionados
    Então o primeiro item deve conter codigo numérico
    E o primeiro item deve conter descricao não vazia
    E o primeiro item deve conter territorio_saber booleano

  Cenário: Listar componentes de regência por ano com sucesso
    Dado que possuo acesso à API de componentes de regência
    Quando envio uma requisição GET para listar componentes de regência do ano 5
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de componentes de regência
    E cada item deve conter codigo e descricao

  Cenário: Listar componentes por funcionário com sucesso
    Dado que possuo acesso à API de componentes por funcionário
    Quando envio uma requisição GET para listar componentes do funcionário
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de componentes do funcionário

  Cenário: Listar grade curricular com sucesso
    Dado que possuo acesso à API de grade curricular
    Quando envio uma requisição GET para listar grade curricular do ano 2010
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de grade curricular

  Cenário: Listar agrupamentos por território do saber via POST com sucesso
    Dado que possuo acesso à API de agrupamentos por território do saber
    Quando envio uma requisição POST para listar agrupamentos por ids
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de agrupamentos por ids

  Cenário: Listar agrupamentos correlacionados em lote via POST com sucesso
    Dado que possuo acesso à API de agrupamentos correlacionados em lote
    Quando envio uma requisição POST para listar agrupamentos correlacionados em lote
    Então o status da resposta deve ser 200
    E o retorno deve ser uma lista de agrupamentos correlacionados em lote
