#read_scale test:
import binascii
from time import sleep
import os

def read_scale(hid_num=0, debug=False):
    """
    Reads the raw bytes from the scale and returns a tuple of value and 
    unit of measure.

    returns: (<value>, <unit>)
    """
    scale_device_name = '/dev/hidraw{}'.format(hid_num)
    if os.path.exists(scale_device_name):
        with open(scale_device_name, 'rb') as scale:
            #the scale outputs 6 bytes at a time:
            byte = scale.read(6)
            while(byte != ''):
                byte = scale.read(6)
                #convert to something we can look at easily:
                raw_bytes = binascii.hexlify(byte)
                #turn the raw bytes into characters:
                byte_vals = [chr(i) for i in raw_bytes[-4:]]
                #ordering of the bytes, smallest to largest:
                ordering = (2, 3, 0, 1) 
                #rearrange and merge according to ordering:
                ordered_bytes = ''.join([byte_vals[index] for index in ordering])
                #get an int from the rerranged hex characters:
                bytes_to_int = int('0x' + ordered_bytes, 0)
                is_grams = 'bff' not in str(raw_bytes[5:8])
                #if the scale is tared when not empty, this byte changes:
                if '5' in str(chr(raw_bytes[3])):
                    sign = '-'
                else:
                    sign = ''
                if is_grams:
                    unit = 'g'
                    output_text = '{} grams'.format(bytes_to_int)
                else:
                    unit = 'oz'
                    bytes_to_int /= 10
                    pounds, ounces = bytes_to_int // 16, round(bytes_to_int % 16, 2)
                    if debug:
                        output_text = '{}{} lb. {} oz.'.format(sign, int(pounds), ounces)
                        #print(output_text)
                #return either total grams or total ounces:
                return bytes_to_int, unit
    else:
        #print("Scale not connected or powered on.")
        return None, None

def oz_to_g(oz=10, places=0):
    """
    converts ounces to grams
    """
    return round(oz * 28.3495, places)

def g_to_oz(g=283.5, places=1):
    """
    converts ounces to grams
    """
    return round(g / 28.3495, places)

def easy_measure(output_unit='g', tries=5):
    #TODO: there's a problem with weighing grams
    measurement = None
    for _ in range(tries):
        try:
            measurement, scale_unit = read_scale()
            if None not in (measurement, scale_unit):
                break
        except OSError: #handle error for connection loss during read_scale() execution
            #print("Connection Lost")
    else:
        return None
    if scale_unit == 'oz' and output_unit == 'g':
        return oz_to_g(measurement), 'g'
    elif scale_unit == 'g' and output_unit == 'oz':
        return g_to_oz(measurement), 'oz'
    else:
        return measurement, output_unit

def main():
    while True:
        sleep(.5)
        print(easy_measure())

if __name__ == "__main__":
    main()
