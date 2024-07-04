import configparser
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from uvicorn import run
from typing import Optional

app = FastAPI()
config = configparser.ConfigParser()
config.read('/config/config.properties')

MONGO_URI = config.get('DatabaseSection', 'mongo.uri')
client = AsyncIOMotorClient(MONGO_URI)

db = client['test']
collection = db['facts']


def get_timestamp(date_string: Optional[str]) -> int:
    if not date_string:
        return 0
    return int(datetime.strptime(date_string, '%Y-%m-%d').timestamp() * 1000)


@app.get("/facts")
async def get_facts(start: Optional[str] = None, end: Optional[str] = None):
    query = {}
    try:
        MIN_START_TIMESTAMP = int((datetime.now() - timedelta(days=3)).timestamp() * 1000)
        query["timestamp"] = {"$gte": max(MIN_START_TIMESTAMP, get_timestamp(start))}
        if end:
            query["timestamp"].update({"$lt": get_timestamp(end)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    facts = []
    async for fact in collection.find(query):
        fact['_id'] = str(fact['_id'])
        facts.append(fact)
    return facts


@app.get("/facts/{id}")
async def get_fact_by_id(id: str):
    fact = await collection.find_one({"id": int(id)})
    if fact:
        fact['_id'] = str(fact['_id'])
        return fact
    else:
        raise HTTPException(status_code=404, detail="Fact not found")
    
if __name__ == "__main__":
    run(app, host="0.0.0.0", port=int(config.get('ServerSection', 'server.port')))
