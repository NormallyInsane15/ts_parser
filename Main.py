# -*- coding: utf-8 -*
from flask import Flask,render_template,request,redirect,session,url_for,jsonify,make_response,Markup,flash,get_flashed_messages
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename

import os
import Config
import FileParser
import TsParser
import PatParser
import PmtParser
import PesParser
import EsParser
import struct

app = Flask(__name__)
Bootstrap(app)

@app.route('/', methods=['POST', 'GET'])
def index():
  if request.method == 'POST':
        f = request.files['file']
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        upload_path = os.path.join(basepath, 'static/uploads',
                                   secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)
        result = main(upload_path)
        # while result:
        #     return render_template\
        #         (
        #             'index.html',
        #             prog=result['prog'],
        #             stream=result['stream'],
        #             descriptor=result['stream'],
        #             cei=result['cei']
        #         )
        return render_template \
        (
                  'index.html',
                  prog=result[0]['prog'],
                  stream=result[0]['stream'],
                  descriptor=result[0]['stream'][0]['drm'],
                  cei=result[0]['cei']
        )
  return render_template('index.html')

def main(upload_path):
    filehandle = open(upload_path, 'rb')
    file_size = os.path.getsize(upload_path)
    position = 0
    load_postion = 0
    pat_flag = 0
    prog = []
    stream=[]
    cei = []
    result = []
    filehandle.seek(position, os.SEEK_SET)
    try:
        # global stream
        # global cei
        while(position < file_size):
            if filehandle.read(position+188) == "" or filehandle.read(position+188) == 0:
                print('file end!')
                break
            #================================================================================
            packet = bytes(filehandle.read(188))
            TsParserObj = TsParser.TsParser()
            ts_head = TsParserObj.getHeader(packet[:4])
            if ts_head == -1:
                break
            #================================================================================
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
                load_postion = load_postion + struct.unpack('>B', packet[load_postion:load_postion+1])[0] + 1

            filehandle.seek(load_postion, os.SEEK_CUR)
            #================================================================================
            if ((ts_head['PID'] == 0x0000) and (pat_flag != 1)):
                pat = TsParserObj.getPat(packet[load_postion:load_postion+8])
                if pat != -1:
                    patParserObj = PatParser.PatParser()
                    prog = patParserObj.get_prog_detail(pat['section_length'], pat_data=packet[load_postion+8:load_postion+8+pat['section_length']])
                    pat_flag = 1
            # ================================================================================
            if len(prog) != 0:
                for prog_item in prog:
                    if "PMT_PID" in prog_item and ts_head['PID'] == prog_item['PMT_PID']:
                        pmt_header = TsParserObj.getPmt(packet[load_postion:load_postion+12])
                        if pmt_header != -1 and pmt_header['table_id'] == 0x02:
                            pmtObj = PmtParser.PmtParser()
                            stream = pmtObj.get_stream_detail(pmt_header, packet[load_postion+12+pmt_header['program_info_length']:pmt_header['section_length']+3-4])
                            print(stream)
            # ================================================================================
            if len(stream) != 0:
                for stream_item in stream:
                    if "elementary_PID" in stream_item and ts_head['PID'] == stream_item['elementary_PID'] and ts_head['payload_unit_start_indicator'] ==1:
                        PesParserObj = PesParser.PesParser()
                        pes_header = PesParserObj.getHeader(packet[4:4+6])
                        if pes_header != -1:
                            esParserObj = EsParser.EsParser()
                            cei = esParserObj.videoSequence(packet[4+14:])
                            if cei != -1:
                                print(cei)

            position += 188
            filehandle.seek(position, os.SEEK_SET)
            if cei !=-1 and len(cei) != 0:
                result.append\
                    (
                        {
                            'prog': prog,
                            'stream': stream,
                            'cei': cei
                        }
                    )
                return result
        # return result
    except IOError:
        print('IO error! maybe reached EOF')
    finally:
        filehandle.close()

print('================================================\n')


if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port='8080',
        debug=True
    )