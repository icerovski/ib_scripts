from forex_python.converter import CurrencyRates
import datetime

c = CurrencyRates(force_decimal=True)
trade_date = datetime.datetime(2022, 5, 25)

rate = c.get_rate('USD', 'BGN', trade_date)
print(rate)
