# -*- coding: utf-8 -*-
#######
#######
# home.py
#######
#######
# 2022-07-15T06:00
# 2022-07-15T09:30
# 2022-07-15T14:30
# 2022-07-15T21:00
# 2022-07-17T07:00
# 2022-07-17T23:00
# 2022-07-18T07:00
# 2022-07-18T23:18
# 2022-07-19T15:49 
# 2022-07-20T22:00
# 2022-07-22T12:00 
# 2022-07-23T12:00 
# 2022-07-24T10:30 
# 2022-07-25T13:30 
# 2022-07-28T19:00 
# 2022-07-29T22:30 Trying session state still
#     7/17 WIP アップロードこの方法ではcacheが働かない。memo機能も試したがでUploadのCacheは使わないでいくべき。
#

###
# Imports
###
import sys
import traceback
import math
import locale
import datetime
import time
import io
import uuid
import json
import base64
import tempfile
from pathlib import Path
# from urllib.request import Request, urlopen
import requests
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image, ImageDraw, ImageFilter
import altair as alt
import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode, JsCode
# import cv2
# from pdf2image import convert_from_path


#####
#####
# Locale, timezone and others
#####
#####

###
# Locale
###
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # WORKED in mac for months. No good on Docker
# locale.setlocale(locale.LC_ALL, 'C.UTF-8')  # Not work on mac local. probably works on all machines and all docker
# locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8') # No good on Heroku
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8') # for mac

###
# Timezone
###
tz_jst = datetime.timezone(datetime.timedelta(hours=9))


###
# Global
###
# df_today = df_today.rename({"Hokkaido":"北海道", "Aomori":"青森","Akita":"秋田",
#       "Iwate":"岩手", "Miyagi":"宮城","Yamagata":"山形", "Fukushima":"福島", 
#       "Ibaraki":"茨城", "Tochigi":"栃木", "Gunma":"群馬", "Saitama":"埼玉",
#       "Chiba":"千葉", "Tokyo":"東京", "Kanagawa":"神奈川",
#       "Niigata":"新潟", "Toyama":"富山", "Ishikawa":"石川",
#       "Fukui":"福井", "Yamanashi":"山梨", "Nagano":"長野", 
#       "Gifu":"岐阜","Shizuoka":"静岡", "Aichi":"愛知", "Mie":"三重",
#       "Shiga":"滋賀", "Kyoto":"京都", "Osaka":"大阪","Hyogo":"兵庫",
#       "Nara":"奈良", "Wakayama":"和歌山", 
#       "Tottori":"鳥取","Shimane":"島根", "Okayama":"岡山",
#       "Hiroshima":"広島", "Yamaguchi":"山口",
#       "Kagawa":"香川", "Tokushima":"徳島","Ehime":"愛媛", "Kochi":"高知", 
#       "Fukuoka":"福岡", "Saga":"佐賀", "Nagasaki":"長崎",
#       "Kumamoto":"熊本", "Oita":"大分", "Miyazaki":"宮崎",
#       "Kagoshima":"鹿児島", "Okinawa":"沖縄"})
#


#####
#####
# Functions
#####
#####


###
# Secret get ocr json from a pdf file
###
# OCRテキスト取得  PDFは一回１０枚まで対応
# pdf_fn = 'pdf_diary_'+str(diary_id)+"_" + diary_date.strftime('%Y%m%d')
def get_ocr_json_from_pdf_file(pdffile, diary_id, diary_date, diary_page):
    api_url = os.environ.get('CLOVA_API_URL')
    secret_key = os.environ.get('CLOVA_SECRET_KEY')
    request_json = {
        "images": [
            {
                "format": "pdf",
                "name": "pdf_diary_"+str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+str(diary_page)
            }
        ],
        "version": "V2",
        "requestId": str(uuid.uuid4()),
        "timestamp": int(round(time.time() * 1000)),
        "lang":"ja"
    }
    
    headers = {
        "X-OCR-SECRET": secret_key
    }
    payload = {"message": json.dumps(request_json).encode('UTF-8')}
    files = [
        ("file", open(pdffile,'rb'))
    ]
    response = requests.request('POST', api_url, headers=headers, data = payload, files = files)
    # print(response.status_code)
    
    # response_json_fn = "res_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.json'
    response_json_fn = "res_" + str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+str(diary_page)+'.json'
    with open(response_json_fn, 'w') as f:
        json.dump(response.json(), f, indent=4)

    return response.json()


###
# Secret get ocr json from a jpeg file
###
def get_ocr_json_from_jpg_file(jpgfile, diary_id, diary_date, diary_page):
    api_url = os.environ.get('CLOVA_API_URL')
    secret_key = os.environ.get('CLOVA_SECRET_KEY')
    # request_json = {
    #    "images": [
    #        {
    #            "format": "jpg",
    #            "name": "jpg_diary_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')
    #        }
    #    ],
    #    "version": "V2",
    #    "requestId": str(uuid.uuid4()),
    #    "timestamp": int(round(time.time() * 1000)),
    #    "lang":"ja"
    #}
    request_json = {
        "images": [
            {
                "format": "jpg",
                "name": "jpg_diary_"+str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+str(diary_page)
            }
        ],
        "version": "V2",
        "requestId": str(uuid.uuid4()),
        "timestamp": int(round(time.time() * 1000)),
        "lang":"ja"
    }
    
    headers = {
        "X-OCR-SECRET": secret_key
    }
    payload = {"message": json.dumps(request_json).encode('UTF-8')}
    files = [
        ("file", open(jpgfile,'rb'))
    ]
    response = requests.request('POST', api_url, headers=headers, data = payload, files = files)
    # print(response.status_code)
    
    # response_json_fn = "res_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.json'
    response_json_fn = "res_" + str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+str(diary_page)+'.json'
    with open(response_json_fn, 'w') as f:
        json.dump(response.json(), f, indent=4)
    
    return response.json()


###
###
# Get ocr text from a pdf file through json
###
def get_ocr_dataframe_from_pdf_file(pdffile, diary_id, diary_date, diary_page):
    res_json = get_ocr_json_from_pdf_file(pdffile, diary_id, diary_date, diary_page)
    df_res = pd.read_json(res_json, orient='columns')
    
    d_values = []
    d_polys = []
    for i, val in enumerate(df_s['images'][0]['fields']):
        d_values.append(val['inferText'])
        d_polys.append(val['boundingPoly'])
        print('.'*20)
        print(val)
        for j, v in enumerate(val['boundingPoly']['vertices']):
            print('i'+str(i), 'j'+str(j), v['x'], v['y'])
            
    ret_df = 'abcde'           
    return(ret_df)
            



###
# Get ocr text from a jpg file through json
###
def get_ocr_dataframe_from_jpg_file(jpgfile, diary_id, diary_date, diary_page):
    res_json = get_ocr_json_from_jpg_file(jpgfile, diary_id, diary_date, diary_page)
    df_res = pd.read_json(res_json, orient='columns')
    
    d_values = []
    d_polys = []
    for i, val in enumerate(df_s['images'][0]['fields']):
        d_values.append(val['inferText'])
        d_polys.append(val['boundingPoly'])
        print('.'*20)
        print(val)
        for j, v in enumerate(val['boundingPoly']['vertices']):
            print('i'+str(i), 'j'+str(j), v['x'], v['y'])
            
    ret_df = 'abcde'           
    return(ret_df)
            
            
### Convert a DataFrame to CSV with utf-8-sig
###
@st.experimental_memo 
def convert_df_to_csv(df):
    df_to_cfv = df.to_csv().encode('utf-8-sig')
    return df_to_cfv


###
### Load a single XLSX file
###
# @st.experimental_memo(suppress_st_warning=True) # これを有効にすると読まなくなる，内部処理されてるのだろうから不要
def upload_xlsx_file_func():
    uploaded_xlsxfile = st.file_uploader("日誌のファイル(XLSX)を選んでください。",
                                          accept_multiple_files=False)
    return uploaded_xlsxfile


###
### Load a single PDF file
###
# @st.experimental_memo(suppress_st_warning=True) # これを有効にすると読まなくなる，内部処理されてるのだろうから不要
def upload_pdf_file_func():
    uploaded_pdffile = st.file_uploader("日誌の画像PDFファイルを選んでください。",
                                        accept_multiple_files=False)
    return uploaded_pdffile


###
# Show PDF
###
def show_pdf(file_path:str):
    """Show the PDF in Streamlit
    That returns as html component

    Parameters
    ----------
    file_path : [str]
        Uploaded PDF file path
    """

    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe width="50%" height="350" type="application/pdf" src="data:application/pdf;base64,{base64_pdf}" /iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


###
### Load multiple JPG files
###
# @st.experimental_memo(suppress_st_warning=True) # 内部処理されてるのだろうから不要
def upload_jpg_files_func():
    uploaded_jpgfiles = st.file_uploader("日誌のJPG画像を選んでください。",
                                         accept_multiple_files=True,
                                         type='jpg')
    return uploaded_jpgfiles


###
### Load single JPG file
###
# @st.experimental_memo(suppress_st_warning=True)  # 内部処理されてるのだろうから不要
def upload_jpg_file_func():
    uploaded_jpgfile = st.file_uploader("日誌のJPG画像を選んでください。",
                                         accept_multiple_files=False,
                                         type='jpg')
    return uploaded_jpgfile


###
### Take a photo by user's camera
###
# @st.experimental_memo(suppress_st_warning=True) # これを有効にすると読まなくなる，内部処理されてるのだろうから不要
def take_photo_func():
    # "Take a snapshot of today's diary"
    image_file_buffer = st.camera_input("日誌画像を撮影してください。")
    return image_file_buffer


###
### Calculate datetime from the special format date and time
###
#
# Wakeup and bed set
def calculate_datetime_from_date_and_time_strings(date_dt, hour_s, minute_s, pm_adjust_b):
#   time_tmp = datetime.time(hour=int(hour_s), minute=int(minute_s)) # without timezone
    time_tmp = datetime.time(hour=int(hour_s), minute=int(minute_s), tzinfo=tz_jst)
    # for check
    # print(time_tmp, time_tmp, time_tmp.tzinfo))
    if pm_adjust_b:
        ret = datetime.datetime.combine(date_dt, time_tmp) + datetime.timedelta(hours=12)
    else:
        ret = datetime.datetime.combine(date_dt, time_tmp)
    return ret


###
### Update counter
###
def update_counter():
    st.session_state.count += st.session_state.increment_value
    st.session_state.last_updated = st.session_state.update_time

    
#####
#####
# Main script
#####
#####
def main():
  try:    
    ###
    # Title display
    ###
    st.set_page_config(layout='wide', page_title='Diary manager')
    hide_menu_style = """
      <style>
      #MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
      </style>
      """
    st.markdown(hide_menu_style, unsafe_allow_html=True)
    st.title('排尿日誌マネージャー（産褥期）')
    st.text('Copyright (c) 2022 tmoriics (2022-07-29T22:30)')

    ###
    # Load heavy things
    ###
    form1_sample1_image = Image.open('images/diary_form1_sample1.png')
    form1_sample1_xlsx_image = Image.open('images/urination_data_sample1.png')

    ###
    # Setting by the sidebar
    ###
    graph_background_color = "#EEFFEE"
    # graph_background_color = st.sidebar.color_picker('Graph background color', value='#EEFFEE')
    # display_recognized_image = False
    display_recognized_image = st.sidebar.checkbox('Display recognized image(s)')

    ###
    ### Session state
    ###
    if 'count' not in st.session_state:
        st.session_state.count = 0
        st.session_state.last_updated = datetime.time(0, 0)

        
    ###
    ### Preparation of place holoder For Aggrid 
    ###
    ud_e = st.empty()

    
    ###
    # Column 1 start
    ###
    lcol1, rcol1 = st.columns(2)
    
    
    ###
    # Today set
    ###
    dt_now = datetime.datetime.now(tz_jst)
    rcol1.markdown('### 現在の日時：'+dt_now.strftime('%Y年%m月%d日 %H:%M'+'です。'))

    weather_url = 'https://weather.tsukumijima.net/api/forecast'
    params = {'city': 130010}
    r = requests.get(weather_url, params=params)
    weather_data=r.json()
    # with open('data/tmp.json', 'w') as f:
    #   json.dump(weather_data, f, indent=4)
    rcol1.image(weather_data['forecasts'][1]['image']['url'])
    rcol1.text('明日の東京の天気： '+weather_data['forecasts'][1]['telop'])
    # rcol1.write('HEADLINE'+weather_data['description']['headlineText'])
    # rcol1.write(weather_data['description']['text'][:101])

    
    ###
    # Check point by streamlit secrets management function
    ###
#     cp_e = st.empty()
#     with cp_e.container():
#         guess = st.text_input("What is the password?")
#         if guess != st.secrets["password"]:
#             st.warning("Please input the correct password.")
#             st.stop()
#         st.success('Thank you for inputting the password.')
#         # time.sleep(1)
#     cp_e.empty()
    
    
    ###
    # Diary ID input
    ###
    idi_e = lcol1.empty()
    with idi_e.container():
        diary_id_string = st.text_input("日誌の対象者IDを数字（4桁）で入力してください。")
        if len(diary_id_string) != 0:
            diary_id = int(float(diary_id_string))
            if diary_id <= 1000:
                st.stop()
            else:
                st.success('入力が確認できました。' + str(diary_id))
        else:
            st.warning('対象者IDの入力を御願いします。')
            st.stop()
    idi_e.empty()
    lcol1.info('日誌対象者IDは'+str(diary_id)+'です。')
    
    
    ###
    # Diary date input
    ###
    #
    # for dummy
    # diary_year_string = '2022'
    # diary_month_string = '5'
    # diary_day_string = '1'
    # ##### diary_date = datetime.date.fromisoformat(diary_date_string)
    # diary_date = datetime.date(year=int(diary_year_string),
    #                          month=int(diary_month_string), day=int(diary_day_string),tzinfo=tz_jst))
    #
    # by date_input
    di_e = lcol1.empty()
    with di_e.container():
        diary_date = st.date_input("日誌の日付を西暦で入力してください。",
                                   (dt_now+datetime.timedelta(days=3)).date())
        if diary_date == (dt_now+datetime.timedelta(days=3)).date():
            st.warning('日付の入力を御願いします。')
            st.stop()
        st.success('入力が確認できました。'+diary_date.strftime('%Y年%m月%d日'))
        # time.sleep(2)
    di_e.empty()
    lcol1.info('日誌対象日は'+diary_date.strftime('%Y年%m月%d日'+'です。'))
    
    ###
    # Diary page input
    ###
    # diary_page_string = '1'
    pi_e = lcol1.empty()
    with pi_e.container():
        diary_page_string = st.text_input("日誌の何ページ目か，数字で入力してください。")
        if len(diary_page_string) != 0:
            diary_page = int(float(diary_page_string))
            if diary_page >= 9999:
                st.stop()
            else:
                st.success('入力が確認できました。'+diary_page_string)
        else:
            st.warning('日誌のページの入力を御願いします。')
            st.stop()
    pi_e.empty()
    lcol1.info('日誌ページはp.'+diary_page_string+'です。')
    
    ###
    # Column 1 end
    ###
    
    
    ###
    # Wakeup and bed set
    ###
    #
    # Wakeup and bedtime default set
    wakeup_hour_string = '6'
    wakeup_minute_string = '00'
    wakeup_pm_adjust_boolean = False
    wakeup_datetime = calculate_datetime_from_date_and_time_strings(diary_date,
                                                                    wakeup_hour_string,
                                                                    wakeup_minute_string,
                                                                    wakeup_pm_adjust_boolean)
    bed_hour_string = '9'
    bed_minute_string = '00'
    bed_pm_adjust_boolean = True
    bed_datetime = calculate_datetime_from_date_and_time_strings(diary_date,
                                                                 bed_hour_string,
                                                                 bed_minute_string,
                                                                 bed_pm_adjust_boolean)
    next_wakeup_hour_string = '5'
    next_wakeup_minute_string = '55'
    next_wakeup_pm_adjust_boolean = False
    next_wakeup_datetime = calculate_datetime_from_date_and_time_strings(diary_date + datetime.timedelta(days=1),
                                                                         next_wakeup_hour_string,
                                                                         next_wakeup_minute_string,
                                                                         next_wakeup_pm_adjust_boolean)
    next_bed_hour_string = '9'
    next_bed_minute_string = '05'
    next_bed_pm_adjust_boolean = True
    next_bed_datetime = calculate_datetime_from_date_and_time_strings(diary_date + datetime.timedelta(days=1),
                                                                      next_bed_hour_string,
                                                                      next_bed_minute_string,
                                                                      next_bed_pm_adjust_boolean)
    #
    # Wakeup time display
    st.markdown('### 起床時刻：')
    st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
    
    
    ###
    # Diary read
    ###
    #
    # Diary image(s) upload
    st.header("日誌画像アップロード")
    ei = st.empty()
    with ei.container():
        ri = st.radio("日誌画像をアップロードしてください。スマホカメラでいま撮影しても構いません。",
                     ('画像ファイル(JPG)', '画像ファイル(PDF)', 'カメラ撮影', 'ファイル(XLSX)'),
                      horizontal=True)
        if ri == 'ファイル(XLSX)':
            uploaded_xlsx_file = upload_xlsx_file_func()
            if uploaded_xlsx_file is not None:
                st.success('日誌データが登録されました。')
                ocr_urination_data_df = pd.read_excel(uploaded_xlsx_file, sheet_name=0, index_col=None)
            else:
                st.write('このような日誌データ（XLSX形式。排尿回数13回以下）をアップロードしてください。')
                st.image(form1_sample1_xlsx_image, caption='日誌例', width=480)
                st.stop()
        elif ri == '画像ファイル(PDF)':
            uploaded_pdf_file = upload_pdf_file_func()
            if uploaded_pdf_file is not None:
                # uploaded_pdf_file is a file-like.
                st.success('日誌画像が登録されました。')
                # WIP
                # PDF対応難しい pdf2imageがLinuxで使えない。
                # Poppler問題を解決しないといけない。
                # さらにPDFから画像複数ページへの変換かハンドリング工夫をしないといけない。
                with tempfile.NamedTemporaryFile(delete=False) as pdf_tmp_file:
                    fp = Path(pdf_tmp_file.name)
                    fp.write_bytes(uploaded_pdf_file.getvalue())
                # pimgs = convert_from_path(pdf_tmp_file.name)
                # st.image(pimgs, caption='Uploaded image(s)')
                st.write(show_pdf(pdf_tmp_file.name))
                ### with しないならCLOSE()すべきだがwithしてるので不要。
                st.write("filename: ", uploaded_pdf_file.name)
                # WIP dummy data
                ocr_urination_data_df = pd.read_csv("data/urination_data_sample1.csv")
                # ocr_urination_data_df = get_ocr_dataframe_from_pdf_file(pdf_tmp_file.name, diary_id, diary_date, diary_page)
            else: 
                st.write('このような日誌画像をアップロードしてください。')
                st.image(form1_sample1_image, caption='日誌画像例', width=120)
                st.stop()
        # elif ri == '画像ファイル(JPG)':
            # WIP
            # JPGが複数ページのときに対応しないとならない
            # uploaded_jpg_files = upload_jpg_files_func()
            #     if uploaded_jpg_files:
            #         st.success('日誌画像が登録されました。')
            #         dimgs = []
            #         for i, uploaded_jpg_file in enumerate(uploaded_jpg_files):
            #             # 複数枚きたときの扱いはここから改変。下のdimgに一枚ずつ入っている。
            #             #    bytes_data = uploaded_jpg_file.read()
            #             bytes_data = uploaded_jpg_file.getvalue()
            #             dimgs.append(Image.open(io.BytesIO(bytes_data)))
            #             st.image(dimgs[i], caption='Uploaded jpeg image '+str(i),
            #                      use_column_width=True)
            #             st.write("filename: ", uploaded_jpg_file.name)
            #             # WIP dummy data
            #             ocr_urination_data_df = pd.read_csv(
            #                 "data/urination_data_sample1.csv")
        elif ri == '画像ファイル(JPG)':
            uploaded_jpg_file = upload_jpg_file_func()
            if uploaded_jpg_file is not None:
                # uploaded_jpg_file is a file-like.
                st.success('日誌画像が登録されました。')
                with tempfile.NamedTemporaryFile(delete=False) as jpg_tmp_file:
                    fp = Path(jpg_tmp_file.name)
                    fp.write_bytes(uploaded_jpg_file.getvalue())
                    # jimg = Image.open(jpg_tmp_file.name)
                    # st.image(jimg, caption='Uploaded jpg image',use_column_width=False)
                    # for check
                    # print(jpg_tmp_file.name)
                bytes_data = uploaded_jpg_file.getvalue()  
                dimg = Image.open(io.BytesIO(bytes_data))
                st.image(dimg, caption='Uploaded jpeg image ', use_column_width=True)
                ### with しないならCLOSE()すべきだがwithしてるので不要。
                st.write("filename: ", uploaded_jpg_file.name)
                # WIP dummy data
                ocr_urination_data_df = pd.read_csv("data/urination_data_sample1.csv")
                # ocr_urination_data_df = get_ocr_dataframe_from_jpg_file(jpg_tmp_file.name, diary_id, diary_date)
            else:
                st.write('このような日誌画像(JPG)をアップロードしてください。')
                w = form1_sample1_image.width
                h = form1_sample1_image.height
                im_a = Image.new("L", (w, h), 0)
                draw = ImageDraw.Draw(im_a)
                draw.ellipse( ((w*0.01,h*0.01), (w-w*0.01,h-h*0.01)), fill=255)
                im_a_filtered = im_a.filter(ImageFilter.GaussianBlur(96))
                form1_sample1_image.putalpha(im_a_filtered)
                form1_sample1_draw = ImageDraw.Draw(form1_sample1_image)
                form1_sample1_draw.line( ((w*0.01, h*0.01),
                                          (w-w*0.01, h*0.01), 
                                          (w-w*0.01, h-h*0.01), 
                                          (w*0.01, h-h*0.01), 
                                          (w*0.01, h*0.01)), 
                                         fill=(0, 192, 192), 
                                         width=48 )
                st.image(form1_sample1_image, caption='日誌画像例', width=240)
                st.stop()
        else: # 'カメラ撮影'
            photo_file_buffer = take_photo_func()
        #   camera_image = st.camera_input("Take a snapshot of today's diary")
        #   if camera_image:
        #       st.image(camera_image, caption='Taken diary snapshot')
            if photo_file_buffer is not None:
                ##########
                # photo_file_buffer is a file-like.
                st.success('撮影画像が登録されました。')
                ##########
                # WIP start erase or not?
                with tempfile.NamedTemporaryFile(delete=False) as photo_tmp_file:
                    fp = Path(photo_tmp_file.name)
                    fp.write_bytes(photo_file_buffer.getvalue())
                    # ccjimg = Image.open(photo_tmp_file.name)
                    # st.image(ccimg, caption='Taken photo',use_column_width=False)
                    # for check
                    # print(photo_tmp_file.name)
                # WIP end erase or not
                ##########
                cimg = Image.open(photo_file_buffer)
                cimg_array = np.array(cimg)
                st.write(cimg_array.shape)
                st.image(cimg, caption='日誌画像', width=256)
                # jpg_fn = 'diary_'+str(diary_id)+"_" + diary_date.strftime('%Y%m%d')+'.jpg'
                jpg_fn = str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.jpg'
                btn = st.download_button(label="Download the registered image",
                                         data=photo_file_buffer,
                                         file_name=jpg_fn,
                                         mime="image/jpg")
                # WIP dummy data
                ocr_urination_data_df = pd.read_csv("data/urination_data_sample1.csv")
                # ocr_urination_data_df = get_ocr_dataframe_from_jpg_file(photo_tmp_file.name, diary_id, diary_date)
            else:
                st.write('このような日誌画像を縦長で撮影してください。')
                st.image(form1_sample1_image, caption='日誌画像例', width=256)
                st.stop()
    # ei.empty()
    # if st.button("アップロードのやり直し"):
    #   st.experimental_memo.clear()
    
    
    ###
    # Diary recognition
    ###
    #
    # Diary image recognition by OCR
    #
    # virtual recognition
    # ocr_urination_data_df = pd.DataFrame(np.arange(13*8).reshape(13, 8),
    # columns=['時', '分', '排尿量', 'もれ', '尿意', '切迫感', '残尿感', 'メモ'])
    # ocr_urination_data_df.loc[:] = [
    ##     ['8', '00', '100', '無', '有・無', '有・無', '有・無', ''],
    ##     ['10', '30', '250', '無', '有・無', '有・無', '有・無', ''],
    ##     ['13', '00', '300', '無', '有・無', '有・無', '有・無', ''],
    ##     ['17', '00', '225', '無', '有・無', '有・無', '有・無', ''],
    ##     ['19', '55', '125', '無', '有・無', '有・無', '有・無', ''],
    ##     ['22', '30', '100', '無', '有・無', '有・無', '有・無', ''],
    ##     ['1', '30', '150', '無', '有・無', '有・無', '有・無', ''],
    ##     ['7', '00', '200', '無', '有・無', '有・無', '有・無', ''],
    ##     ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ##     ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ##     ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ##     ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    # ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', '']]
    # small checks
    # st.write(ocr_urination_data_df['もれ'])
    # st.write(ocr_urination_data_df['もれ'] == '有')
    # st.write(ocr_urination_data_df['もれ'] == '無')
    # st.write(ocr_urination_data_df[ocr_urination_data_df['もれ'] == '有'])
    # st.write(ocr_urination_data_df[ocr_urination_data_df['もれ'] == '無'])
    # WIP
    #
    # actual recognition
    #######################################

    ###
    ###
    ###
    # df creation from ocr df by deep copy 
    urination_data_df = ocr_urination_data_df.copy()
    # for check
    # st.write(urination_data_df)

    ###
    # Date and time adjustment (Day and hour)
    ###
    ##########
    # 2022-07-14T16:00 修正
    #  st.write("<font color='red'>最初の行が深夜０時以降だと日付けがおかしくなる｡</font>", unsafe_allow_html=True)
    # 2022-07-14T17:15 修正
    #  st.write("<font color='red'>零時以降が翌日日付けにならない｡</font>", unsafe_allow_html=True)
    ##########
    #
    # Add some English name columns
    urination_data_df['year'] = diary_date.strftime("%Y")
    urination_data_df['month'] = diary_date.strftime("%m")
    urination_data_df['day'] = diary_date.strftime("%d")
    urination_data_df['時'].replace('', np.nan, inplace=True)
    urination_data_df['分'].replace('', np.nan, inplace=True)
    urination_data_df['hour'] = urination_data_df['時'].astype(float)
    urination_data_df['minute'] = urination_data_df['分'].astype(float)
    urination_data_df['排尿量'].replace('', np.nan, inplace=True)
    urination_data_df['micturition'] = urination_data_df['排尿量'].astype(float)
    # urination_data_df['catheterization'] = urination_data_df['導尿量'].astype(float)
    urination_data_df['no_leakage'] = [True if b ==
                                       '無' else False for b in urination_data_df['もれ']]
    urination_data_df['leakage'] = [1.0 if b !=
                                    '無' else 0.0 for b in urination_data_df['もれ']]
    urination_data_df['desire'] = [True if b ==
                                   '有' else False for b in urination_data_df['尿意']]
    urination_data_df['urgency'] = [True if b ==
                                    '有' else False for b in urination_data_df['切迫感']]
    urination_data_df['remaining'] = [True if b ==
                                      '有' else False for b in urination_data_df['残尿感']]
    urination_data_df['memo'] = urination_data_df['メモ']
    # for check
    # print(urination_data_df[['year', 'month', 'day', 'hour', 'minute']])
    urination_data_df['datetime_tmp'] = pd.to_datetime(
        urination_data_df[['year', 'month', 'day', 'hour', 'minute']]).dt.tz_localize('Asia/Tokyo')
    #####  COERCE  urination_data_df[['year', 'month', 'day', 'hour', 'minute']], errors='coerce')
    urination_data_df['datetime_tmp_before'] = urination_data_df['datetime_tmp'].shift(1)
    urination_data_df['datetime_tmp_after_check'] = urination_data_df['datetime_tmp'] > urination_data_df['datetime_tmp_before']
    # for check
    # print(urination_data_df['datetime_tmp_after_check'])
    
    #
    # COPY
    urination_data_df['datetime'] = urination_data_df['datetime_tmp']
    
    #
    # After midnight adjustment
    after_midnight = False
    after_midnight_state = ''
    for index, row in urination_data_df.iterrows():
        if (after_midnight == False) and (row['datetime_tmp_after_check'] == False):
            if index == 0:
                if row['datetime_tmp'] < wakeup_datetime:
                    after_midnight = True
                    # 24, 25時以降にhourをいじり, datetimeをつくる
                    urination_data_df.at[index,
                                         'hour'] = urination_data_df.at[index, 'hour'] + 24
                    urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                                   'datetime_tmp'] + datetime.timedelta(hours=24)
                    after_midnight_state = "Line 0 and the first after midnight"
                else:
                    after_midnight_state = "Line 0"
                    urination_data_df.at[index,
                                         'datetime'] = urination_data_df.at[index, 'datetime_tmp']
            else:
                after_midnight = True
                # 24, 25時以降にhourをいじり, datetimeをつくる
                after_midnight_state = "First after midnight"
                #
                # rowhour = rowhour + 24
                # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
                urination_data_df.at[index,
                                     'hour'] = urination_data_df.at[index, 'hour'] + 24
                urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                               'datetime_tmp'] + datetime.timedelta(hours=24)
        elif after_midnight == True:
            # 24, 25時以降ということであるので，hourをいじり, datetimeをつくる
            after_midnight_state = "Second or later after midnight"
            urination_data_df.at[index,
                                 'hour'] = urination_data_df.at[index, 'hour'] + 24
            urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                           'datetime_tmp'] + datetime.timedelta(hours=24)
            # rowhour = rowhour + 24
            # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
        else:
            after_midnight_state = "Before midnight"
            urination_data_df.at[index,
                                 'datetime'] = urination_data_df.at[index, 'datetime_tmp']
        # for check
        print(after_midnight_state)
    # for check
    print(urination_data_df[['datetime', 'datetime_tmp_after_check', 'day', 'hour']])
    
    #
    # Calculate time difference
    urination_data_df['time_difference'] = urination_data_df['datetime'].diff()
    urination_data_df['time_difference'] = urination_data_df['time_difference'].dt.total_seconds() / 60.0
    
    #
    # Time phase
    first_after_wakeup_found = False
    # WIP
    # 最初の行が９時以降ならfirst_after_wakeup_found = Trueにしてしまうことにするかどうか。
    first_after_next_wakeup_found = False
    urination_data_df['time_phase'] = urination_data_df['datetime']
    for index, row in urination_data_df.iterrows():
        if row['datetime'] < wakeup_datetime:
            urination_data_df.at[index, 'time_phase'] = 'before_wakeup'
        elif row['datetime'] < bed_datetime:
            if first_after_wakeup_found == False:
                first_after_wakeup_found = True
                urination_data_df.at[index,
                                     'time_phase'] = 'first_after_wakeup'
            else:
                urination_data_df.at[index, 'time_phase'] = 'day_time'
        elif row['datetime'] < next_wakeup_datetime:
            urination_data_df.at[index, 'time_phase'] = 'after_bed'
        else:
            if first_after_next_wakeup_found == False:
                first_after_next_wakeup_found = True
                urination_data_df.at[index, 'time_phase'] = 'first_after_next_wakeup'
            else:
                urination_data_df.at[index, 'time_phase'] = 'next_day_time'
    #
    #  first after bed datetime for FIST SLEEP CALCULATION
    first_after_bed_found = False
    for index, row in urination_data_df.iterrows():
        if row['datetime'] >= bed_datetime:
            if first_after_bed_found == False:
                first_after_bed_found = True
                first_after_bed_datetime = row['datetime']
                
    #
    # Drop some temporal English name columns
    urination_data_df.drop(columns=[
        'datetime_tmp', 'datetime_tmp_before', 'datetime_tmp_after_check'], inplace=True)
    # for check
    # st.write(urination_data_df)

    
    ###
    # Recognized diary display
    ###
    rd_e = st.empty()
    with rd_e.container():
        #
        # Recognized diary document display
        st.header("日誌データ（認識結果）")

        ##
        # OCR image(s) display
        ##
        if display_recognized_image:
            st.subheader("画像（読み取り結果）")
            if ri == '画像ファイル(JPG)':
                resimg = Image.open(
                    'images/diary_form1_sample1_virtually_recognized.png')
                st.image(resimg, caption='認識された日誌画像', width=240)
            elif ri == '画像ファイル(PDF)':
                resimg = Image.open(
                    'images/diary_form1_sample1_virtually_recognized.png')
                st.image(resimg, caption='認識された日誌画像', width=120)
            elif ri == 'カメラ撮影':
                resimg = Image.open(
                    'images/diary_form1_sample1_virtually_recognized.png')
                st.image(resimg, caption='認識された日誌画像', width=256)
            else:
                st.warning('画像ではなく表ファイルがアップロードされています（画像認識は無し）。')
                
        ##
        # OCR diary doument csv
        ###
        st.subheader("テーブル（読み取り結果）")
        #
        # OCR diary document csv by st.table
        st.table(ocr_urination_data_df)
        #
        # Downloadable OCR diary document csv by st.table
        ocr_urination_data_csv = convert_df_to_csv(ocr_urination_data_df)
        # ocr_urination_data_csv_fn = "ocr_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        ocr_urination_data_csv_fn = "ocr_"+ str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.csv'
        st.download_button(label="Download OCR diary document as CSV",
                           data=ocr_urination_data_csv,
                           file_name=ocr_urination_data_csv_fn,
                           mime='text/csv')

        ###
        # Recognized image(s) display
        ###
        st.subheader("テーブル（認識結果）")

        ###
        # Downloadable recognized document (=data) Type A
        ###
        #
        # Downloadable recognized document preparation Type A
        ud_df1_tmp = urination_data_df.drop(columns=['時', '分',
                                                     'year', 'month', 'day',
                                                     'hour', 'minute',
                                                     'micturition',
                                                     'leakage', 'desire', 'urgency', 'remaining',
                                                     'memo'])
        ud_df1 = ud_df1_tmp.dropna(subset=['datetime'])
        #
        # Downloadable recognized document display Type A by st.table
        st.table(ud_df1.style.highlight_max(axis=0))
        #
        # Downloadable recognized document CSV (=data CSV)
        ud_df1_csv = convert_df_to_csv(ud_df1)
        # ud_df1_csv_fn = "ud_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        ud_df1_csv_fn = "ud_"+ str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.csv'
        # st.subheader("日誌データ（認識結果）のCSV形式でのダウンロード")
        st.download_button(label="Download recognized data as CSV",
                           data=ud_df1_csv,
                           file_name=ud_df1_csv_fn,
                           mime='text/csv')
                
        ###
        # Downloadable editable document (=data) Type B
        ###
        #
        # Downloadable editable document preparation Type B 
        ud_df2_tmp = urination_data_df.drop(columns=['時', '分',
                                                     '排尿量', 'もれ',
                                                     '尿意', '切迫感', '残尿感', 'メモ', 
                                                     'year', 'month', 'day',
                                                     'hour', 'minute',
                                                     'time_difference'])
        
        #
        # Downloadable editable document display Type B by Aggrid
        st.subheader("テーブル（編集用）")
        cellstyle_jscode = JsCode(
            """
        function(params) {
            if (params.value.includes('day_time')) {
                return {
                    'color': 'white',
                    'backgroundColor': 'darkred'
                }
            } else {
                return {
                    'color': 'black',
                    'backgroundColor': 'white'
                }
            }
        };
        """
        )
        urination_data_gb = GridOptionsBuilder.from_dataframe(ud_df2_tmp)
        urination_data_gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        urination_data_gb.configure_pagination()
        urination_data_gb.configure_side_bar()
#       urination_data_gb.configure_default_column(groupable=True, value=True, enableRowGroup=True,
#                                                  aggFunc="sum", editable=True)
        urination_data_gb.configure_default_column(groupable=True, editable=True)
        urination_data_gb.configure_column("time_phase", cellStyle=cellstyle_jscode)
        urination_data_gb.configure_column("datetime", type=["customeDateTimeFormat"],
                                           custom_format_string='yyyy-MM-dd HH:mm zzz')
        urination_data_gridOptions = urination_data_gb.build()
        ud_gd = AgGrid(ud_df2_tmp, theme='blue',
                       gridOptions=urination_data_gridOptions,
                       # enable_enterprise_modules=True,
                       allow_unsafe_jscode=True,
                       update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,)
        #
        # Downloadable edited document preparation Type B
        ud_df2 = ud_gd['data']
        # Downloadable edited document Type B 
        ud_df2_csv = convert_df_to_csv(ud_df2)
        # ud_df2_csv_fn = "gd_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        ud_df2_csv_fn = "gd_"+ str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.csv'
        # st.subheader("日誌データ（編集後）のCSV形式でのダウンロード")
        st.download_button(label="Download edited data as CSV",
                           data=ud_df2_csv,
                           file_name=ud_df2_csv_fn,
                           mime='text/csv')

        #
        # plotly graph
        with ud_e.container():
            # st.write(urination_data_gd["selected_rows"])
            selected_rows_gd = ud_gd["selected_rows"]
            selected_rows = pd.DataFrame(selected_rows_gd)
            if len(selected_rows) != 0:
                fig_gd = px.bar(selected_rows, "time_phase", color="no_leakage")
                st.plotly_chart(fig_gd)
    
    
    ###
    # Micturition graph display
    ###
    md_e = st.empty()
    with md_e.container():
        st.header("当該日の尿量・漏れ量グラフ")
        vol_df = urination_data_df[['datetime', 'micturition', 'leakage']]
        ### novice localize way
        ### vol_df['datetime_Japan'] = urination_data_df['datetime'].dt.tz_localize('Asia/Tokyo')
        ### vol_df.drop(columns='datetime', inplace=True)
        ## chart_df = pd.melt(vol_df, id_vars=['datetime_Japan'],
        ##                     var_name='parameter', value_name='value')
        ## chart_base = alt.Chart(chart_df).encode(x='datetime_Japan', y='value', color='parameter')
        ### aware utc/jst way
        chart_df = pd.melt(vol_df, id_vars=['datetime'],
                           var_name='parameter', value_name='value')
        chart_base = alt.Chart(chart_df).encode(x='datetime', y='value', color='parameter')
        chart_layer = alt.layer(chart_base.mark_line(), chart_base.mark_point(), background=graph_background_color, title='Volume and leak')
        st.altair_chart(chart_layer, use_container_width=True)
        # for check
        # st.write(pd.DataFrame(vol_df))
    
    
    ###
    # Column 2 start 
    ###
    lcol2, rcol2 = st.columns(2)
    
    ###
    # Wakeup time and bed time display
    ###
    wb_e = rcol2.empty()
    with wb_e.container():
        st.header('起床時刻・就寝時刻・翌日起床時刻・翌日就寝時刻：')
        st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        st.text('対象日の就寝時刻は' + bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        st.text('対象日の就寝時刻と起床時刻の差は' + str(bed_datetime-wakeup_datetime) + 'です。')
        st.text('翌日の起床時刻は' + next_wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        st.text('翌朝の起床時刻と対象日の就寝時刻の差（つまり睡眠時間）' +
                str(next_wakeup_datetime - bed_datetime) + 'です。')
        st.text('翌日の就寝時刻は' + next_bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です。')
        st.text('翌日の就寝時刻と起床時刻の差は' +
                str(next_bed_datetime - next_wakeup_datetime) + 'です。')
        
        
    ###
    # Indices display
    ###
    ind_e = lcol2.empty()
    with ind_e.container():
        st.header('排尿関連指標：')
        if first_after_bed_found == True:
            first_sleep_time = (first_after_bed_datetime - bed_datetime).total_seconds() / 60
        else:
            first_sleep_time = 0
        number_of_urination = len(urination_data_df[(urination_data_df['time_phase'] == 'day_time') | (
            urination_data_df['time_phase'] == 'after_bed') | (urination_data_df['time_phase'] == 'first_after_next_wakeup')])
        number_of_daytime_urination = len(
            urination_data_df[urination_data_df['time_phase'] == 'day_time'])
        number_of_nocturnal_urination = len(urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')])
        daytime_urination_volume = urination_data_df[urination_data_df['time_phase'] == 'day_time'].micturition.sum(
        )
        nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.sum()
        urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.sum()
        if np.isnan(daytime_urination_volume) == True:
            daytime_urination_volume =0.0
        if np.isnan(nocturnal_urination_volume) == True:
            nocturnal_urination_volume =0.0
        if np.isnan(urination_volume) == True:
            urination_volume =0.0
        if number_of_urination != 0:
            urination_volume_per_cycle = urination_volume / number_of_urination
        else:
            urination_volume_per_cycle = 0
        minimum_single_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.min()
        maximum_single_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup') | (urination_data_df['time_phase'] == 'day_time')].micturition.max()
        minimum_single_nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.min()
        maximum_single_nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed')
                                                                      | (
            urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.max()
        average_urination_interval = urination_data_df.mean(
            numeric_only=True).time_difference
        minimum_urination_interval = urination_data_df.min(
            numeric_only=True).time_difference
        maximum_urination_interval = urination_data_df.max(
            numeric_only=True).time_difference
        if np.isnan(maximum_single_urination_volume) == True:
            maximum_single_urination_volume =0.0
        if np.isnan(minimum_single_urination_volume) == True:
            minimum_single_urination_volume =0.0
        if np.isnan(maximum_single_nocturnal_urination_volume) == True:
            maximum_single_nocturnal_urination_volume =0.0
        if np.isnan(minimum_single_nocturnal_urination_volume) == True:
            minimum_single_nocturnal_urination_volume =0.0
        if urination_volume != 0: 
            noctural_plyuria_index = float(
                nocturnal_urination_volume * 100.0 / urination_volume)
        else:
            noctural_plyuria_index = 0.0
        
        # WIP
        # maximum_voided_volumeに漏れや導尿をいれてない
        maximum_voided_volume = maximum_single_urination_volume
        if maximum_voided_volume != 0:
            nocturia_index = math.ceil(float(nocturnal_urination_volume / maximum_voided_volume))
        else:
            nocturia_index = int(1)
        pnv = nocturia_index - 1
        nbci = number_of_nocturnal_urination - pnv
        #
        number_of_urinary_tracts = 0
        urinary_tract_volume = 0
        urinary_tract_volume_per_cycle = 0
        minimum_single_urinary_tract_volume = 0
        maximum_single_urinary_tract_volume = 0
        # 昼間排尿回数 8回以上 昼間頻尿
        # 夜間排尿回数 1回以上 夜間頻尿 Nocturia episodesという
        # 最大一回排尿量 maximum voided volume MVV という
        # 夜間多尿指数(NPi) 夜間排尿量/一日尿量 （若年20％，高齢33％のスレショルド）
        #
        # 夜間頻尿指数(Ni) 夜間排尿量/最大一回排尿量 （Ni>1が夜間頻尿。切り上げ）
        # 予測夜間排尿回数(PNV)  (夜間排尿量/最大一回排尿量) - 1
        # 夜間膀胱容量指数(NBCi) 実際の夜間排尿回数-予測夜間排尿回数 （NBCi>0を機能的膀胱容量低下での夜間頻尿）
        # 多尿 一日尿量が40ml/kg以上というスレショルド
        # 初回睡眠時間 Hours of undisturbed sleep
        #
        # 体重
        # 最大排尿量/体重 （4ml/kg以下が機能的膀胱容量低下のスレショルド）
        # 残尿回数
        # 一日残尿量
        # 尿失禁回数
        # 尿失禁量(g/日)

        ###
        # Downloadable indices 
        ###
        ###############################
        # WIP
        # first date handling should be re-designed for web
        diary_first_date = diary_date
        #
        #
        # Downloadable indices preparation
        diary_first_date_int = int(diary_first_date.strftime('%Y%m%d'))
        diary_date_int = int(diary_date.strftime('%Y%m%d'))
        indices_df = pd.DataFrame(columns=['指標', '値', '単位'],
                                  data=[
                                      ['日誌対象者ID', int(diary_id), ''],
                                      ['日誌初回日付', int(diary_first_date_int), ''],
                                      ['日誌ページ', int(diary_page), ''],
                                      ['日誌日付', int(diary_date_int), ''],
                                      ['初回睡眠時間(HUS)', int(first_sleep_time), '分'],
                                      ['最大尿量(MVV)', int(
                                          maximum_voided_volume), 'ml'],
                                      ['夜間多尿指数(NPi)', int(
                                          noctural_plyuria_index), '％'],
                                      ['夜間頻尿指数(Ni)', int(nocturia_index), ''],
                                      ['予測夜間排尿回数(PNV)', int(pnv), '回'],
                                      ['夜間膀胱容量指数(NBCi)', int(nbci), '回'],
                                      ['昼間排尿回数', int(
                                          number_of_daytime_urination), '回'],
                                      ['夜間排尿回数', int(
                                          number_of_nocturnal_urination), '回'],
                                      ['一日排尿回数', int(number_of_urination), '回'],
                                      ['昼間排尿量', int(
                                          daytime_urination_volume), 'ml'],
                                      ['夜間排尿量(NUV)', int(
                                          nocturnal_urination_volume), 'ml'],
                                      ['一日排尿量', int(urination_volume), 'ml'],
                                      ['一回排尿量', int(
                                          urination_volume_per_cycle), 'ml / 回'],
                                      ['最小一回排尿量', int(
                                          minimum_single_urination_volume), 'ml'],
                                      ['最大一回排尿量', int(
                                          maximum_single_urination_volume), 'ml'],
                                      ['最小一回夜間排尿量', int(
                                          minimum_single_nocturnal_urination_volume), 'ml'],
                                      ['最大一回夜間排尿量(NBC)', int(
                                          maximum_single_nocturnal_urination_volume), 'ml'],
                                      ['平均排尿間隔', int(
                                          average_urination_interval), '分'],
                                      ['最小排尿間隔', int(
                                          minimum_urination_interval), '分'],
                                      ['最大排尿間隔', int(
                                          maximum_urination_interval), '分'],
                                      ['一日導尿回数', int(
                                          number_of_urinary_tracts), '回'],
                                      ['一日導尿量', int(urinary_tract_volume), 'ml'],
                                      ['一回導尿量', int(
                                          urinary_tract_volume_per_cycle), 'ml / 回'],
                                      ['最小一回導尿量', int(
                                          minimum_single_urinary_tract_volume), 'ml'],
                                      ['最大一回導尿量', int(
                                          maximum_single_urinary_tract_volume), 'ml'],
        ])
        
        #
        # Downloadable indices display
        st.table(indices_df)
        #
        # Downloadable indices CSV
        indices_csv = convert_df_to_csv(indices_df)
        # indices_csv_fn = "indices_" +  str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        indices_csv_fn = "indices_"+ str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.csv'
        st.subheader("排尿関連指標のCSV形式でのダウンロード")
        st.download_button(label="Download indices as CSV",
                           data=indices_csv,
                           file_name=indices_csv_fn,
                           mime='text/csv')
        
        #
        # Downloadable composite XLSX
        ########## WIP
        ########## creating multi sheet by BytesIO is not working 20220728T1937
#        ud_df1.insert(0, 'date_time', ud_df1['datetime'].apply(lambda d: pd.Timestamp(d).isoformat()))
#        ud_df1_for_composite = ud_df1.drop(columns='datetime')
#        composite_xlsx_fn = "composite_"+ str(diary_id)+"_"+diary_date.strftime('%m%d')+'_p'+diary_page_string+'.xlsx'
#        composite_xlsx_output = io.BytesIO()
#        with pd.ExcelWriter(composite_xlsx_output) as composite_writer:
#            ud_df1_for_composite.to_excel(composite_writer, sheet_name = ud_df1_csv_fn)
#            indices_df.to_excel(composite_writer, sheet_name = indices_csv_fn)
#            ocr_urination_data_df.to_excel(composite_writer, sheet_name = ocr_urination_data_csv_fn)
#            # composite_writer.save()
#            composite_xlsx_processed_data = composite_xlsx_output.getvalue()
#        st.subheader("複合したXLSX形式でのダウンロード")
#        st.download_button(label="Download composite as XLSX",
#                           data=composite_xlsx_processed_data,
#                           file_name=composite_xlsx_fn)
        
    ###
    # Column 2 end
    ###
    
    ###
    ### Refresh if needed
    ###
    #
    # st.button("Re-run")

  except Exception:
    print("Exception from app. ")
    print("-"*60)
    traceback.print_exc(file=sys.stdout)
    print("-"*60)
          
    
###
###
###
if __name__ == "__main__":
    main()





# df = pd.read_sql('SELECT * FROM product', con=conn)
# st.write(df)
# gd = GridOptionsBuilder.from_dataframe(df)
# gd.configure_pagination(enabled=True)
# gd.configure_default_column(editable=True, groupable=True)
# sel_mode = st.radio('Selection Type', options=['single', 'multiple'])
# gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
# gridoptions = gd.build()
# grid_table = AgGrid(df, gridOptions=gridoptions,
#                     update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
#                     height=500,
#                     allow_unsafe_jscode=True,
#                     # enable_enterprise_modules = True,
#                     theme='fresh')
# 
# sel_row = grid_table["selected_rows"]
# st.subheader("Output")
# st.write(sel_row)
# 
# df_selected = pd.DataFrame(sel_row)
# 
# if st.button('Update db', key=1):
#     for i, r in df_selected.iterrows():
#         id = r['id']
#         cnt = r['count']
#         update(id, cnt)
# 
#     st.write('##### Updated db')
#     df_update = pd.read_sql('SELECT * FROM product', con=conn)
#     st.write(df_update)
# 
# cur.close()
# conn.close()


#  aa_e = st.empty()
#  with aa_e.form(key='cp-e-form'):
#      message = st.text_input("Input your message, please.")
#      submitted = st.form_submit_button('送信')
#      if submitted: 
#        st.success('The message is '+message)


#######
#######
#######
#######
#######

