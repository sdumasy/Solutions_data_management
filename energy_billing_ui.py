import random
import streamlit as st
import dbx
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
import uuid

uploaded_files = st.file_uploader('Upload twee Edmij factuur bestanden!!', accept_multiple_files = True)

df_factuur = None
validated = True

def have_same_elements(list1, list2):
    return set(list1) == set(list2)


if len(uploaded_files) != 0:
	print(uploaded_files)
	for item in uploaded_files:

		if df_factuur is None:

			df_factuur = pd.read_excel(item, dtype={'EanCode': str})
		else:
			df_new = pd.read_excel(item, dtype={'EanCode': str})
			df_factuur = pd.concat([df_factuur, df_new])

		if 'kWh_Factuur' not in df_factuur:
			st.warning('kWh_Factuur kolom niet aanwezig in Excel!')
			validated = False


if validated and len(uploaded_files) == 2:

	#clean columns
	df_factuur = df_factuur.loc[:, ~df_factuur.columns.str.contains('^Unnamed')]
	df_factuur.columns = df_factuur.columns.str.replace(' ', '', regex=False).str.replace('.', '', regex=False)
	# df_factuur['EanCode'] = df_factuur['EanCode'].astype('float').astype('string')
	# df_factuur['EanCode'] = df_factuur['EanCode'].apply(lambda x: f"{int(x)}" if pd.notnull(x) else "")
	df_factuur.reset_index(drop=True, inplace=True)
	df_factuur
	print(df_factuur.dtypes)
	butt = st.button('Upload bestanden!')
	jaar = df_factuur['jaar'].iloc[0]
	maand = df_factuur['maand'].iloc[0]

	if butt:

		folder_path = f'edmij_invoice/{jaar}/{maand:02}/01'

		buffer = BytesIO()
		df_factuur.to_csv(buffer, index=False)
		csv_bytes = buffer.getvalue()

		access_token = dbx.get_databricks_access_token()

		new_headers = {
			'Authorization': f'Bearer {access_token}',
			'Content-Type': 'application/json'
		}

		succeeded = False
		file_path = f'/Volumes/bstcsnldatascienceaws-dev-internal/general/general/{folder_path}/{uuid.uuid4()}.csv'
		sql_url = f'https://dbc-27e7bf13-aae5.cloud.databricks.com/api/2.0/fs/files{file_path}'

		resp = dbx.send_put_request_with_retry(sql_url, csv_bytes, new_headers)

		st.toast('Files uploaded succesfully!')

	