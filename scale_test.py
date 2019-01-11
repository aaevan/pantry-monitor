#read_scale test:

import binascii

def read_scale(hid_num=0):
    with open('/dev/hidraw{}'.format(hid_num), 'rb') as scale:
        try:
            #the scale outputs 6 bytes at a time:
            byte = scale.read(6)
            while(byte != ''):
                byte = scale.read(6)
                #convert to something we can look at easily:
                raw_bytes = binascii.hexlify(byte)
                byte_vals = [chr(i) for i in raw_bytes[-4:]]
                ordering = (2, 3, 0, 1) #ordering of the bytes, smallest to largest
                ordered_bytes = ''.join([byte_vals[index] for index in ordering])
                bytes_to_int = int('0x' + ordered_bytes, 0)
                #print([(i, chr(byte)) for i, byte in enumerate(raw_bytes)])
                print("raw_bytes[5:8] : {}".format(raw_bytes[5:8]))
                print(raw_bytes, raw_bytes[-4:], "|", byte_vals, "|", ordered_bytes, "|", bytes_to_int)
        finally:
            scale.close()

read_scale()
