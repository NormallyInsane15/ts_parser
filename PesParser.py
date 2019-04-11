# -*- coding: utf-8 -*

import os
import struct
class PesParser:

    def getHeader(self,pes_header):
        b0, b1, b2, b3, b4, b5 = struct.unpack('6B', pes_header)
        packet_start_code_prefix = (b0 << 16) | (b1 << 8) | b2
        stream_id = b3
        PES_packet_length = (b4 << 8) | b5
        if packet_start_code_prefix == 0x000001:
            return \
                {
                    'packet_start_code_prefix':packet_start_code_prefix,
                    'stream_id':stream_id,
                    'PES_packet_length':PES_packet_length
                }
        return -1

    def getDetail(self, data):
        idx = 0
        b0, b1, b2, b3, b4, b5, b6, b7, b8 = struct.unpack('>9B', data)
        packet_start_code_prefix = (b0 << 16) | (b1 << 8) | b3
        stream_id = b4
        PES_packet_length = (b4 << 8) | b5
        idx += 6
        if stream_id != 0xBC and \
                stream_id != 0xBE and \
                stream_id != 0xBF and \
                stream_id != 0xF0 and \
                stream_id != 0xF1 and \
                stream_id != 0xFF and \
                stream_id != 0xF2 and \
                stream_id != 0xF8:
            PES_scrambling_control = (b6 >> 4) & 0x3
            PES_priority = (b6 >> 3) & 0x1
            data_alignment_indicator = (b6 >> 2) & 0x1
            copyright = (b6 >> 1) & 0x1
            original_or_copy = b6 & 0x1
            PTS_DTS_flags = b7 >> 6
            ESCR_flag = (b7 >> 5) & 0x1
            ES_rate_flag = (b7 >> 4) & 0x1
            DSM_trick_mode_flag = (b7 >> 3) & 0x1
            additional_copy_info_flag = (b7 >> 2) & 0x1
            PES_CRC_flag = (b7 >> 1) & 0x1
            PES_extension_flag = b7 & 0x1
            PES_header_data_length = b8

            PES_packet_data = data + 8 + PES_header_data_length
            PES_packet_data_length = PES_packet_data - data

        elif stream_id == 0xBE:
            PES_packet_data = 0
        else:
            PES_packet_data = data + 6
            PES_packet_data_length = 6
        return \
            {
                'packet_start_code_prefix': packet_start_code_prefix,
                'stream_id': stream_id,
                'PES_packet_length': PES_packet_length,
                'PES_scrambling_control': PES_scrambling_control,
                'PES_priority': PES_priority,
                'data_alignment_indicator': data_alignment_indicator,
                'copyright': copyright,
                'original_or_copy': original_or_copy,
                'PTS_DTS_flags': PTS_DTS_flags,
                'ESCR_flag': ESCR_flag,
                'ES_rate_flag': ES_rate_flag,
                'DSM_trick_mode_flag': DSM_trick_mode_flag,
                'additional_copy_info_flag': additional_copy_info_flag,
                'PES_CRC_flag': PES_CRC_flag,
                'PES_extension_flag': PES_extension_flag,
                'PES_header_data_length': PES_header_data_length
            }