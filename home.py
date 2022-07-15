#####
##### home.py
##### WIP
##### 2022-07-15T06:00
##### 2022-07-15T09:30
##### 2022-07-15T14:30
#####

### 
# Imports
###
import datetime
import time
from urllib.request import Request, urlopen
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
import cv2
import requests
import altair as alt
import streamlit as st


#####
#####
# Functions
#####
#####

###
###
###
# @st.cache(suppress_st_warning=True)
def upload_file_func():
#    uploaded_file = st.file_uploader("Choose a diary image of the day",
    uploaded_file = st.file_uploader("日誌の画像PDFファイルを選んでください。",
                                     accept_multiple_files=False)
    return uploaded_file

###
###
###
# @st.cache(suppress_st_warning=True)
def upload_jpgfiles_func():
#   uploaded_jpgfiles = st.file_uploader("Choose diary images of the day",
    uploaded_jpgfile = st.file_uploader("日誌のJPG画像を選んでください。",
                                        accept_multiple_files=True,
                                        type='jpg')
    return uploaded_jpgfiles

###
###
###
# @st.cache(suppress_st_warning=True)
def take_photo_func():
    #   image_file_buffer = st.camera_input("Take a snapshot of today's diary")
    image_file_buffer = st.camera_input("日誌画像を撮影してください。")
    return image_file_buffer

###
###
###
@st.cache
def convert_df_to_csv(df):
    return df.to_csv().encode('utf-8-sig')


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
      </style>
      """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('排尿日誌マネージャー')
st.text('Copyright (c) 2022 tmoriics')


###
# Setting by the sidebar
###
#
# Setup parameters
graph_background_color = "#EEFFEE"
display_recognized_image = False
#
# Sidebar display
# graph_background_color = st.sidebar.color_picker(
#    'Graph background color', value='#EEFFEE')
display_recognized_image = st.sidebar.checkbox('Display recognized image(s)')


###
### Column preparation
###
lcol, rcol = st.columns(2)


###
### Today set
###
dt_now = datetime.datetime.now()
rcol.text('現在の日時：'+dt_now.strftime('%Y年%m月%d日 %H:%M:%S'+'です。'))


###
# Check point by streamlit secrets management function
###
e = st.empty()
c = e.container()
guess = c.text_input("What is the password?")
if guess != st.secrets["password"]:
    c.warning("Please input the password.")
    st.stop()
c.success('Thank you for inputting the password.')
time.sleep(1)    
e.empty()


###
### Diary date input
###
# diary_year_string = '2022'
# diary_month_string = '5'
# diary_day_string = '1'
# ##### diary_date = datetime.date.fromisoformat(diary_date_string)
# diary_date = datetime.date(year=int(diary_year_string),
#                          month=int(diary_month_string), day=int(diary_day_string))
le = lcol.empty()
lc = le.container()
diary_date = lc.date_input("日誌の日付を西暦で入力してください。",
                           (dt_now+datetime.timedelta(days=3)).date())
if diary_date == (dt_now+datetime.timedelta(days=3)).date(): 
    lc.warning('日付の入力を御願いします。')
    st.stop()
lc.success('入力が確認できました。'+diary_date.strftime('%Y年%m月%d日'))
time.sleep(2)
le.empty()
lc = lcol.container()
lc.success('日誌対象日は'+diary_date.strftime('%Y年%m月%d日'+'です。'))


###
### Wakeup and bed set
###
#
# Wakeup and bed set
# wakeup_hour_string = '6'
# wakeup_minute_string = '00'
# wakeup_hour_pm_adjust_boolean = False
wakeup_hour_string = '6'
wakeup_minute_string = '00'
wakeup_hour_pm_adjust_boolean = False
wakeup_time_tmp = datetime.time(
    hour=int(wakeup_hour_string), minute=int(wakeup_minute_string))
if wakeup_hour_pm_adjust_boolean:
    wakeup_datetime = datetime.datetime.combine(
        diary_date, wakeup_time_tmp) + datetime.timedelta(hours=12)
else:
    wakeup_datetime = datetime.datetime.combine(diary_date, wakeup_time_tmp)
# bed_hour_string = '9'
# bed_minute_string = '00'
# bed_time_pm_adjust_boolean = True
bed_hour_string = '9'
bed_minute_string = '00'
bed_time_pm_adjust_boolean = True
bed_time_tmp = datetime.time(
    hour=int(bed_hour_string), minute=int(bed_minute_string))
if bed_time_pm_adjust_boolean:
    bed_datetime = datetime.datetime.combine(
        diary_date, bed_time_tmp) + datetime.timedelta(hours=12)
else:
    bed_datetime = datetime.datetime.combine(diary_date, bed_time_tmp)
# next_wakeup_hour_string = '5'
# next_wakeup_minute_string = '55'
# next_wakeup_time_pm_adjust_boolean = False
next_wakeup_hour_string = '5'
next_wakeup_minute_string = '55'
next_wakeup_time_pm_adjust_boolean = False
next_wakeup_time_tmp = datetime.time(
    hour=int(next_wakeup_hour_string), minute=int(next_wakeup_minute_string))
if next_wakeup_time_pm_adjust_boolean:
    next_wakeup_datetime = datetime.datetime.combine(
        diary_date + datetime.timedelta(days=1), next_wakeup_time_tmp) + datetime.timedelta(hours=12)
else:
    next_wakeup_datetime = datetime.datetime.combine(
        diary_date + datetime.timedelta(days=1), next_wakeup_time_tmp)
# next_bed_hour_string = '9'
# next_bed_minute_string = '05'
# next_bed_time_pm_adjust_boolean = True
next_bed_hour_string = '9'
next_bed_minute_string = '05'
next_bed_time_pm_adjust_boolean = True
next_bed_time_tmp = datetime.time(
    hour=int(next_bed_hour_string), minute=int(next_bed_minute_string))
if next_bed_time_pm_adjust_boolean:
    next_bed_datetime = datetime.datetime.combine(diary_date + datetime.timedelta(days=1),
                                                  next_bed_time_tmp) + datetime.timedelta(hours=12)
else:
    next_bed_datetime = datetime.datetime.combine(
        diary_date + datetime.timedelta(days=1), next_bed_time_tmp)
#
# Wakeup time display
st.markdown('### 起床時刻：')
st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')


###
# Diary read
###
#
# Diary image(s) upload
st.markdown("## 日誌画像アップロード")
# A Image.open('images/samp1.jpg')
# B
img = Image.open('images/diary_form1_sample1.png')
ri = st.radio("日誌画像をアップロードしてください。スマホカメラでいま撮影しても構いません。",
              ('PDFファイル', '画像ファイル', 'カメラ'), horizontal=True)
if ri == 'PDFファイル':
    st.write('このような日誌画像をアップロードしてください．')
    st.image(img, caption='日誌画像例', width=120)
    uploaded_file = upload_file_func()
    if uploaded_file is not None:
        st.success('日誌画像が登録されました．')
        ####
        # PDFから画像への変換をしないといけない
        ####
        dimg = Image.open(uploaded_file)
        st.image(dimg, caption='Uploaded image', use_column_width=True)
elif ri == '画像ファイル':
    st.write('このような日誌画像をアップロードしてください．')
    st.image(img, caption='日誌画像例', width=120)
    uploaded_jpgfiles = upload_jpgfiles_func()
    if uploaded_jpgfiles is not None:
        for uploaded_jpgfile in uploaded_jpgfiles:
            st.success('日誌画像が登録されました．')
            ####
            # 複数枚きたときの扱いをしないといけない
            ####
            dimg = Image.open(uploaded_jpgfile)
            st.image(dimg, caption='Uploaded jpeg images',
                     use_column_width=True)
else:
    st.write('このような日誌画像を縦長で撮影してください．')
    st.image(img, caption='日誌画像例', width=120)
    image_file_buffer = take_photo_func()
#   camera_image = st.camera_input("Take a snapshot of today's diary")
#   if camera_image:
#       st.image(camera_image, caption='Taken diary snapshot')
    if image_file_buffer is not None:
        st.success('撮影画像が登録されました．')
        cimg = Image.open(image_file_buffer)
        cimg_array = np.array(cimg)
        st.write(cimg_array.shape)
        st.image(cimg, caption='日誌画像', width=256)
        jpg_fn = 'diary'+diary_date.strftime('%Y%m%d')+'.jpg'
        btn = st.download_button(label="Download the registered image",
                                 data=image_file_buffer,
                                 file_name=jpg_fn,
                                 mime="image/jpg")

###
# Diary recognition
###
#
# Diary image recognition by OCR
########## WIP
# virtual recognition A
# urination_data_df = pd.read_csv('data/m1modified.csv', sep=',')
# urination_data_df = pd.read_csv('data/virtually_recognized_m1modified.csv', sep=',')
# urination_data_df = pd.read_csv('data/recognized_m1modified.csv', sep=',')
# st.write(   pd.DataFrame(urination_data_df))
# virtual recognition B
urination_data_df = pd.DataFrame(np.arange(13*8).reshape(13, 8),
                                 columns=['時', '分', '排尿量', 'もれ', '尿意', '切迫感', '残尿感', 'メモ'])
urination_data_df.loc[:] = [
    ['8', '00', '100', '無', '有・無', '有・無', '有・無', ''],
    ['10', '30', '250', '無', '有・無', '有・無', '有・無', ''],
    ['13', '00', '300', '無', '有・無', '有・無', '有・無', ''],
    ['17', '00', '225', '無', '有・無', '有・無', '有・無', ''],
    ['19', '55', '125', '無', '有・無', '有・無', '有・無', ''],
    ['22', '30', '100', '無', '有・無', '有・無', '有・無', ''],
    ['1', '30', '150', '無', '有・無', '有・無', '有・無', ''],
    ['7', '00', '200', '無', '有・無', '有・無', '有・無', ''],
    ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', ''],
    ['', '', '', '無・少量・中量・多量', '有・無', '有・無', '有・無', '']]
########## small checks
# st.write(urination_data_df['もれ'])
# st.write(urination_data_df['もれ'] == '有')
# st.write(urination_data_df['もれ'] == '無')
# st.write(urination_data_df[urination_data_df['もれ'] == '有'])
# st.write(urination_data_df[urination_data_df['もれ'] == '無'])

########## hidden function
###
### Downloadable diary document csv
###
# urination_data_csv = convert_df_to_csv(urination_data_df)
# urination_data_csv_fn = "diary"+diary_date.strftime('%Y%m%d')+'.csv'
# st.download_button(label="Download diary document as CSV",
#                    data=urination_data_csv,
#                    file_name=urination_data_csv_fn,
#                    mime='text/csv')


###
### Recognized diary display
###
e = st.empty()
c = e.container()
#
# Recognized diary document display
st.markdown("# 日誌データ表示（認識結果）")
#
# Recognized image(s) display
if display_recognized_image:
    # if uploaded_files is not None or image_file_buffer is not None:
    # June
    # resimg1 = Image.open('images/res1-1.jpg')
    # resimg2 = Image.open('images/res1-2.jpg')
    # rescol1, rescol2 = st.columns(2)
    # rescol1.image(resimg1, caption='Recognized diary P.1', width=256)
    # rescol2.image(resimg2, caption='Recognized diary P.2', width=256)
    # July
    resimg = Image.open('images/diary_form1_sample1_virtually_recognized.png')
    c.image(resimg, caption='認識された日誌画像', width=240)

    
###
### Date and time adjustment (Day and hour)
###
##########
# 2022-07-14T16:00 修正
#  st.write("<font color='red'>最初の行が深夜０時以降だと日付けがおかしくなる｡修正中</font>", unsafe_allow_html=True)
# 2022-07-14T17:15 修正
#  st.write("<font color='red'>零時以降が翌日日付けにならない｡修正中</font>", unsafe_allow_html=True)
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
urination_data_df['datetime_tmp'] = pd.to_datetime(
    urination_data_df[['year', 'month', 'day', 'hour', 'minute']])
#    urination_data_df[['year', 'month', 'day', 'hour', 'minute']], errors='coerce')
urination_data_df['datetime_tmp_before'] = urination_data_df['datetime_tmp'].shift(1)
urination_data_df['datetime_tmp_after_check'] =urination_data_df['datetime_tmp'] > urination_data_df['datetime_tmp_before']
########## for check
# print(urination_data_df['datetime_tmp_after_check'])

#
# After midnight adjustment
after_midnight = False
urination_data_df['datetime'] = urination_data_df['datetime_tmp']
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
            urination_data_df.at[index,
                                 'hour'] = urination_data_df.at[index, 'hour'] + 24
            urination_data_df.at[index, 'datetime'] = urination_data_df.at[index,
                                                                           'datetime_tmp'] + datetime.timedelta(hours=24)
            # rowhour = rowhour + 24
            # rowdatetime = rowdatetime_tmp + datetime.timedelta(hours=24)
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
########## for check
# print(urination_data_df[['datetime', 'datetime_tmp_after_check', 'day', 'hour']])
#
# Calculate time difference
urination_data_df['time_difference'] = urination_data_df['datetime'].diff()
urination_data_df['time_difference'] = urination_data_df['time_difference'].dt.total_seconds() / 60.0
#
# Drop some temporal English name columns
urination_data_df.drop(columns=['datetime_tmp', 'datetime_tmp_before', 'datetime_tmp_after_check'], inplace=True)
########## for check
# st.write(urination_data_df)


###
### Downloadable recognized document (=data)
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
# st.dataframe(ud_df.style.highlight_max(axis=0))
st.table(ud_df.style.highlight_max(axis=0))


###
# Downloadable recognized document CSV (=data CSV)
###
st.markdown("# CSV形式でのダウンロード")
ud_csv = convert_df_to_csv(ud_df)
ud_csv_fn = "ud"+diary_date.strftime('%Y%m%d')+'.csv'
st.download_button(label="Download data as CSV",
                   data=ud_csv,
                   file_name=ud_csv_fn,
                   mime='text/csv')


###
# Micturition graph display
###
st.markdown("# 当該日の尿量・漏れ量グラフ")
vol_df = urination_data_df[['datetime', 'micturition', 'leakage']]
vol_df['datetime_Japan'] = urination_data_df['datetime'].dt.tz_localize(
    'Asia/Tokyo')
vol_df.drop(columns='datetime', inplace=True)
chart_df = pd.melt(vol_df, id_vars=['datetime_Japan'],
                   var_name='parameter', value_name='value')
chart = alt.Chart(chart_df, background=graph_background_color,
                  title='Volume and leak').mark_line().encode(x='datetime_Japan',
                                                              y='value', color='parameter')
st.altair_chart(chart, use_container_width=True)
st.write(pd.DataFrame(vol_df))


###
### Wakeup time and bed time display
###
st.markdown('### 起床時刻・就寝時刻・翌日起床時刻・翌日就寝時刻：')
st.text('対象日の起床時刻は' + wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
st.text('対象日の就寝時刻は' + bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
st.text('対象日の就寝時刻と起床時刻の差は' + str(bed_datetime-wakeup_datetime) + 'です．')
st.text('翌日の起床時刻は' + next_wakeup_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
st.text('翌朝の起床時刻と対象日の就寝時刻の差（つまり睡眠時間）' + str(next_wakeup_datetime - bed_datetime) + 'です．')
st.text('翌日の就寝時刻は' + next_bed_datetime.strftime("%Y-%m-%dT%H:%M") + 'です．')
st.text('翌日の就寝時刻と起床時刻の差は' + str(next_bed_datetime - next_wakeup_datetime) + 'です．')


