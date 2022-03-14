import csv
import itertools

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

def float_entry(db_line, date_col, q_col, p_col):
    pass

def opposite_signs(x, y):
    return (y >= 0) if (x < y) else (x < 0)

def same_signs(x, y):
    return (x * y > 0)

# loop through database and list all unique symbols at index[0]
# skip lines when the same symbol
def unique_symbols(db, symbol_col, date_col, q_col, p_col):
    i = 0
    trade_dict = {}
    while i < len(db):
        # Sort out unique symbols and their trades
        symbol = db[i][symbol_col]
        first_trade = db[i][q_col]

        entry = []
        exit = []
        while db[i][symbol_col] == symbol:
            current_contracts = db[i][q_col]
            current_price = db[i][p_col]
            trade_date = db[i][date_col]
            invested = current_contracts * current_price

            float_line = [trade_date, current_contracts, current_price, invested]

            # Evaluate the sign of the first trade to determine your strategy: either long or short
            if same_signs(first_trade, current_contracts):
                entry.append(float_line)
            else:
                exit.append(float_line)
            
            i += 1

            # during the final itteration i goes beyond len(db) and 
            # when it returns to the while loop to check one final time
            # db[i][0] is no longer a valid statement, because there is 
            # no i index in the db. It produces an error. That's why 
            # you need to check if i is within the len(db) range.
            if i >= len(db):
                # print(f'Total number of transactions: {i}')
                break
        
        # print(f'Entry: {entry}')
        # print(f'Exit: {exit}')
        trade_dict[symbol] = [entry, exit]
    
    return(trade_dict)

def compare_sub_lists(l):

    pass

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
    trade_dict = unique_symbols(db, symbol_col=0, date_col=2, q_col=3, p_col=4)
    for key, value in trade_dict.items():
        print(f'{key} : {value}')
    
    # for i in trade_dict:
    #     x = trade_dict[i]['Entry']
    #     y = trade_dict[i]['Exit']

        # simultaneous iterration over two lists
        # https://www.programiz.com/python-programming/dictionary
        # https://www.geeksforgeeks.org/python-accessing-key-value-in-dictionary/
        # for (a,b) in itertools.zip_longest(x, y):
        #     print (a, b)
