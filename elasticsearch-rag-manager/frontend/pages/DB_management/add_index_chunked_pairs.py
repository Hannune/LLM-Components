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
        "index_type": "chunked_pairs",
        "creation_date": datetime.now().isoformat(),
        "latest_update": datetime.now().isoformat(),
        "number_of_data": 0,
        "embedding_model": st.session_state["selected_embedding_model"],
        "vector_size": st.session_state["vector_size"],
        "chunk_size": st.session_state["chunk_size"], # "chunk_size": "256",
        "overlaps": st.session_state["overlaps"],
        "chunking_method": st.session_state["chunking_method"],
    }
    
    return properties



def main():
    st.title("Add Chunked Pairs Index")
    # 1. Get chunked pairs index list
    
    index_list_chunked_pairs = db.get_all_data_in_index_with_fields("metadata_chunked_pairs", ["index_name", "embedding_model", "vector_size", "chunking_method"])
    if index_list_chunked_pairs is None:
        st.error("No chunked pairs index available")
        return
    index_name_list_chunked_pairs = list(index_list_chunked_pairs.keys())

    # 3. Get total number of indexes
    number_index_chunked_pairs = len(index_list_chunked_pairs)

    # 4. Display list of chunked pairs indexes
    st.subheader("Chunked Pairs Index List")
    st.write(f"index_list_chunked_pairs: {index_name_list_chunked_pairs}")

    # 5. Enter index properties
    st.session_state["new_index_name"] = "chunked-pairs-" + st.text_input("Enter index_name(**essential**)")
    st.session_state["new_description"] = st.text_area("Enter description(optional)") 
    st.session_state["purpose"] = st.text_area("Enter purpose(optional)")
    st.session_state["chunking_method"] = st.selectbox("Select Chunking Method", ["naive"]) 
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


    # Get chunk information    
    st.session_state["vector_size"] = models_dimension
    st.session_state["chunk_size"] = st.slider("Enter chunk size", min_value=128, max_value=1024, step=128, value=256)
    st.session_state["overlaps"] = st.slider("Enter overlaps", min_value=0., max_value=0.95, step=0.05, value=0.2)


    # 6. Check if index name already exists    
    if st.session_state["new_index_name"] in index_name_list_chunked_pairs:
        st.session_state["index_name_valid"] = False
        st.warning("Index name already exists")
    elif st.session_state["new_index_name"] == "":
        st.session_state["index_name_valid"] = False
    else:
        st.success("Index name is available")
        st.session_state["index_name_valid"] = True

    st.write(f"Total number of chunked pairs indexes: {number_index_chunked_pairs}")
    # write properties(dict) as table in streamlit
    st.write("Index Metadata Mapping")
    properties = set_properties()
    st.write(properties)
    
    if st.session_state["index_name_valid"]:
        if st.button("Create New Index"):
            db.post_add_index("chunked_pairs", st.session_state["new_index_name"], properties)

            # clear session state
            for key in st.session_state.keys():
                if key == "password_correct":
                    continue
                del st.session_state[key]
                
            st.session_state["index_name_valid"] = False
            del properties