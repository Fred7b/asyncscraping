import asyncio
from urllib.parse import urlparse
import aiohttp
import async_timeout
import uvloop
import requests
from bs4 import BeautifulSoup


async def fetch(session, url):
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


async def soup_d(html, display_result=False):
    # soup = BeautifulSoup(html, 'html.parser')
    soup = BeautifulSoup(html, 'lxml')
    if display_result:
        print(soup.prettify())
    return soup


async def extract_local_links(html):
    soup = await soup_d(html)
    return soup


async def extract_menu_urls(html, root_domain):
    soup = await soup_d(html)
    href_urls = soup.find("ul", id="menu-tags-menu").find_all("a")
    links = [a['href'] for a in href_urls]
    paths = []
    for x in links:
        link = urlparse(x).path
        paths.append(root_domain + link)
    return paths


async def collect_articles_url(html):
    """
    collect articles url from first page
    :param html:
    :return: urls
    """
    soup = await soup_d(html)
    href_urls = soup.find_all("a", class_="article-link")
    links = [a['href'] for a in href_urls]
    return links


async def extract_article_data(html):
    soup = await soup_d(html)
    try:
        title = soup.find("div", class_="post-title").find("h1").text
    except:
        title = ''
    try:
        content = soup.find("div", class_="entry-content", itemprop="articleBody").text
    except:
        content = ''

    data = {'title': title,
            'content': content}
    return data


async def main(url):
    async with aiohttp.ClientSession() as session:
        parsed_url = urlparse(url)
        root_domain = parsed_url.netloc
        domain = parsed_url.geturl()
        html = await fetch(session, url)
        menu_urls = await extract_menu_urls(html, domain)

        paths_article = []
        for m_url in menu_urls[:-1]:
            html = await fetch(session, m_url)
            article_data = await collect_articles_url(html)

            for article in article_data:
                paths_article.append(article)

        print(len(paths_article))
        for ap in paths_article:
            article_html = await fetch(session, ap)
            data = await extract_article_data(article_html)
            print(data)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main('https://tproger.ru/'))
except:
    pass
