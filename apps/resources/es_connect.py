from elasticsearch import Elasticsearch

es = Elasticsearch("10.136.70.232:9200",timeout=60)

paper_index = 'papers'
patent_index = 'patents'
