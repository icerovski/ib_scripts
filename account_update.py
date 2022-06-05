import csv
from forex_python.converter import CurrencyRates
from datetime import date

def fx_converter(source, destination, date_input):
    cur = CurrencyRates()
    fx_date = date.fromisoformat(date_input)
    rate = cur.get_rate(source, destination, fx_date)
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
            "Base currency",
            "Quantity",
            "Date entry",
            "Price entry",
            "Cost",
            "Date exit",
            "Price exit",
            "Revenue",
            "Profit",
            "FX at entry",
            "Price entry BGN",
            "Cost BGN",
            "FX at exit",
            "Price exit BGN",
            "Revenue BGN",
            "Profit BGN",
        ]

        writer = csv.writer(destination_file)

        writer.writerow(fieldnames)

        for single_list in data_set:
            line = []
            for item in single_list:
                line.append(str(item))

            writer.writerow(line)

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
    for ticker, val in tickers_data.items():
        if val['Asset Category'] == 'Equity and Index Options':
            factor = 100
        else:
            factor = 1
        ticker_currency = val['Currency']
        remaining_quantity = 0
        is_closing_a_lot = False

        for line_dict in val['Transactions']:
            # Check if 'ClosedLot' is in the values. If yes, then we have a transaction, incl. opening and closing.
            if sub_criteria['DataDiscriminator'][1] in line_dict.values():
            
                if is_closing_a_lot is False:
                    # Identify the previous line, which is the line for the exit transaction
                    previous_line_dict_index = val['Transactions'].index(line_dict) - 1
                    exit_line_dict = val['Transactions'][previous_line_dict_index]

                    # The same for each calculation until remaining quntity becomes zero
                    exit_date = exit_line_dict['Date']
                    exit_price = exit_line_dict['Price']
                    exit_quantity = factor * exit_line_dict['Quantity']
                    fx_rate_exit = fx_converter(val['Currency'], 'BGN', exit_line_dict['Date'])

                    remaining_quantity += exit_quantity
                    is_closing_a_lot = True
                
                # Fill up database
                entry_quantity = factor * line_dict['Quantity']
                cost = entry_quantity * line_dict['Price']
                fx_rate_entry = fx_converter(val['Currency'], 'BGN', line_dict['Date'])
                revenue = entry_quantity * exit_line_dict['Price']
                data_line = [
                    ticker,
                    ticker_currency,
                    entry_quantity,
                    line_dict['Date'],
                    line_dict['Price'],
                    cost,
                    exit_date,
                    exit_price,
                    revenue,
                    revenue - cost,
                    fx_rate_entry,
                    fx_rate_entry * line_dict['Price'],
                    fx_rate_entry * cost,
                    fx_rate_exit,
                    fx_rate_exit * exit_price,
                    fx_rate_exit * revenue,
                    fx_rate_exit * revenue - fx_rate_entry * cost,
                    ]

                tax_statement_array.append(data_line)

                remaining_quantity += entry_quantity
                if remaining_quantity == 0:
                    is_closing_a_lot = False

    write_tax_statement_csv(tax_statement_array)
if __name__ == "__main__":
    main()
