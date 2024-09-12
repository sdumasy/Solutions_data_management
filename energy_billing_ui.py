import random
import streamlit as st
import dbx
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sys
import date_util, funcs
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
import calendar

uploaded_files = st.file_uploader('Upload twee Edmij factuur bestanden!', accept_multiple_files = True)

df_factuur = None
validated = True

def have_same_elements(list1, list2):
    return set(list1) == set(list2)

if len(uploaded_files) != 0:
	print(uploaded_files)
	for item in uploaded_files:

		df_factuur = pd.read_excel(item)
		if 'kWh_Factuur' not in df_factuur:
			st.warning('kWh_Factuur kolom niet aanwezig in Excel!')
			validated = False

jaar = df_factuur['jaar'].iloc[0]
maand = df_factuur['maand'].iloc[0]
if validated and len(uploaded_files) == 2:
	butt = st.button('Upload bestanden!')

	if butt:

		folder_path = f'edmij_invoices/{jaar}/{maand:02}/01'


		access_token = dbx.get_databricks_access_token()
		new_headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}
		succeeded = False

		for file in uploaded_files:

			file_path = f'/Volumes/bstcsnldatascienceaws-dev-internal/general/general/{folder_path}/{file.name}'
			sql_url = f'https://dbc-27e7bf13-aae5.cloud.databricks.com/api/2.0/fs/files{file_path}'

			uploaded_file = file.read()

			resp = dbx.send_put_request_with_retry(sql_url, uploaded_file, new_headers)

		st.toast('Files uploaded succesfully!')

	