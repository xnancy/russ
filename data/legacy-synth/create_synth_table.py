import json
import psycopg2
from os import listdir
from os.path import isfile, join
from synth_generator import run_create_template

from multiprocessing import Pool


def create_element_table(fileName):
  # name = fileName.split("_DOT_json")[0] + "_elements"
  create_table = "CREATE TABLE " + fileName + "(styles json, xid integer, height integer, width integer, topcoord integer, hidden boolean, children integer[], ref integer, toplevel boolean, classes text, tag text, html_id text, innertext text, leftcoord integer, attributes json, id_website integer, id SERIAL PRIMARY KEY, image_text text, website text, FOREIGN KEY(id_website) REFERENCES websites(id))"

  con = psycopg2.connect(user="lxcgasgqutnxqf",
                                          password="4e136676c0b826659e6b00bd1e5fac2bce004d853d324b2083638cd71c321d43",
                                          host="ec2-54-156-53-71.compute-1.amazonaws.com",
                                          port="5432",
                                          database="d3nialk4215ojk")
  cur = con.cursor()
  cur.execute(create_table)
  cur.close()
          # commit the changes
  con.commit()
  con.close()


def addToTable(row):
  sql = "INSERT INTO " + n + "(styles, xid, height, width, topcoord, hidden, children, ref, toplevel, classes, tag, html_id, innertext, leftcoord, attributes, id_website) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
  conn = psycopg2.connect(
    host="ec2-54-156-53-71.compute-1.amazonaws.com",
    user="lxcgasgqutnxqf",
    password="4e136676c0b826659e6b00bd1e5fac2bce004d853d324b2083638cd71c321d43",
    database="d3nialk4215ojk",
    port="5432"
  )
  cur = conn.cursor()
  cur.execute(sql, (row))
  element_id = cur.fetchone()[0]
  print(element_id)
  conn.commit()
  cur.close()
  conn.close()


onlyfiles = [f for f in listdir("/content/drive/My Drive/SiteBotCS294W/phrasenode/data/phrase-node-dataset/infos/") if ("unzipped" in f and f != "unzipped")]

files=[onlyfiles[100]]
print(files)
tables = []
for name in files:
  n = name.split("unzippedinfo-")[1].replace(".", "_DOT_").split("_DOT_json")[0] + "_elements"
  tables.append(n)
  create_element_table(n)
  path = '/content/drive/My Drive/SiteBotCS294W/phrasenode/data/phrase-node-dataset/infos/' + name
  with open(path) as f:
    a = json.load(f)
  commands = []
  for elem in a['info']:
    r = elem
    if 'xid' in r:
      html_id = r['id'] if r['id'] != None else "None"
      html_text = r['text'] if 'text' in r  else "None"
      row = (json.dumps(r['styles']), r['xid'], r['height'], r['width'], r['top'], r['hidden'], r['children'], r['ref'], r['topLevel'], r['classes'], r['tag'], html_id, html_text, r['left'], json.dumps(r['attributes']), 1)
      commands.append(row)

  with Pool(processes=10) as pool:
    pool.map(addToTable, commands)


for t in tables:
  run_create_template(t, "info-" + t.replace("_DOT_", ".").split("_elements")[0])
