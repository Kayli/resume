import Fastify from 'fastify'
import cors from '@fastify/cors'

const fastify = Fastify({ logger: true })

fastify.get('/api/hello', async (request, reply) => {
  return { message: 'Hello from Fastify' }
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
