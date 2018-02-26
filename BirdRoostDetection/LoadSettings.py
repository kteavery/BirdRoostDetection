import json
from pprint import pprint

data = json.load(open('settings.json'))

WORKING_DIRECTORY = str(data["cwd"])
LABEL_CSV = str(data["label_csv"])
ML_SPLITS_DATA= str(data["ml_splits_csv"])

print WORKING_DIRECTORY, LABEL_CSV, ML_SPLITS_DATA