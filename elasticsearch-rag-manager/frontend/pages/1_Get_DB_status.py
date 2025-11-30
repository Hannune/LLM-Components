"""
In this file we will get the list of index from elastic search

"""

import streamlit as st
import json
from utils.send_request_to_backend import _db_api
from check_password import check_password

db = _db_api()

def main():    
    
    # Reset es, remove all the index and create only metadata indices
    col1, col2 = st.columns([1, 3])
    if col1.button("Reset DB"):
        # if col2.button("Are you sure?"):
        res = db.reset_es()
        st.success("Done")

    # get index list
    index_type_list = ["full_text", "full_vector", "chunked_pairs"]

    col1, col2 = st.columns([4, 1])
    col2.button("Refresh", key="1")

    st.subheader(f"Index list from metadata indexes")
    for index_type in index_type_list:
        res = db.get_all_data_in_index_with_fields(f"metadata_{index_type}", ["index_name"])
        if res is None:
            st.error(f"No {index_type} index available")
            continue
        st.write(f"{index_type} Index List")
        st.write(res)

    col1, col2 = st.columns([4, 1])
    col2.button("Refresh", key="2")

    st.write("***")
    # TODO get all the index status in dictionary format
    # get all index
    st.subheader("All Index List")
    index_list = db.get_all_index()
    if index_list is None:
        st.error("No index available")
        return
    st.write(f"index list from all indexes")
    st.write(index_list)
    # each index will have only have title or index_name fields as list
    for index in index_list:
        if index[0] == ".":
            continue
        if "metadata" in index:
            fields = ["index_name"]
        elif "full-text" in index:
            fields = ["title"]
        else:
            fields = ["original_full_text_data_title"]
        res = db.get_all_data_in_index_with_fields(index, fields)
        if res is None:
            st.error(f"Unable to retrieve data from {index} index")
            continue
        st.write(f"**Index name: {index}**")
        st.write(f"Number of documents: {len(res)}")
        with st.expander("Show all titles"):
            for title in res.keys():
                st.write(f"{title}")
        st.write("***")
        # st.write(res.keys())
    st.write("***")

    col1, col2 = st.columns([4, 1])
    col2.button("Refresh", key="3")
    
if check_password():
    main()