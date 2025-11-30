import streamlit as st
from pages.DB_management import add_data_full_text, add_data_full_vector, add_data_chunked_pairs
from check_password import check_password

# Add code to give warning when there is no index where the data can be added

def main():
    st.title("Add Data")
    
    selected_data_type = st.sidebar.radio("Select data type to be added", ["Full Text", "Full Vector", "Chunked Pairs"])

    if selected_data_type == "Full Text":
        add_data_full_text.main()
    elif selected_data_type == "Full Vector":
        add_data_full_vector.main()
    elif selected_data_type == "Chunked Pairs": 
        add_data_chunked_pairs.main()

    st.sidebar.button("Refresh", key="2")
if check_password():
    main()

