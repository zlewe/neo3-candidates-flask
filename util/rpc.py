import requests
import json

import base64
import hashlib
import pandas as pd

rpc_url = "http://neo3.edgeofneo.com:10332"

def _rpc_call(method, param = None):
    if param:
      payload = json.dumps({
                              "jsonrpc": "2.0",
                              "id": 1,
                              "method": method,
                              "params": [
                                          param[0],
                                          param[1],
                                          []
                                      ]
                          })
    else:
      payload = json.dumps({
                              "jsonrpc": "2.0",
                              "id": 1,
                              "method": method,
                              "params": []
                          })
    headers = {'content-type': "application/json", 'cache-control': "no-cache"}
    try:
        response = requests.request("POST", rpc_url, data=payload, headers=headers)
        return json.loads(response.text)
    except requests.exceptions.RequestException as e:
        print(e)
    except:
        print('Unknown Error')
        
def get_block():
    return _rpc_call("getblockcount")['result']

def _invoke_contract(hash, method):
    return _rpc_call("invokefunction", [hash, method])

def _get_committee_info():
    return _invoke_contract("0xb776afb6ad0c11565e70f8ee1dd898da43e51be1","getAllInfo")

def _get_candidates():
    return _invoke_contract('0xef4073a0f2b305a38ec4050e4d3d28bc40ea63f5','getCandidates')

def _decode_bytestring(value):
    return base64.b64decode(value).decode()

def _decode_committee(com):
    committee = []
    committee.append(com[0]['value'])
    for field in com[1:]:
        committee.append(_decode_bytestring(field['value']))

    return committee

def _from_json(json):
    com_list = []
    for x in json['value']:
        com_list.append(_decode_committee(x['value']))
    
    return com_list

def _b64pubkey_to_b64scripthash(key):
    b = bytearray(base64.b64decode(key))
    ver = bytearray.fromhex('0C21')+b+bytearray.fromhex('4156E7B327')
    
    hash_256 = hashlib.sha256()
    hash_256.update(ver)
    obj = hashlib.new('ripemd160', hash_256.digest())
    ripemd_160_value = obj.hexdigest() #scripthash
    hash = base64.b64encode(bytes.fromhex(ripemd_160_value)).decode()
    return hash

def get_table(show_hash = False):
    COLUMN_NAMES = ['Hash(Base64)', 'Name', 'Location', 'Website', 'Email', 'Github', 'Telegram', 'Twitter', 'Description', 'Logo']
    resp = _get_committee_info()
    committee_list = _from_json(resp['result']['stack'][0])
    df = pd.DataFrame(committee_list, columns = COLUMN_NAMES)
    df.insert(0, 'Vote', 0)
    
    resp_invoke = _get_candidates()
    unknown_list = []

    for candidate in resp_invoke['result']['stack'][0]['value']:
        key = _b64pubkey_to_b64scripthash(candidate['value'][0]['value'])
        vote = candidate['value'][1]['value']

        if key in df['Hash(Base64)'].values:
            df.loc[df['Hash(Base64)'] == key, 'Vote'] = vote
        else:
            unknown_list.append([vote, key])

    if unknown_list:
        COL = ['Vote', 'Hash(Base64)']
        df_unknown = pd.DataFrame(unknown_list, columns = COL)

    if not show_hash:
        df = df.drop(['Hash(Base64)'], axis=1)
    
    return df, df_unknown
