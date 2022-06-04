import csv
from operator import sub

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

                if row[1] == sub_criteria['Header'] and \
                row[2] in sub_criteria['DataDiscriminator']:
                    data.append(row)

    # counter = 0
    # with open(str(source_file), "r") as source_file:
    #     reader = csv.reader(source_file, delimiter=",")
    #     for row in reader:
    #         if row[0] == "Trades" and (row[1] == "Data" or row[1] == "ClosedLot"):
    #             counter += 1  # used to count the transactions
    #             row = [
    #                 counter,
    #                 *row,
    #             ]  # using unpack insert an item in the begining of the list
    #             data.append(row)  # append the newly created row to the data
    #             print(data)

    return data

def pull_ticker(row, ticker_index):
    ticker_name = row[ticker_index]
    if ticker_name and ticker_name != 'Symbol':
        return ticker_name
    else:
        return None

def call_ticker_names(data_list):
    symbol_index = header_index('Symbol', data_list)
    ticker_list = []
    # Start from 1 to omit the Header row
    for i in range(1, len(data_list)):
        row = data_list[i]
        ticker = row[symbol_index]
        # Excludes 'Symbol' as a potential ticker name, because it catches it as such.
        if ticker and ticker != 'Symbol':
            if ticker not in ticker_list:
                ticker_list.append(ticker)

    return ticker_list

def header_index(header, array):
    return array[0].index(header)

def pull_ticker_data(ticker, data_list):
    symbol_index = header_index('Symbol', data_list)
    ticker_raw_data = []
    for i in range(len(data_list)):
        if data_list[i][symbol_index] == ticker:
            ticker_raw_data.append(data_list[i])

    return ticker_raw_data

def transponse(matrix):
    rows = len(matrix)
    cols = len(matrix[0])

    matrix_t = []
    for width in range(cols):
        row = []
        for height in range(rows):
            row.append(matrix[height][width])
        matrix_t.append(row)

    return matrix_t

def compute_ticker_data(symbol, data):
    result = pull_ticker_data(symbol, data)
    return transponse(result)

# def trade_entry = {
#         "Ticker":str,
#         "Date entry":str,
#         "Quantity entry":int,
#         "Price entry":float,
#         "Expense":float,
#         "Date exit":str,
#         "Quantity exit":int,
#         "Price exit":float,
#         "Income":float,
#         "Profit":float,
#     }

def main():
    source_file_name = "ib_statement.csv"
    trades_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
    }
    trades_data = call_data(source_file_name, 'Trades', trades_criteria)
    
    key_titles = (
        'Symbol',
        'Asset Category',
        'Currency',
        'Exchange',
        'DataDiscriminator',
        'Date/Time',
        'Quantity',
        'T. Price'
    )
    headers = {}
    print(trades_data[0])
    print(trades_data[0].index('Header'))
    for item in trades_data[0]:
        if item in (key_titles):
            headers[item] = trades_data[0].index(item)

    print(headers.items())

    # ticker_index = header_index('Symbol', trades_data)
    # asset_category_index = header_index('Asset Category', trades_data)
    # currency_index = header_index('Currency', trades_data)
    # exchange_index = header_index('Exchange', trades_data)
    # transaction_type_index = header_index('DataDiscriminator', trades_data)
    # date_index = header_index('Date/Time', trades_data)
    # quantity_index = header_index('Quantity', trades_data)
    # price_index = header_index('T. Price', trades_data)


    ticker_dict = {}
    for row in trades_data:
        ticker_name = pull_ticker(row, headers['Symbol'])
        if ticker_name:
            ticker_current_transactions = {
                'Transaction': row[headers['DataDiscriminator']],
                'Date':row[headers['Date/Time']],
                'Quantity':row[headers['Quantity']],
                'Price':row[headers['T. Price']]
            }
            if ticker_name not in ticker_dict:
                ticker_dict[ticker_name] = {}
                ticker_dict[ticker_name]['Asset Category'] = row[headers['Asset Category']]
                ticker_dict[ticker_name]['Currency'] = row[headers['Currency']]
                ticker_dict[ticker_name]['Exchange'] = row[headers['Exchange']]
                ticker_dict[ticker_name]['Transactions'] = [ticker_current_transactions]
            else:
                ticker_dict[ticker_name]['Transactions'].append(ticker_current_transactions)

    print(ticker_dict.keys())
    print(ticker_dict.values())
    print(ticker_dict.items())

    tickers = call_ticker_names(trades_data)

    for ticker in tickers:
        ticker_data = compute_ticker_data(ticker, trades_data)
        profit_index = header_index('Realized P/L', trades_data)
        flag_index = header_index('DataDiscriminator', trades_data)

        for i in range(len(ticker_data[0])):
            # If trade has zero realized Profit or Loss, this means it is not yet closed.
            # So, you skip to next 'i', because you only report realized profit/ loss.
            rlzd = ticker_data[profit_index][i]
            if float(rlzd) != 0:
                flag = ticker_data[flag_index][i]
                if flag in ('Trade', 'ClosedLot'):
                    print(f'{ticker}: {ticker_data[flag_index][i]}')

        for i, v in enumerate(ticker_data[flag_index]):
            if v == 'Trade':
                print(i, v)
if __name__ == "__main__":
    main()
