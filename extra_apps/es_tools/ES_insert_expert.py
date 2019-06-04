from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json
import time 
import uuid
import os

es = Elasticsearch(
    ['127.0.0.1'],
    port=9200
)

path = os.curdir
files= os.listdir(path)

num_id = 0
try:
    for filename in files:
        if filename == 'mag_authors_10.txt':
            with open(filename,'r') as fin:
                s = time.time()
                actions = []
                for line in fin:
                    expert = json.loads(line)
                    ind = expert['id']
                    expert.pop('id')
                    action = {
                            "_index": "authors",
                            "_type": "author",
                            "_id": ind,
                            "_source": expert
                    }
                    actions.append(action)
                    num_id += 1
                    if num_id % 20000 == 0:
                        a = helpers.bulk(es, actions)
                        actions = []
                        e = time.time()
                        print("{} {}s".format(a,e-s))
                    if num_id == 100000:
                        break
                if len(actions):
                    a = helpers.bulk(es, actions)
                    actions = []
                    e = time.time()
                    print("{}s".format(e-s))
finally:
    print("{} doc inserted.".format(num_id))