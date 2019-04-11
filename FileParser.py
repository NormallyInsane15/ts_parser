# -*- coding: utf-8 -*
import struct
import binascii
class FileParser:
    # def __init__(self):
    #     print('this is class FileParser!\n')

    def open(self, file_path):
        return open(file_path, 'rb')

    def readFile(self,filehandle, startPos, width):
        filehandle.seek(startPos,0)
        if width == 4:
            string = filehandle.read(4)
            if string == '':
                raise IOError
            return struct.unpack('<L',string[:4])[0]
            # ts_packet = binascii.b2a_hex(string)
            # return str(ts_packet, encoding="utf-8")
        elif width == 2:
            string = filehandle.read(2)
            if string == '':
                raise IOError
            return struct.unpack('<H',string[:2])[0]
        elif width == 1:
            string = filehandle.read(1)
            if string == '':
                raise IOError
        # return struct.unpack('<B',string[:1])[0]
            ts_packet = binascii.b2a_hex(string)
            return str(ts_packet, encoding="utf-8")