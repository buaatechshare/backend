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
        data = None

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
        data = None

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
        data = None

    return data

def get_certain_fos_paper(FoS,count):

    output = []
    for id in FoS:
        expr = "And(Ty='0',Composite(F.FId=" + str(id) +"))"
        params = urllib.parse.urlencode({
            # Request parameters
            'expr': expr,
            'model': 'latest',
            'count': count,
            'offset': '0',
            'attributes': 'Id',
        })
        try:
            conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')
            conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            data = json.loads(data.decode(encoding='utf8'))
            data = data['entities']
            id_list = []
            for i in data:
                id_list.append(i['Id'])
            output.append(id_list)
        except Exception as e:
            data = None
            return data
    return output

def get_paper_details(p_id):
    #     "fos"
    #     "references"
    #     "doi": "string",
    #     "url"
    #     "abstract": "string"
    #
    #
    #     云端数据
    output = {}
    params = urllib.parse.urlencode({
        # Request parameters
        'expr': "And(Ty='0',Id=" + str(p_id) + ")",
        'model': 'latest',
        'count': '10',
        'offset': '0',
        'attributes': 'F.FN,RId,E',
    })
    try:
        conn = http.client.HTTPSConnection('api.labs.cognitive.microsoft.com')
        conn.request("GET", "/academic/v1.0/evaluate?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data.decode(encoding='utf8'))
        data = data['entities'][0]

        if 'F' in data.keys():
            field_set = []
            for i in data['F']:
                field_set.append(i['FN'])
            output['fos'] = field_set
        else:
            output['fos'] = None

        if 'RId' in data.keys():
            output['references'] = data['RId']
        else:
            output['references'] = None
        if 'E' in data.keys():
            data = data['E']
            data = json.loads(data)
            if 'DOI' in data.keys():
                output['doi'] = data['DOI']
            else:
                output['doi'] = None

            if 'S' in data.keys():
                url_set = []
                for i in data['S']:
                    url_set.append(i['U'])
                output['url'] = url_set
            else:
                output['url'] = None

            if 'IA' in data.keys():
                data = data['IA']
                length = data['IndexLength']
                word = data['InvertedIndex']
                words = [''] * length
                for key in word.keys():
                    indexs = word[key]
                    for i in indexs:
                        words[i] = key
                data = ''
                for i in words:
                    data = data + i + ' '
                output['abstract'] = data
            else:
                output['abstract'] = None
    except Exception as e:
        data = None
        return data
    return output