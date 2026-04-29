import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';

let response;

function getEnvOrFail(key) {
  const value = Cypress.env(key);

  expect(value, `Variável de ambiente ${key} não definida`).to.exist;
  expect(value, `${key} está undefined`).to.not.be.undefined;
  expect(value.toString(), `${key} está vazio`).to.not.be.empty;

  return value;
}

// =========================
// COMPONENTES CURRICULARES
// =========================

Given('que possuo acesso à API de componentes curriculares', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição GET para listar componentes curriculares', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes curriculares', () => {
  expect(response.body).to.be.an('array');
  expect(response.body.length).to.be.greaterThan(0);
});

Then('cada item deve conter codigo e descricao', () => {
  response.body.forEach((item) => {
    expect(item).to.have.property('codigo');
    expect(item).to.have.property('descricao');
  });
});

// =========================
// AGRUPAMENTOS
// =========================

Given('que possuo acesso à API de agrupamentos correlacionados', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição GET para listar agrupamentos correlacionados', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/800001/territorio-saber/agrupamentos-correlacionados/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de agrupamentos correlacionados', () => {
  expect(response.body).to.be.an('array');
  expect(response.body.length).to.be.greaterThan(0);
});

Then('cada item deve conter codigo, descricao e territorio_saber', () => {
  response.body.forEach((item) => {
    expect(item).to.have.property('codigo');
    expect(item).to.have.property('descricao');
    expect(item).to.have.property('territorio_saber');
  });
});

Then('o primeiro item deve conter codigo numérico', () => {
  expect(response.body[0].codigo).to.be.a('number');
});

Then('o primeiro item deve conter descricao não vazia', () => {
  expect(response.body[0].descricao).to.be.a('string').and.not.empty;
});

Then('o primeiro item deve conter territorio_saber booleano', () => {
  expect(response.body[0].territorio_saber).to.be.a('boolean');
});

// =========================
// REGÊNCIA POR ANO
// =========================

Given('que possuo acesso à API de componentes de regência', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição GET para listar componentes de regência do ano {int}', (ano) => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/anos/${ano}/regencia/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes de regência', () => {
  expect(response.body).to.be.an('array');
  expect(response.body.length).to.be.greaterThan(0);
});

// =========================
// FUNCIONÁRIO
// =========================

Given('que possuo acesso à API de componentes por funcionário', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('FUNCIONARIO_CODIGO');
});

When('envio uma requisição GET para listar componentes do funcionário', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const funcionario = getEnvOrFail('FUNCIONARIO_CODIGO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/funcionarios/${funcionario}/?agrupaComponenteCurricular=false&checaMotivoDisponibilizacao=true&consideraTurmaInfantil=true&planejamento=false`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes do funcionário', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// GRADE CURRICULAR
// =========================

Given('que possuo acesso à API de grade curricular', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição GET para listar grade curricular do ano {int}', (ano) => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/grade-curricular/${ano}/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de grade curricular', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// NOVO: POST AGRUPAMENTOS POR IDS
// =========================

Given('que possuo acesso à API de agrupamentos por território do saber', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição POST para listar agrupamentos por ids', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  const body = [1216, 1217]; // payload mínimo válido

  return cy.request({
    method: 'POST',
    url: `${apiUrl}/api/v1/componentes-curriculares/territorio-saber/agrupamentos/`,
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body,
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de agrupamentos por ids', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// STATUS
// =========================

Then('o status da resposta deve ser 200', () => {
  expect(response.status).to.eq(200);
});

// =========================
// POST AGRUPAMENTOS CORRELACIONADOS EM LOTE
// =========================

Given('que possuo acesso à API de agrupamentos correlacionados em lote', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
});

When('envio uma requisição POST para listar agrupamentos correlacionados em lote', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');

  // payload mínimo obrigatório (Swagger exige array)
  const body = [1216, 1217];

  return cy.request({
    method: 'POST',
    url: `${apiUrl}/api/v1/componentes-curriculares/territorio-saber/agrupamentos-correlacionados/`,
    qs: {
      dataBase: '2024-01-01', // opcional, mas ajuda evitar comportamento inesperado
    },
    headers: {
      accept: 'application/json',
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body,
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de agrupamentos correlacionados em lote', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// COMPONENTES POR TURMA
// =========================

Given('que possuo acesso à API de componentes por turma', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('TURMA_CODIGO');
});

When('envio uma requisição GET para listar componentes da turma', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const turma = getEnvOrFail('TURMA_CODIGO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/`,
    qs: {
      adicionarComponentesPlanejamento: true,
      codigoTurmas: turma,
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes por turma', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// PAP POR TURMA
// =========================

Given('que possuo acesso à API de componentes PAP', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('TURMA_PAP_CODIGO');
  getEnvOrFail('LOGIN_FUNCIONARIO');
});

When('envio uma requisição GET para listar componentes PAP da turma', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const turma = getEnvOrFail('TURMA_PAP_CODIGO');
  const login = getEnvOrFail('LOGIN_FUNCIONARIO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/${turma}/pap/?login=${login}`,
    headers: {
      accept: '*/*',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes PAP', () => {
  // aceita array OU boolean (comportamento real da API)
  expect(response.body).to.satisfy((body) => {
    return Array.isArray(body) || typeof body === 'boolean';
  });

  // se for array, valida conteúdo
  if (Array.isArray(response.body)) {
    expect(response.body.length).to.be.greaterThan(0);
  }
});

// =========================
// SEM ATRIBUIÇÃO
// =========================

Given('que possuo acesso à API de componentes sem atribuição', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('TURMA_SEM_ATRIBUICAO');
  getEnvOrFail('DATA_BASE');
});

When('envio uma requisição GET para listar componentes sem atribuição da turma', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const turma = getEnvOrFail('TURMA_SEM_ATRIBUICAO');
  const dataBase = getEnvOrFail('DATA_BASE');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/${turma}/sem-atribuicao/?dataBase=${dataBase}`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes sem atribuição', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// COMPONENTES BRUTOS POR TURMA
// =========================

Given('que possuo acesso à API de componentes brutos por turma', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('TURMA_CODIGO');
});

When('envio uma requisição GET para listar componentes brutos da turma', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const turma = getEnvOrFail('TURMA_CODIGO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/brutos/`,
    qs: {
      codigoTurmas: turma,
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes brutos por turma', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// VIGÊNCIA POR TURMA / UE
// =========================

Given('que possuo acesso à API de vigência de componentes', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('ANO_LETIVO');
  getEnvOrFail('COMPONENTE_CURRICULAR');
  getEnvOrFail('UE_CODIGO');
});

When('envio uma requisição GET para listar vigência de componentes', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const anoLetivo = getEnvOrFail('ANO_LETIVO');
  const componente = getEnvOrFail('COMPONENTE_CURRICULAR');
  const ueCodigo = getEnvOrFail('UE_CODIGO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/vigencia/`,
    qs: {
      anoLetivo,
      componentesCurriculares: componente,
      ueCodigo,
      // semestre opcional (mantido fora para evitar erro de contrato)
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de vigência de componentes', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// COMPONENTES POR UE / MODALIDADE / ANO LETIVO
// =========================

Given('que possuo acesso à API de componentes por UE e modalidade', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('UE_CODIGO');
  getEnvOrFail('MODALIDADE');
  getEnvOrFail('ANO_LETIVO_GRADE');
  getEnvOrFail('ANO_ESCOLAR');
});

When('envio uma requisição GET para listar componentes por UE, modalidade e ano letivo', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const ue = getEnvOrFail('UE_CODIGO');
  const modalidade = getEnvOrFail('MODALIDADE');
  const anoLetivo = getEnvOrFail('ANO_LETIVO_GRADE');
  const anoEscolar = getEnvOrFail('ANO_ESCOLAR');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/ues/${ue}/modalidades/${modalidade}/anos/${anoLetivo}/`,
    qs: {
      anosEscolares: anoEscolar,
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes por UE e modalidade', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// TURMAS PROGRAMA POR UE / MODALIDADE / ANO LETIVO
// =========================

Given('que possuo acesso à API de turmas programa', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('UE_CODIGO');
  getEnvOrFail('MODALIDADE');
  getEnvOrFail('ANO_LETIVO_GRADE');
});

When('envio uma requisição GET para listar componentes de turmas programa', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const ue = getEnvOrFail('UE_CODIGO');
  const modalidade = getEnvOrFail('MODALIDADE');
  const anoLetivo = getEnvOrFail('ANO_LETIVO_GRADE');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/ues/${ue}/modalidades/${modalidade}/anos/${anoLetivo}/turmas-programa/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes de turmas programa', () => {
  expect(response.body).to.be.an('array');
});

// =========================
// COMPONENTES POR UE E TURMAS
// =========================

Given('que possuo acesso à API de componentes por UE e turmas', () => {
  getEnvOrFail('API_URL');
  getEnvOrFail('API_KEY');
  getEnvOrFail('UE_TURMAS_CODIGO');
  getEnvOrFail('TURMA_CODIGO');
});

When('envio uma requisição GET para listar componentes por UE e turmas', () => {
  const apiUrl = getEnvOrFail('API_URL');
  const apiKey = getEnvOrFail('API_KEY');
  const ue = getEnvOrFail('UE_TURMAS_CODIGO');
  const turma = getEnvOrFail('TURMA_CODIGO');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/ues/${ue}/turmas/`,
    qs: {
      turmas: turma,
    },
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res;
  });
});

Then('o retorno deve ser uma lista de componentes por UE e turmas', () => {
  expect(response.body).to.be.an('array');
});