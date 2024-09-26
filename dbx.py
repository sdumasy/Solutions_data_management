from typing import Dict
import requests
import time
import streamlit as st


def get_databricks_access_token():
        
	token_url = 'https://dbc-27e7bf13-aae5.cloud.databricks.com/oidc/v1/token'
	# replace with secrets
	client_id = '8a93bcaf-c3bd-478d-976a-625144e9019e'
	client_secret = 'dose3697ae045235b973e83de53928bdd755'

	payload = {
		'grant_type': 'client_credentials',
		'scope': 'all-apis'
	}
	print('hi')

	response = requests.post(token_url, auth=(client_id, client_secret), data=payload).json()
	return response['access_token']

def send_put_request_with_retry(url, data, headers, max_retries=10):

	attempt = 0
	while attempt < max_retries:

		response = requests.put(url, data = data, headers = headers)
		
		if response.status_code == 204:
			return 'ok'
		else:
			attempt += 1
			time.sleep(1) 

	raise Exception('failed')

def send_request_with_retry(url, data, headers, max_retries=10):

	attempt = 0
	while attempt < max_retries:

		response = requests.post(url, json = data, headers = headers)
		
		if response.status_code == 200:
			response_json = response.json()

			if 'status' in response_json and response_json['status']['state'] == 'FAILED':
				attempt += 1
				time.sleep(1) 
			else:
				return response_json
		else:
			attempt += 1
			time.sleep(1) 

	raise Exception('failed')

@st.cache_data
def exec_sql_get_request(query: str, random_num_cache_reload: None):

	access_token = get_databricks_access_token()

	sql_url = 'https://dbc-27e7bf13-aae5.cloud.databricks.com/api/2.0/sql/statements/'

	new_headers = {
		'Authorization': f'Bearer {access_token}',
		'Content-Type': 'application/json'
	}
		
	data = {
		"warehouse_id": "41296b4a82242355",
		"catalog": "bstcsnldatascienceaws-dev-internal",
		"schema": "general",
		"format": "INLINE",
		"statement": query,
	}

	return send_request_with_retry(sql_url, data, new_headers)