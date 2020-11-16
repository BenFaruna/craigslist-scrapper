import requests

from bs4 import BeautifulSoup
from django.shortcuts import render
from requests.compat import quote_plus

from . import models

BASE_CRAIGSLIST_URL = 'https://atlanta.craigslist.org/search/?query={}&min_price={}&max_price={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    minimum = request.POST.get('min')
    maximum = request.POST.get('max')
    models.Search.objects.create(search=search)

    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search), minimum, maximum)
    response = requests.get(final_url)
    data = response.text

    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})

    final_posting = []

    for post in post_listings:
        post_title = post.find('a', class_='result-title').text
        post_url = post.find('a').get('href')

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://www.craigslist.org/images/peace.jpg'

        if post.a.find('span', class_='result-price'):
            post_price = post.a.find('span', class_='result-price').text
        else:
            post_price = 'N/A'

        final_posting.append((post_title, post_url, post_price, post_image_url))

    context = {
        'search': search,
        'final_posting': final_posting,
    }
    
    return render(request, 'scrapper/new_search.html', context)
