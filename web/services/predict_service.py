import requests
from typing import List, Dict, Any
from web.core.config import settings


INFERENCE_URL = settings.INFERENCE_URL  # e.g. http://ml:9000


def get_attributes() -> List[str]:
    res = requests.get(f"{INFERENCE_URL}/attributes")
    res.raise_for_status()
    return res.json()


def predict(instances: List[Dict[str, Any]]) -> List[float]:
    payload = {"instances": instances}

    res = requests.post(
        f"{INFERENCE_URL}/invocations",
        json=payload,
    )
    res.raise_for_status()

    return res.json().get("predictions", [])