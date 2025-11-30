import streamlit as st
import streamlit as st
from utils.send_request_to_backend import _db_api
import config as cfg

db = _db_api()

def main():
    st.title("This is Add Data")
    """
    1. Get full text index list and chunked pairs index list
    2. Get available embedding models list
    3. For each chunked pairs index, if there is no embedding models for this index in available embedding models list, remove that index from the list
    4. Show the list and informations of the full text index
    5. Show the list and informations of the chunked pairs index with following informations
        index_name/description/purpose/extraction method/embedding_model/vector size/chunking method
    6. Select full text index and chunked pairs index
    7. Get titles from selected full text index data
    8. Select titles from the list

    Backend
    9. Embed selected titles with selected embedding models

    
    """

    # 1. Get full text index list and chunked pairs index list
    index_list_full_text = db.get_all_data_in_index_with_fields("metadata_full_text", ["index_name"])
    index_list_chunked_pairs = db.get_all_data_in_index_with_fields("metadata_chunked_pairs", ["index_name", "description", "purpose", "embedding_model", "vector_size", "chunking_method"])
    if index_list_full_text is None:
        st.error("No full_text index available")
        return
    if index_list_chunked_pairs is None:
        st.error("No chunked pairs index available")
        return

    # 2. Get available embedding models list
    embedding_models_deployed = db.get_models_list()

    # 3. For each chunked pairs index, if there is no embedding models for this index in available embedding models list, remove that index from the list
    for index in list(index_list_chunked_pairs.keys()):
        info = index_list_chunked_pairs[index]
        if info["embedding_model"] not in embedding_models_deployed:
            del index_list_chunked_pairs[index]

        
    # 4. Show the list and informations of the full text index
    st.write("Full Text Index List")
    st.write(index_list_full_text)
    if len(index_list_full_text) == 0:
        st.warning("There is no index available, please create a new index for full text")
        return

    # 5. Show the list and informations of the chunked pairs index with following informations
    #     index_name/description/purpose/extraction method/embedding_model/vector size/chunking method
    st.write("Chunked Pairs Index List")
    st.write(index_list_chunked_pairs)
    if len(index_list_chunked_pairs) == 0:
        st.warning("There is no index available, please create a new index for chunked pairs")
        return

    # 6. Select full text index and chunked pairs index
    selected_full_text_index_name = st.selectbox("Select Full Text Index", list(index_list_full_text.keys()))
    selected_chunked_pairs_index_name = st.selectbox("Select Chunked Pairs Index", list(index_list_chunked_pairs.keys()))

    # 7. Get titles from selected full text index data
    full_text_titles = db.get_all_data_in_index_with_fields(selected_full_text_index_name, ["title"])
    chunked_pairs_titles = db.get_all_data_in_index_with_fields(selected_chunked_pairs_index_name, ["original_full_text_data_title"])

    if full_text_titles is None or chunked_pairs_titles is None:
        st.error(f"Error in getting titles from {selected_full_text_index_name} or {selected_chunked_pairs_index_name}")
        return
    
    full_text_titles_available = list(set(full_text_titles.keys()) - set(chunked_pairs_titles.keys()))
    if len(full_text_titles_available) == 0:
        st.warning("There is no document available in selected full text index")
        return
    
    # 8. Select titles from the list

    selected_titles = st.multiselect("Select Titles", full_text_titles_available, full_text_titles_available)


    # Get basic properties for job(model) from selected full vector index
    if "info" not in st.session_state:
        st.session_state["info"] = {}
        st.session_state["info_tmp"] = {}
    if st.button("Reset info"):
        st.session_state["info"] = {}
        st.session_state["info_tmp"] = {}
    
    for title in selected_titles:
        if title not in st.session_state["info"]:
            st.session_state["info_tmp"][title] = {}
            st.write(f"Add information for {title}")

            st.session_state["info_tmp"][title]["chunked_text_vector_pairs"] = {} # after embedding
            st.session_state["info_tmp"][title]["added_date"] = "" # after adding
            st.session_state["info_tmp"][title]["original_full_text_index_name"] = index_list_full_text[selected_full_text_index_name]["index_name"]
            st.session_state["info_tmp"][title]["original_full_text_index_id"] = index_list_full_text[selected_full_text_index_name]["id"]
            st.session_state["info_tmp"][title]["original_full_text_data_title"] = title
            st.session_state["info_tmp"][title]["original_full_text_data_id"] = full_text_titles[title]["id"]

            # st.write(st.session_state["info_tmp"][title]["original_full_text_index_name"])
            st.session_state["info"][title] = st.session_state["info_tmp"][title]
            st.session_state["info_tmp"][title] = {}
            st.divider()

    st.write(f'Total number of files selected: {len(st.session_state["info"])}')

    # Backend
    # 9. Embed selected titles with selected embedding models
    if len(st.session_state["info"]) == len(selected_titles):
        if st.button("Add data"):
            jobs = []
            for title, properties in st.session_state["info"].items():
                job = {
                    "settings":{
                        "target_index_type": "chunked_pairs",
                        "index_name_full_text": selected_full_text_index_name,
                        "index_name_full_vector": None,
                        "index_name_chunked_pairs": selected_chunked_pairs_index_name,
                        "properties": properties, 
                        "embedding_model": index_list_chunked_pairs[selected_chunked_pairs_index_name]["embedding_model"],
                        "metadata_index_modify_id": index_list_chunked_pairs[selected_chunked_pairs_index_name]["id"],
                        "full_text_index_modify_id": properties["original_full_text_index_id"],
                    },
                    "text_file": None
                }

                jobs.append(job)
            res = db.post_add_data(jobs)
            if "error" in res:
                st.error(res["error"])
            else:
                st.success("Data added to job manager successfully")

            for key in st.session_state.keys():
                if key == "password_correct":
                    continue
                del st.session_state[key]
            del selected_titles
    else:
        st.write(f'len(st.session_state["info"]): {len(st.session_state["info"])}')
        st.write(f'len(selected_titles): {len(selected_titles)}')