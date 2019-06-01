from elasticsearch import Elasticsearch

es = Elasticsearch("127.0.0.1:9200")

ret0 = es.search(
    index="papers",
    body={
        "query":{
            "multi_match":{
                "query":"biology",
                "fields":[
                    "title",
                    "abstract",
                    "keywords",
                    "fos"
                ]
            }
        }
    }
)

paperID = "3b19c2e6-450d-44f5-83ec-ff944aa9421d"

ret1 = es.get(
    index='papers',
    id=paperID,
)

print(ret1)