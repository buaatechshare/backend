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
        if filename[:3]=='pat':
            with open(filename,'r',encoding='utf-8') as fin:
                s = time.time()
                actions = []
                for line in fin:
                    patent = json.loads(line)["Patent"]
                    # ind = paper['id']
                    # paper.pop('id')
                    action = {
                        "_index": "patents",
                        "_type": "patent",
                        # "_id": ind,
                        "_source": patent
                    }
                    actions.append(action)
                    num_id += 1
                    if num_id % 20000 == 0:
                        a = helpers.bulk(es, actions)
                        actions = []
                        e = time.time()
                        print("{} {}s".format(a,e-s))
                    # if num_id == 100000:
                    #     break
                if len(actions):
                    a = helpers.bulk(es, actions)
                    actions = []
                    e = time.time()
                    print("{}s".format(e-s))
finally:
    print("{} doc inserted.".format(num_id))