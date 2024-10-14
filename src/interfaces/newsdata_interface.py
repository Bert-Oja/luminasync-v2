import requests

from logging_config import get_logger


class NewsDataInterfaceException(Exception):
    pass


class NewsDataInterface:
    def __init__(self, api_key: str) -> None:
        self.logger = get_logger(self.__class__)
        self.api_key = api_key
        self.base_url = "https://newsdata.io/api/1/latest"
        self.params = {
            "apikey": self.api_key,
            # "language": "en",
            "size": 10,
            "removeduplicate": 1,
        }

    def fetch_news_data(self, country=None, category="top", query=None) -> dict:
        url = self.base_url
        if country:
            self.params["country"] = country
        if category:
            self.params["category"] = category
        if query:
            self.params["q"] = query
        try:
            self.logger.info("Fetching news data.")
            response = requests.get(url, params=self.params, timeout=30)
            data = response.json()
            if response.status_code != 200:
                self.logger.error(f"Error fetching news data: {data['message']}")
                raise NewsDataInterfaceException(
                    f"Error fetching news data: {data['message']}"
                )

            articles = []
            for article in data["results"]:
                articles.append(
                    {
                        "title": article["title"],
                        "description": article["description"],
                        "url": article["link"],
                        "source": article["source_name"],
                        "published_at": article["pubDate"],
                    }
                )

            return articles

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching news data: {e}")
            raise NewsDataInterfaceException(f"Error fetching news data: {e}") from e
