import asyncio
import json

from fastapi import APIRouter
import requests

router = APIRouter()

@router.get('/api/news')
async def news():
    r = requests.get('https://api.warframestat.us/pc/news')
    result_json = r.json()
    return result_json

