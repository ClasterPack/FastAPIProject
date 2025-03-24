import json
from typing import Optional
from elasticsearch import AsyncElasticsearch, helpers, logger

es: Optional[AsyncElasticsearch] = None

async def get_elastic() -> AsyncElasticsearch:
    return es

async def dump_to_elasticsearch(input_file: str, index_name: str):

    elastic = await get_elastic()

    with open(input_file, 'r') as f:
        documents = json.load(f)

    actions = []
    for doc in documents:
        action = {
            "_op_type": "index",
            "_index": index_name,
            "_id": doc["_id"],
            "_source": doc["_source"]
        }
        actions.append(action)

    success, failed = await helpers.async_bulk(elastic, actions)
    logger.info(f"Successfully indexed {success} documents.")
    if failed:
        logger.warn(f"Failed to index {failed} documents.")
    await elastic.close()

