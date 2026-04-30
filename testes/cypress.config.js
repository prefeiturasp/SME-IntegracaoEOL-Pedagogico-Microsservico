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
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  database: process.env.DB_DATABASE,
}

const envKeys = [
  'USUARIO_HOMOL_ADMIN',
  'USUARIO_HOMOL_EXTERNO',
  'SENHA_HOMOL',
  'API_KEY',
  'API_URL',
  'FUNCIONARIO_CODIGO',
  'TURMA_CODIGO',
  'TURMA_PAP_CODIGO',
  'LOGIN_FUNCIONARIO',
  'TURMA_SEM_ATRIBUICAO',
  'DATA_BASE',
  'ANO_LETIVO',
  'COMPONENTE_CURRICULAR',
  'UE_CODIGO',
  'MODALIDADE',
  'ANO_LETIVO_GRADE',
  'ANO_ESCOLAR',
  'UE_TURMAS_CODIGO',
]

export default defineConfig({
  e2e: {
    watchForFileChanges: true,

    supportFile: 'cypress/support/e2e.js',

    viewportWidth: 1920,
    viewportHeight: 1080,
    video: false,

    retries: { runMode: 2, openMode: 0 },

    screenshotOnRunFailure: false,
    chromeWebSecurity: false,
    experimentalRunAllSpecs: true,
    failOnStatusCode: false,

    specPattern: ['cypress/e2e/**/*.feature'],

    defaultCommandTimeout: 60000,
    requestTimeout: 60000,
    execTimeout: 60000,
    pageLoadTimeout: 60000,


    env: {
      allure: true,
    },

    async setupNodeEvents(on, config) {
      
      allureWriter(on, config)

      
      config.env.allure = true

      
      const webpackConfig = {
        module: {
          rules: [
            {
              test: /\.js$/,
              exclude: [/node_modules/],
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

      // ✅ Banco
      const pool = new pg.Pool(dbConfig)
      const dbTasks = postgreSQL.loadDBPlugin(pool)

      on('task', {
        ...dbTasks,

        async uploadFile({ method = 'POST', url, headers = {}, filePath }) {
          const form = new FormData()

          if (filePath && filePath.trim() !== '') {
            form.append('file', fs.createReadStream(filePath))
          }

          const response = await axios({
            method,
            url,
            headers: { ...headers, ...form.getHeaders() },
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

      
      const customVariable = Object.fromEntries(
        envKeys.map((key) => [key, process.env[key] ?? ''])
      )

      config.env = {
        ...config.env,
        ...customVariable,
        db: dbConfig,
      }

      return await cloudPlugin(on, config)
    },
  },
})