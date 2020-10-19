import psycopg2
import pandas as pd
import json
from template import Templates
# **dict as arg used similarly as dict as arg except ** will pass values not reference

class Element:
    def __init__(self, row):
        self.website= ''
        self.styles = row['styles']
        self.xid = row['xid']
        self.height = row['height']
        self.width = row['width']
        self.topcoord = row['topcoord']
        self.hidden = row['hidden']
        self.children = row['children']
        self.ref = row['ref']
        self.toplevel = row['toplevel']
        self.classes = row['classes']
        self.tag = row['tag']
        self.html_id = row['html_id']
        self.innertext = row['innertext']
        self.leftcoord = row['leftcoord']
        self.attributes = row['attributes']
        self.id_website = row['id_website']
        self.image_text = row['image_text']


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


def run_create_template(name, web):
  query = "select * from " + name + "  where hidden = FALSE"
  records = get_db_rows(query)
  for i in range(len(records)):
      element = Element(records.iloc[i])
      element.name = web
      Templates.generate_text_match(element)
