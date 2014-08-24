"""
For some CommonMeasurement, quote data is needed to calculate the result. For example, P/E Ratio is price / entity where the stock price will not be there in any statement, we will need an external source to get the stock price on that date, or something like average of that month.
If this method raises NotImplementedError, all CommonMeasurements which need price data will return 0
"""
from datetime import date
import requests
import json

hostname = "127.0.0.1:8000"

def get_quote(symbol, fiscal_period_end_date):
    # raise NotImplementedError
    api_url = 'http://{hostname}/get_quote?symbol={symbol}&year={year}&month={month}'.format(
        hostname=hostname,
        symbol=symbol,
        year=fiscal_period_end_date.year,
        month=fiscal_period_end_date.month
    )
    r = requests.get(api_url)
    obj = json.loads(r.text)
    if not obj:
        return 0
    return round(sum([x['close_price'] for x in obj])/float(len(obj)), 2)

if __name__ == '__main__':
    print get_quote('AAPL', date(2014, 3, 3))
