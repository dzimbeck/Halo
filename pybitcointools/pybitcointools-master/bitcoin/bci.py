#!/usr/bin/python
import urllib2, json, re, random, sys

# Makes a request to a given URL (first argument) and optional params (second argument)
def make_request(*args):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'+str(random.randrange(1000000)))]
    try:
        return opener.open(*args).read().strip()
    except Exception,e:
        try: p = e.read().strip()
        except: p = e
        raise Exception(p)

# Gets the unspent outputs of one or more addresses
def unspent(*args):
    # Valid input formats: history([addr1, addr2,addr3])
    #                      history(addr1, addr2, addr3)
    if len(args) == 0: return []
    elif isinstance(args[0],list): addrs = args[0]
    else: addrs = args
    u = []
    for addr in addrs:
        try: data = make_request('https://blockchain.info/unspent?address='+addr)
        except Exception,e: 
            if str(e) == 'No free outputs to spend': continue
            else: raise Exception(e)
        try:
            jsonobj = json.loads(data)
            #print 'd',data
            for o in jsonobj["unspent_outputs"]:
                h = o['tx_hash'].decode('hex')[::-1].encode('hex')
                u.append({
                    "output": h+':'+str(o['tx_output_n']),
                    "value": o['value'] 
                })
        except:
            raise Exception("Failed to decode data: "+data)
    return u

def blockr_unspent(*args):
    # Valid input formats: history([addr1, addr2,addr3])
    #                      history(addr1, addr2, addr3)
    if len(args) == 0: return []
    elif isinstance(args[0],list): addrs = args[0]
    else: addrs = args
    res = make_request('https://btc.blockr.io/api/v1/address/unspent/'+','.join(addrs))
    data = json.loads(res)['data']
    o = []
    if 'unspent' in data: data = [data]
    for dat in data:
        for u in dat['unspent']:
            o.append({
                "output": u['tx']+':'+str(u['n']),
                "value": int(u['amount'].replace('.',''))
            })
    return o

# Gets the transaction output history of a given set of addresses,
# including whether or not they have been spent
def history(*args):
    # Valid input formats: history([addr1, addr2,addr3])
    #                      history(addr1, addr2, addr3)
    if len(args) == 0: return []
    elif isinstance(args[0],list): addrs = args[0]
    else: addrs = args

    txs = []
    for addr in addrs:
        offset = 0
        while 1:
            data = make_request('https://blockchain.info/address/%s?format=json&offset=%s' % (addr,offset))
            try:
                jsonobj = json.loads(data)
            except:
                raise Exception("Failed to decode data: "+data)
            txs.extend(jsonobj["txs"])
            if len(jsonobj["txs"]) < 50: break
            offset += 50
            sys.stderr.write("Fetching more transactions... "+str(offset)+'\n')
    outs = {}
    for tx in txs:
        for o in tx["out"]:
            if o['addr'] in addrs:
                key = str(tx["tx_index"])+':'+str(o["n"])
                outs[key] = { 
                    "address" : o["addr"],
                    "value" : o["value"],
                    "output" : tx["hash"]+':'+str(o["n"]),
                    "block_height" : tx.get("block_height",None)
                }
    for tx in txs:
        for i, inp in enumerate(tx["inputs"]):
            if inp["prev_out"]["addr"] in addrs:
                key = str(inp["prev_out"]["tx_index"])+':'+str(inp["prev_out"]["n"])
                if outs.get(key): outs[key]["spend"] = tx["hash"]+':'+str(i)
    return [outs[k] for k in outs]

# Pushes a transaction to the network using https://blockchain.info/pushtx
def pushtx(tx):
    if not re.match('^[0-9a-fA-F]*$',tx): tx = tx.encode('hex')
    return make_request('https://blockchain.info/pushtx','tx='+tx)

def eligius_pushtx(tx):
    if not re.match('^[0-9a-fA-F]*$',tx): tx = tx.encode('hex')
    s = make_request('http://eligius.st/~wizkid057/newstats/pushtxn.php','transaction='+tx+'&send=Push')
    strings = re.findall('string[^"]*"[^"]*"',s)
    for string in strings:
        quote = re.findall('"[^"]*"',string)[0]
        if len(quote) >= 5: return quote[1:-1]

def last_block_height():
    data = make_request('https://blockchain.info/latestblock')
    jsonobj = json.loads(data)
    return jsonobj["height"]

# Gets a specific transaction
def bci_fetchtx(txhash):
    if not re.match('^[0-9a-fA-F]*$',txhash): txhash = txhash.encode('hex')
    data = make_request('https://blockchain.info/rawtx/'+txhash+'?format=hex')
    return data

def blockr_fetchtx(txhash):
    if not re.match('^[0-9a-fA-F]*$',txhash): txhash = txhash.encode('hex')
    jsondata = json.loads(make_request('https://btc.blockr.io/api/v1/tx/raw/'+txhash))
    return jsondata['data']['tx']['hex']

def fetchtx(txhash):
    try: return bci_fetchtx(txhash)
    except: return blockr_fetchtx(txhash)

def firstbits(address):
    if len(address) >= 25:
        return make_request('https://blockchain.info/q/getfirstbits/'+address)
    else:
        return make_request('https://blockchain.info/q/resolvefirstbits/'+address)
