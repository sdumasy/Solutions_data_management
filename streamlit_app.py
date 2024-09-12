import streamlit as st
st.set_page_config(layout="wide")

st.title("Solution data management tool")


pg = st.navigation([st.Page("deals_ui.py"), st.Page("energy_billing_ui.py")])
pg.run()