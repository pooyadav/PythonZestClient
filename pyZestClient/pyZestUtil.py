__author__ = 'pooyadav'

import os
from zestHeader import ZestHeader

format_map = {'TEXT': 0, 'BINARY': 42, 'JSON': 50}  # generate path to CURVE key


def toZmqCurvePath(path, key, basePath='certificates'):
    """


      :rtype : path
      :param path:
      :param key:
      :param basePath:
      """
    os.path.join(path, basePath)
    pass


def check_content_format(format):
    if format in format_map.keys():
        return True
    else:
        raise Exception("KKK")


content_format_to_int = lambda format: format_map.get(format, 0)


def parse(msg):

    """
    Parses a message
            header order
        |code|oc|tkl|
        |_0__|_1|_2_|
    :param msg:
    """
    #assert type(msg) is bytearray, "Cannot parse header- invalid format, should be byte array"
    #assert len(msg) < 4, "Cannot parse header - not enough bytes"
    zr = zestHeader()
    print(zr["code"])
    print("received code")
    zr["code"] = msg[0]
    zr["oc"] = msg[1]
    zr["tkl"] = int.from_bytes(bytes(msg[2:4]),byteorder='big')

    print(zr["code"])
    print(zr["oc"])
    print(zr["tkl"])

    #Test again this block
    if zr["tkl"] > 0:
        zr["token"] = str(bytes(msg[4:4+zr["tkl"]],byteorder='big'), encoding="utf-8")

    offset = 4 + zr["tkl"]

    for i in range(0, zr["oc"]):
        zoh = parseZestOptionsHeader(msg, offset)
        print("zoh returned")
        zr["options"].append(zoh)
        offset = offset + 4 + len(zoh)
        print(offset)

    print(len(msg))
    print(offset)
    if(len(msg) > offset):
        print("msg has a payload")
        zr["payload"] = str(msg[offset-1:], 'utf-8')
        print("  ", zr["payload"])
    return zr


def zestHeader():
    return { "oc":0,
        "code": 0,
        "tkl": 0,
        "token": "",
        "options": [],
        "payload": "",}



def marshalZestHeader(header):
    print(header)
    optionsLen = [li['len']+4 for li in header["options"]]
    optionsLen = sum(optionsLen)-4
    print(optionsLen)
    payloadLen = len(bytearray(header["payload"], "utf8"))
    bufferSize = 8+header["tkl"]+ optionsLen + payloadLen
    print(bufferSize)
    buff = bytearray(bufferSize)
    x = memoryview(buff)
    buff[0] = header["code"]
    buff[1] = header["oc"]
    buff[2:4] = header["tkl"].to_bytes(2, byteorder='big', signed=True) #Fix this for integer
    #buff[4] = header['token']
    offset = 4 + header["tkl"]
    for i in range(0, header["oc"]):
        zoh = MarshalZestOptionsHeader(header["options"][i])
        print("received data from option bytes")
        buff[offset:offset+len(zoh)]= zoh
        offset = offset+len(zoh)
    buff[offset:offset+payloadLen] = bytearray(header["payload"], "utf8")
    return buff


def MarshalZestOptionsHeader(zoh):
    print("inside Zest Options")
    buff1 = bytearray(4+ int(zoh["len"]))
    x = int(zoh["number"])
    buff1[0:2] = x.to_bytes(2, byteorder='big', signed=False)
    buff1[2:4] = zoh["len"].to_bytes(2, byteorder='big', signed=False)
    if(zoh["number"] == 12):
        buff1[4:6] = zoh["value"].to_bytes(2, byteorder='big', signed=False)
    elif(zoh["number"] == 14):
        buff1[4:8] = zoh["value"].to_bytes(4, byteorder='big', signed=False)
    else:
        l = int(zoh["len"])
        buff1[4:5+l] = bytes(str(zoh["value"]),encoding="utf-8")
    return buff1

def parseZestOptionsHeader(msg, offset):
    print("parse called")
    zoh = newZestOptionHeader(0,0,0)
    zoh["number"] = int.from_bytes(bytes(msg[offset:offset+2]),byteorder='big',signed=False)
    zoh["len"] = int.from_bytes(bytes(msg[offset+2:offset+4]),byteorder='big',signed=False)
    zoh["value"] = str(msg[offset+4:offset+4+zoh["len"]], 'utf-8')
    print(zoh["value"])
    return zoh


def newZestOptionHeader(num,len1,val):
    print("newzest called")
    return {"number":num,
        "len": len1,
        "value": val,}
