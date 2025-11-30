import streamlit as st
import requests

def clear_session_state():
    st.session_state = {}


def handle_response(res):
    try:
        res.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        try:
            return res.json()  # Try to parse the response as JSON
        except ValueError:
            print("Response content is not valid JSON")
            return None
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print the HTTP error
        try:
            return res.json()  # Try to parse the error response as JSON
        except ValueError:
            print("Error response content is not valid JSON")
            return None
    except Exception as err:
        print(f"Other error occurred: {err}")  # Print any other errors
        return None
