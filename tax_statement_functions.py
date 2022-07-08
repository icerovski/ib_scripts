import csv
from datetime import date, timedelta
from dateutil.parser import *

def date_converter(date_input):
    date_time_obj = parse(date_input)
    date_time_str = date_time_obj.strftime('%Y-%m-%d')
    return date_time_str

def fx_converter(currency, date_input, fx_data):
    if currency == 'USD':
        closest_date = find_closest_date(date_input, fx_data)
        forex = float(fx_data.get(closest_date))
    if currency == 'EUR':
        forex = 1.95583
    return forex

def find_closest_date(date_input, fx_data):
    if date_input not in fx_data:
        # "При липса на обявен курс от БНБ към 18:00 ч. се използва предхождащият го курс, обявен от БНБ."
        # So, I subtract one day to get to the new_date. Then convert to str, because function uses str.
        new_date = str(date.fromisoformat(date_input) - timedelta(days=1))
        return find_closest_date(new_date, fx_data)
    return date_input

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

def list_to_dict(keys, values):
    zipped_list = zip(keys, values)
    return dict(zipped_list)

def call_FX(source_file):
    data = {}
    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        for row in reader:
            data[switch_date_format(row[0])] = row[3]
    return data

def switch_date_format(date_str):
    date_list = date_str.split('.')
    date_list[0], date_list[-1] = date_list[-1], date_list[0]
    return '-'.join(date_list)

def call_data(source_file, main_criterion, sub_criteria=None):
    data = []
    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        assigned_header = False
        for row in reader:
            if row[0] == main_criterion:
                if sub_criteria:
                    # The first row is always the header. Assign it to your list.
                    if not assigned_header:
                        data.append(row)
                        assigned_header = True
                        continue
                
                    if row[2] in ('Trade', 'ClosedLot'):
                        data.append(row)
                else:
                    data.append(row[2:])

    return data

def call_info(source_file, data_name, asset_category):
    data = []
    # data_name = 'Financial Instrument Information'
    assigned_header = False

    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')

        for row in reader:
            if row[0].startswith(data_name):
                # Assign header to the dataset
                if row[1] == 'Header' and not assigned_header:
                    data.append(row)
                    assigned_header = True
                    continue
                
                # Assign the dataset depending on data_name
                if data_name == 'Financial Instrument Information':
                    if row[2] == asset_category:
                        data.append(row[2:])
                elif data_name == 'Trades':
                    if row[3] == asset_category and row[2] in ('Trade', 'ClosedLot'):
                        data.append(row)

    return data

def call_data_test(source_file, asset_category):
    data = []
    assigned_header = False

    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')

        for row in reader:
            if row[0].startswith('Trades'):
                if row[1] == 'Header' and not assigned_header:
                    data.append(row)
                    assigned_header = True
                    continue
                if row[3] == asset_category and row[2] in ('Trade', 'ClosedLot'):
                    data.append(row[2:])

    return data

def write_tax_statement_csv(data_set, item, month_input):
    output_file = 'U8432685' + '_' + month_input + '_' + 'Tax_Statement.csv' 
    with open(output_file, item) as destination_file:

        writer = csv.writer(destination_file)

        for single_list in data_set:
            line = []
            for item in single_list:
                line.append(str(item))

            writer.writerow(line)
        
        writer.writerow('')

def main():
    usdbgn_dict = call_FX('USDBGN.csv')

    month_input = input('Provide YYYYMM:')
    source_file_name = 'U8432685' + '_' + month_input + '_' + month_input + ".csv"
    sub_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
        }

    # PULL DATA FROM ORIGIN FILE
    # ticker info - of all instruments that were traded for the period
    stocks_info = call_info(source_file_name, 'Financial Instrument Information', 'Stocks')
    options_info = call_info(source_file_name, 'Financial Instrument Information', 'Equity and Index Options')
    tickers_info = stocks_info + options_info
    tickers_info.append(['Forex', 'EUR.USD', 'EUR.USD', '', '', '', '', '', '', '', '', '', '', '', '' ])
    headers_info = tickers_info.pop(0)

    # all trades
    trades_data = call_data(source_file_name, 'Trades', sub_criteria)

    stocks_trades = call_info(source_file_name, 'Trades', 'Stocks')
    options_trades = call_info(source_file_name, 'Trades', 'Equity and Index Options')
    tickers_trades = stocks_trades + options_trades

    headers_trades = trades_data.pop(0)

    # which are assigned for the case of options
    assigned_options = call_data(source_file_name, 'Option Exercises, Assignments and Expirations')
    headers_assigned = assigned_options.pop(0)

    # Fill up ticker DATABASE
    tickers_data = {} # database in the form of dictionary where each unique ticker is a key and has a list of values to it

    # BASIC INFO
    for ticker in tickers_info:
        if ticker[1] == 'Symbol':
            headers_info = ticker
            continue
        
        current_info_dict = list_to_dict(headers_info, ticker)

        # When analyzing Options, Symbol of the option in Trades table equals Description in Info talbes
        if current_info_dict['Asset Category'] == 'Equity and Index Options':
            ticker_name = current_info_dict['Description']
            ticker_description = ''
        else:
            ticker_name = current_info_dict['Symbol']
            ticker_description = current_info_dict['Description']

        tickers_data[ticker_name] = {
            'Description':ticker_description,
            'Asset Category':current_info_dict['Asset Category'],
            'Asset Type':current_info_dict['Type'],
            'Exchange':current_info_dict['Listing Exch'],
            'Currency':'',
            'Transactions':[],
            'Realized':False,
            'Assigned':False,
        }
   
    # ASSIGNED OPTIONS
    for option in assigned_options:
        current_option = list_to_dict(headers_assigned, option)
        ticker_name = current_option['Symbol']
        if ticker_name in tickers_data:
            # tickers_objects[ticker_name].assign_option(current_option)
            if current_option['Transaction Type'] == 'Assignment':
                tickers_data[ticker_name]['Assigned'] = True

    # TICKER TRANSACTIONS
    for line in trades_data:
        current_trade_dict = list_to_dict(headers_trades, line)

        # Below checks if we reached the Header before Options data and skips it
        ticker_name = current_trade_dict['Symbol']

        # TRANSACTIONS
        tickers_data[ticker_name]['Transactions'].append(
            {
            'DataDiscriminator':current_trade_dict['DataDiscriminator'],
            # 'Date':comma_break(current_trade_dict['Date/Time']),
            'Date':date_converter(current_trade_dict['Date/Time']),
            'Quantity':int(comma_cleanup(current_trade_dict['Quantity'])),
            'Price':float(current_trade_dict['T. Price']),
            'Commission':float(comma_cleanup(current_trade_dict['Comm/Fee'])),
        }
        )

        # CURRENCY
        if not tickers_data[ticker_name]['Currency']:
            tickers_data[ticker_name]['Currency'] = current_trade_dict['Currency']
        
        # REALIZED
        if not tickers_data[ticker_name]['Realized']:
            if current_trade_dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
                tickers_data[ticker_name]['Realized'] = True


    # FILL UP TWO MAIN STATEMENTS
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
            'Ticker','Description','Category','Type','Exchange','Quantity','Cost BGN','Revenue BGN','Profit BGN'
        ]
    ]

    counter = 0
    # Clean data file from assigned options

    for k, v in list(tickers_data.items()):
        if v['Assigned'] == True:
            del tickers_data[k]

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
        ticker_total_quantity = 0
        ticker_total_cost = 0
        ticker_total_revenue = 0

        for line_dict in val['Transactions']:

            # TYPE OF LINE
            if line_dict['DataDiscriminator'] == 'Trade':
                # The same for each calculation until remaining quntity becomes zero
                exit_date = line_dict['Date']
                exit_quantity = factor * line_dict['Quantity']
                exit_price = line_dict['Price']
                exit_commission_pos = -1 * line_dict['Commission']
                fx_rate_exit = fx_converter(val['Currency'], exit_date, usdbgn_dict)

                remaining_quantity += exit_quantity
                # is_closing_a_lot = True

            # Check if 'ClosedLot' is in the values. If yes, then we have a transaction, incl. opening and closing.
            elif line_dict['DataDiscriminator'] == 'ClosedLot':
                entry_date = line_dict['Date']
                entry_quantity = factor * line_dict['Quantity']
                # NB!!!
                # Entry price from 'ClosedLot already includes the entry commission that you've paid at entry. So, the 'cost' is also net of commissions.
                # Therefore, for consistency you include commission in the exit as well, i.e. revenue = exit_quantity * exit_price - exit_commission
                entry_price = line_dict['Price']
                cost = entry_quantity * entry_price
                q_share = abs(entry_quantity / exit_quantity)
                revenue = entry_quantity * exit_price - exit_commission_pos * q_share
                fx_rate_entry = fx_converter(val['Currency'], entry_date, usdbgn_dict)
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
                    (revenue - cost),
                    fx_rate_entry,
                    (fx_rate_entry * entry_price),
                    (fx_rate_entry * cost),
                    fx_rate_exit,
                    (fx_rate_exit * exit_price),
                    (fx_rate_exit * revenue),
                    (fx_rate_exit * revenue - fx_rate_entry * cost),
                    ]

                counter += 1
                print(f'{counter} {tax_statement_data_line}')
                tax_statement_array.append(tax_statement_data_line)
               
                ticker_total_quantity += entry_quantity
                ticker_total_cost += fx_rate_entry * cost
                ticker_total_revenue += fx_rate_exit * revenue

        tax_statement_array_summary.append(
            [
            ticker,
            val['Description'],
            val['Asset Category'],
            val['Asset Type'],
            val['Exchange'],
            ticker_total_quantity,
            ticker_total_cost,
            ticker_total_revenue,
            (ticker_total_revenue - ticker_total_cost)
            ]
        )

    total_cost = 0
    total_revenue = 0
    total_profit = 0
    for i in range(1, len(tax_statement_array_summary)):
        total_cost += tax_statement_array_summary[i][-3]
        total_revenue += tax_statement_array_summary[i][-2]
        total_profit += tax_statement_array_summary[i][-1]

    tax_statement_array_summary.append(['Total', '', '', '', '', '', \
        total_cost, total_revenue, total_profit])
    
    write_tax_statement_csv(tax_statement_array_summary, 'w', month_input)
    write_tax_statement_csv(tax_statement_array, 'a', month_input)
    
    print(*tax_statement_array_summary, sep='\n')

if __name__ == "__main__":
    main()
