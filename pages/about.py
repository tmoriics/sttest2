#####
##### about.py
##### 
##### 2022-07-15T06:00
#####
### 
# Imports
###
import datetime
import time
from urllib.request import Request, urlopen
import pandas as pd
from PIL import Image
import streamlit as st


#####
#####
# Functions
#####
#####

#####
#####
# Main Script
#####
#####

###
# Preload
###
img = Image.open('images/aicenter.jpg')

###
# Title section
###
st.set_page_config(page_title='About this site')
hide_menu_style = """
      <style>
      #MainMenu {visibility: hidden;}
      </style>
      """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.title('このサイトについて')
st.write('About this site @tmoriics')
st.image(img, caption='AI Center of the University of Tokyo', use_column_width=False)
st.markdown('Copyright: ')
st.text('(c) 2022 tmoriics')
st.markdown('## アプリの機能：')
st.text('排尿日誌の認識とそれに基づく指標演算を行います。')


###
# Progress bar
###
bar = st.progress(0)
frame_text = st.empty()
for i in range(100):
    bar.progress(i)
    frame_text.text("%i/100" % (i + 1))
    time.sleep(0.05)
frame_text.text("Now you can proceed.")
time.sleep(0.5)
bar.empty()
frame_text.empty()


