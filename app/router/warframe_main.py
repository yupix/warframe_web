import asyncio
import json
import os
import re

import requests
from fastapi import APIRouter, Request

from app import templates

router = APIRouter()


async def get_news():
    r = requests.get('https://api.warframestat.us/pc/news')
    result_json = r.json()
    return result_json


async def check_fissure_star_image(star_name):
    base_url = 'https://s3.akarinext.org/assets/*/warframe_site/map/'
    star_name = star_name.replace(' ', '_')
    star_list = {'Uranus': 'Uranus.jpg', 'Mars': 'Mars.jpg', 'Void': 'Void.jpg', 'Kuva_Fortress': 'Kuva_Fortress.jpg', 'Eris': 'Elis.jpg', 'Venus': 'Venus.jpg', 'Mercury': 'Mercury.jpg',
                 'Phobos': 'Phobos.jpg', 'Ceres': 'Ceres.jpg', 'Europa': 'Europa.jpg', 'Jupiter': 'Jupiter.jpg', 'Sedna': 'Sedna.jpg', 'Saturn': 'Saturn.jpg', 'Earth': 'Earth.jpg',
                 'Deimos': 'Deimos.jpg', 'Pluto': 'Pluto.jpg', 'Neptune': 'Phobos.jpg'}
    if star_list.get(f'{star_name}', None):
        star_image = f"{base_url}{star_list.get(f'{star_name}')}"
    else:
        star_image = None
    return star_image


async def replace_word(text: str) -> str:
    word_list = {'Relay': 'リレー'}
    for word in word_list.keys():
        if word in text:
            hit_word = word_list.get(word)
            text = text.replace(word, hit_word)
    return text

async def change_language(normal_star_name, star_name):
    _star_name = star_name
    star_name = star_name.replace(' ', '_')
    star_list = {'Uranus': '天王星', 'Mars': '火星', 'Void': 'Void', 'Kuva_Fortress': 'KUVA 要塞', 'Eris': '準惑星エリス', 'Venus': '金星', 'Mercury': '水星',
                 'Phobos': 'フォボス', 'Ceres': '準惑星ケレス', 'Europa': '衛星エウロパ', 'Jupiter': '木星', 'Sedna': '小惑星セドナ', 'Saturn': '土星', 'Earth': '地球',
                 'Deimos': 'ダイモス', 'Pluto': '冥王星', 'Neptune': '海王星'}

    if star_list.get(f'{star_name}'):
        star_name = normal_star_name.replace(_star_name, star_list.get(f'{star_name}'))
    else:
        star_name = _star_name
    return star_name


async def change_team_name_language(team_name):
    _team_name = team_name
    team_name = team_name.replace(' ', '_')
    team_list = {'Infested': '感染体', 'Corpus': 'コーパス', 'Grineer': 'グリニア'}

    if team_list.get(f'{team_name}'):
        star_name = team_name.replace(_team_name, team_list.get(f'{team_name}'))
    else:
        star_name = _team_name
    return star_name


async def change_team_mission_desc_language(mission_name):
    _mission_name = mission_name
    mission_type = mission_name.replace(' ', '_')
    mission_list = {'Infested_Outbreak': '感染拡大', 'Phorid_Manifestation': 'PHORID 出現', 'Grineer_Offensive': 'グリニア、侵攻', 'Corpus_Siege': 'コーパス、進撃'}
    if mission_list.get(f'{mission_type}'):
        mission_name = mission_list.get(f'{mission_type}')
    else:
        mission_name = _mission_name
    return mission_name


async def get_start_name(result_json: json, mode: str = None):
    if mode != 'baro':
        for i, fissure in enumerate(result_json):
            star_name = str(re.findall("(?<=\().+?(?=\))", fissure['node'])).replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('\'', '')
            star_node = re.sub("\(.+?\)", "", fissure['node'])
            star_image = await check_fissure_star_image(star_name)
            result_json[i]['star_name_only'] = star_name
            star_name = await change_language(fissure['node'], star_name)
            result_json[i]['star_image'] = star_image
            result_json[i]['star_name'] = star_name
            result_json[i]['star_node'] = star_node
    else:
        star_name = str(re.findall("(?<=\().+?(?=\))", result_json['location'])).replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('\'', '')
        star_node = await replace_word(re.sub("\(.+?\)", "", result_json['location']))
        star_image = await check_fissure_star_image(star_name)
        result_json['star_name_only'] = await change_language(star_name, star_name)
        star_name = await change_language(result_json['location'], star_name)
        result_json['star_image'] = star_image
        result_json['star_name'] = star_name
        result_json['star_node'] = star_node

    return result_json


async def check_team(team_name):
    base_url = 'https://s3.akarinext.org/assets/*/warframe_site/team/'
    team_name = team_name.replace(' ', '_')
    team_list = {'Corpus': 'Corpus.svg', 'Grineer': 'Grineer_logo.svg', 'Infested': 'infested.svg'}
    if team_list.get(f'{team_name}', None):
        team_image = f"{base_url}{team_list.get(f'{team_name}')}"
    else:
        team_image = None
    return team_image


async def check_team_reward(attacker_reward, defender_reward, reward_list):
    if attacker_reward not in reward_list:
        reward_list.append(f'{attacker_reward}')

    if defender_reward not in reward_list:
        reward_list.append(f'{defender_reward}')

    return reward_list


async def invasions_team(result_json):
    reward_list = []
    for i, invasion in enumerate(result_json):
        if len(invasion['attackerReward']['asString']) == 0:
            result_json[i]['attackerReward']['asString'] = 'クレジット'
        if len(invasion['defenderReward']['asString']) == 0:
            result_json[i]['defenderReward']['asString'] = 'クレジット'
        defending_team_image = await check_team(invasion['defendingFaction'])
        attacking_team_image = await check_team(invasion['attackingFaction'])
        defending_team_ja = await change_team_name_language(invasion['defendingFaction'])
        attacking_team_ja = await change_team_name_language(invasion['attackingFaction'])
        reward_list = await check_team_reward(invasion['attackerReward']['asString'], invasion['defenderReward']['asString'], reward_list)
        mission_desc = await change_team_mission_desc_language(invasion['desc'])

        result_json[i]['mission_desc'] = mission_desc
        result_json[i]['defending_team_image'] = defending_team_image
        result_json[i]['attacking_team_image'] = attacking_team_image
        result_json[i]['defending_team_ja'] = defending_team_ja
        result_json[i]['attacking_team_ja'] = attacking_team_ja
    return result_json, reward_list


async def get_fissures():
    r = requests.get('https://api.warframestat.us/pc/fissures')
    result_json = await get_start_name(r.json())
    return result_json


async def item_image(result_json):
    r = requests.get('https://s3.akarinext.org/assets/*/warframe_site/data/json/All.json')
    for i, item in enumerate(result_json['inventory']):
        for item_list in r.json():
            if item['item'].replace(' ', '') in item_list['uniqueName']:
                print('hit')
                result_json['inventory'][i]['image_link'] = f'https://cdn.warframestat.us/img/{item_list["imageName"]}'
                break
            elif item['item'] in item_list['name']:
                print('hit')
                result_json['inventory'][i]['image_link'] = f'https://cdn.warframestat.us/img/{item_list["imageName"]}'
                break
    return result_json


async def void_trader():
    if os.path.exists('./tmp/void_trader.json'):
        with open('./tmp/void_trader.json', encoding='utf-8') as f:
            result_json = json.load(f)
    else:
        r = requests.get('https://api.warframestat.us/pc/voidTrader')
        result_json = r.json()
        time = result_json['activation'].split('.')[0].replace('T', '-').split('-')
        next_time = f'{time[0]} / {time[1]}/{time[2]} {time[3]}'
        expiry = result_json['expiry'].split('.')[0].replace('T', '-').split('-')
        expiry_time = f'{expiry[0]} / {expiry[1]}/{expiry[2]} {expiry[3]}'
        result_json['reformat_activation'] = next_time
        result_json['reformat_expiry'] = expiry_time
        result_json = await item_image(result_json)
        result_json = await get_start_name(result_json, mode='baro')
        with open('./tmp/void_trader.json', mode='wt', encoding='utf-8') as file:
            json.dump(result_json, file, ensure_ascii=False, indent=2)

    return result_json


async def get_invasions():
    r = requests.get('https://api.warframestat.us/pc/invasions')
    result_json = await get_start_name(r.json())
    result_json, reward_list = await invasions_team(result_json)
    return result_json, reward_list


@router.get('/')
async def index(request: Request):
    print(await replace_word('Strata Relay'))
    news_json = await get_news()
    fissures_json = await get_fissures()
    trader = await void_trader()
    return templates.TemplateResponse(
        "index.html", {"request": request, "news_json": news_json, "fissures_json": fissures_json, "void_trader": trader}
    )


@router.get('/fissures')
async def fissures(request: Request):
    fissures_json = await get_fissures()
    return templates.TemplateResponse(
        "fissures/index.html", {"request": request, "fissures_json": fissures_json}
    )


@router.get('/invasions')
async def invasions(request: Request):
    invasions_json, reward_list = await get_invasions()
    return templates.TemplateResponse(
        "invasions/index.html", {"request": request, "invasions_json": invasions_json, "reward_list": reward_list}
    )
