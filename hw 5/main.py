import aiohttp
from datetime import datetime, timedelta
import sys
import asyncio
import json

class HTTPError(Exception):
    pass

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            raise HTTPError(f"Request error: {e}")
        except aiohttp.http_exceptions.HttpProcessingError as e:
            raise HTTPError(f"HTTP error: {e}")
        except json.JSONDecodeError:
            raise HTTPError("Error decoding ")

def usd_eur(data: dict):
    result = {}
    if not isinstance(data, dict):
        print("Invalid data format")
        return result

    if 'exchangeRate' in data:
        for rate in data['exchangeRate']:
            if rate['currency'] in ['USD', 'EUR']:
                result[rate['currency']] = {
                    'sale': rate.get('saleRate', 'N/A'),
                    'purchase': rate.get('purchaseRate', 'N/A')
                }
    return result

async def main(number_days: int):
    result = []
    for day in range(number_days):
        d = datetime.now() - timedelta(days=day)
        shift = d.strftime('%d.%m.%Y')
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
            rates = usd_eur(response)
            if rates:
                result.append({shift: rates})
        except HTTPError as err:
            print(f'Error for {shift}: {err}')
            continue
    return result

if __name__ == '__main__':
    try:
        number_days = int(sys.argv[1])
    except ValueError:
        print("ValueError")
        sys.exit(1)

    if not (1 <= number_days <= 10):
        print('You can only view rates for the last 10 days')
        sys.exit(1)

    results = asyncio.run(main(number_days))
    print(json.dumps(results, indent=2, ensure_ascii=False))