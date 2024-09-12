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

def toggle_form():
    st.session_state.show_form = not st.session_state.show_form

silver_table_name = 'general.silver_tcsnl_deals'

if 'show_form' not in st.session_state:
    st.session_state.show_form = False

if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []

if 'refresh_int' not in st.session_state:
     st.session_state.refresh_int = 0

query = f'SELECT * FROM {silver_table_name}'

print(st.session_state.refresh_int)
print(query)
result = dbx.exec_sql_get_request(query, st.session_state.refresh_int)

header_names = [x['name'] for x in result['manifest']['schema']['columns']]

df_pd = pd.DataFrame(result['result']['data_array'], columns=header_names)


gb = GridOptionsBuilder.from_dataframe(df_pd)
gb.configure_selection('multiple', use_checkbox=True)
grid_options = gb.build()

response = AgGrid(df_pd, gridOptions=grid_options, GridUpdateMode=GridUpdateMode.MANUAL, pre_selected_rows=st.session_state.selected_rows)

st.session_state.selected_rows = response['selected_rows']

if st.session_state.selected_rows is not None and len(st.session_state.selected_rows) > 0:
	if st.button("Delete selected rows"):
        
		df_reset = st.session_state.selected_rows.reset_index()

		delete_deal_list = [x for x in df_reset['deal']]
		delete_deal_string = "('" + "', '".join(delete_deal_list) + "')"

		query = f'delete from {silver_table_name} where deal in {delete_deal_string}'
		result = dbx.exec_sql_get_request(query, funcs.randint())

		st.session_state.selected_rows = []  # Clear the selection
		st.toast('Deals deleted!')
		st.session_state.refresh_int = funcs.randint()
		st.rerun()

st.button("Create new deal", on_click=toggle_form)


q1_date, q2_date = date_util.get_next_quarter_dates(datetime.today())

if st.session_state.show_form:
# Display the form
	with st.form(key='deal_form'):
		deal = st.text_input('Deal')
		trade_date = st.date_input('Trade Date', datetime.today())
		start_date = st.date_input('Start Date', q1_date)
		end_date = st.date_input('End Date', q2_date)
		quantity_mw = st.number_input('Quantity (MW)', min_value=0.0, step=0.01)
		quantity_mwh = st.number_input('Quantity (MWh)', min_value=0, step=1)
		price = st.number_input('Price', min_value=0.0, step=0.01)
		base_peak = st.selectbox('Base/Peak', ['BASE', 'PEAK'])

		submit_button = st.form_submit_button(label='Submit')

		if submit_button:
			funcs.check_conditions_and_merge(silver_table_name, deal, trade_date, start_date, end_date, quantity_mw, quantity_mwh, price, base_peak)
