# -*- coding: utf-8 -*
import os
import struct
import binascii

class TsParser:

    # ISO/IEC 13818-1的2.4.3.2 Transport Stream packet layer
    # 读取TS Packet头部
    # 参数：TS packet头部4字节数据
    # 返回值：TS Packet头部各字段
    def getHeader(self, ts_packet_str):
        sys_byte, byte2, byte3, byte4 = struct.unpack('>4B', ts_packet_str)
        if sys_byte == 0x47:
            # 返回字典{}
            return \
                {
                    'sys_byte': sys_byte,
                    'transport_error_indicator': byte2 >> 7,
                    'payload_unit_start_indicator': byte2 >> 6,
                    'transport_priority': byte2 >> 5,
                    'PID': ((byte2 & 0x1F) << 8) | byte3,
                    'transport_scrambling_control': (byte4 >> 6) & 0x3,
                    'adaption_field_control': (byte4 >> 4) & 0x3,
                    'continuity_counter': byte4 & 0x0F
                }
        else:
            return -1

    # 读取PAT SECTION头部
    # 参数：PAT SECTION头部8字节数据
    # 返回值：PAT SECTION头部各字段
    def getPat(self,pat_section):
        table_id, byte2, byte3, byte4,byte5,byte6,section_number,last_section_number\
            = struct.unpack('8B', pat_section)
        if table_id == 0x00:
            # 返回字典{}
            return \
                {
                    'table_id': table_id,
                    'section_syntax_indicator': byte2 >> 7,
                    '0': (byte2 >> 6) & 0x01,
                    'reserved1': (byte2 >> 4) & 0x03,
                    'section_length': ((byte2 & 0x0F) << 8) | byte3,
                    'transport_stream_id': byte4 << 8 | byte5,
                    'reserved2': byte6 >> 6,
                    'version_number': (byte6 >> 1) & 0x1F,
                    'current_next_indicator': byte6 & 0x01,
                    'section_number': section_number,
                    'last_section_number': last_section_number,
                    'CRC_32': -1
                }
        else:
            return -1

    # 读取PMT SECTION头部
    # 参数：PMT SECTION头部8字节数据
    # 返回值：PMT SECTION头部各字段
    def getPmt(self,pmt_section):
        table_id, byte2, byte3, byte4, byte5, byte6, section_number, last_section_number,\
        byte9, byte10, byte11, byte12 \
            = struct.unpack('12B', pmt_section)
        if table_id == 0x02:
            return \
                {
                    'table_id': table_id,
                    'section_syntax_indicator': byte2 >> 7,
                    '0': (byte2 >> 6) & 0x01,
                    'reserved1': (byte2 >> 4) & 0x03,
                    'section_length': ((byte2 & 0x0F) << 8) | byte3,
                    'program_number': byte4 << 8 | byte5,
                    'reserved2': byte6 >> 6,
                    'version_number': (byte6 >> 1) & 0x1F,
                    'current_next_indicator': byte6 & 0x01,
                    'section_number': section_number,
                    'last_section_number': last_section_number,
                    'reserved3': byte9 >> 5,
                    'PCR_PID': (byte9 & 0x1F) << 8 | byte10,
                    'reserved4': byte11 >> 4,
                    'program_info_length': (byte11 & 0x0F) << 8 | byte12
                }
        else:
            return -1

    def getPes(self):
        pass

    def getEs(self):
        pass

