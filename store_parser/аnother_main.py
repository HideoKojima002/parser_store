import datetime
import requests
import csv
from fake_useragent import UserAgent
from bs4 import BeautifulSoup


def numberiser_for_offer(input_string):
    return ''.join(char for char in input_string if char.isnumeric())


def collect_data(city_code='10'):  # St Petersburg - 15    Moscow - 10
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    ua = UserAgent()
    print('Подождите...')

    headers = {
        'User-Agent': f'{ua.random}',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    }

    cookies = {
        'pickupStore': f'{city_code}',
        'metroStoreId': f'{city_code}',
    }

    page = 1

    city_codes = {
        '10': 'Moscow',
        '15': 'St_Petersburg',
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
                # 'Есть ли товар'
            )
        )

    while True:
        # try:
        response = requests.get(url=f'https://online.metro-cc.ru/virtual/shchedrye-vyhodnye-do-50-2-26917?page={page}', headers=headers, cookies=cookies)
        # except requests.exceptions.ConnectionError:
        #     print("Site not rechable", f'https://online.metro-cc.ru/virtual/shchedrye-vyhodnye-do-50-2-26917?page={page}')
        # with open('index.html', 'w', encoding='utf-8') as file:
        #     file.write(response.text)

        # with open('index.html', encoding='utf-8') as file:
        #     src = file.read()

        soup = BeautifulSoup(response.text, 'lxml')

        # city_name = soup.find('button', class_='header-address__receive-button').text.strip()

        cards = soup.find_all('div', class_='catalog-2-level-product-card')

        # print(page, len(cards))
        if cards:
            for card in cards:
                card_title = card.find('span', class_='product-card-name__text').text.strip()
                print(card_title)
                card_availability = card.find('button', class_='good-is-out-of-stock-hoverable')
                # card_out_of_stock = card.find('a', class_='out-of-stock')
                if card_availability:
                    continue
                try:
                    link_url_tag = card.find('a', class_='product-card-photo__link reset-link')['href']
                    card_link_url = f'https://online.metro-cc.ru{link_url_tag}'
                except TypeError:
                    continue
                card_regular_price_tag = card.find('span', class_='product-price__sum-rubles').text.strip()
                card_regular_price = f'{card_regular_price_tag} P'
                try:
                    promo_price_tag = card.find('span', class_='product-card-prices__old').text.strip()
                    card_promo_price = f'{numberiser_for_offer(promo_price_tag)} P'
                    if card_promo_price:
                        card_promo_price, card_regular_price = card_regular_price, card_promo_price
                    else:
                        card_promo_price = 'Промо цена не найдена'
                except AttributeError:
                    card_promo_price = 'Промо цена не найдена'

                card_response = requests.get(url=card_link_url, headers=headers)

                card_soup = BeautifulSoup(card_response.text, 'lxml')

                card_id_tag = card_soup.find('p', class_='product-page-content__article').text.strip()
                card_id = numberiser_for_offer(card_id_tag)

                brand_tag = card_soup.find('a', class_='product-attributes__list-item-link')
                card_brand = brand_tag.text.strip() if brand_tag else ''

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
                            # card_availability,
                        )
                    )

            page += 1
        else:
            print(f'Файл {city}_{cur_time}.csv успешно записан.')
            break


def main():
    collect_data(city_code='10')  # St Petersburg - 15    Moscow - 10


if __name__ == '__main__':
    main()
