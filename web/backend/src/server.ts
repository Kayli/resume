import Fastify from 'fastify'
import cors from '@fastify/cors'
import fastifyStatic from '@fastify/static'
import fs from 'fs/promises'
import path from 'path'
import yaml from 'js-yaml'

const fastify = Fastify({ logger: true })

// register CORS inside start() to avoid top-level await in ESM graph
// and register static assets for the frontend (built with Vite -> `dist`).
const start = async () => {
  try {
    await fastify.register(cors, { origin: true })

    // Serve built frontend static files if present. Frontend build output
    // is at web/frontend/dist relative to project root. In dev mode the
    // Vite dev server serves assets, so skip registering static files
    // when the `dist` directory doesn't exist to avoid startup failure.
    const frontendDist = path.resolve(__dirname, '../../..', 'web', 'frontend', 'dist')
    try {
      await fs.access(frontendDist)
      await fastify.register(fastifyStatic, {
        root: frontendDist,
        prefix: '/',
        index: false
      })
      fastify.log.info(`Serving frontend static files from ${frontendDist}`)
    } catch (err) {
      fastify.log.info(`Frontend dist not found at ${frontendDist}, skipping static registration`)
    }

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

    // SPA fallback: for any non-API GET request that wasn't handled by static files,
    // return index.html so client-side routing works.
    fastify.setNotFoundHandler(async (request, reply) => {
      // If the path looks like an API route, return 404 JSON
      if (request.url && request.url.startsWith('/api/')) {
        reply.code(404).send({ error: 'Not found' })
        return
      }

      try {
        // send index.html from the frontend dist
        const indexPath = path.join(frontendDist, 'index.html')
        const index = await fs.readFile(indexPath, 'utf8')
        reply.type('text/html').send(index)
      } catch (err) {
        // If index.html not found, return 404
        reply.code(404).send({ error: 'Not found' })
      }
    })

    const port = Number(process.env.PORT_BACKEND) || 5000
    const host = process.env.HOST_BACKEND || '0.0.0.0'
    await fastify.listen({ port, host })
  } catch (err) {
    fastify.log.error(err)
    process.exit(1)
  }
}

start()
