"""
1. Get full text index list
2. Get index properties keys from index metadata
3. Get total number of indexes

4. Display list of full text indexes
5. Enter index name
6. Check if index name already exists

7. Enter index metadata properties

8. Add information to index metadata
9. Create new index

"""
import streamlit as st
from utils.send_request_to_backend import _db_api
from datetime import datetime

db = _db_api()

def set_properties():
    properties = {
        "index_name": st.session_state["new_index_name"],
        "user": st.session_state["user"],
        "description": st.session_state["new_description"],
        "purpose": st.session_state["purpose"],
        "index_type": "full_text",
        "creation_date": datetime.now().isoformat(),
        "latest_update": datetime.now().isoformat(),
        "number_of_data": 0,
        "extraction_method": "naive"
    }
    
    return properties


def main():
    st.title("Add Full Text Index")
    # 1. Get full text index list
    index_list_full_text = db.get_all_data_in_index_with_fields("metadata_full_text", ["index_name", "description", "purpose"])
    if index_list_full_text is None:
        st.error("No full_text index available")
        return
    index_name_list_full_text = list(index_list_full_text.keys())

    # 3. Get total number of indexes
    number_index_full_text = len(index_list_full_text)

    # 4. Display list of full text indexes
    st.subheader("Full Text Index List")
    st.write(index_list_full_text)

    # 5. Enter index name
    st.session_state["new_index_name"] = "full-text-" + st.text_input("Enter index_name(**essential**)")
    st.session_state["new_description"] = st.text_area("Enter description(optional)") 
    st.session_state["purpose"] = st.text_area("Enter purpose(optional)")
    st.session_state["user"] = st.text_input("Enter user(optional)", "all")


    # 6. Check if index name already exists    
    if st.session_state["new_index_name"] in index_name_list_full_text:
        st.session_state["index_name_valid"] = False
        st.warning("Index name already exists")
    elif st.session_state["new_index_name"] == "":
        st.session_state["index_name_valid"] = False
    else:
        st.success("Index name is available")
        st.session_state["index_name_valid"] = True

    st.write(f"Total number of full text indexes: {number_index_full_text}")
    # write properties(dict) as table in streamlit
    st.write("Index Metadata Mapping")
    properties = set_properties()
    st.write(properties)
    
    if st.session_state["index_name_valid"]:
        if st.button("Create New Index"):
            db.post_add_index("full_text", st.session_state["new_index_name"], properties)
            
            # # clear session state
            for key in st.session_state.keys():
                if key == "password_correct":
                    continue
                del st.session_state[key]
            st.session_state["index_name_valid"] = False
            del properties



