


class GetQuery:
    @staticmethod
    def id_query():
        query = {
            "size": 0,  # No need to return documents
            "aggs": {
                "max_id": {
                    "max": {
                        "field": "id"
                    }
                }
            }
        }   
        return query


    @staticmethod
    def index_to_field_query():
        pass