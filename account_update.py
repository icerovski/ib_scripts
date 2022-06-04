import csv
from typing import Type

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

def main():
    source_file_name = "ib_statement.csv"
    trades_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
    }
    trades_data = call_data(source_file_name, 'Trades', trades_criteria)
    headers = trades_data.pop(0)

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
    header_index = {}
    for item in headers:
        if item in (key_headers_list):
            header_index[item] = headers.index(item)

    tickers_data = {}
    for row in trades_data:
        ticker_name = row[header_index['Symbol']]
        ticker_current_transactions = {
            'Type':row[header_index['DataDiscriminator']],
            'Date':row[header_index['Date/Time']],
            'Quantity':row[header_index['Quantity']],
            'Price':row[header_index['T. Price']]
        }
        if ticker_name not in tickers_data:
            tickers_data[ticker_name] = {}
            tickers_data[ticker_name]['Asset Category'] = row[header_index['Asset Category']]
            tickers_data[ticker_name]['Currency'] = row[header_index['Currency']]
            tickers_data[ticker_name]['Exchange'] = row[header_index['Exchange']]
            tickers_data[ticker_name]['Transactions'] = [ticker_current_transactions]
        else:
            tickers_data[ticker_name]['Transactions'].append(ticker_current_transactions)

    # for key, value in tickers_data.items():
    #     print(key, value)
    # for key in tickers_data:
    #     current_ticker = tickers_data[key]
    #     cat = current_ticker['Asset Category']
    #     realized = current_ticker['Transactions']
    #     rlzd_value = 'ClosedLot'
    #     list_of_bool = [True for elem in realized if rlzd_value in elem.values()]
    #     if any(list_of_bool):
    #         print(f'{key} - {cat}')

    open_val = 'Trade'
    close_val = 'ClosedLot'
    transaction_start = False
    transaction_in_progress = False
    transaction_close = False
    for key in tickers_data:    
        ticker_transactions = tickers_data[key]['Transactions']
        for sub_key in ticker_transactions:
            if sub_key['Type'] == open_val:
                transaction_start == True
            elif sub_key['Type'] == close_val:
                transaction_in_progress = True
            
        for sub_key in ticker_transactions:
            if sub_key['Type'] == rlzd_value:
                is_realized = True
                break
        if is_realized:
            print(key)

            for i in range(len(ticker_transactions)):
                print(ticker_transactions[i])
        else:
            continue
        
if __name__ == "__main__":
    main()
