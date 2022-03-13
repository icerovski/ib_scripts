import csv
from multiprocessing.sharedctypes import Value

def sort_ib_file():
    data = []
    counter = 0
    with open('ib_statement.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'Trades' and row[1] == 'Data':
                counter += 1 # used to count the transactions
                row = [counter, *row] # using unpack insert an item in the begining of the list
                data.append(row) # append the newly created row to the data

        return(data)

def compress_db(raw_db, symbol_col, date_col, q_col, p_col):
    db = []
    # This is erazing existing values with new ones, until we get a different key
    # I guess this is a feature of dictionary, so perhaps I should use lists only
    for x in raw_db:
        symbol_val = x[symbol_col]
        date_val = clean_date(x[date_col]) # Use the date_col to find the date/time and clean it up
        q_val = int(convert_str(x[q_col])) 
        p_val = float(convert_str(x[p_col]))
        float_row = [symbol_val, x[0], date_val, q_val, p_val]
        db.append(float_row)
    
    return(db)

def clean_date(line):
    D = ''
    for char in line:
        if char != ',':
            D += char
        else:
            break
    
    return(D)

# Some string numbers have ',' in them; clean up before conversion
def convert_str(line):
    S = ''
    for char in line:
        if char != ',':
            S += char
        else:
            continue
    
    return(S)

def print_db(db):
    for x in db:
        print(x[:1], '-->', x[1:])

def wa_invested(q1, p1, q2, p2):
    ans = (q1 * p1 + q2 * p2) / (q1 + q2)
    return(ans)

# loop through database and list all unique symbols at index[0]
# skip lines when the same symbol
def unique_symbols(db, symbol_col, date_col, q_col, p_col):
    i = 0
    while i < len(db):
        # Sort out unique symbols and their trades
        symbol = db[i][symbol_col]
        print(f'\n{symbol}')
        
        # Evaluate the sign of the first trade to determine your strategy: either long or short
        if db[i][q_col] > 0:
            is_long_trade = True
        else:
            is_long_trade = False

        while db[i][symbol_col] == symbol:
            trade_contracts = db[i][q_col]
            trade_price = db[i][p_col]
            trade_date = db[i][date_col]
            invested = trade_contracts * trade_price

            if is_long_trade and trade_contracts > 0:
                print('Entry:')
            elif not is_long_trade and trade_contracts < 0:
                print('Entry')
            else:
                print('Exit')

            print(f'\t {trade_date}: {trade_contracts} * {trade_price} = {invested}')
            
            i += 1

            # during the final itteration i goes beyond len(db) and 
            # when it returns to the while loop to check one final time
            # db[i][0] is no longer a valid statement, because there is 
            # no i index in the db. It produces an error. That's why 
            # you need to check if i is within the len(db) range.
            if i >= len(db):
                print(f'Total number of transactions: {i}')
                break

# round_trade_sum = 0 # if equal to zero then we have a round trade
# remaining_shares = 0
# entry_number = 0 # number of shares entered into
# exit_number = 0 # number of shares exited

symbol_col = 6 + 1
date_col = 7 + 1
q_col = 8 + 1
p_col = 10 + 1

if __name__ == "__main__":
    raw_db = sort_ib_file()
    db = compress_db(raw_db, symbol_col, date_col, q_col, p_col)
    # print_db(db)
    unique_symbols(db, symbol_col=0, date_col=2, q_col=3, p_col=4)