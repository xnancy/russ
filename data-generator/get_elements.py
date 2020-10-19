from os import listdir
from os.path import isfile, join
import gzip
import shutil


onlyfiles = [f for f in listdir("/content/drive/My Drive/SiteBotCS294W/phrasenode/data/phrase-node-dataset/infos/v6/")]
# print(onlyfiles)
for name in onlyfiles:
  if name != 'info-salesforce.com.gz':
    print(name)
    unz = "/content/drive/My Drive/SiteBotCS294W/phrasenode/data/phrase-node-dataset/infos/v6/" + name
    pathToSave = "/content/drive/My Drive/SiteBotCS294W/phrasenode/data/phrase-node-dataset/infos/unzipped/" + name.split(".gz")[0] + ".json"
    f = gzip.open(unz, 'rb')
    with open(pathToSave, 'wb') as f_out:
        shutil.copyfileobj(f, f_out)
