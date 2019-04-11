# -*- coding: utf-8 -*
import os
import Config
import FileParser
import TsParser
import PatParser
import PmtParser
import PesParser
import EsParser
import struct
from flask import Flask

app = Flask(__name__)

@app.route('/')
def main():
    filehandle = open(Config.file_path, 'rb')
    file_size = os.path.getsize(Config.file_path)
    position = 0
    load_postion = 0
    pat_flag = 0
    prog = []
    stream = []
    filehandle.seek(position, os.SEEK_SET)
    try:
        while (position < file_size):

            if filehandle.read(position + 188) == "" or filehandle.read(position + 188) == 0:
                print('file end!')
                break
            # ================================================================================
            packet = bytes(filehandle.read(188))
            TsParserObj = TsParser.TsParser()
            ts_head = TsParserObj.getHeader(packet[:4])
            if ts_head == -1:
                break
            # ====python -m pip install --upgrade pip============================================================================
            if ts_head['adaption_field_control'] == 0 or ts_head['adaption_field_control'] == 2:
                position += 188
                filehandle.seek(position, os.SEEK_SET)
                continue
            elif ts_head['adaption_field_control'] == 1:
                load_postion = 4
            else:
                filehandle.seek(3, os.SEEK_CUR)
                load_postion = 4 + struct.unpack('>B', packet[4:5])[0] + 1

            if ts_head['payload_unit_start_indicator'] == 1:
                load_postion = load_postion + struct.unpack('>B', packet[load_postion:load_postion + 1])[0] + 1

            filehandle.seek(load_postion, os.SEEK_CUR)
            # ================================================================================
            if ((ts_head['PID'] == 0x0000) and (pat_flag != 1)):
                pat = TsParserObj.getPat(packet[load_postion:load_postion + 8])
                if pat != -1:
                    patParserObj = PatParser.PatParser()
                    prog = patParserObj.get_prog_detail(pat['section_length'], pat_data=packet[
                                                                                        load_postion + 8:load_postion + 8 +
                                                                                                         pat[
                                                                                                             'section_length']])
                    pat_flag = 1
            # ================================================================================
            elif len(prog) != 0:
                for prog_item in prog:
                    if "PMT_PID" in prog_item and ts_head['PID'] == prog_item['PMT_PID']:
                        pmt_header = TsParserObj.getPmt(packet[load_postion:load_postion + 12])
                        if pmt_header != -1 and pmt_header['table_id'] == 0x02:
                            pmtObj = PmtParser.PmtParser()
                            stream = pmtObj.get_stream_detail(pmt_header, packet[load_postion + 12 + pmt_header[
                                'program_info_length']:pmt_header['section_length'] + 3 - 4])
                            print(stream)
            # ================================================================================
            if len(stream) != 0:
                for stream_item in stream:
                    if "elementary_PID" in stream_item and ts_head['PID'] == stream_item['elementary_PID'] and ts_head[
                        'payload_unit_start_indicator'] == 1:
                        PesParserObj = PesParser.PesParser()
                        pes_header = PesParserObj.getHeader(packet[4:4 + 6])
                        if pes_header != -1:
                            esParserObj = EsParser.EsParser()
                            cei = esParserObj.videoSequence(packet[4 + 14:])
                            if cei != -1:
                                print(cei)
            position += 188
            filehandle.seek(position, os.SEEK_SET)
    except IOError:
        print('IO error! maybe reached EOF')
    except EOFError:
        pass
    finally:
        filehandle.close()


print('================================================\n')
