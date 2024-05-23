import requests

class SolrUtil:

    @staticmethod
    def check_existing_id(entry_id, solr_url):
        """
        Check if an entry with the given ID already exists in Solr.
        :param entry_id: The ID to check.
        :return: True if exists, False otherwise.
        """
        url = f"{solr_url}/select"
        params = {
            "q": f"id:{entry_id}",
            "wt": "json"
        }
        response = requests.get(url, params=params)
        results = response.json()
        # Check if there are any documents returned
        return results['response']['numFound'] > 0

    @staticmethod
    def add_entry(entry_data, solr_url):
        """
        Add an entry to Solr if the ID does not exist already.
        :param entry_data: A dictionary representing the data to index.
        """
        if not SolrUtil.check_existing_id(entry_data.get('id'), solr_url):
            url = f"{solr_url}/update?commit=true"
            headers = {
                "Content-Type": "application/json"
            }
            response = requests.post(url, headers=headers, json=[entry_data])
            return response.json()
        else:
            return {"error": "Entry with the given ID already exists."}

    @staticmethod
    def search_entries(search_string, solr_url, start, rows):
        """
        Search entries in Solr.
        :param search_string: The query string for search.
        """
        url = f"{solr_url}/select"
        params = {
            "q": search_string,
            "wt": "json",
            "rows": rows,
            "start": start
        }
        response = requests.get(url, params=params)
        return response.json()