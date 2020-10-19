import psycopg2
import pandas as pd
import json
from template import Templates
# **dict as arg used similarly as dict as arg except ** will pass values not reference

class Element:
    def __init__(self, row):
        self.website= ''
        self.styles = row[0]
        self.xid = row[1]
        self.height = row[2]
        self.width = row[3]
        self.topcoord = row[4]
        self.hidden = row[5]
        self.children = row[6]
        self.ref = row[7]
        self.toplevel = row[8]
        self.classes = row[9]
        self.tag = row[10]
        self.html_id = row[11]
        self.innertext = row[12]
        self.leftcoord = row[13]
        self.attributes = row[14]
        self.id_website = row[15]
        # self.image_text = row['image_text']


def get_db_rows(query: str):
    try:
        connection = psycopg2.connect(user="lxcgasgqutnxqf",
                                        password="4e136676c0b826659e6b00bd1e5fac2bce004d853d324b2083638cd71c321d43",
                                        host="ec2-54-156-53-71.compute-1.amazonaws.com",
                                        port="5432",
                                        database="d3nialk4215ojk")
        cursor = connection.cursor()

        print("Selecting rows from mobile table using cursor.fetchall")
        records = pd.read_sql_query(query, connection)

        return records

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def run_create_template(web, records):
  for i in range(len(records)):
      element = Element(records[i])
      element.website = web
      path = "../../synthetic_elements/" + web + "_synth.text"
      Templates.generate_text_match(element, path)
