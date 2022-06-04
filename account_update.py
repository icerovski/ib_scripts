import csv

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

    entry_lot = 'ClosedLot'
    exit_lot = 'Trade'
    for key in tickers_data:    
        ticker_transactions = tickers_data[key]['Transactions']
        # exit_trade = []
        remaining_quantity = 0

        for i in range(len(ticker_transactions)):
            if ticker_transactions[i]['Type'] == entry_lot:
                entry_trade = ticker_transactions[i]
                if remaining_quantity == 0:
                    exit_trade = ticker_transactions[i-1]
                    remaining_quantity = exit_trade['Quantity'] + entry_trade['Quantity']
                else:
                    remaining_quantity += entry_trade['Quantity']
                    print(remaining_quantity)


            # while remaining_quantity > 0:
            #     entry_trade = ticker_transactions[i]
            #     remaining_quantity += entry_trade['Quantity']
            #     temp_sum = entry_trade['Quantity'] + exit_trade['Quantity']
            #     print(temp_sum)
            
        # for sub_key in ticker_transactions:
        #     # temp_sum = 0
        #     if sub_key['Type'] == entry_lot:
        #         temp_sum = 0
        #         # transaction_start == True
        #         temp_sum += sub_key['Quantity']
        #     elif sub_key['Type'] == exit_lot:
        #         temp_sum += sub_key['Quantity']
        
if __name__ == "__main__":
    main()
