import os
from grobid_client.grobid_client import GrobidClient
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2] # PaperNavigator/

CONFIG_PATH = BASE_DIR / "config" / "grobid_config.json"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = GrobidClient(config_path=str(CONFIG_PATH))

def grobid_xml_generator(client):
    client.process(
        "processFulltextDocument",
        str(UPLOAD_DIR),
        output=str(OUTPUT_DIR),
        n=1
    )



