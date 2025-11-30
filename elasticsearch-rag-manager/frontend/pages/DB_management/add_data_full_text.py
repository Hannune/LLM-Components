import streamlit as st
from utils.send_request_to_backend import _db_api
from datetime import datetime
import config as cfg
import time
import random


db = _db_api()




def set_properties(doc_name):
    st.session_state["info_tmp"][doc_name]["title"] = ".".join(doc_name.split(".")[:-1])
    st.session_state["info_tmp"][doc_name]["pages"] = 0
    st.session_state["info_tmp"][doc_name]["published_date"] = datetime.now().isoformat()
    st.session_state["info_tmp"][doc_name]["added_date"] = ""
    st.session_state["info_tmp"][doc_name]["characters"] = 0
    st.session_state["info_tmp"][doc_name]["source_type"] = doc_name.split(".")[-1]
    st.session_state["info_tmp"][doc_name]["text"] = ""
    st.session_state["info_tmp"][doc_name]["file_name"] = doc_name
    if st.session_state["add_all_at_once"]:
        st.session_state["info_tmp"][doc_name]["author"] = ""
        st.session_state["info_tmp"][doc_name]["description"] = ""
        st.session_state["info_tmp"][doc_name]["series_num"] = ""
        st.session_state["info_tmp"][doc_name]["url"] = ""
    else:
        st.session_state["info_tmp"][doc_name]["author"] = st.text_input("Author")
        st.session_state["info_tmp"][doc_name]["description"] = st.text_input("Description")
        st.session_state["info_tmp"][doc_name]["series_num"] = st.number_input("Series ID", min_value=0)
        st.session_state["info_tmp"][doc_name]["url"] = st.text_input("URL")


def main():
    """
    1. Get full text index list
    2. Select index
    3. Get data from selected index
    

    4. Upload files
    5. Check the file types and number
    6. For the files that are in the right format, create a container for each file
    7. Input following informations for full text index
        title: 
        pages: 
        author
        published date: 
        added date: `datetime.now()`
        characters: `추출된 텍스트 측정`
        description: 
        series_id: 
        url: 
        source_type: keyword
        text: `추출된 텍스트`
        file_name: 


    8. Add data to the selected index
    9. Modify metadata index
    """

    st.session_state["add_all_at_once"] = st.toggle("Add all at once", True)
    st.write(st.session_state["add_all_at_once"])

    # display list of indexes and tell users to create new index if there is no index you want to use
    index_list_full_text = db.get_all_data_in_index_with_fields("metadata_full_text", ["index_name", "purpose", "description"])
    if index_list_full_text is None:
        st.error("No full_text index available")
        return

    st.write("Full Text Index List")
    st.write(index_list_full_text)
    if len(index_list_full_text) == 0:
        st.warning("There is no index available, please create a new index for full text")
        return


    st.session_state["selected_index"] = st.selectbox("Select an index", list(index_list_full_text.keys()))
    st.session_state["selected_index_id"] = index_list_full_text[st.session_state["selected_index"]]["id"]
    
    # upload data as list
    docs = st.file_uploader("Choose a file", accept_multiple_files=True)

    if docs is None:
        return
    elif type(docs) != list:
        st.write(type(docs))
        docs = [docs]

    # if "docs" not in st.session_state:
    #     st.session_state["info"] = {}

    # check if the number of files are between 1 and 10, if not display error message
    # also check if the files are in the right format
    # iterate through the docs and if the docs[i].name is not in cfg.supported_file_types remove it from the docs
    # after going through all the files in docs, if the length of docs is 0, display error message
    if 0 < len(docs) <= cfg.max_num_docs_for_upload:
        for i in range(len(docs)):
            doc = docs[i]
            if docs[i].name.split(".")[-1].lower() not in cfg.supported_file_types:
                st.warning(f"{doc.name} is not in the supported file types, it's been removed from the list")
                del docs[i]
        if len(docs) == 0:
            st.error("No files are available for processing, please upload files in the right format")
            return
        st.session_state["docs"] = docs

    else:
        st.warning(f"Please upload between 1 and {cfg.max_num_docs_for_upload} files")
        return

    if "info" not in st.session_state:
        st.session_state["info"] = {}
        st.session_state["info_tmp"] = {}
    if st.button("Reset info"):
        st.session_state["info"] = {}
        st.session_state["info_tmp"] = {}
        del docs
        return
        
    # create a container for each file
    # for each form (with st.form("form_name")) in the container, input following informations
    for doc in docs:
        if doc.name not in st.session_state["info"]:
            st.session_state["info_tmp"][doc.name] = {}

            if st.session_state["add_all_at_once"]:
                set_properties(doc.name)
                st.session_state["info_tmp"][doc.name]["text"] = doc
                st.session_state["info"][doc.name] = st.session_state["info_tmp"][doc.name]
                st.session_state["info_tmp"][doc.name] = {}
            else:
                with st.form(f"form_{doc.name}"):
                    st.write(f"Add informations for {doc.name}")

                    set_properties(doc.name)
                    
                    # st.session_state["info_tmp"][doc.name]["title"] = ".".join(doc.name.split(".")[:-1])
                    # st.session_state["info_tmp"][doc.name]["pages"] = 0
                    # st.session_state["info_tmp"][doc.name]["author"] = st.text_input("Author")
                    # st.session_state["info_tmp"][doc.name]["published_date"] = datetime.now().isoformat()
                    # st.session_state["info_tmp"][doc.name]["added_date"] = ""
                    # st.session_state["info_tmp"][doc.name]["characters"] = 0
                    # st.session_state["info_tmp"][doc.name]["description"] = st.text_input("Description")
                    # st.session_state["info_tmp"][doc.name]["series_num"] = st.number_input("Series ID", min_value=0)
                    # st.session_state["info_tmp"][doc.name]["url"] = st.text_input("URL")
                    # st.session_state["info_tmp"][doc.name]["source_type"] = doc.name.split(".")[-1]
                    # st.session_state["info_tmp"][doc.name]["text"] = ""
                    # st.session_state["info_tmp"][doc.name]["file_name"] = doc.name

                    st.write(st.session_state["info_tmp"][doc.name])
                    
                    if st.form_submit_button("Submit"):
                        st.session_state["info_tmp"][doc.name]["text"] = doc
                        st.session_state["info"][doc.name] = st.session_state["info_tmp"][doc.name]
                        st.session_state["info_tmp"][doc.name] = {}



    if len(st.session_state["info"]) == len(docs):
        if st.button("Add data"):
            jobs = []
            for doc_name, properties in st.session_state["info"].items():
                text_file = properties["text"]
                properties["text"] = ""
                
                job = {
                    "settings":{
                        "target_index_type": "full_text",
                        "index_name_full_text": st.session_state["selected_index"],
                        "index_name_full_vector": None,
                        "index_name_chunked_pairs": None,
                        "properties": properties, 
                        "embedding_model": None,
                        "metadata_index_modify_id": st.session_state["selected_index_id"],
                        "full_text_index_modify_id": None,
                    },
                    "text_file": text_file
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
            del docs

    else:
        st.write(f"len(st.session_state['info']): {len(st.session_state['info'])}")
        st.write(f"len(docs): {len(docs)}")