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

Given('que possuo acesso à API de componentes de regência', () => {
  getEnvOrFail('API_URL_NOVA');
  getEnvOrFail('API_KEY');
});

// ======================================================
// WHEN
// ======================================================

When(
  'envio uma requisição GET para listar componentes de regência do ano {int}',
  (anoTurma) => {
    const apiUrl = getEnvOrFail('API_URL_NOVA');
    const apiKey = getEnvOrFail('API_KEY');

    const endpoint =
      `${apiUrl}/api/v1/componentes-curriculares/anos/${anoTurma}/regencia/`;

    cy.log(`Endpoint => ${endpoint}`);

    return cy.request({
      method: 'GET',
      url: endpoint,
      headers: {
        accept: 'application/json',
        'X-API-Key': apiKey,
      },
      failOnStatusCode: false,
    })
    .then((res) => {

      cy.log(`STATUS => ${res.status}`);
      cy.log(`BODY => ${JSON.stringify(res.body)}`);

      // VALIDAÇÃO DIRETA
      expect(res.status).to.eq(200);

    });
  }
);

// ======================================================
// THEN
// ======================================================

Then('a API deve responder com sucesso', () => {
  cy.log('Validação executada com sucesso');
});