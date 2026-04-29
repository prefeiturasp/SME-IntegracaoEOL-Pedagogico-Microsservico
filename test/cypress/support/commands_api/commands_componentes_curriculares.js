Cypress.Commands.add('getComponentesCurriculares', () => {
  return cy.request({
    method: 'GET',
    url: `${Cypress.env('API_URL')}/api/v1/componentes-curriculares/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': Cypress.env('API_KEY'),
    },
    failOnStatusCode: false,
  });
});