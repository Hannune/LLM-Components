import streamlit as st


def main():
    st.title("This is How to page")

    add_index_description = """
    In this page you can add new index for full text, full vector, or chunked pairs.
    It will be lot helpful to add purpose of each index when creating new index.

    full_text
        - index for raw text
        - multiple index can coexist, which contains same text source but different **parsing method**
    full_vector
        - index for embedding
        - multiple index can coexist, which contains same text source but different **embedding model and vector size**
    chunked_pairs
        - index for chunked pairs
        - multiple index can coexist, which contains same text source but different **chunking method**
        - chunking method includes:
            - embedding model
            - chunk method(naive, sentencepiece, semantic)
            - vector size

    """

    add_data_description = """
    In this page you can add new data to existing index.

    Each data added to each index will be processed according to the index type
        parsing method, embedding model, vector size, chunking method ... etc.
    Any data from any source can be added to any index, but it is recommended to add data according to purpose of each index
        So it's important to keep same format of data for full_text index
    If the data has already been added to the index, the data will not be added
        It's because when the data is added to the index, the data is processed and stored in the index with given method
    """

    todo = """
    - Set rules for each index when creation
        - These rules will be kept in metadata index
        - Add "rules" for each mappings in metadata index
    - Check if the data exists in the index before adding
        - This will be done by checking the index to be added
        - So the index, especially full_vector and chunked_pairs, should keep track of the data where it came from(like full text index information)
    """