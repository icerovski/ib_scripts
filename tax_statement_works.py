import csv
from datetime import date, timedelta, datetime
# from dateutil.parser import *
from dateutil import parser
from dateutil import relativedelta

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
    date_time_obj = parser.parse(date_input)
    date_time_str = date_time_obj.strftime('%Y-%m-%d')
    return date_time_str

def fx_converter(currency, date_input, fx_data):
    if currency == 'USD':
        closest_date = find_closest_date(date_input, fx_data)
        forex = float(fx_data.get(closest_date))
    if currency == 'EUR':
        forex = 1.95583
    return forex

def find_closest_date(current_date, fx_data):
    if current_date not in fx_data:
        # "При липса на обявен курс от БНБ към 18:00 ч. се използва предхождащият го курс, обявен от БНБ."
        # So, I subtract one day to get to the new_date.
        new_date = current_date + relativedelta.relativedelta(days=-1)
        return find_closest_date(new_date, fx_data)
    return current_date

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
    with open(str(source_file), 'r', encoding='utf-8-sig') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        for row in reader:
            current_date = switch_date_format(row[0])
            datetime_obj = parser.parse(current_date)
            data[datetime_obj] = row[3]
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
                
                    if row[1] == sub_criteria['Header'] and row[2] in sub_criteria['DataDiscriminator']:
                        data.append(row)
                else:
                    data.append(row[2:])

    return data

def write_tax_statement_csv(destination_file, data_set, item):

    with open(str(destination_file), item) as destination_file:

        writer = csv.writer(destination_file)

        for single_list in data_set:
            line = []
            for item in single_list:
                line.append(str(item))

            writer.writerow(line)
        
        writer.writerow('')

def main():
    path = '/media/sf_IB/'
    start_month = input('Start month (YYYYMM):')
    end_month = input('End month (YYYYMM):')

    usdbgn_dict = call_FX(path + 'USDBGN.csv')
    source_file_name = path + 'U8432685' + '_' + start_month + '_' + end_month + ".csv"
    destination_file_name = path + 'U8432685' + '_' + start_month + '_' + end_month + "_tax_statement.csv"
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
        if ticker[1] == 'Symbol':
            headers_info = ticker
            continue
        
        current_info_dict = list_to_dict(headers_info, ticker)

        # When analyzing Options, Symbol of the option in Trades table equals Description in Info talbes
        asset_category = current_info_dict['Asset Category']
        if asset_category == 'Stocks':
            ticker_name = current_info_dict['Symbol']
            ticker_description = current_info_dict['Description']
        elif asset_category == 'Equity and Index Options':
            ticker_name = current_info_dict['Description']
            ticker_description = ''
        elif asset_category == 'Bonds':
            ticker_name = current_info_dict['Issuer']
            ticker_description = current_info_dict['Description']
        else:
            ticker_name = current_info_dict['Symbol']
            ticker_description = current_info_dict['Description']

        # if current_info_dict['Asset Category'] == 'Equity and Index Options':
        #     ticker_name = current_info_dict['Description']
        #     ticker_description = ''
        # else:
        #     ticker_name = current_info_dict['Symbol']
        #     ticker_description = current_info_dict['Description']

        tickers_data[ticker_name] = {
            'Description':ticker_description,
            'Asset Category':current_info_dict['Asset Category'],
            'Asset Type':current_info_dict['Type'],
            'Exchange':current_info_dict['Listing Exch'],
            'Currency':'',
            'Transactions':[],
            'Realized':False,
            'Taxable': True,
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

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # FOREX P/L
    # forex_raw_data = call_data(source_file_name, 'Forex P/L Details')
    # if forex_raw_data:
    #     headers_forex = forex_raw_data.pop(0)

    #     # Fill up central database
    #     for forex in forex_raw_data:
    #         if not forex[2].startswith('Forex'):
    #             continue

    #         print(forex)
            
    #     print(headers_forex)
        
    # TICKER TRANSACTIONS
    for line in trades_data:
        current_trade_dict = list_to_dict(headers_trades, line)

        # If Asset Category is 'Bonds' the ticker_name should be shortened
        if current_trade_dict['Asset Category'] == 'Bonds':
            ticker_name = str(current_trade_dict['Symbol'].split('<br/>')[0])
        else:
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
        # if ticker_name == 'TLT 17JUN22 117.0 P':
        #     print(ticker_name)
        #     for row in tickers_data[ticker_name]['Transactions']:
        #         print(row)

        tickers_objects[ticker_name].add_transaction(current_trade_dict)

        # CURRENCY
        if not tickers_data[ticker_name]['Currency']:
            tickers_data[ticker_name]['Currency'] = current_trade_dict['Currency']
        
        tickers_objects[ticker_name].chose_currency(current_trade_dict)

        # REALIZED
        if not tickers_data[ticker_name]['Realized']:
            if current_trade_dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
                tickers_data[ticker_name]['Realized'] = True
        
        tickers_objects[ticker_name].realize_transaction(current_trade_dict, sub_criteria)

        # TAXABLE
        if tickers_data[ticker_name]['Taxable']:
            if tickers_data[ticker_name]['Currency'] == 'EUR' or tickers_data[ticker_name]['Asset Type'] == 'COMMON':
                tickers_data[ticker_name]['Taxable'] = False
        

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
            'Ticker','Description','Category','Type','Exchange','Quantity','Cost BGN','Revenue BGN','Profit BGN','Taxable'
        ]
    ]

    counter = 0

    # Loop through the dictionary and perform calculations
    for ticker, val in tickers_data.items():

        if ticker == 'TLT 17JUN22 117.0 P':
            print(ticker)
            continue

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
        ticker_total_cost_USD = 0
        ticker_total_revenue_USD = 0

        for line_dict in val['Transactions']:

            # TYPE OF LINE
            if line_dict['DataDiscriminator'] == 'Trade':
                # The same for each calculation until remaining quntity becomes zero
                exit_date = line_dict['Date']
                exit_quantity = factor * line_dict['Quantity']
                exit_price = line_dict['Price']
                exit_commission_pos = -1 * line_dict['Commission']
                fx_rate_exit = fx_converter(val['Currency'], parser.parse(exit_date), usdbgn_dict)

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
                fx_rate_entry = fx_converter(val['Currency'], parser.parse(entry_date), usdbgn_dict)
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
                # print(f'{counter} {tax_statement_data_line}')
                tax_statement_array.append(tax_statement_data_line)
               
                ticker_total_quantity += entry_quantity
                # UNCOMMENT if you want to get results in BGN
                ticker_total_cost += fx_rate_entry * cost
                ticker_total_revenue += fx_rate_exit * revenue
                # ticker_total_cost += cost
                # ticker_total_revenue += revenue
                
                ticker_total_cost_USD += cost
                ticker_total_revenue_USD += revenue

        taxable_profit = 0
        ticker_profit = ticker_total_revenue - ticker_total_cost
        ticker_profit_USD = ticker_total_revenue_USD - ticker_total_cost_USD

        if val['Taxable']:
            taxable_profit = ticker_profit
        else:
            taxable_profit = min(0, ticker_profit)

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
            ticker_profit,
            taxable_profit,
            ticker_profit_USD
            ]
        )

    total_cost = 0
    total_revenue = 0
    total_profit = 0
    total_taxable_profit = 0
    total_profit_USD = 0
    for i in range(1, len(tax_statement_array_summary)):
        total_cost += tax_statement_array_summary[i][-5]
        total_revenue += tax_statement_array_summary[i][-4]
        total_profit += tax_statement_array_summary[i][-3]
        total_taxable_profit += tax_statement_array[i][-2]
        total_profit_USD += tax_statement_array[i][-1]

    tax_statement_array_summary.append(['Total', '', '', '', '', '', \
        total_cost, total_revenue, total_profit, total_taxable_profit, total_profit_USD])
    
    write_tax_statement_csv(destination_file_name, tax_statement_array_summary, 'w')
    write_tax_statement_csv(destination_file_name, tax_statement_array, 'a')
    
    # print(*tax_statement_array_summary, sep='\n')

if __name__ == "__main__":
    main()
