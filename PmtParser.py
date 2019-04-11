# -*- coding: utf-8 -*
import os
import struct

class PmtParser:

    def get_stream_detail(self, pmt_header, stream_data):
        stream = []
        idx = 0
        while (idx < pmt_header['section_length']+3-4):
            if len(stream_data[idx:idx+9]) == 0:
                break
            b1, b2, b3, b4, b5 = struct.unpack('5B', stream_data[idx:idx+5])

            drm = self.get_ChinaDRM_descriptor(stream_data[idx+5:idx+5+4])
            if drm != -1:
                drm['databytes'] = self.get_ChinaDRM_databytes(stream_data[idx+5+4: idx+5+4+drm['descriptor_length']-2])

            STREAM_INFO = \
                {
                    'stream_type': b1,
                    'elementary_PID':(((b2 & 0x1F) << 8 | b3) & 0x1FFF),
                    'ES_info_length': ((b4 & 0x0F) << 8 | b5),
                    'drm': drm
                }
            if self.check_type(STREAM_INFO['stream_type']):
                stream.append(STREAM_INFO)
            idx += (5 + STREAM_INFO['ES_info_length'])
        return stream


    def get_ChinaDRM_descriptor(self, descriptor):
        drm = -1
        descriptor_tag, descriptor_length, byte3, byte4 = struct.unpack('>4B', descriptor)
        if descriptor_tag == 0xC0:
            drm = \
                {
                    'descriptor_tag': descriptor_tag,
                    'descriptor_length': descriptor_length,
                    'video_format': byte3 >> 4,
                    'video_encryption_method': byte3 & 0x0F,
                    'audio_format': byte4 >> 4,
                    'audio_encryption_method': byte4 & 0x0F
                }

        return drm

    def get_ChinaDRM_databytes(self, data):
        result = ''
        if len(data) > 0:
            temp_result = struct.unpack('>'+str(len(data))+'B', data)
            for item in temp_result:
                result += str(item)
        return result

    def check_type(self,type):
        if (type >= 0x00 and type <= 0x1E) or (type == 0x24) or (type == 0x42) or (type == 0x7F)\
            or (type >= 0x80 and type <= 0x86) or (type == 0x90) or (type == 0x92) or (type == 0x93)\
            or (type >= 0x99 and type <= 0x9B) or (type == 0xA1) or (type == 0xA2) or (type == 0xEA)\
            or (type >= 0xF0 and type <= 0xF2) or (type == 0xFF) or (type == 0x20):
            return 0
        return -1
