# -*- coding: utf-8 -*
import os
import struct

class EsParser:

    def videoSequence(self, sequence):
        idx = 0
        cei = -1
        sequence_header = self.sequenceHeader(sequence[idx:idx+4])
        if sequence_header != -1:
            if "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xb0:
                cei = self.CEI_Info(sequence[50:50+67])

            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB1:
                pass
            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB2:
                pass
            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB3:
                pass
            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB5:
                cei = self.extensionAndUserData(sequence)
            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB6:
                pass
            elif "video_sequence_start_code" in sequence_header and sequence_header['video_sequence_start_code'] == 0xB7:
                pass

        return cei

    def sequenceHeader(self,header):
        b1, b2, b3, b4 = struct.unpack('>4B', header)
        if b1 != 0:
            return -1
        video_prefix = (b1 << 16) | (b2 << 8) | b3
        video_sequence_start_code = b4
        if video_prefix == 0x000001:
            return \
                {
                    'video_prefix':video_prefix,
                    'video_sequence_start_code':video_sequence_start_code
                }
        return -1

    def extensionAndUserData(self,type,extension):
        cei = -1
        b1 = struct.unpack('>B', extension[:1])[0]
        if type == 0xB5:
            flag = b1 >> 4
            if flag == 2:pass
            if flag == 3:pass
            if flag == 4:pass
            if flag == 10:pass
            if flag == 11:pass
            if flag == 13:
                cei = self.CEI_Info(extension[:67])
        elif type == 0xB2:
            pass

        return cei

    def CEI_Info(self, data):
        IV = ''
        IV_length = 0
        cei_length = 2
        current_key_id, next_key_id = 0,0

        b1, b2, b3, b4, b5, b6, b7, b8, \
        b9, b10, b11, b12, b13, b14, b15, b16, \
        b17, b18, b19,b20, b21, b22, b23, b24, \
        b25, b26, b27, b28, b29, b30, b31, b32, \
        b33, b34, b35, b36, b37, b38, b39, b40, \
        b41, b42, b43, b44, b45, b46, b47, b48, \
        b49, b50, b51, b52, b53, b54, b55, b56, \
        b57, b58, b59, b60, b61, b62, b63, b64, \
        b65, b66, b67 \
            = struct.unpack('67B', data)

        for i in range(67):
            exec('byte{} = {}'.format(i, i))
        extension_id = b1 >> 4

        if extension_id == 13:
            reserved = b1 & 0x0F
            # CEI_DATA
            encryption_flag = b2 >> 7
            next_key_id_flag = (b2 >> 6) & 0x01

            if encryption_flag == 1:
                # 16B
                # current_key_id =  (b3<<15)|(b4<<14)|(b5<<13)|(b6<<12)|(b7<<11)|(b8<<10)|(b9<<9)|(b10<<8)\
                #                   |(b11<<7)|(b12<<6)|(b13<<5)|(b14<<4)|(b15<<3)|(b16<<2)|(b17<<1)|b18
                current_key_id = '{:x}'.format(b3)+'{:x}'.format(b4)+'{:x}'.format(b5)+'{:x}'.format(b6) \
                                 +'{:x}'.format(b11)+'{:x}'.format(b12)+'{:x}'.format(b13)+'{:x}'.format(b14) \
                                 +'{:x}'.format(b15)+'{:x}'.format(b16)+'{:x}'.format(b17)+'{:x}'.format(b18)
                IV_length = b19
                IV = '{:02x}'.format(b20) + '{:02x}'.format(b21) + '{:02x}'.format(b22) \
                     + '{:02x}'.format(b23) + '{:02x}'.format(b24) + '{:02x}'.format(b25) + '{:02x}'.format(b26) \
                     + '{:02x}'.format(b27) + '{:02x}'.format(b28) + '{:02x}'.format(b29) + '{:02x}'.format(b30) \
                     + '{:02x}'.format(b31) + '{:02x}'.format(b32) + '{:02x}'.format(b33) + '{:02x}'.format(b34) \
                     + '{:02x}'.format(b35)
                cei_length += IV_length

            if next_key_id_flag == 1:
                next_key_id =  '{:x}'.format(b19)+'{:x}'.format(b20)+'{:x}'.format(b21)+'{:x}'.format(b22) \
                                +'{:x}'.format(b23)+'{:x}'.format(b24)+'{:x}'.format(b25)+'{:x}'.format(b26) \
                                +'{:x}'.format(b27)+'{:x}'.format(b28)+'{:x}'.format(b29)+'{:x}'.format(b30)\
                                + '{:02x}'.format(b31) + '{:02x}'.format(b32) + '{:02x}'.format(b33) + '{:02x}'.format(b34)
                IV_length = b35
                IV = '{:02x}'.format(b36) + '{:02x}'.format(b37) + '{:02x}'.format(b38) \
                     + '{:02x}'.format(b39) + '{:02x}'.format(b40) + '{:02x}'.format(b41) + '{:02x}'.format(b42) \
                     + '{:02x}'.format(b43) + '{:02x}'.format(b44) + '{:02x}'.format(b45) + '{:02x}'.format(b46) \
                     + '{:02x}'.format(b47) + '{:02x}'.format(b48) + '{:02x}'.format(b49) + '{:02x}'.format(b50)\
                     + '{:02x}'.format(b51)
                cei_length += IV_length

            return \
                {
                    'cei_length': cei_length,
                    'encryption_flag': encryption_flag,
                    'next_key_id_flag': next_key_id_flag,
                    'current_key_id': current_key_id,
                    'next_key_id': next_key_id,
                    'IV_length': IV_length,
                    'IV': IV
                }
        return -1