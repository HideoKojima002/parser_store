import datetime
import requests
import csv
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


def collect_data(city_code='0000073738'):  # St Petersburg - 0000103664    Moscow - 0000073738
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    ua = UserAgent()
    print('Подождите...')

    headers = {
        'User-Agent': f'{ua.random}',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    }

    cookies = {
        'selected_city_code': f'{city_code}'
    }

    page = 1

    city_codes = {
        '0000073738': 'Moscow',
        '0000103664': 'St_Petersburg',
    }
    city = city_codes.get(city_code, None)

    with open(f'{city}_{cur_time}.csv', mode='w',  encoding='utf-16', newline='') as file:
        writer = csv.writer(file, delimiter='\t')  # , delimiter=','

        writer.writerow(
            (
                'id товара',
                'Наименование',
                'Ссылка на товар',
                'Регулярная цена',
                'Промо цена',
                'Бренд',
                'Есть ли товар'
            )
        )

    while True:
        response = requests.get(url=f'https://4lapy.ru/shares/home/?page={page}', headers=headers, cookies=cookies)

        # with open(f'index.html', 'w', encoding='utf-8') as file:
        #     file.write(response.text)

        # with open('index.html', encoding='utf-8') as file:
        #     src = file.read()

        soup = BeautifulSoup(response.text, 'lxml')

        # soup = BeautifulSoup(response.content, "html.parse")
        # city = soup.find('span', class_='b-combobox__name-city')

        cards = soup.find_all('div', class_='b-common-item--catalog-item')

        for card in cards:
            card_id = card.find('span', class_='b-common-item__sticker-wrap')['data-offerid']
            card_title = card.find('span', class_='b-item-name').text.strip()
            link_url_tag = card.find('a', class_='b-common-item__description-wrap')['href']
            card_link_url = f'https://4lapy.ru{link_url_tag}'

            card_regular_price = card.find('span', class_='b-common-item__bottom_current_price').text.strip()
            promo_price_tag = card.find('span', class_='b-common-item__prev-price js-sale-origin')
            card_promo_price = promo_price_tag.text.strip()
            if card_promo_price:
                card_promo_price, card_regular_price = card_regular_price, card_promo_price
            else:
                card_promo_price = 'Промо цена не найдена'

            brand_tag = card.find('span', class_='span-strong')
            card_brand = brand_tag.text.strip() if brand_tag else ''

            if page <= 27:
                card_availability = 'Есть в наличии'

            else:
                card_availability = 'Нет в наличии'
                continue


            with open(f'{city}_{cur_time}.csv', mode='a', encoding='utf-16', newline='') as file:
                writer = csv.writer(file, delimiter='\t')  # , delimiter=','
                writer.writerow(
                    (
                        card_id,
                        card_title,
                        card_link_url,
                        card_regular_price,
                        card_promo_price,
                        card_brand,
                        card_availability,
                    )
                )

        try:
            button_next = soup.find('li', class_='b-pagination__item b-pagination__item--next').text.strip()
            # print(button_next, page)
        except AttributeError:
            print(f'Файл {city}_{cur_time}.csv успешно записан.')
            break
        page += 1


def main():
    collect_data(city_code='0000073738')  # St Petersburg - 0000103664    Moscow - 0000073738


if __name__ == '__main__':
    main()
