# -*- coding: utf-8 -*-

#####
# home.py
#####
# 7/17 WIP cacheが働かない。memo機能も試したが十分早いのでUploadのCacheは使わないでしばらくいく。
# 2022-07-15T06:00
# 2022-07-15T09:30
# 2022-07-15T14:30
# 2022-07-15T21:00
# 2022-07-17T07:00
# 2022-07-17T23:00
# 2022-07-18T07:00
# 2022-07-18T23:18
# 2022-07-19T15:49 Trying session state
# 
#####


###
# Imports
###
import math
import locale
import datetime
import time
import io
import base64
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen
import requests
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
# import cv2
import altair as alt
import streamlit as st
# from pdf2image import convert_from_path


#####
#####
# Locale and others
#####
#####

###
# Locale
###
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

###
# Timezone
###
tz_jst = datetime.timezone(datetime.timedelta(hours=9))


#####
#####
# Functions
#####
#####

###
# PDF
###
# def show_pdf(file_path:str):
#     """Show the PDF in Streamlit
#     That returns as html component
#
#     Parameters
#     ----------
#     file_path : [str]
#         Uploaded PDF file path
#     """
#
#     with open(file_path, "rb") as f:
#         base64_pdf = base64.b64encode(f.read()).decode("utf-8")
#     pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf">'
#     st.markdown(pdf_display, unsafe_allow_html=True)
#

###
###
###
@st.experimental_memo
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8-sig')


###
###
###
# @st.experimental_memo(suppress_st_warning=True)
def upload_pdf_file_func():
    #    uploaded_file = st.file_uploader("Choose a diary image of the day",
    uploaded_pdffile = st.file_uploader("日誌の画像PDFファイルを選んでください。",
                                        accept_multiple_files=False)
    return uploaded_pdffile


###
###
###
# @st.experimental_memo(suppress_st_warning=True) # これを有効にすると読んでも[]のままになる。
def upload_jpg_files_func():
    #   uploaded_jpgfiles = st.file_uploader("Choose diary images of the day",
    uploaded_jpgfiles = st.file_uploader("日誌のJPG画像を選んでください。",
                                         accept_multiple_files=True,
                                         type='jpg')
    return uploaded_jpgfiles


###
###
###
# @st.cache(suppress_st_warning=True)
# @st.experimental_memo(suppress_st_warning=True)
def take_photo_func():
    #   image_file_buffer = st.camera_input("Take a snapshot of today's diary")
    image_file_buffer = st.camera_input("日誌画像を撮影してください。")
    return image_file_buffer


#####
#####
# Main script
#####
#####

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
st.text('Copyright (c) 2022 tmoriics (2022-07-17T20:41)')


###
# Setting by the sidebar
###
#
# Setup parameters
graph_background_color = "#EEFFEE"
display_recognized_image = False
#
# Sidebar display
# # # graph_background_color = st.sidebar.color_picker('Graph background color', value='#EEFFEE')
display_recognized_image = st.sidebar.checkbox('Display recognized image(s)')


###
# Column 1 start
###
lcol1, rcol1 = st.columns(2)


###
# Today set
###
dt_now = datetime.datetime.now(tz_jst)
rcol1.text('現在の日時：'+dt_now.strftime('%Y年%m月%d日 %H:%M:%S'+'です。'))


###
# Check point by streamlit secrets management function
###
cp_e = st.empty()
with cp_e.container():
    guess = st.text_input("What is the password?")
    if guess != st.secrets["password"]:
        st.warning("Please input the password.")
        st.stop()
    st.success('Thank you for inputting the password.')
    # time.sleep(1)
cp_e.empty()


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
# diary_year_string = '2022'
# diary_month_string = '5'
# diary_day_string = '1'
# ##### diary_date = datetime.date.fromisoformat(diary_date_string)
# diary_date = datetime.date(year=int(diary_year_string),
#                          month=int(diary_month_string), day=int(diary_day_string),tzinfo=tz_jst))
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
# Column 1 end
###


###
# Wakeup and bed set
###
#
# Wakeup and bed set
def calculate_datetime_from_date_and_time_strings(date_dt, hour_s, minute_s, pm_adjust_b):
#   time_tmp = datetime.time(hour=int(hour_s), minute=int(minute_s))
    time_tmp = datetime.time(hour=int(hour_s), minute=int(minute_s), tzinfo=tz_jst)
    # print(time_tmp)
    # print(type(time_tmp))
    # print(time_tmp.tzinfo)
    if pm_adjust_b:
        ret = datetime.datetime.combine(
            date_dt, time_tmp) + datetime.timedelta(hours=12)
    else:
        ret = datetime.datetime.combine(date_dt, time_tmp)
    return ret


# wakeup_time_tmp = datetime.time(
#     hour=int(wakeup_hour_string), minute=int(wakeup_minute_string),tzinfo=tz_jst))
# if wakeup_pm_adjust_boolean:
#     wakeup_datetime = datetime.datetime.combine(
#         diary_date, wakeup_time_tmp) + datetime.timedelta(hours=12)
# else:
#     wakeup_datetime = datetime.datetime.combine(diary_date, wakeup_time_tmp)
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
st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')


###
# Diary read
###
#
# Diary image(s) upload
st.header("日誌画像アップロード")
# Image.open('images/samp1.jpg')
form1_sample1_image = Image.open('images/diary_form1_sample1.png')
form1_sample1_xlsx_image = Image.open('images/urination_data_sample1.png')
ei = st.empty()
with ei.container():
    # ri = st.radio("日誌画像をアップロードしてください。スマホカメラでいま撮影しても構いません。",
    #              ('画像ファイル(PDF)', '画像ファイル(JPG)', 'カメラ撮影', 'ファイル(XLSX)'),
    ri = st.radio("日誌データをアップロードしてください。スマホカメラでいま撮影しても構いません。",
                  ('画像ファイル(JPG)', 'カメラ撮影', 'ファイル(XLSX)'),
                  horizontal=True)
    # if ri == 'PDFファイル':
    #    uploaded_pdf_file = upload_pdf_file_func()
    #    if uploaded_pdf_file is not None:
    #        st.success('日誌画像が登録されました．')
    #        # Poppler問題を解決しないといけないさらにPDFから画像複数ページへの変換をしないといけない
    #        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #          fp = Path(tmp_file.name)
    #          fp.write_bytes(uploaded_pdf_file.getvalue())
    #          pmgs = convert_from_path(tmp_file.name)
    #          st.image(pimgs, caption='Uploaded image')
    #      FP.CLOSE()すべきかな？
    #    else: 
    #     st.write('このような日誌画像をアップロードしてください．')
    #     st.image(form1_sample1_image, caption='日誌画像例', width=120)
    #     st.stop()
    if ri == '画像ファイル(JPG)':
        uploaded_jpg_files = upload_jpg_files_func()
        if uploaded_jpg_files:
            st.success('日誌画像が登録されました．')
            dimgs = []
            for i, uploaded_jpg_file in enumerate(uploaded_jpg_files):
                # 複数枚きたときの扱いはこれでよい。下のdimgに一枚ずつ入っている。
                #               bytes_data = uploaded_jpg_file.read()
                bytes_data = uploaded_jpg_file.getvalue()
                dimgs.append(Image.open(io.BytesIO(bytes_data)))
                st.image(dimgs[i], caption='Uploaded jpeg image '+str(i),
                         use_column_width=True)
                st.write("filename: ", uploaded_jpg_file.name)
                # WIP dummy data
                urination_data_df = pd.read_csv(
                    "data/urination_data_sample1.csv")
        else:
            st.write('このような日誌画像(JPG)をアップロードしてください．')
            st.image(form1_sample1_image, caption='日誌画像例', width=240)
            st.stop()
    elif ri == 'ファイル(XLSX)':
        uploaded_xlsx_file = st.file_uploader("日誌のファイル(XLSX)を選んでください。",
                                              accept_multiple_files=False)
        if uploaded_xlsx_file is not None:
            st.success('日誌データが登録されました。')
            urination_data_df = pd.read_excel(
                uploaded_xlsx_file, sheet_name=0, index_col=None)
        else:
            st.write('このような日誌データ（XLSX形式。最大排尿回数13回）をアップロードしてください．')
            st.image(form1_sample1_xlsx_image, caption='日誌例', width=480)
            st.stop()
#   elif ri == 'カメラ撮影':
    else:
        photo_file_buffer = take_photo_func()
    #   camera_image = st.camera_input("Take a snapshot of today's diary")
    #   if camera_image:
    #       st.image(camera_image, caption='Taken diary snapshot')
        if photo_file_buffer is not None:
            st.success('撮影画像が登録されました．')
            cimg = Image.open(photo_file_buffer)
            cimg_array = np.array(cimg)
            st.write(cimg_array.shape)
            st.image(cimg, caption='日誌画像', width=256)
            jpg_fn = 'diary_'+str(diary_id)+"_" + \
                diary_date.strftime('%Y%m%d')+'.jpg'
            btn = st.download_button(label="Download the registered image",
                                     data=photo_file_buffer,
                                     file_name=jpg_fn,
                                     mime="image/jpg")
            # WIP dummy data
            urination_data_df = pd.read_csv("data/urination_data_sample1.csv")
        else:
            st.write('このような日誌画像を縦長で撮影してください．')
            st.image(form1_sample1_image, caption='日誌画像例', width=240)
            st.stop()
# ei.empty()
# if st.button("アップロードのやり直し"):
#   st.experimental_memo.clear()


###
# Diary recognition
###
#
# Diary image recognition by OCR
# WIP
# virtual recognition
# urination_data_df = pd.DataFrame(np.arange(13*8).reshape(13, 8),
# columns=['時', '分', '排尿量', 'もれ', '尿意', '切迫感', '残尿感', 'メモ'])
# urination_data_df.loc[:] = [
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
# st.write(urination_data_df['もれ'])
# st.write(urination_data_df['もれ'] == '有')
# st.write(urination_data_df['もれ'] == '無')
# st.write(urination_data_df[urination_data_df['もれ'] == '有'])
# st.write(urination_data_df[urination_data_df['もれ'] == '無'])


###
# hidden function Downloadable diary document csv
###
# urination_data_csv = convert_df_to_csv(urination_data_df)
# urination_data_csv_fn = "diary_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
# st.download_button(label="Download diary document as CSV",
#                    data=urination_data_csv,
#                    file_name=urination_data_csv_fn,
#                    mime='text/csv')


###
# Recognized diary display
###
rd_e = st.empty()
with rd_e.container():
    #
    # Recognized diary document display
    st.header("日誌データ（認識結果）")
    #
    # Recognized image(s) display
    if display_recognized_image:
        if ri == '画像ファイル(JPG)':
            resimg = Image.open(
                'images/diary_form1_sample1_virtually_recognized.png')
            st.image(resimg, caption='認識された日誌画像', width=240)
        elif ri == 'カメラ撮影':
            resimg = Image.open(
                'images/diary_form1_sample1_virtually_recognized.png')
            st.image(resimg, caption='認識された日誌画像', width=256)
        else:
            st.warning('画像ではなく表ファイルがアップロードされています（画像認識は無し）。')

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
    print(urination_data_df[['year', 'month', 'day', 'hour', 'minute']])
    urination_data_df['datetime_tmp'] = pd.to_datetime(
        urination_data_df[['year', 'month', 'day', 'hour', 'minute']]).dt.tz_localize('Asia/Tokyo')
    #####    urination_data_df[['year', 'month', 'day', 'hour', 'minute']], errors='coerce')
    print(urination_data_df['datetime_tmp'])
    urination_data_df['datetime_tmp_before'] = urination_data_df['datetime_tmp'].shift(
        1)
    urination_data_df['datetime_tmp_after_check'] = urination_data_df['datetime_tmp'] > urination_data_df['datetime_tmp_before']
    # for check
    # print(urination_data_df['datetime_tmp_after_check'])

    #
    # COPY
    urination_data_df['datetime'] = urination_data_df['datetime_tmp']
    #
    # After midnight adjustment
    after_midnight = False
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
                    print("Line 0 and the first after midnight")
                else:
                    print("Line 0")
                    urination_data_df.at[index,
                                         'datetime'] = urination_data_df.at[index, 'datetime_tmp']
            else:
                after_midnight = True
                # 24, 25時以降にhourをいじり, datetimeをつくる
                print("First after midnight")
                #
                # rowhour = rowhour + 24
                # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
                urination_data_df.at[index,
                                     'hour'] = urination_data_df.at[index, 'hour'] + 24
                urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                               'datetime_tmp'] + datetime.timedelta(hours=24)
        elif after_midnight == True:
            # 24, 25時以降ということであるので，hourをいじり, datetimeをつくる
            print("Second or later after midnight")
            urination_data_df.at[index,
                                 'hour'] = urination_data_df.at[index, 'hour'] + 24
            urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                           'datetime_tmp'] + datetime.timedelta(hours=24)
            # rowhour = rowhour + 24
            # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
        else:
            print("Before midnight")
            urination_data_df.at[index,
                                 'datetime'] = urination_data_df.at[index, 'datetime_tmp']
    # for check
    # print(urination_data_df[['datetime', 'datetime_tmp_after_check', 'day', 'hour']])
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
                urination_data_df.at[index,
                                     'time_phase'] = 'first_after_next_wakeup'
            else:
                urination_data_df.at[index, 'time_phase'] = 'next_day_time'
    first_after_bed_found = False
    for index, row in urination_data_df.iterrows():
        if row['datetime'] >= bed_datetime:
            if first_after_bed_found == False:
                first_after_bed_found = True
                first_after_bed_datetime = row['datetime']
    # for check
    print(urination_data_df)
    #
    # Drop some temporal English name columns
    urination_data_df.drop(columns=[
                           'datetime_tmp', 'datetime_tmp_before', 'datetime_tmp_after_check'], inplace=True)
    # for check
    # st.write(urination_data_df)

    ###
    # Downloadable recognized document (=data)
    ###
    #
    #  Downloadable recognized document preparation
    ud_df1 = urination_data_df.drop(columns=['時', '分', 'year', 'month', 'day',
                                             'hour', 'minute',
                                             'micturition',
                                             'leakage', 'desire', 'urgency', 'remaining',
                                             'memo'])
    ud_df = ud_df1.dropna(subset=['datetime'])
    #
    #  Downloadable recognized document display
    st.table(ud_df.style.highlight_max(axis=0))


###
# Downloadable recognized document CSV (=data CSV)
###
rdc_e = st.empty()
with rdc_e.container():
    st.subheader("日誌データ（認識結果）のCSV形式でのダウンロード")
    ud_csv = convert_df_to_csv(ud_df)
    ud_csv_fn = "ud_"+str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
    st.download_button(label="Download data as CSV",
                       data=ud_csv,
                       file_name=ud_csv_fn,
                       mime='text/csv')


###
# Micturition graph display
###
md_e = st.empty()
with md_e.container():
    st.header("当該日の尿量・漏れ量グラフ")
    vol_df = urination_data_df[['datetime', 'micturition', 'leakage']]
    ### localize way
    ### vol_df['datetime_Japan'] = urination_data_df['datetime'].dt.tz_localize(
    ###    'Asia/Tokyo')
    ### vol_df.drop(columns='datetime', inplace=True)
    ## chart_df = pd.melt(vol_df, id_vars=['datetime_Japan'],
    ##                     var_name='parameter', value_name='value')
    ## chart_base = alt.Chart(chart_df).encode(x='datetime_Japan', y='value', color='parameter')
    ### utc way
    chart_df = pd.melt(vol_df, id_vars=['datetime'],
                       var_name='parameter', value_name='value')
    chart_base = alt.Chart(chart_df).encode(x='datetime', y='value', color='parameter')
    chart_layer = alt.layer(chart_base.mark_line(), chart_base.mark_point(), background=graph_background_color, title='Volume and leak')
    st.altair_chart(chart_layer, use_container_width=True)
#   st.write(pd.DataFrame(vol_df))


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
    st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
    st.text('対象日の就寝時刻は' + bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
    st.text('対象日の就寝時刻と起床時刻の差は' + str(bed_datetime-wakeup_datetime) + 'です．')
    st.text('翌日の起床時刻は' + next_wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
    st.text('翌朝の起床時刻と対象日の就寝時刻の差（つまり睡眠時間）' +
            str(next_wakeup_datetime - bed_datetime) + 'です．')
    st.text('翌日の就寝時刻は' + next_bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
    st.text('翌日の就寝時刻と起床時刻の差は' +
            str(next_bed_datetime - next_wakeup_datetime) + 'です．')


###
# Indices display
###
ind_e = lcol2.empty()
with ind_e.container():
    st.header('排尿関連指標：')
    first_sleep_time = (first_after_bed_datetime -
                        bed_datetime).total_seconds() / 60
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
    maximum_single_nocturnal_urination_volume = urination_data_df[(urination_data_df['time_phase'] == 'after_bed') | (
        urination_data_df['time_phase'] == 'first_after_next_wakeup')].micturition.max()
    average_urination_interval = urination_data_df.mean(
        numeric_only=True).time_difference
    minimum_urination_interval = urination_data_df.min(
        numeric_only=True).time_difference
    maximum_urination_interval = urination_data_df.max(
        numeric_only=True).time_difference
    if urination_volume != 0:
        noctural_plyuria_index = float(
            nocturnal_urination_volume * 100.0 / urination_volume)
    else:
        noctural_plyuria_index = 0.0
    # WIP
    # maximum_voided_volumeに漏れや導尿をいれてない
    maximum_voided_volume = maximum_single_urination_volume
    if maximum_voided_volume != 0:
        nocturia_index = math.ceil(
            float(nocturnal_urination_volume / maximum_voided_volume))
    else:
        nocturia_index = int(1)
    pnv = nocturia_index - 1
    nbci = number_of_nocturnal_urination - pnv

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
    diary_date_int = int(diary_date.strftime('%Y%m%d'))
    indices_df = pd.DataFrame(columns=['指標', '値', '単位'],
                              data=[
                                  ['日誌対象者ID', int(diary_id), ''],
                                  ['日付', int(diary_date_int), ''],
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
    st.table(indices_df)
    ###
    # Downloadable indices CSV
    ###
    indc_e = st.empty()
    with indc_e.container():
        st.subheader("排尿関連指標のCSV形式でのダウンロード")
        indices_csv = convert_df_to_csv(indices_df)
        indices_csv_fn = "indices_" + \
            str(diary_id)+"_"+diary_date.strftime('%Y%m%d')+'.csv'
        st.download_button(label="Download indices as CSV",
                           data=indices_csv,
                           file_name=indices_csv_fn,
                           mime='text/csv')

###
# Column 2 end
###

###
### Refresh if needed
###
#
# st.button("Re-run")

###
###
###
#
# if __name__ == "__main__":
#     main()


