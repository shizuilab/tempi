import numpy as np

def to_float_from_11073_32bit_float(data):
    tmp = int.from_bytes(data,'little')
    uint32val = np.array([tmp],dtype=np.uint32)

    # 仮数部を求める(0-24bit)
    tmp = bin(uint32val[0] & 0xffffff)
    mantissa = int(tmp,0)

    # 指数部を求める(25-32bit)
    tmp = int(data[3])
    tmp2 = np.array([tmp],dtype=np.byte)
    exponent = int(tmp2[0])

    # 実数を計算
    ret = round(mantissa * pow(10,exponent),1)
    return ret
