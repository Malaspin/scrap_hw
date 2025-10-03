import httpx
from fake_headers import Headers
import bs4
import datetime

headers = Headers(os='lin', headers=True).generate()

class Parser:

    base_url = 'https://habr.com/'
    url = 'https://habr.com/ru/articles/'

    client = httpx.AsyncClient()

    def __init__(self,keyword_list):
        self.page = None
        self.KEYWORDS = keyword_list


    async def start_get_data(self):
        # await asyncio.sleep(3)
        resp = await self.client.get(url=self.url, headers=headers)
        soup = bs4.BeautifulSoup(resp.text, features='lxml')
        page = soup.select('article.tm-articles-list__item')
        self.page = page

    async def get_href_head(self,href=False, head=False):
         page = self.page
         for ref in page:
             hd = ref.select_one('a.tm-title__link')
             if href:
                 yield self.base_url + hd['href'][1:]
             if head:
                 yield hd.select_one('span').text

    async def get_prev_text(self):
        page = self.page
        for txt in page:
            paragraphs = txt.select('p')
            for p in paragraphs:
                p_text = p.text
                yield p_text

    async def get_all_text(self):
        lincs =[linc async for linc in self.get_href_head(href=True)]
        for linc in lincs:
            resp = await self.client.get(linc, headers=headers)
            soup = bs4.BeautifulSoup(resp.text, features='lxml')
            paragraphs = soup.select('div[xmlns="http://www.w3.org/1999/xhtml"] > p')
            p_all = ''.join(p.text for p in paragraphs)
            yield p_all

    async def get_datetime(self):
        page = self.page
        for dt in page:
            date_time = datetime.datetime.fromisoformat(dt.select_one('time')['datetime'])
            yield date_time

    async def get_hashtag(self):
        page = self.page
        for hashtag in page:
            hash_tag = hashtag.select('a.tm-publication-hub__link > span:not(.tm-article-snippet__profiled-hub) ')
            ht_all = ''.join(h.text for h in hash_tag)
            yield ht_all

    async def return_data(self):
        await self.start_get_data()
        dt_gen = self.get_datetime()
        head_gen = self.get_href_head(head=True)
        href_gen = self.get_href_head(href=True)
        hashtag_gen = self.get_hashtag()
        preview_gen = self.get_prev_text()
        all_text_gen = self.get_all_text()
        while True:
            try:
                date_time = await anext(dt_gen)
                head = await anext(head_gen)
                href = await anext(href_gen)
                hashtag = await anext(hashtag_gen)
                prev_text = await anext(preview_gen)
                full_text = await anext(all_text_gen)  
                all_data_post = ' '.join([head] + [hashtag] + [prev_text] + [full_text]).lower()
                if any(keyword.lower() in all_data_post for keyword in self.KEYWORDS):
                    yield (date_time, head, href)
            except StopAsyncIteration:
                break 