"""

"""

from pages.DB_management import add_index_full_text, add_index_full_vector, add_index_chunked_pairs
import streamlit as st
from check_password import check_password


def main():
    selected_index_type = st.sidebar.radio("Select Index Type to be added", ["Full Text", "Full Vector", "Chunked Pairs"])
    

    if selected_index_type == "Full Text":
        add_index_full_text.main()
    elif selected_index_type == "Full Vector":
        add_index_full_vector.main()
    elif selected_index_type == "Chunked Pairs":
        add_index_chunked_pairs.main()
    st.button("Refresh", key="1")
if check_password():
    main()