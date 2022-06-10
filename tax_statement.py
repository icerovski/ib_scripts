import csv
from decimal import *
from datetime import date, timedelta

def fx_converter(currency, date_input, fx_data):
    if currency == 'USD':
        closest_date = find_closest_date(date_input, fx_data)
        forex = Decimal(fx_data.get(closest_date))
    if currency == 'EUR':
        forex = Decimal('1.95583')
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

    source_file_name = "ib_statement.csv"
    main_criterion = 'Trades'
    sub_criteria = {
        'Header':'Data',
        'DataDiscriminator':('Trade', 'ClosedLot')
    }

    tickers_data = {} # This is the main DATABASE

    # TICKER INFO
    tickers_info = call_data(source_file_name, 'Financial Instrument Information')
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
        }

    # TICKER TRANSACTIONS
    trades_data = call_data(source_file_name, main_criterion, sub_criteria)
    headers_trades = trades_data.pop(0)

    for line in trades_data:
        current_trade_dict = list_to_dict(headers_trades, line)

        # Below checks if we reached the Header before Options data and skips it
        ticker_name = current_trade_dict['Symbol']

        tickers_data[ticker_name]['Transactions'].append(
            {
            'DataDiscriminator':current_trade_dict['DataDiscriminator'],
            'Date':comma_break(current_trade_dict['Date/Time']),
            'Quantity':int(comma_cleanup(current_trade_dict['Quantity'])),
            'Price':float(current_trade_dict['T. Price']),
            'Commission':float(comma_cleanup(current_trade_dict['Comm/Fee'])),
        }
        )

        if not tickers_data[ticker_name]['Currency']:
            tickers_data[ticker_name]['Currency'] = current_trade_dict['Currency']

        if not tickers_data[ticker_name]['Realized']:
            if current_trade_dict['DataDiscriminator'] == sub_criteria['DataDiscriminator'][1]:
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
                exit_price = Decimal(line_dict['Price'])
                exit_commission_pos = -1 * Decimal(line_dict['Commission'])
                fx_rate_exit = fx_converter(val['Currency'], line_dict['Date'], usdbgn_dict)

                remaining_quantity += exit_quantity
                # is_closing_a_lot = True

            # Check if 'ClosedLot' is in the values. If yes, then we have a transaction, incl. opening and closing.
            elif line_dict['DataDiscriminator'] == 'ClosedLot':
                entry_date = line_dict['Date']
                entry_quantity = factor * line_dict['Quantity']
                # NB!!!
                # Entry price from 'ClosedLot already includes the entry commission that you've paid at entry. So, the 'cost' is also net of commissions.
                # Therefore, for consistency you include commission in the exit as well, i.e. revenue = exit_quantity * exit_price - exit_commission
                entry_price = Decimal(line_dict['Price'])
                cost = entry_quantity * entry_price
                q_share = Decimal(abs(entry_quantity / exit_quantity))
                revenue = entry_quantity * exit_price - exit_commission_pos * q_share
                fx_rate_entry = fx_converter(val['Currency'], line_dict['Date'], usdbgn_dict)
                tax_statement_data_line = [
                    ticker,
                    ticker_currency,
                    entry_quantity,
                    entry_date,
                    entry_price.quantize(Decimal('0.00')),
                    cost.quantize(Decimal('0.00')),
                    exit_date,
                    exit_price.quantize(Decimal('0.00')),
                    revenue.quantize(Decimal('0.00')),
                    (revenue - cost).quantize(Decimal('0.00')),
                    fx_rate_entry.quantize(Decimal('0.0000')),
                    (fx_rate_entry * entry_price).quantize(Decimal('0.00')),
                    (fx_rate_entry * cost).quantize(Decimal('0.00')),
                    fx_rate_exit.quantize(Decimal('0.0000')),
                    (fx_rate_exit * exit_price).quantize(Decimal('0.00')),
                    (fx_rate_exit * revenue).quantize(Decimal('0.00')),
                    (fx_rate_exit * revenue - fx_rate_entry * cost).quantize(Decimal('0.00')),
                    ]

                counter += 1
                print(f'{counter} {tax_statement_data_line}')
                tax_statement_array.append(tax_statement_data_line)
               
                ticker_total_quantity += entry_quantity
                ticker_total_cost += fx_rate_entry * cost
                ticker_total_revenue += fx_rate_exit * revenue

        tax_statement_array_summary.append([
            ticker,
            val['Description'],
            val['Asset Category'],
            val['Asset Type'],
            val['Exchange'],
            ticker_total_quantity,
            ticker_total_cost.quantize(Decimal('0.00')),
            ticker_total_revenue.quantize(Decimal('0.00')),
            (ticker_total_revenue - ticker_total_cost).quantize(Decimal('0.00'))])

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

if __name__ == "__main__":
    main()
