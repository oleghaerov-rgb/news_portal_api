import requests


class NewsAPIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Token {token}'})

    def register(self, username, email, password, first_name='', last_name=''):
        response = self.session.post(
            f'{self.base_url}/api/users/',
            json={
                'username': username,
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
            },
        )
        return self._json(response)

    def login(self, username, password):
        response = self.session.post(
            f'{self.base_url}/api/token/',
            json={
                'username': username,
                'password': password,
            },
        )
        data = self._json(response)
        if response.status_code == 200 and 'token' in data:
            self.session.headers.update({'Authorization': f"Token {data['token']}"})
        return data

    def create_news(self, title, content, summary=''):
        response = self.session.post(
            f'{self.base_url}/api/news/',
            json={
                'title': title,
                'content': content,
                'summary': summary,
            },
        )
        return self._json(response)

    def get_news(self, news_id=None, author=None, page=None):
        url = f'{self.base_url}/api/news/{news_id}/' if news_id else f'{self.base_url}/api/news/'
        params = {}
        if author is not None:
            params['author'] = author
        if page is not None:
            params['page'] = page
        response = self.session.get(url, params=params)
        return self._json(response)

    def update_news(self, news_id, **kwargs):
        response = self.session.patch(
            f'{self.base_url}/api/news/{news_id}/',
            json=kwargs,
        )
        return self._json(response)

    def delete_news(self, news_id):
        response = self.session.delete(f'{self.base_url}/api/news/{news_id}/')
        return response.status_code

    def get_users(self, user_id=None):
        url = f'{self.base_url}/api/users/{user_id}/' if user_id else f'{self.base_url}/api/users/'
        response = self.session.get(url)
        return self._json(response)

    @staticmethod
    def _json(response):
        try:
            return response.json()
        except ValueError:
            return {
                'status_code': response.status_code,
                'text': response.text,
            }
