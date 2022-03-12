import csv
import pandas as pd

def sort_ib_file():
    data = []
    counter = 0
    with open('multi_20220103_20220310.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == 'Trades' and row[1] == 'Data':
                counter += 1 # used to count the transactions
                row = [counter, *row] # using unpack insert an item in the begining of the list
                data.append(row) # append the newly created row to the data

        return(data)

def convert_to_dict(raw_table, key_col, item_1_col, item_2_col, item_3_col):
    ib_dict = {}
    for x in raw_table:
        key = clean_date(x[key_col])
        ib_dict[x[0]] = [key, x[item_1_col], x[item_2_col], x[item_3_col]]
    
    return(ib_dict)

def clean_date(line):
    D = ''
    for char in line:
        if char != ',':
            D += char
        else:
            break
    
    return(D)

# round_trade_sum = 0 # if equal to zero then we have a round trade
# remaining_shares = 0
# entry_number = 0 # number of shares entered into
# exit_number = 0 # number of shares exited

symbol_col = 6 + 1
date_col = 7 + 1
q_col = 8 + 1
p_col = 10 + 1

if __name__ == "__main__":
    raw_table = sort_ib_file()
    print(raw_table)
    table = convert_to_dict(raw_table, date_col, symbol_col, q_col, p_col)
    print(table)
    