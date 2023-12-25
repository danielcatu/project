import requests
url = "http://localhost:9090"


def get(path, params=None):
    response = requests.get(url+path, params)
    return response.json()["data"]


def execute_query(query):
    response = get('/api/v1/query', params={'query': query})
    return response["result"]


def get_container_name(result, container_name):
    container_data = []
    for container in result:
        if container["metric"]["container"] == container_name:
            container_data.append(container)
    return container_data
