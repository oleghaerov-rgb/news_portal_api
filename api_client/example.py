from client import NewsAPIClient


BASE_URL = 'http://127.0.0.1:8000'


def main():
    client = NewsAPIClient(BASE_URL)

    print('Register:')
    print(client.register(
        username='api_user',
        email='api_user@example.com',
        password='StrongPass123!',
        first_name='API',
        last_name='User',
    ))

    print('Login:')
    print(client.login('api_user', 'StrongPass123!'))

    print('Create news:')
    created = client.create_news(
        title='API news example',
        summary='Short summary for API news',
        content='This is a long enough text for the API news example. It has more than fifty symbols.',
    )
    print(created)

    news_id = created.get('id')
    if news_id:
        print('Get one news:')
        print(client.get_news(news_id))

        print('Update news:')
        print(client.update_news(news_id, summary='Updated summary from API client'))

        print('Delete news:')
        print(client.delete_news(news_id))

    print('List news:')
    print(client.get_news())


if __name__ == '__main__':
    main()
