import date_util
import streamlit as st
import dbx
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sys
import json


def randint():
     return random.randint(0, sys.maxsize)


def get_time_product(date1: datetime, date2: datetime):
    # Ensure date1 is earlier than date2
	year_string = str(date1.year)[-2:]
	if date2.month == date1.month:
		short_month = date1.strftime("%b")
		return f'{short_month}-{year_string}'
	elif date2.month - date1.month == 2:
		quarter_num = (date1.month - 1) // 3 + 1
		return f'Q{quarter_num}-{year_string}'
	elif date2.month - date1.month == 11:
		return f'CAL-{year_string}'

	return None


def check_conditions_and_merge(
		silver_table_name, input_dict
):
	# check dates and merge if valid
	if input_dict['start_date'].day != 1:
		st.warning('Start date is not on first of the month!')
		return
	elif not date_util.is_last_day_of_month(input_dict['end_date']):
		st.warning('End date is not on end of the month!')
		return
	elif input_dict['start_date'].year != input_dict['end_date'].year:
		st.warning('Start date and end date not in same year')
		return

	if input_dict['deal'] == '':
		st.warning('Deal id is empty!')
		return

	total_percentage_sum = sum(input_dict['cpo_percentages'].values())

	if total_percentage_sum != 100:
		st.warning("Sum of cpo percentages doesn't equal 100")
		return
     
	product_name = get_time_product(input_dict['start_date'], input_dict['end_date'])

	if product_name == None:
		st.warning('Invalid product, did you select a month/quarter/year?')
		return

	deal_value = input_dict['quantity_mwh'] * input_dict['price']
	cpo_named_struc = f"map({str(input_dict['cpo_percentages']).replace(':', ',')[1:-1].lower()})"

	insert_query = f"""
		MERGE INTO {silver_table_name} AS target
		USING (VALUES 
			('{input_dict['deal']}', '{input_dict['trade_date']}', '{input_dict['start_date']}', '{input_dict['end_date']}', '{product_name}', {input_dict['quantity_mw']},
			{input_dict['quantity_mwh']}, {input_dict['price']}, '{input_dict['base_peak']}', {deal_value}, {cpo_named_struc})
		) AS source
		ON target.deal = source.col1
		WHEN MATCHED THEN 
		UPDATE SET 
			target.trade_date = source.col2,
			target.start_date = source.col3,
			target.end_date = source.col4,
			target.product = source.col5,
			target.quantity_MW = source.col6,
			target.quantity_MWh = source.col7,
			target.price = source.col8,
			target.base_peak = source.col9,
			target.deal_value = source.col10,
			target.cpo_percentages = source.col11
		WHEN NOT MATCHED THEN 
		INSERT (deal, trade_date, start_date, end_date, product, quantity_MW, quantity_MWh, price, base_peak, deal_value, cpo_percentages)
		VALUES (source.col1, source.col2, source.col3, source.col4, source.col5, source.col6, source.col7, source.col8, source.col9, source.col10, source.col11);
	"""

	print(insert_query)

	result = dbx.exec_sql_get_request(insert_query, randint())
	st.session_state.refresh_int = randint()
	st.rerun()