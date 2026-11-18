"""Host reference codec, not a sensor driver."""
import struct

def crc16(data):
    crc=0xffff
    for b in data:
        crc^=b<<8
        for _ in range(8):crc=((crc<<1)^0x1021)&0xffff if crc&0x8000 else (crc<<1)&0xffff
    return crc

def imu_frame(seq,uptime,values,flags=1):
    if len(values)!=6:raise ValueError('six values required')
    b=bytearray(32)
    struct.pack_into('<BBBBHIB',b,0,0x53,1,1,flags,seq,uptime,12)
    struct.pack_into('<6h',b,11,*values)
    struct.pack_into('<H',b,30,crc16(b[:30]))
    return bytes(b)

def decode(b):
    if len(b)!=32:raise ValueError('length')
    if b[:2]!=b'\x53\x01':raise ValueError('version')
    if b[10]>18 or b[29]!=0:raise ValueError('payload/reserved')
    if crc16(b[:30])!=struct.unpack_from('<H',b,30)[0]:raise ValueError('crc')
    if any(b[11+b[10]:29]):raise ValueError('padding')
    if b[2]==1:
        if b[10]!=12:raise ValueError('IMU length')
        return struct.unpack('<6h',b[11:23])
    if b[2] not in (2,3,4):raise ValueError('type')
    return b[11:11+b[10]]
