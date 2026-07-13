import { Given, When, Then } from "cypress-cucumber-preprocessor/steps";

let response;

function getEnvOrFail(key) {
  const value = Cypress.env(key);

  expect(value, `Variável de ambiente ${key} não definida`).to.exist;
  expect(value, `${key} está undefined`).to.not.be.undefined;
  expect(value.toString(), `${key} está vazio`).to.not.be.empty;

  return value;
}

// =========================
// TURMAS REGULARES
// =========================

Given("que possuo acesso à API de turmas regulares", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("UE_CODIGO");
  getEnvOrFail("ANO_LETIVO");
  getEnvOrFail("MODALIDADE");
});

When("envio uma requisição POST para listar turmas regulares", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const ue = getEnvOrFail("UE_CODIGO");
  const anoLetivo = getEnvOrFail("ANO_LETIVO");
  const modalidade = getEnvOrFail("MODALIDADE");

  return cy
    .request({
      method: "POST",
      url: `${apiUrl}/api/v1/pedagogico/turmas/turmas-regulares/`,
      headers: {
        accept: "application/json",
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: {
        ue_codigo: ue,
        ano_letivo: Number(anoLetivo),
        modalidade_codigo: Number(modalidade),
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de turmas regulares", () => {
  expect(response.body).to.be.an("array");
});

When(
  "envio uma requisição POST para listar turmas regulares sem autenticação",
  () => {
    const apiUrl = getEnvOrFail("API_URL");
    const ue = getEnvOrFail("UE_CODIGO");
    const anoLetivo = getEnvOrFail("ANO_LETIVO");
    const modalidade = getEnvOrFail("MODALIDADE");

    return cy
      .request({
        method: "POST",
        url: `${apiUrl}/api/v1/pedagogico/turmas/turmas-regulares/`,
        headers: {
          accept: "application/json",
          "Content-Type": "application/json",
        },
        body: {
          ue_codigo: ue,
          ano_letivo: Number(anoLetivo),
          modalidade_codigo: Number(modalidade),
        },
        failOnStatusCode: false,
      })
      .then((res) => {
        response = res;
      });
  },
);

// =========================
// TURMAS PROGRAMA (POST)
// =========================

Given("que possuo acesso à API de turmas programa via POST", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("UE_CODIGO");
  getEnvOrFail("ANO_LETIVO");
  getEnvOrFail("MODALIDADE");
});

When("envio uma requisição POST para listar turmas programa", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const ue = getEnvOrFail("UE_CODIGO");
  const anoLetivo = getEnvOrFail("ANO_LETIVO");
  const modalidade = getEnvOrFail("MODALIDADE");

  return cy
    .request({
      method: "POST",
      url: `${apiUrl}/api/v1/pedagogico/turmas/turmas-programa/`,
      headers: {
        accept: "application/json",
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: {
        ue_codigo: ue,
        ano_letivo: Number(anoLetivo),
        modalidade_codigo: Number(modalidade),
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de turmas programa", () => {
  expect(response.body).to.be.an("array");
});

// =========================
// LISTAR TURMAS (POST)
// =========================

Given("que possuo acesso à API de listar turmas", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("TURMA_CODIGO");
});

When("envio uma requisição POST para listar turmas", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const turma = getEnvOrFail("TURMA_CODIGO");

  return cy
    .request({
      method: "POST",
      url: `${apiUrl}/api/v1/pedagogico/turmas/listar-turmas/`,
      headers: {
        accept: "application/json",
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
      },
      body: [Number(turma)],
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de turmas", () => {
  expect(response.body).to.be.an("array");
});

// =========================
// DADOS DE TURMA (GET)
// =========================

Given("que possuo acesso à API de dados de turma", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("TURMA_CODIGO");
});

When("envio uma requisição GET para consultar dados da turma", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const turma = getEnvOrFail("TURMA_CODIGO");

  return cy
    .request({
      method: "GET",
      url: `${apiUrl}/api/v1/pedagogico/turmas/${turma}/dados/`,
      headers: {
        accept: "application/json",
        "X-API-Key": apiKey,
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve conter dados da turma", () => {
  expect(response.body).to.be.an("object");
  expect(response.body).to.not.be.empty;
});

When(
  "envio uma requisição GET para consultar dados de uma turma inexistente",
  () => {
    const apiUrl = getEnvOrFail("API_URL");
    const apiKey = getEnvOrFail("API_KEY");

    return cy
      .request({
        method: "GET",
        url: `${apiUrl}/api/v1/pedagogico/turmas/0/dados/`,
        headers: {
          accept: "application/json",
          "X-API-Key": apiKey,
        },
        failOnStatusCode: false,
      })
      .then((res) => {
        response = res;
      });
  },
);

// =========================
// SINCRONIZAÇÕES INSTITUCIONAIS
// =========================

Given(
  "que possuo acesso à API de sincronizações institucionais de turma",
  () => {
    getEnvOrFail("API_URL");
    getEnvOrFail("API_KEY");
    getEnvOrFail("UE_CODIGO");
    getEnvOrFail("TURMA_CODIGO");
  },
);

When("envio uma requisição GET para listar sincronizações da turma", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const ue = getEnvOrFail("UE_CODIGO");
  const turma = getEnvOrFail("TURMA_CODIGO");

  return cy
    .request({
      method: "GET",
      url: `${apiUrl}/api/v1/pedagogico/turmas/ues/${ue}/turmas/${turma}/sincronizacoes-institucionais/`,
      headers: {
        accept: "application/json",
        "X-API-Key": apiKey,
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de sincronizações", () => {
  expect(response.body).to.be.an("array");
});

Then("a resposta de sincronizações deve ser válida", () => {
  expect(response).to.exist;
  expect([200, 404]).to.include(response.status);
  if (response.status === 200) {
    expect(response.body).not.be.empty;
  }
});

// =========================
// ANOS LETIVOS DA UE
// =========================

Given("que possuo acesso à API de anos letivos da UE", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("UE_CODIGO");
});

When("envio uma requisição GET para listar anos letivos da UE", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");
  const ue = getEnvOrFail("UE_CODIGO");

  return cy
    .request({
      method: "GET",
      url: `${apiUrl}/api/v1/pedagogico/turmas/ue/${ue}/sincronizacoes-institucionais/anos-letivos/`,
      headers: {
        accept: "application/json",
        "X-API-Key": apiKey,
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de anos letivos", () => {
  expect(response.body).to.be.an("array");
});

// =========================
// TURMAS HISTÓRICAS DO PROFESSOR
// =========================

Given("que possuo acesso à API de turmas históricas do professor", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
  getEnvOrFail("ANO_LETIVO");
  getEnvOrFail("LOGIN_FUNCIONARIO");
});

When(
  "envio uma requisição GET para listar turmas históricas do professor",
  () => {
    const apiUrl = getEnvOrFail("API_URL");
    const apiKey = getEnvOrFail("API_KEY");
    const anoLetivo = getEnvOrFail("ANO_LETIVO");
    const professor = getEnvOrFail("LOGIN_FUNCIONARIO");

    return cy
      .request({
        method: "GET",
        url: `${apiUrl}/api/v1/pedagogico/turmas/anos-letivos/${anoLetivo}/professor/${professor}/turmas-historicas-geral/`,
        headers: {
          accept: "application/json",
          "X-API-Key": apiKey,
        },
        failOnStatusCode: false,
      })
      .then((res) => {
        response = res;
      });
  },
);

Then("o retorno deve ser uma lista de turmas históricas", () => {
  expect(response.body).to.be.an("array");
});

// =========================
// ITINERÁRIO DO ENSINO MÉDIO
// =========================

Given("que possuo acesso à API de itinerário do ensino médio", () => {
  getEnvOrFail("API_URL");
  getEnvOrFail("API_KEY");
});

When("envio uma requisição GET para listar itinerário do ensino médio", () => {
  const apiUrl = getEnvOrFail("API_URL");
  const apiKey = getEnvOrFail("API_KEY");

  return cy
    .request({
      method: "GET",
      url: `${apiUrl}/api/v1/pedagogico/turmas/itinerario/ensino-medio/`,
      headers: {
        accept: "application/json",
        "X-API-Key": apiKey,
      },
      failOnStatusCode: false,
    })
    .then((res) => {
      response = res;
    });
});

Then("o retorno deve ser uma lista de itinerários", () => {
  expect(response.body).to.be.an("array");
});

// =========================
// STATUS
// =========================

Then("o status da resposta de turmas deve ser 200", () => {
  expect(response).to.exist;
  expect(response.status).to.eq(200);
});

Then("o status da resposta de turmas deve ser 404", () => {
  expect(response).to.exist;
  expect(response.status).to.eq(404);
});

Then("o status da resposta de turmas deve ser 401 ou 403", () => {
  expect(response).to.exist;
  expect([401, 403]).to.include(response.status);
});
