import random
import math
import streamlit as st
import dbx
import json
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import sys
import date_util, funcs
from datetime import datetime
from dateutil.relativedelta import relativedelta

def toggle_form():
    st.session_state.show_form = not st.session_state.show_form

def show_form():
	st.session_state.show_form = True

silver_table_name = 'general.silver_tcsnl_deals'

if 'show_form' not in st.session_state:
    st.session_state.show_form = False

if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []

if 'refresh_int' not in st.session_state:
     st.session_state.refresh_int = 0

query = f'SELECT * FROM {silver_table_name}'

base_peak_list = ['BASE', 'PEAK']
cpos = ['mrae', 'amsterdam', 'utrecht', 'fryslan', 'other']

# get sql request
result = dbx.exec_sql_get_request(query, st.session_state.refresh_int)

# build dataframe
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



if 'input_widget_dict' not in st.session_state:
	q1_date, q2_date = date_util.get_next_quarter_dates(datetime.today())
	cpo_percentages = {x: 0 for x in cpos}
	st.session_state.input_widget_dict = {
		'deal': '',
		'trade_date': datetime.today(),
		'start_date': q1_date,
		'end_date': q2_date,
		'quantity_mw': 0.0,
		'quantity_mwh': 0.0,
		'price': 0.0,
		'cpo_selected': [],
		'cpo_percentages': cpo_percentages,
		'base_peak': 'BASE'
	}


if st.session_state.selected_rows is not None and len(st.session_state.selected_rows) == 1:
	if st.button("Edit selected row", on_click=show_form):
		row = st.session_state.selected_rows.iloc[0]
		date_format = '%Y-%m-%d'
		cpo_percentages = json.loads(row['cpo_percentages'])
		cpo_percentages = {key: int(value) for key, value in cpo_percentages.items()}

		st.session_state.input_widget_dict = {
				'deal': row['deal'],
				'trade_date': datetime.strptime(row['trade_date'], date_format),
				'start_date': datetime.strptime(row['start_date'], date_format),
				'end_date': datetime.strptime(row['end_date'], date_format),
				'quantity_mw': float(row['quantity_MW']),
				'quantity_mwh': float(row['quantity_MWh']),
				'price': float(row['price']),
				'cpo_selected': cpo_percentages.keys(),
				'cpo_percentages': cpo_percentages,
				'base_peak': row['base_peak']
		}
	
st.button("Create new deal", on_click=toggle_form)


if st.session_state.show_form:
	st.session_state.input_widget_dict['deal'] = st.text_input('Deal', st.session_state.input_widget_dict['deal'])
	st.session_state.input_widget_dict['trade_date'] = st.date_input('Trade Date', st.session_state.input_widget_dict['trade_date'])
	st.session_state.input_widget_dict['start_date'] = st.date_input('Start Date', st.session_state.input_widget_dict['start_date'])
	st.session_state.input_widget_dict['end_date'] = st.date_input('End Date', st.session_state.input_widget_dict['end_date'])

	st.session_state.input_widget_dict['quantity_mw'] = st.number_input(
		'Quantity (MW)', min_value=0.0, step=0.01, value=st.session_state.input_widget_dict['quantity_mw']
	)
	st.session_state.input_widget_dict['quantity_mwh'] = st.number_input(
		'Quantity (MWh)', min_value=0.0, step=1.0, value=st.session_state.input_widget_dict['quantity_mwh']
	)
	st.session_state.input_widget_dict['price'] = st.number_input('Price', min_value=0.0, step=0.01, value = st.session_state.input_widget_dict['price'])
	st.session_state.input_widget_dict['base_peak'] = st.selectbox(
		'Base/Peak', base_peak_list, base_peak_list.index(st.session_state.input_widget_dict['base_peak'])
	)

	st.session_state.input_widget_dict['cpo_selected'] = st.multiselect("CPO's", cpos, st.session_state.input_widget_dict['cpo_selected'])

	if len(st.session_state.input_widget_dict['cpo_selected']) > 0:
		
		st.write('Selecteer deal percentages!')
		for index, cpo_item in enumerate(st.session_state.input_widget_dict['cpo_selected']):


			if sum(st.session_state.input_widget_dict['cpo_percentages'].values()) == 0:
				percentage_selected = math.floor(100 / len(st.session_state.input_widget_dict['cpo_selected']))
				# if divide by 3 then add 1 to the first row
				if index == 0 and len(st.session_state.input_widget_dict['cpo_selected']) == 3:
					percentage_selected = percentage_selected + 1
			else:
				if cpo_item in st.session_state.input_widget_dict['cpo_percentages'].keys():
					percentage_selected = st.session_state.input_widget_dict['cpo_percentages'][cpo_item]
				else:
					percentage_selected = 0

			st.session_state.input_widget_dict['cpo_percentages'][cpo_item] = st.slider(f"{cpo_item}", 0, 100, percentage_selected)

	submit_button = st.button(label='Submit')

	if submit_button:
		funcs.check_conditions_and_merge(silver_table_name, st.session_state.input_widget_dict)
