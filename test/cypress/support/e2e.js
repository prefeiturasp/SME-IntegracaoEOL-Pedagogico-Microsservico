import '@shelex/cypress-allure-plugin'

// Seus comandos
import './commands_api/commands_componentes_curriculares'

// Evita quebra de teste
Cypress.on('uncaught:exception', () => false)