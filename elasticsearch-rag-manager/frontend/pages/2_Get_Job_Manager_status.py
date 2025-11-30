from utils.send_request_to_backend import _db_api
import streamlit as st
from check_password import check_password

db = _db_api()

def main():
    # get queue status
    job_manager_status = db.get_job_manager_status()
    st.subheader("Job Manager Status")
    st.write(job_manager_status)
    st.write("***")
    st.button("Refresh")

if check_password():
    main()