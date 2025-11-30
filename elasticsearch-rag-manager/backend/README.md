## Middle server to safely execute DB operation
- This server deals with operations related DB, in this case elasticsearch
- Current purpose of DB is RAG
### Operations for DB management
- Read information
  - Get summarized information on DB
- Add index
  - full text index
  - full vector index, chunked pair index
- Add data
  - full text -> full text index
  - full text embedded vectors -> full vector index
  - chunked full text embedded vector -> chunked pair index