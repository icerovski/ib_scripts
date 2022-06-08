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
    if line:
        digit = ""
        for char in line:
            if char != ",":
                digit += char
            else:
                continue
    else:
        digit = 0

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

def write_tax_statement_csv(data_set, item):
    with open("tax_statement.csv", item) as destination_file:

        writer = csv.writer(destination_file)

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
        'T. Price',
        'Comm/Fee'
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
            'Price':float(row[header_index['T. Price']]),
            'Commission':float(comma_cleanup(row[header_index['Comm/Fee']])),
        }

        if ticker_name not in tickers_data:
            tickers_data[ticker_name] = {}
            tickers_data[ticker_name]['Asset Category'] = row[header_index['Asset Category']]
            tickers_data[ticker_name]['Currency'] = row[header_index['Currency']]
            tickers_data[ticker_name]['Exchange'] = row[header_index['Exchange']]
            tickers_data[ticker_name]['Transactions'] = [ticker_current_transactions]
            tickers_data[ticker_name]['Realized'] = False
        else:
            tickers_data[ticker_name]['Transactions'].append(ticker_current_transactions)
            if not tickers_data[ticker_name]['Realized']:
                if sub_criteria['DataDiscriminator'][1] in ticker_current_transactions.values():
                    tickers_data[ticker_name]['Realized'] = True

    # Set up three main Statements
    tax_statement_array = [
        [
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
    ]

    tax_statement_array_summary = [
        [
            'Ticker','Quantity','Cost BGN','Revenue BGN','Profit BGN'
        ]
    ]

    counter = 0

    # Loop through the dictionary and perform calculations
    for ticker, val in tickers_data.items():
        if not val['Realized']:
            continue
        
        # Ticker specific calculations
        if val['Asset Category'] == 'Equity and Index Options':
            factor = 100
        else:
            factor = 1

        ticker_currency = val['Currency']
        remaining_quantity = 0
        # is_closing_a_lot = False

        ticker_total_quantity = 0
        ticker_total_cost = 0
        ticker_total_revenue = 0

        for line_dict in val['Transactions']:

            # TYPE OF LINE
            if sub_criteria['DataDiscriminator'][0] in line_dict.values():
                exit_line_dict = line_dict
                # The same for each calculation until remaining quntity becomes zero
                exit_date = exit_line_dict['Date']
                exit_quantity = factor * exit_line_dict['Quantity']
                exit_price = exit_line_dict['Price']
                exit_commission_pos = -1 * exit_line_dict['Commission']
                fx_rate_exit = fx_converter(val['Currency'], 'BGN', exit_line_dict['Date'])

                remaining_quantity += exit_quantity
                # is_closing_a_lot = True

            # Check if 'ClosedLot' is in the values. If yes, then we have a transaction, incl. opening and closing.
            if sub_criteria['DataDiscriminator'][1] in line_dict.values():
                entry_date = line_dict['Date']
                entry_quantity = factor * line_dict['Quantity']
                # NB!!!
                # Entry price from 'ClosedLot already includes the entry commission that you've paid at entry. So, the 'cost' is also net of commissions.
                # Therefore, for consistency you include commission in the exit as well, i.e. revenue = exit_quantity * exit_price - exit_commission
                entry_price = line_dict['Price']
                cost = entry_quantity * entry_price
                q_share = abs(entry_quantity / exit_quantity)
                revenue = entry_quantity * exit_price - exit_commission_pos * q_share
                fx_rate_entry = fx_converter(val['Currency'], 'BGN', line_dict['Date'])
                tax_statement_data_line = [
                    ticker,
                    ticker_currency,
                    entry_quantity,
                    entry_date,
                    entry_price,
                    cost,
                    exit_date,
                    exit_price,
                    revenue,
                    revenue - cost,
                    fx_rate_entry,
                    fx_rate_entry * entry_price,
                    fx_rate_entry * cost,
                    fx_rate_exit,
                    fx_rate_exit * exit_price,
                    fx_rate_exit * revenue,
                    fx_rate_exit * revenue - fx_rate_entry * cost,
                    ]


                counter += 1
                # print(f'{counter}', end=' ')
                print(f'{counter} {tax_statement_data_line}')
                tax_statement_array.append(tax_statement_data_line)

                # remaining_quantity += entry_quantity
                # if remaining_quantity == 0:
                #     is_closing_a_lot = False
                
                ticker_total_quantity += entry_quantity
                ticker_total_cost += fx_rate_entry * cost
                ticker_total_revenue += fx_rate_exit * revenue
                
        tax_statement_array_summary.append([
            ticker,
            ticker_total_quantity,
            ticker_total_cost,
            ticker_total_revenue,
            ticker_total_revenue - ticker_total_cost])

    total_cost = 0
    total_revenue = 0
    total_profit = 0
    for i in range(1, len(tax_statement_array_summary)):
        total_cost += tax_statement_array_summary[i][2]
        total_revenue += tax_statement_array_summary[i][3]
        total_profit += tax_statement_array_summary[i][4]
  
    tax_statement_array_summary.append(['Total', '-', \
        total_cost, total_revenue, total_profit])
    
    write_tax_statement_csv(tax_statement_array_summary, 'w')
    write_tax_statement_csv(tax_statement_array, 'a')

if __name__ == "__main__":
    main()
