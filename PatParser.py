# -*- coding: utf-8 -*
import struct
import os

class PatParser:

    def get_prog_detail(self, section_length, pat_data):
        prog_info = []
        idx = 0
        while (idx < section_length - 4):
            b1, b2, b3, b4 = struct.unpack('4B', pat_data[idx:idx+4])
            PROG_INFO = \
                {
                    'program_number': (b1 << 8) | b2,
                    'PMT_PID': (b3 & 0x1F) << 8 | b4
                }

            prog_info.append(PROG_INFO)
            idx += 4
        return prog_info

