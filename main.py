import asyncio
from src.parser import Parser

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

parser = Parser(keyword_list=KEYWORDS)

async def main():
    result_find = parser.return_data()
    while True:
        try:
            data = await anext(result_find)
            print(f"""Дата публикации: {data[0]},
                Заголовок: {data[1]},
                Ссылка: {data[2]}\n""")
        except StopAsyncIteration:
            break

if __name__ == '__main__':
    asyncio.run(main())