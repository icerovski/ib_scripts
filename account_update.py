import csv
from forex_python.converter import CurrencyRates
import datetime

def fx_converter(source, destination, date):
    c = CurrencyRates(force_decimal=True)
    trade_date = datetime.datetime(2022, 5, 25)
    rate = c.get_rate('USD', 'BGN', trade_date)
    return rate

def comma_break(line):
    digit = ""
    for char in line:
        if char != ",":
            digit += char
        else:
            break

    return digit

def comma_cleanup(line):
    digit = ""
    for char in line:
        if char != ",":
            digit += char
        else:
            continue

    return digit

def call_data(source_file, main_criterion, sub_criteria):
    data = []
    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        assigned_header = False
        for row in reader:
            if row[0] == main_criterion:
                # The first row is always the header. Assign it to your list.
                if not assigned_header:
                    data.append(row)
                    assigned_header = True
                    continue

                if row[1] == sub_criteria['Header'] and row[2] in sub_criteria['DataDiscriminator']:
                    data.append(row)

    return data

def write_tax_statement_csv(data_set):
    with open("tax_statement.csv", "w") as destination_file:
        fieldnames = [
            "Ticker",
            "FX",
            "Date entry",
            "Quantity",
            "Price entry",
            "Expense",
            "Date exit",
            "Quantity",
            "Price exit",
            "Income",
            "Profit",
        ]
        writer = csv.writer(destination_file)

        writer.writerow(fieldnames)

        for single_list in data_set:
            line = []
            for item in single_list:
                line.append(str(item))

            writer.writerow(line)

def prepare_data_for_tax_statement():
    data_line = []

    pass

def main():
    source_file_name = "ib_statement.csv"
    main_criterion = 'Trades'
    sub_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
    }

    trades_data = call_data(source_file_name, main_criterion, sub_criteria)
    headers = trades_data.pop(0)

    # Create a dictionary to have 'name of header':'index' as a key value pair
    header_index = {}
    key_headers_list = (
        'Symbol',
        'Asset Category',
        'Currency',
        'Exchange',
        'DataDiscriminator',
        'Date/Time',
        'Quantity',
        'T. Price'
    )
    for item in headers:
        if item in (key_headers_list):
            header_index[item] = headers.index(item)

    # Create a dictionary database
    tickers_data = {}
    for row in trades_data:
        ticker_name = row[header_index['Symbol']]
        ticker_current_transactions = {
            'Type':row[header_index['DataDiscriminator']],
            'Date':comma_break(row[header_index['Date/Time']]),
            'Quantity':int(comma_cleanup(row[header_index['Quantity']])),
            'Price':float(row[header_index['T. Price']])
        }
        if ticker_name not in tickers_data:
            tickers_data[ticker_name] = {}
            tickers_data[ticker_name]['Asset Category'] = row[header_index['Asset Category']]
            tickers_data[ticker_name]['Currency'] = row[header_index['Currency']]
            tickers_data[ticker_name]['Exchange'] = row[header_index['Exchange']]
            tickers_data[ticker_name]['Transactions'] = [ticker_current_transactions]
        else:
            tickers_data[ticker_name]['Transactions'].append(ticker_current_transactions)

    # Perform calculations
    tax_statement_array = []
    entry_lot = 'ClosedLot'
    for key in tickers_data:
        if tickers_data[key]['Asset Category'] == 'Equity and Index Options':
            factor = 100
        else:
            factor = 1
        ticker_currency = tickers_data[key]['Currency']
        ticker_transactions = tickers_data[key]['Transactions']
        remaining_quantity = 0
        is_closing_a_lot = False

        for i in range(len(ticker_transactions)):
            if ticker_transactions[i]['Type'] == entry_lot:
                # !!!!!!!!!!!!!!!
                # Consider adding each element to the data line on the go
                # data_line_temp = []
                # data_line_temp.append(key)
                # data_line_temp.append(ticker_currency)
                # data_line_temp.append(entry_trade['Date'])
                # data_line_temp.append(factor * entry_trade['Quantity'])
                # data_line_temp.append(entry_trade['Price'])
                # data_line_temp.append(factor * entry_trade['Quantity'] * entry_trade['Price'])
                # data_line_temp.append(fx_converter(ticker_currency, 'BGN', entry_date['Date']))

                if is_closing_a_lot == False:
                    exit_trade = ticker_transactions[i-1]
                    exit_date = exit_trade['Date']
                    exit_price = exit_trade['Price']
                    exit_quantity = factor * exit_trade['Quantity']
                    fx_rate = fx_converter(ticker_currency, 'BGN', exit_date)

                    remaining_quantity += exit_quantity
                    is_closing_a_lot = True
                
                entry_trade = ticker_transactions[i]
                entry_date = entry_trade['Date']
                entry_price = entry_trade['Price']
                entry_quantity = factor * entry_trade['Quantity']
                
                # Convert FX
                fx_rate = fx_converter()

                # Fill up database
                data_line = [key, ticker_currency, \
                    entry_date, entry_quantity, entry_price, entry_quantity * entry_price, \
                    exit_date, entry_quantity, exit_price, entry_quantity * exit_price, \
                        (exit_price - entry_price) * entry_quantity]
                tax_statement_array.append(data_line)
                
                remaining_quantity += entry_trade['Quantity']
                if remaining_quantity == 0:
                    is_closing_a_lot = False
    
    write_tax_statement_csv(tax_statement_array)
        
if __name__ == "__main__":
    main()
