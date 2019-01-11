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
                is_grams = 'bff' not in str(raw_bytes[5:8])
                if is_grams:
                    output_text = '{} grams'.format(bytes_to_int)
                else:
                    bytes_to_int /= 10
                    pounds, ounces = bytes_to_int // 16, round(bytes_to_int % 16, 2)
                    output_text = '{} lb. {} oz.'.format(int(pounds), ounces)
                #print(raw_bytes, raw_bytes[-4:], "|", byte_vals, "|", ordered_bytes, "|", bytes_to_int, unit)
                print(raw_bytes, output_text)
        finally:
            scale.close()

read_scale()
