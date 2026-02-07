import Fastify from 'fastify'
import cors from '@fastify/cors'
import fs from 'fs/promises'
import path from 'path'
import yaml from 'js-yaml'

const fastify = Fastify({ logger: true })

fastify.get('/api/hello', async (request, reply) => {
  return { message: 'Hello from Fastify' }
})

fastify.get('/api/resume', async (request, reply) => {
  try {
    const resumePath = path.resolve(__dirname, '../../..', 'data/resume.yaml')
    const raw = await fs.readFile(resumePath, 'utf8')
    const data = yaml.load(raw)
    return data
  } catch (err) {
    fastify.log.error(err)
    reply.code(500).send({ error: 'Failed to load resume' })
  }
})

const start = async () => {
  try {
    // register CORS inside start() to avoid top-level await in ESM graph
    await fastify.register(cors, { origin: true })
    const port = Number(process.env.PORT_BACKEND) || 5000
    const host = process.env.HOST_BACKEND || '0.0.0.0'
    await fastify.listen({ port, host })
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}

start()
