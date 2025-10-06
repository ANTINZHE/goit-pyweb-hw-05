import sys
import platform
import aiohttp
import asyncio
from datetime import date, timedelta, datetime


def get_currency_rates(json_from_url):
    """Фільтруємо потрібні валюти"""
    rates = json_from_url.get("exchangeRate")
    filtered = [r for r in rates if r.get("currency") in ("USD", "EUR")]
    return filtered


async def get_normal_url(session, date):
    """Отримуємо дані з API"""
    url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'

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

async def process_day(session, str_date):
    """Отримуємо дані для однієї дати"""
    json_from_url = await get_normal_url(session, str_date)
    currency_rates = get_currency_rates(json_from_url)
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
        for day in range(count_of_days):
            current_date = today_date - timedelta(days=day)
            str_date = datetime.strftime(current_date, "%d.%m.%Y")
            day_data = await process_day(session, str_date)
            main_list.append(day_data)
    return main_list

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main())
    print(r)
