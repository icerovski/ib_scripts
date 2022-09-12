import csv
from datetime import date, timedelta
from dateutil.parser import *

class Ticker:
    def __init__(self, name, category, instrument, exchange, currency=None, realized=False, assigned=False, transactions=[]):
        self.name = name
        self.category = category
        self.instrument = instrument
        self.exchange = exchange
        self.currency = currency
        self.realized = realized
        self.assigned = assigned
        self.transactions = transactions
    
    def add_transaction(self, dict):
        self.transactions.append(
            {
            'DataDiscriminator':dict['DataDiscriminator'],
            # 'Date':comma_break(dict['Date/Time']),
            'Date':date_converter(dict['Date/Time']),
            'Quantity':int(comma_cleanup(dict['Quantity'])),
            'Price':float(dict['T. Price']),
            'Commission':float(comma_cleanup(dict['Comm/Fee'])),
        }
        )
    
    def assign_option(self, dict):
        if dict['Transaction Type'] == 'Assignment':
            self.assigned = True
    
    def chose_currency(self, dict):
        if self.currency == None:
            self.currency = dict['Currency'] 

    def realize_transaction(self, dict, sub_criteria):
        if not self.realized and not self.assigned:
            if dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
                self.realized = True

        


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

def pull_data(source_file, criterion):
    data = []
    with open(str(source_file), 'r') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        for row in reader:
            if row[0] == criterion:
                data.append(row[1:])
    return data

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
                
                    if row[1] == sub_criteria['Header'] and row[2] in sub_criteria['DataDiscriminator']:
                        data.append(row)
                else:
                    data.append(row[2:])

    return data

def write_tax_statement_csv(data_set, item):
    with open("tax_statement.csv", item) as destination_file:

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
    main_criterion = 'Trades'
    sub_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
    }


    # PULL DATA FROM ORIGIN FILE
    # ticker info - of all instruments that were traded for the period
    tickers_info = call_data(source_file_name, 'Financial Instrument Information')
    tickers_info.append(['Forex', 'EUR.USD', 'EUR.USD', '', '', '', '', '', '', '', '', '', '', '', '' ])
    headers_info = tickers_info.pop(0)

    # all trades
    trades_data = call_data(source_file_name, main_criterion, sub_criteria)
    headers_trades = trades_data.pop(0)


    # Fill up ticker DATABASE
    tickers_data = {} # database in the form of dictionary where each unique ticker is a key and has a list of values to it
    tickers_objects = {} # database is a list of Ticker objects and value is a list of transactions

    # BASIC INFO
    for ticker in tickers_info:
        # if ticker[1] == 'Symbol':
        #     headers_info = ticker
        #     continue
        
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
        }

        # create ticker object
        tickers_objects[ticker_name] = Ticker(
            ticker_name,
            current_info_dict['Asset Category'],
            current_info_dict['Type'],
            current_info_dict['Listing Exch'],
        )
    
    # ASSIGNED OPTIONS
    # Pull data from original file (which are assigned for the case of options)
    assigned_options = call_data(source_file_name, 'Option Exercises, Assignments and Expirations')
    if assigned_options:
        headers_assigned = assigned_options.pop(0)

        # Fill up central database
        for option in assigned_options:
            current_option = list_to_dict(headers_assigned, option)
            current_ticker = current_option['Symbol']
            if current_ticker in tickers_objects:
                tickers_objects[current_ticker].assign_option(current_option)
                # if current_option['Transaction Type'] == 'Assignment':
                #     tickers_objects[ticker_name].assigned = True
        
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

        tickers_objects[ticker_name].add_transaction(current_trade_dict)

        # CURRENCY
        if not tickers_data[ticker_name]['Currency']:
            tickers_data[ticker_name]['Currency'] = current_trade_dict['Currency']
        
        tickers_objects[ticker_name].chose_currency(current_trade_dict)

        # REALIZED
        if not tickers_data[ticker_name]['Realized']:
            # if current_trade_dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
            if current_trade_dict['DataDiscriminator'].startswith(sub_criteria['DataDiscriminator'][1]):
                tickers_data[ticker_name]['Realized'] = True
        
        tickers_objects[ticker_name].realize_transaction(current_trade_dict, sub_criteria)


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # FOREX P/L
    forex_raw = pull_data(source_file_name, 'Forex P/L Details')
    
    list_forex = []
    is_open = False
    for line in forex_raw:
        if line[0] == 'Header':
            header_forex = line[1:]
            continue
        if line[3].startswith('Forex'):
            list_forex.append(line[1:])
            is_open = True
        elif line[3].startswith('Closed Lot'):
            if is_open:
                list_forex.append(line[1:])
        else:
            is_open = False
    
    # Rename header: Description -> DataDiscriminator
    index_fix = header_forex.index('Description')
    header_forex.pop(index_fix)
    header_forex.insert(index_fix, 'DataDiscriminator')
    # Fill up database
    for line in list_forex:
        current_trade_dict = list_to_dict(header_forex, line)

        ticker_name = 'EUR.USD'
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

        tickers_objects[ticker_name].add_transaction(current_trade_dict)

        # CURRENCY
        if not tickers_data[ticker_name]['Currency']:
            tickers_data[ticker_name]['Currency'] = current_trade_dict['Currency']
        
        tickers_objects[ticker_name].chose_currency(current_trade_dict)

        # REALIZED
        if not tickers_data[ticker_name]['Realized']:
            # if current_trade_dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
            if current_trade_dict['DataDiscriminator'].startswith(sub_criteria['DataDiscriminator'][1]):
                tickers_data[ticker_name]['Realized'] = True
        
        tickers_objects[ticker_name].realize_transaction(current_trade_dict, sub_criteria)

    # for line in list_raw:
    #     print('\n'.join(list(map(str, line))))

    # FILL UP STATEMENTS
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
            'Ticker','Description','Category','Type','Exchange','Quantity','Cost BGN','Revenue BGN','Profit BGN'
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
    
    write_tax_statement_csv(tax_statement_array_summary, 'w')
    write_tax_statement_csv(tax_statement_array, 'a')
    
    print(*tax_statement_array_summary, sep='\n')


###################################################################################
    # GENERAL INFORMATION
    # 1. Pull up raw info data for each instrument
    info_raw = pull_data(source_file_name, 'Financial Instrument Information')
    info_raw.append(['Data', 'Forex', 'EUR.USD', 'EUR.USD', '', '', '', '', '', '', '', '', '', '', '' ])
    print('\n'.join(list(map(str, info_raw))))
    for row in info_raw:
        if row[0] == 'Header':
            print(row)

    # 2. Distribute data into a dictionary
    
    # 3. Check for assigned options and update data base accordingly
    
    # TRADE DATA
    # 1. Pull raw data
    trades_raw = pull_data(source_file_name, 'Trades')
    forex_raw = pull_data(source_file_name, 'Forex P/L Details')
    
    list_raw = []
    counter = -1
    for line in trades_raw:
        if line[0] == 'Header':
            counter += 1
            list_raw.append([])
            # list_raw[counter].append(line)
            # continue
        list_raw[counter].append(line[1:])
    list_raw.pop(-1)

    for line in list_raw:
        print('\n'.join(list(map(str, line))))
    
    #################################################################################
if __name__ == "__main__":
    main()
