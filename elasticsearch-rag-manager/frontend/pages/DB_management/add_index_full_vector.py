"""
1. Get full text index list

2. Select full text index

3. Get list of embedding models from selected full text index
4. Get list of deployed embedding models

5. Get available embedding models
    = set(available deployed embedding models list) - set(embedding model list from selected full text index)
6. Select embedding models

7. Display generated full vector index names
8. Enter new full vector index name
9. Check if full vector index name already exists

10. Enter index metadata properties information

11. Add full vector index
12. Update selected full text index
13. Add information to index metadata



index: index metadata의 full text index
    generated full vector index info
        length(id): {index name: index_name,
        user: user,
        embedding model: model}
    embedding models
        {full_vector: embedding model 추가}



full vector index properties
    vector: list
    original title: str
    original id: int
    vector shape: list
    added date: date




index metadata properties information
streamlit으로 아래 항목 입력
(index metadata index)
    index name:
    user: 
    description: 
    Index_type: “full vector”
    creation date: `datetime.now()`
    embedding models: {full_vector: 선택된 모델}
    latest update: `datetime.now()`
    id: 전체 index의 개수
    number of data: 0
    matching original index: 선택된 full text index
    index type id: full vectors index 의 개수
    full text preprocessing: None
    generated full vector index info: {}
    generated chunked pairs index info: {}


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
        "index_type": "full_vector",
        "creation_date": datetime.now().isoformat(),
        "latest_update": datetime.now().isoformat(),
        "number_of_data": 0,
        "embedding_model": st.session_state["selected_embedding_model"],
        "vector_size": st.session_state["vector_size"]
    }
    
    return properties


def main():
    st.title("Add Full Vector Index")
    # 1. Get full text index list

    index_list_full_vector = db.get_all_data_in_index_with_fields("metadata_full_vector", ["index_name", "embedding_model", "vector_size"])
    if index_list_full_vector is None:
        st.error("There is no full vector index available")
        return
    index_name_list_full_vector = list(index_list_full_vector.keys())


    # 3. Get total number of indexes
    number_index_full_vector = len(index_list_full_vector)

    # 4. Display list of full text indexes
    st.subheader("Full Vector Index List")
    st.write(f"index_list_chunked_pairs: {index_name_list_full_vector}")

    # 5. Enter index name
    st.session_state["new_index_name"] = "full-vector-" + st.text_input("Enter index_name(**essential**)")
    st.session_state["new_description"] = st.text_area("Enter description(optional)") 
    st.session_state["purpose"] = st.text_area("Enter purpose(optional)")
    st.session_state["user"] = st.text_input("Enter user(optional)", "all")


    # Get available embedding models
    embedding_models_deployed = db.get_models_list()
    if embedding_models_deployed is None:
        st.error("There is no embedding model available")
        return

    embedding_models_deployed = {model: val for model, val in embedding_models_deployed.items() if "embedding" in model}

    st.write(f"embedding_models_deployed: {embedding_models_deployed}")

    st.session_state["selected_embedding_model"] = st.selectbox("Select Embedding Models", embedding_models_deployed)
    
    models_dimension = embedding_models_deployed[st.session_state["selected_embedding_model"]]["dimension"]
    st.session_state["vector_size"] = models_dimension

    # 6. Check if index name already exists    
    if st.session_state["new_index_name"] in index_name_list_full_vector:
        st.session_state["index_name_valid"] = False
        st.warning("Index name already exists")
    elif st.session_state["new_index_name"] == "":
        st.session_state["index_name_valid"] = False
    else:
        st.success("Index name is available")
        st.session_state["index_name_valid"] = True

    st.write(f"Total number of full text indexes: {number_index_full_vector}")
    # write properties(dict) as table in streamlit
    st.write("Index Metadata Mapping")
    properties = set_properties()
    st.write(properties)
    
    if st.session_state["index_name_valid"]:
        if st.button("Create New Index") and st.session_state["selected_embedding_model"]:
            db.post_add_index("full_vector", st.session_state["new_index_name"], properties)

            # clear session state
            for key in st.session_state.keys():
                if key == "password_correct":
                    continue
                del st.session_state[key]
            st.session_state["index_name_valid"] = False
            del properties
            
    elif not st.session_state["selected_embedding_model"]:
        st.warning("Please select at least one embedding model")
    elif not st.session_state["index_name_valid"]:
        st.warning("Please enter a valid index name")