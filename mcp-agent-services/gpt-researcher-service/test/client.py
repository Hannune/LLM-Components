import requests

# Simple research without files
def research(session_id, query, base_url="http://localhost:8000"):
    response = requests.post(
        f"{base_url}/research",
        data={"session_id": session_id, "query": query}
    )
    return response.json()

# Research with files
def research_with_files(session_id, query, file_paths, base_url="http://localhost:8000"):
    files = [("files", open(f, "rb")) for f in file_paths]
    response = requests.post(
        f"{base_url}/research",
        data={"session_id": session_id, "query": query},
        files=files
    )
    for _, f in files:
        f.close()
    return response.json()


# Example usage
if __name__ == "__main__":
    # # Simple research
    # result = research("session-001", "What are the latest AI trends?")
    # print(result["report"])

    # With files (uncomment to use)
    result = research_with_files("session-002", "Analyze given file name of 'llms.txt'", ["llms.txt"])
    print(result["report"])
