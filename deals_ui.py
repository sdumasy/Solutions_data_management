import random
import streamlit as st
import dbx
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sys

def toggle_form():
    st.session_state.show_form = not st.session_state.show_form

def randint():
     return random.randint(0,sys.maxsize)

plat_table_name = 'general.silver_tcsnl_deals'


if 'show_form' not in st.session_state:
    st.session_state.show_form = False

if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []

if 'refresh_int' not in st.session_state:
     st.session_state.refresh_int = 0

query = f'SELECT * FROM {plat_table_name}'

print(st.session_state.refresh_int)
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

		query = f'delete from {plat_table_name} where deal in {delete_deal_string}'
		result = dbx.exec_sql_get_request(query, randint())

		st.session_state.selected_rows = []  # Clear the selection
		st.toast('Deals deleted!')
		st.session_state.refresh_int = randint()
		st.rerun()

st.button("Create new deal", on_click=toggle_form)

if st.session_state.show_form:
# Display the form
	with st.form(key='deal_form'):
		deal = st.text_input('Deal')
		trade_date = st.date_input('Trade Date', datetime.today())
		start_date = st.date_input('Start Date', datetime.today())
		end_date = st.date_input('End Date', datetime.today())
		quantity_mw = st.number_input('Quantity (MW)', min_value=0.0, step=0.01)
		price = st.number_input('Price', min_value=0.0, step=0.01)
		base_peak = st.selectbox('Base/Peak', ['BASE', 'PEAK'])
		avg_epex_price = st.number_input('Avg EPEX Price (EUR/kWh)', min_value=0.0, step=0.0001)

		submit_button = st.form_submit_button(label='Submit')

		if submit_button:
			
			insert_query = f"""
				MERGE INTO general.plat_tcsnl_deals AS target
				USING (VALUES 
					('{deal}', '{trade_date}', '{start_date}', '{end_date}', {quantity_mw}, {price}, '{base_peak}', {avg_epex_price})
				) AS source
				ON target.deal = source.col1
				WHEN NOT MATCHED THEN 
				INSERT (deal, trade_date, start_date, end_date, quantity_MW, price, base_peak, avg_epex_price_eur_kwh)
				VALUES (source.col1, source.col2, source.col3, source.col4, source.col5, source.col6, source.col7, source.col8);
			"""

			print(insert_query)

			result = dbx.exec_sql_get_request(insert_query, randint())
			st.session_state.refresh_int = randint()
			st.rerun()