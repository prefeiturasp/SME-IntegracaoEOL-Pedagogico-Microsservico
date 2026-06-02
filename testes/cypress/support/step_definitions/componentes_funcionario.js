import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps';

function getEnvOrFail(key) {
  const value = Cypress.env(key);

  expect(value, `Variável ${key} não definida`).to.exist;
  expect(String(value).trim(), `${key} vazia`).to.not.be.empty;

  return value;
}

// ======================================================
// GIVEN
// ======================================================

Given('que possuo acesso à API de componentes curriculares por funcionário e perfil', () => {
  getEnvOrFail('API_URL_NOVA');
  getEnvOrFail('API_KEY_NOVA');
  getEnvOrFail('LOGIN_FUNCIONARIO');
  getEnvOrFail('ID_PERFIL');
});

// ======================================================
// WHEN
// ======================================================

When('envio uma requisição GET para consultar componentes curriculares do funcionário', () => {
  const apiUrl = getEnvOrFail('API_URL_NOVA');
  const apiKey = getEnvOrFail('API_KEY_NOVA');

  const login = getEnvOrFail('LOGIN_FUNCIONARIO');
  const idPerfil = getEnvOrFail('ID_PERFIL');

  const endpoint =
    `${apiUrl}/api/v1/componentes-curriculares/funcionarios/${login}/perfis/${idPerfil}/`;

  cy.log(`Endpoint => ${endpoint}`);

  return cy.request({
    method: 'GET',
    url: endpoint,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {

    cy.log(`STATUS => ${res.status}`);
    cy.log(`BODY => ${JSON.stringify(res.body)}`);

    // =========================
    // VALIDAÇÃO FLEXÍVEL (API pode retornar 204)
    // =========================
    expect([200, 204]).to.include(res.status);

    if (res.status === 200) {
      expect(res.body).to.be.an('array');
    }

  });
});

// =========================
// SEM AUTENTICAÇÃO
// =========================

When('envio uma requisição GET para componentes do funcionário sem autenticação', () => {
  const apiUrl = getEnvOrFail('API_URL_NOVA');
  const login = getEnvOrFail('LOGIN_FUNCIONARIO');
  const idPerfil = getEnvOrFail('ID_PERFIL');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/funcionarios/${login}/perfis/${idPerfil}/`,
    headers: {
      accept: 'application/json',
    },
    failOnStatusCode: false,
  }).then((res) => {
    cy.wrap(res).as('resNoAuth');
    cy.get('@resNoAuth').then((r) => {
      expect(r.status).to.eq(403);
    });
  });
});

Then('o status da resposta de funcionário deve ser 403', () => {
  cy.log('Validação de 403 executada no When');
});

// =========================
// LOGIN INEXISTENTE
// =========================

When('envio uma requisição GET para componentes de um login inexistente', () => {
  const apiUrl = getEnvOrFail('API_URL_NOVA');
  const apiKey = getEnvOrFail('API_KEY_NOVA');
  const idPerfil = getEnvOrFail('ID_PERFIL');

  return cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/funcionarios/login_inexistente_00000/perfis/${idPerfil}/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    cy.wrap(res.status).as('statusLoginInexistente');
  });
});

Then('a resposta de login inexistente deve ser 200 ou 204', () => {
  cy.get('@statusLoginInexistente').then((status) => {
    expect([200, 204]).to.include(status);
  });
});