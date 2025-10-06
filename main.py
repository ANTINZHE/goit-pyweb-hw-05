import sys
import platform
import aiohttp
import asyncio
from datetime import date, timedelta, datetime


def get_all_currencies(rates):
    """ Отримуємо усі ідентифікатори валют"""
    all_currencies = [rate.get('currency') for rate in rates]
    return all_currencies


def get_currency_rates(json_from_url, all_currencies):
    """Фільтруємо потрібні валюти"""
    rates = json_from_url.get("exchangeRate")
    used_currency = ["USD", "EUR"]
    if len(sys.argv) > 2:
        used_currency.extend(get_currency_from_sys(all_currencies))


    filtered = [rate for rate in rates if r.get("currency") in used_currency]
    return filtered


async def get_normal_url(session, str_date):
    """Отримуємо дані з API"""
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={str_date}'

    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error {response.status}")
                return {}
    except aiohttp.ClientError as e:
        print(e)
        return {}


def get_dats_from_sys():
    """Отримуємо кількість днів з аргументів командного рядка"""
    if len(sys.argv) < 2:
        sys.exit(1)

    try:
        days = int(sys.argv[1])
        if 1 <= days <= 10:
            return days
        else:
            print(" < 10")
            sys.exit(1)
    except ValueError:
        sys.exit(1)

def get_currency_from_sys(all_currencies):
    """Отримуємо додаткові валюти з аргументів командного рядка"""
    added_currencies = []
    try:
        for i in range(len(sys.argv[2:])):
            currency = sys.argv[i + 2]
            if currency not in all_currencies:
                print(f"Error {currency}")
                sys.exit(1)
            else:
                added_currencies.append(currency)
        return added_currencies
    except ValueError:
        sys.exit(1)

async def process_day(session, str_date, all_currencies):
    """Отримуємо дані для однієї дати"""
    json_from_url = await get_normal_url(session, str_date)
    currency_rates = get_currency_rates(json_from_url, all_currencies)
    return {
        str_date: {
            rate["currency"]: {
                "sale": rate.get("saleRate"),
                "purchase": rate.get("purchaseRate")
            }
            for rate in currency_rates
        }
    }


async def main():
    today_date = date.today()
    count_of_days = get_dats_from_sys()
    main_list = []

    async with aiohttp.ClientSession() as session:
        first_date = today_date - timedelta(days=1)
        str_date = datetime.strftime(first_date, "%d.%m.%Y")
        first_json = await get_normal_url(session, str_date)
        all_currencies = get_all_currencies(first_json.get("exchangeRate", []))

        for day in range(count_of_days):
            current_date = today_date - timedelta(days=day + 1)
            str_date = datetime.strftime(current_date, "%d.%m.%Y")
            day_data = await process_day(session, str_date, all_currencies)
            main_list.append(day_data)
    return main_list

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)