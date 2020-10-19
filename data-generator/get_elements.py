from os import listdir
from os.path import isfile, join
import gzip
import shutil
import json
from create_synthetic_data_local import extract_elements
from synth_generator import run_create_template
from tqdm import tqdm

def get_jsons():
  onlyfiles = [f for f in listdir("../../v6/")]
  print(len(onlyfiles))
  for name in tqdm(onlyfiles):
    unz = "../../v6/" + name
    pathToSave = "../../" + name.split(".gz")[0] + ".json"
    f = gzip.open(unz, 'rb')
    a = json.load(f)
    commands = extract_elements(a)
    del a
    run_create_template(name.split(".gz")[0], commands)

get_jsons()