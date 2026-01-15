from grobid_client.grobid_client import GrobidClient

client = GrobidClient(config_path="./config.json")

client.process(
    "processFulltextDocument",
    ".",                    # Input directory
    output="./output",       # Where to save results
    n=10,                   # Number of parallel requests
)
