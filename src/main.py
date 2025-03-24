import logging

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
import os

from api.v1 import films
from core import config
from db import elastic, redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)

    elastic_url = f'http://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'
    elastic.es = AsyncElasticsearch(hosts=[elastic_url])
    index_exists = await elastic.es.indices.exists(index="movies")
    if not index_exists:
        index_mapping = config.ELASTIC_SCHEME['movies']
        logging.debug('Creating index movies in elasticsearch.')
        if await elastic.es.indices.create(index="movies", body=index_mapping):
            elastic_dump_path = os.path.join(config.BASE_DIR, 'db', 'elastic_dump.json')
            await elastic.dump_to_elasticsearch(elastic_dump_path, 'movies')
        else:
            logging.warning('Failed to create index movies in elasticsearch.')


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


# Attach router for films API
app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
