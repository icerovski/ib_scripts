import csv
from datetime import date, timedelta, datetime
from dateutil import parser
from dateutil import relativedelta

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
    with open(str(source_file), 'r', encoding='utf-8-sig') as source_file:
        reader = csv.reader(source_file, delimiter= ',')
        
        assigned_header = False
        sub = ('C', 'Closed Lot')
        for row in reader:
            if row[0] == main_criterion:
                if not assigned_header:
                    data.append(row)
                    assigned_header = True
                    continue
                
                # Choose which line goes into database
                if row[1] == sub_criteria['Header']:
                    condition_1 = row[4]
                    condition_2 = row[11]
                    if condition_1.startswith(sub) or condition_2.startswith(sub):
                        data.append(row)

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
    destination_file_name = path + 'U8432685' + '_' + start_month + '_' + end_month + "_tax_statement_forex.csv"
    main_criterion = 'Forex P/L Details'
    sub_criteria = {
        'Header':'Data',
        'Description':'ClosedLot',
        'Code':'C'
    }


    # # PULL DATA FROM ORIGIN FILE
    trades_data = call_data(source_file_name, main_criterion, sub_criteria)
    headers_trades = trades_data.pop(0)

    # Fill up ticker DATABASE
    tickers_data = {} # database in the form of dictionary where each unique ticker is a key and has a list of values to it

    # BASIC INFO
    ticker_counter = 0
    for ticker in trades_data:
        current_trade_dict = list_to_dict(headers_trades, ticker)

        # Identify the closing transaction
        if str(current_trade_dict['Code']).startswith(sub_criteria['Code']):

            # Unique name for the closing transaction
            ticker_counter += 1
            ticker_name = '{:03d}'.format(ticker_counter) + '_' + current_trade_dict['Description']
            
            # Fill up the info for the closing transaction, i.e. at exit
            tickers_data[ticker_name] = {
                'Description':'Forex',
                'Asset Category':'Forex',
                'Asset Type':'Forex',
                'Exchange':'SMART',
                'Currency':current_trade_dict['FX Currency'],
                'Exit_date':date_converter(current_trade_dict['Date/Time']),
                'Exit_quantity':float(current_trade_dict['Quantity']),
                'Exit_proceeds':float(current_trade_dict['Proceeds in USD']),
                'Exit_basis_USD':float(current_trade_dict['Basis in USD']),
                'Exit_realized':float(current_trade_dict['Realized P/L in USD']),
                'Transactions':[],
                'Realized':False,
                'Taxable': True,
            }
            continue

        # Fill up the opening transactions for the above closing transaction
        tickers_data[ticker_name]['Transactions'].append(
            {
            'Entry_date':date_converter(current_trade_dict['Date/Time']),
            'Entry_quantity':float(current_trade_dict['Quantity']),
            'Proceeds':float(current_trade_dict['Proceeds in USD']),
            'Basis_USD':float(current_trade_dict['Basis in USD']),
            'Realized_USD':float(current_trade_dict['Realized P/L in USD']),
        }
        )

    # SET UP THE MAIN STATEMENTS
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

    # LOOP THROUGH DICTIONARY AND PERFORM CALCULATIONS
    forex_quantity_EUR = 0
    forex_basis_BGN = 0
    forex_proceeds_BGN = 0
    forex_realized_BGN = 0
    forex_realized = 0
    for ticker, val in tickers_data.items():

        exit_date = val['Exit_date']
        exit_quantity = val['Exit_quantity']
        forex_quantity_EUR += exit_quantity

        for line in val['Transactions']:
            tax_statement_data_line = []
            entry_date = line['Entry_date']
            entry_quantity = line['Entry_quantity']
            basis = line['Basis_USD']
            proceeds = line['Proceeds']
            entry_price = (basis / entry_quantity)
            exit_price = (proceeds / entry_quantity)
            realized = line['Realized_USD'] # or you can use (proceeds + basis) but there are some minor diviations from rounding
            
            # Fill up USD
            tax_statement_data_line.append(ticker)
            tax_statement_data_line.append(val['Currency'])
            tax_statement_data_line.append(entry_quantity)
            tax_statement_data_line.append(entry_date)
            tax_statement_data_line.append(entry_price)
            tax_statement_data_line.append(basis)
            tax_statement_data_line.append(val['Exit_date'])
            tax_statement_data_line.append(exit_price)
            tax_statement_data_line.append(proceeds)
            tax_statement_data_line.append(realized)

            # Convert from USD to BGN
            fx_rate_entry = fx_converter('USD', parser.parse(entry_date), usdbgn_dict)
            tax_statement_data_line.append(fx_rate_entry)

            entry_price_BGN = entry_price * fx_rate_entry
            basis_BGN = basis * fx_rate_entry
            tax_statement_data_line.append(entry_price_BGN)
            tax_statement_data_line.append(basis_BGN)

            fx_rate_exit = fx_converter('USD', parser.parse(exit_date), usdbgn_dict)
            tax_statement_data_line.append(fx_rate_exit)

            exit_price_BGN = exit_price * fx_rate_exit
            proceeds_BGN = proceeds * fx_rate_exit
            tax_statement_data_line.append(exit_price_BGN)
            tax_statement_data_line.append(proceeds_BGN)

            realized_BGN = proceeds_BGN + basis_BGN
            tax_statement_data_line.append(realized_BGN)


            tax_statement_array.append(tax_statement_data_line)
               
            exit_quantity -= entry_quantity

            forex_basis_BGN += basis_BGN
            forex_proceeds_BGN += proceeds_BGN
            forex_realized_BGN += realized_BGN
            forex_realized += realized

    tax_statement_array_summary = [
        [
            'Ticker','Description','Category','Type','Exchange','Quantity','Cost BGN','Revenue BGN','Profit BGN','Taxable'
        ]
    ]
    tax_statement_array_summary.append([
        'EURUSD','','Forex','Forex','SMART',forex_quantity_EUR,forex_basis_BGN,forex_proceeds_BGN,forex_realized_BGN,forex_realized
    ])

    write_tax_statement_csv(destination_file_name, tax_statement_array_summary, 'w')
    write_tax_statement_csv(destination_file_name, tax_statement_array, 'a')  

if __name__ == "__main__":
    main()
