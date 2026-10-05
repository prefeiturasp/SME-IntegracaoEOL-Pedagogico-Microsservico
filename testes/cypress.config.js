import { defineConfig } from 'cypress'
import allureWriter from '@shelex/cypress-allure-plugin/writer.js'
import { cloudPlugin } from 'cypress-cloud/plugin'
import dotenv from 'dotenv'
import cucumber from 'cypress-cucumber-preprocessor'
import preprocessor from '@cypress/webpack-preprocessor'
import postgreSQL from 'cypress-postgresql'
import pg from 'pg'
import fs from 'fs'
import FormData from 'form-data'
import axios from 'axios'

dotenv.config()

const dbConfig = {
  user: process.env.DB_USER || '',
  password: process.env.DB_PASSWORD || '',
  host: process.env.DB_HOST || '',
  database: process.env.DB_DATABASE || '',
}

const envKeys = [
  'API_URL',
  'API_URL_NOVA',
  'API_KEY',
  'API_KEY_NOVA',
  'FUNCIONARIO_CODIGO',
  'LOGIN_FUNCIONARIO',
  'ID_PERFIL',
  'TURMA_CODIGO',
  'TURMA_PAP_CODIGO',
  'TURMA_SEM_ATRIBUICAO',
  'UE_TURMAS_CODIGO',
  'DATA_BASE',
  'ANO_LETIVO',
  'ANO_LETIVO_GRADE',
  'ANO_ESCOLAR',
  'COMPONENTE_CURRICULAR',
  'MODALIDADE',
  'UE_CODIGO',
]

export default defineConfig({
  e2e: {
    watchForFileChanges: true,
    supportFile: 'cypress/support/e2e.js',

    viewportWidth: 1920,
    viewportHeight: 1080,

    video: false,
    screenshotOnRunFailure: false,
    chromeWebSecurity: false,

    retries: {
      runMode: 2,
      openMode: 0,
    },

    specPattern: ['cypress/e2e/**/*.feature'],

    defaultCommandTimeout: 120000,
    requestTimeout: 120000,
    responseTimeout: 120000,
    pageLoadTimeout: 120000,

    env: {
      allure: true,
    },

    async setupNodeEvents(on, config) {
      allureWriter(on, config)
      config.env.allure = true

      // =========================
      // WEBPACK + CUCUMBER
      // =========================
      const webpackConfig = {
        module: {
          rules: [
            {
              test: /\.js$/,
              exclude: /node_modules/,
              use: {
                loader: 'babel-loader',
                options: {
                  plugins: ['@babel/plugin-transform-modules-commonjs'],
                },
              },
            },
          ],
        },
      }

      on('file:preprocessor', preprocessor({ webpackOptions: webpackConfig }))
      on('file:preprocessor', cucumber.default())

      // =========================
      // DB
      // =========================
      const pool = new pg.Pool(dbConfig)
      const dbTasks = postgreSQL.loadDBPlugin(pool)

      on('task', {
        ...dbTasks,

        async uploadFile({ method = 'POST', url, headers = {}, filePath }) {
          const form = new FormData()

          if (filePath) {
            form.append('file', fs.createReadStream(filePath))
          }

          const response = await axios({
            method,
            url,
            headers: {
              ...headers,
              ...form.getHeaders(),
            },
            data: form,
            maxBodyLength: Infinity,
            validateStatus: () => true,
          })

          return {
            status: response.status,
            body: response.data,
          }
        },
      })

      // =========================
      // ENV SAFE LOAD
      // =========================
      const customVariable = Object.fromEntries(
        envKeys.map((key) => [key, process.env[key] ?? ''])
      )

      config.env = {
        ...config.env,
        ...customVariable,
        db: dbConfig,
      }

      // =========================
      // WARNINGS (NÃO QUEBRA TESTE)
      // =========================
      envKeys.forEach((key) => {
        if (!process.env[key]) {
          console.warn(`⚠️ ENV não definida: ${key}`)
        }
      })

      return await cloudPlugin(on, config)
    },
  },
})