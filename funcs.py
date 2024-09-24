import date_util
import streamlit as st
import dbx
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import sys


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
		silver_table_name, deal, trade_date, start_date, end_date, quantity_mw, quantity_mwh, price, base_peak
):
	# check dates and merge if valid
	if start_date.day != 1:
		st.warning('Start date is not on first of the month!')
		return
	elif not date_util.is_last_day_of_month(end_date):
		st.warning('End date is not on end of the month!')
		return
	elif start_date.year != end_date.year:
		st.warning('Start date and end date not in same year')
		return
     
	product_name = get_time_product(start_date, end_date)

	if product_name == None:
		st.warning('Invalid product, did you select a month/quarter/year?')
		return

	deal_value = quantity_mwh * price

	insert_query = f"""
		MERGE INTO {silver_table_name} AS target
		USING (VALUES 
			('{deal}', '{trade_date}', '{start_date}', '{end_date}', '{product_name}', {quantity_mw}, {quantity_mwh}, {price}, '{base_peak}', {deal_value})
		) AS source
		ON target.deal = source.col1
		WHEN NOT MATCHED THEN 
		INSERT (deal, trade_date, start_date, end_date, product, quantity_MW, quantity_MWh, price, base_peak, deal_value)
		VALUES (source.col1, source.col2, source.col3, source.col4, source.col5, source.col6, source.col7, source.col8, source.col9, source.col10);
	"""

	print(insert_query)

	result = dbx.exec_sql_get_request(insert_query, randint())
	st.session_state.refresh_int = randint()
	st.rerun()