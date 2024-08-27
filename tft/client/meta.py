
from enum import Enum
import requests
import tft.ql.expr as ql
import multiprocessing


class MetaTFTApis(Enum):
    COMPS_DATA = 'comps_data'
    COMP_STATS = 'comp_stats'
    COMP_DETAILS = 'comp_details'
    SET_DATA = 'set_data'
    CHAMP_ITEMS = 'champ_items'

URLS = {
    MetaTFTApis.COMPS_DATA: "https://api2.metatft.com/tft-comps-api/comps_data",
    MetaTFTApis.SET_DATA: "https://data.metatft.com/lookups/TFTSet12_latest_en_us.json",
    MetaTFTApis.CHAMP_ITEMS: "https://api2.metatft.com/tft-stat-api/unit_detail",
    MetaTFTApis.COMP_DETAILS: "https://api2.metatft.com/tft-comps-api/comp_details"
}

CACHE = {}
CHAMP_CACHE = {}
COMP_CACHE = {}

class MetaTFTClient:
    def fetch(self, api: MetaTFTApis) -> dict:
        global CACHE
        global CHAMP_CACHE
        """Fetches given API and returns a dict. Subsequent requests are cached."""
        if api in CACHE:
            return CACHE[api]
        if api == MetaTFTApis.CHAMP_ITEMS:
            champ_ids = ql.query(self.fetch(MetaTFTApis.SET_DATA)).idx('units').filter(ql.idx('traits').len().gt(0)).map(ql.idx('apiName')).eval()
            champ_ids = {champ_id for champ_id in champ_ids if champ_id not in CHAMP_CACHE}
            with multiprocessing.Pool(20) as pool:
                all_champ_data = pool.map(self.fetch_champ, champ_ids)
            for champ_id, champ_data in zip(champ_ids, all_champ_data):
                CHAMP_CACHE[champ_id] = champ_data
            data = CHAMP_CACHE
        elif api == MetaTFTApis.COMP_DETAILS:
            cids = ql.query(self.fetch(MetaTFTApis.COMPS_DATA)).idx('results.data.cluster_details').map(ql.idx('Cluster')).values().eval()
            cids = {str(cid) for cid in cids if cid not in COMP_CACHE}
            with multiprocessing.Pool(20) as pool:
                all_comp_data = pool.map(self.fetch_comp, cids)
            for cid, comp_data in zip(cids, all_comp_data):
                COMP_CACHE[cid] = comp_data
            data = COMP_CACHE
        else:
            data = requests.get(URLS[api]).json()
        CACHE[api] = data
        return data
        
    
    def fetch_champ(self, champ_id: str) -> dict:
        """Fetches champ data for a particular champion."""
        global CHAMP_CACHE
        if champ_id not in CHAMP_CACHE:
            params = {
                "queue": 1100, # Not sure what this does.
                "patch": "current",
                "rank": "CHALLENGER,DIAMOND,GRANDMASTER,MASTER",
                "permit_filter_adjustment": True, # No clue here either.
                "unit": champ_id
            }
            CHAMP_CACHE[champ_id] = requests.get(URLS[MetaTFTApis.CHAMP_ITEMS], params=params).json()
        return CHAMP_CACHE[champ_id]
    
    def fetch_comp(self, cid: str) -> dict:
        global COMP_CACHE
        if cid not in COMP_CACHE:
            params = {
                'comp': cid,
                'cluster_id': 284
            }
            COMP_CACHE[cid] = requests.get(URLS[MetaTFTApis.COMP_DETAILS], params=params).json()
        return COMP_CACHE[cid]

# APIs with caching.

def get_set_data():
    client = MetaTFTClient()
    return client.fetch(MetaTFTApis.SET_DATA)

def get_comp_data():
    client = MetaTFTClient()
    return client.fetch(MetaTFTApis.COMPS_DATA)

def get_champ_item_data(champ_id: str | None = None):
    client = MetaTFTClient()
    if champ_id is None:
        return client.fetch(MetaTFTApis.CHAMP_ITEMS)
    else:
        return {champ_id: client.fetch_champ(champ_id)}

def get_comp_details(cid: str | int | None = None):
    client = MetaTFTClient()
    if cid is None:
        return client.fetch(MetaTFTApis.COMP_DETAILS)
    else:
        return {str(cid): client.fetch_comp(str(cid))}