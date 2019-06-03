from .Ocp_key import get_key
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': get_key(),
    }

def get_FoS(p_id):

    params = urllib.parse.urlencode({
        # Request parameters
        'expr': "And(Ty='0',Id=" + str(p_id) + ")",
        'model': 'latest',
        'count': '10',
        'offset': '0',
        'attributes': 'F.FN,F.FId',
    })

    try:
        conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data.decode(encoding='utf8'))
        data = data['entities'][0]
        if 'F' in data.keys():
            data = data['F']
        else:
            data = []
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        data = []

    return data

def get_Reference(p_id):

    params = urllib.parse.urlencode({
        # Request parameters
        'expr': "And(Ty='0',Id="+str(p_id)+")",
        'model': 'latest',
        'count': '10',
        'offset': '0',
        'attributes': 'RId,Ti',
    })

    try:
        conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data.decode(encoding='utf8'))
        data = data['entities'][0]
        if 'RId' in data.keys():
            data = data['RId']
        else:
            data = []
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        data = []

    return data

def get_abstract(p_id):

    params = urllib.parse.urlencode({
        # Request parameters
        'expr': "And(Ty='0',Id=" + str(p_id) + ")",
        'model': 'latest',
        'count': '10',
        'offset': '0',
        'attributes': 'E',
    })

    try:
        conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data.decode(encoding='utf8'))
        data = data['entities'][0]
        data = data['E']
        data = json.loads(data)
        if "IA" in data.keys():
            data = data['IA']
            length = data['IndexLength']
            word = data['InvertedIndex']
            words = [' '] * length
            for key in word.keys():
                indexs = word[key]
                for i in indexs:
                    words[i] = key
            data = ''
            for i in words:
                data = data + i + ' '
        else:
            data = ''
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
        data = ''

    return data