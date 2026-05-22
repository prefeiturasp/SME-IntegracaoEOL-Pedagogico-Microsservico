import { Given, When, Then } from 'cypress-cucumber-preprocessor/steps'

let response

function getEnvOrFail(key) {
  const value = Cypress.env(key)

  expect(value, `Variável de ambiente ${key} não definida`).to.exist
  expect(value, `${key} está undefined`).to.not.be.undefined
  expect(value.toString(), `${key} está vazio`).to.not.be.empty

  return value
}

// =========================
// GIVEN (AJUSTADO PARA BATER COM O FEATURE)
// =========================
Given('que possuo acesso à API de validação PAP', () => {
  getEnvOrFail('API_URL_NOVA')
  getEnvOrFail('API_KEY_NOVA')
  getEnvOrFail('TURMA_PAP_CODIGO')
  getEnvOrFail('LOGIN_FUNCIONARIO')
  getEnvOrFail('ID_PERFIL')
})

// =========================
// WHEN
// =========================
When('envio uma requisição GET para validar componente PAP', () => {
  const apiUrl = getEnvOrFail('API_URL_NOVA')
  const apiKey = getEnvOrFail('API_KEY_NOVA')

  const turma = getEnvOrFail('TURMA_PAP_CODIGO')
  const login = getEnvOrFail('LOGIN_FUNCIONARIO')
  const perfil = getEnvOrFail('ID_PERFIL')

  cy.request({
    method: 'GET',
    url: `${apiUrl}/api/v1/componentes-curriculares/turmas/${turma}/funcionarios/${login}/perfis/${perfil}/validar/pap/`,
    headers: {
      accept: 'application/json',
      'X-API-Key': apiKey,
    },
    failOnStatusCode: false,
  }).then((res) => {
    response = res
  })
})

// =========================
// THEN
// =========================
Then('a API de PAP deve responder com sucesso', () => {
  expect(response).to.exist
  expect(response.status).to.eq(200)
})

Then('o retorno da validação PAP deve ser booleano', () => {
  expect(response.body).to.be.a('boolean')
})