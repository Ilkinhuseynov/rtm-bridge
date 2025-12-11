from fastapi import FastAPI
from pydantic import BaseModel
import requests
import hashlib

API_KEY = "3c8b29815e12719e6600694a4b28b086"
AUTH_TOKEN = "1fd24f75990fe6a91f9d179c8634794f587fbcb9"
SHARED_SECRET = "d93ce45f21035c1d"
RTM_URL = "https://api.rememberthemilk.com/services/rest/"

app = FastAPI()

class TasksPayload(BaseModel):
    tasks: list[str]

def make_sig(params: dict) -> str:
    base = SHARED_SECRET + "".join(f"{k}{v}" for k, v in sorted(params.items()))
    return hashlib.md5(base.encode()).hexdigest()

def create_timeline() -> str:
    params = {
        "method": "rtm.timelines.create",
        "api_key": API_KEY,
        "auth_token": AUTH_TOKEN,
        "format": "json",
    }
    params["api_sig"] = make_sig(params)
    rsp = requests.get(RTM_URL, params=params).json()["rsp"]
    if rsp["stat"] != "ok":
        raise RuntimeError(f"Timeline error: {rsp}")
    return rsp["timeline"]

def add_single_task(name: str) -> dict:
    name = name.strip()
    if not name:
        return {"name": name, "skipped": True}

    timeline = create_timeline()
    params = {
        "method": "rtm.tasks.add",
        "api_key": API_KEY,
        "auth_token": AUTH_TOKEN,
        "timeline": timeline,
        "name": name,
        "format": "json",
    }
    params["api_sig"] = make_sig(params)
    rsp = requests.get(RTM_URL, params=params).json()["rsp"]
    return {"name": name, "rsp": rsp}

@app.post("/rtm/add_tasks")
def add_tasks(payload: TasksPayload):
    results = []
    for t in payload.tasks:
        results.append(add_single_task(t))
    return {"results": results}

