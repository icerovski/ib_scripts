import csv
from datetime import date

class Queue:

    def __init__(self) -> None:
        self.items = []
    
    def enqueue(self, item):
        """Takes in an item and inserts that item into the 0th index of the list
        that is representing the Queue.

        The runtime is O(n), or linear time, because inserting into the 0th
        index of a list forces all the other items in the list to move one index
        to the right.
        """
        self.items.insert(0, item)
    
    def dequeue(self):
        """Returns and removes the front-most item of the Queue, which is
        represented by the last item in the list.

        The runtime is O(1), or constant time, because indexing to the end of a
        list happens in constant time.
        """
        if self.items:
            return self.items.pop()
        return None

    def peek(self):
        """Returns the last item in the list, which represents the front-most
        item in the Queue.

        The runtime is constant because we're just indexing to the last item of
        the list and returning the value found there.
        """

        if self.items:
            return self.items[-1]
        return None

    def size(self):
        """Returns the size of the Queue, which is represent by the length of
        the list.

        The runtime is O(1), or constant time, because we're only returning the length."""
        return len(self.items)

    def is_empty(self):
        """Returns a Boolean value expressing whether or not the list
        representing the Queue is empty.

        Runs in constant time, because it's only checking for equality.
        """
        return self.items == []


class tradeTicket:

    def __init__(self) -> None:
        self.items = {}

    def symbol(self, s=None):
        if s: 
            self._symbol = {'symbol':s}
        return self._symbol

    def quantity(self, q=None):
        if q:
            self._quantity = {'quantity':q}
        return self._quantity

    def price(self, p=None):
        if p:
            self._price = {'price':p}
        return self._price
    
    def date(self, d=None):
        if d:
            self._date = {'date':d}
        return self._date
    
    def members(self):
        return self.items

    def __str__(self) -> str:
        return self.items

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

    # symbol_trade = Trade()
    for x in raw_db:
        symbol_val = x[symbol_col]
        date_val = comma_break(x[date_col]) # Use the date_col to find the date/time and clean it up

        q_val = x[q_col]
        # q_val = int(comma_cleanup(x[q_col])) 
        
        p_val = x[p_col]
        # p_val = float(comma_cleanup(x[p_col]))
        
        # symbol_trade.symbol(symbol_val)
        # symbol_trade.date_entry(date_val)
        # symbol_trade.quantity(q_val)
        # symbol_trade.price_entry(p_val)
        # symbol_trade.populate()
        float_row = [symbol_val, date_val, q_val, p_val]

        # db.append(symbol_trade)
        db.append(float_row)
            
    return(db)

def comma_break(line):
    D = ''
    for char in line:
        if char != ',': D += char
        else: break

    return(D)

# Some string numbers have ',' in them; clean up before conversion
def comma_cleanup(line):
    S = ''
    for char in line:
        if char != ',': S += char
        else: continue
    
    return(S)

def print_db(db):
    for x in db:
        print(x[:1], '-->', x[1:])

def same_signs(x, y): (x * y > 0)

# loop through database and list all unique symbols at index[0]
# skip lines when the same symbol
def unique_symbols(db, symbol_col, date_col, q_col, p_col):
    i = 0
    trade_dict = {}
    while i < len(db):
        # Sort out unique symbols and their trades
        symbol = db[i][symbol_col]
              
        print(symbol)
        symbol_trades = Queue()

        while db[i][symbol_col] == symbol:
            current_trade = tradeTicket()

            current_trade.quantity(db[i][q_col])
            current_trade.price(db[i][p_col])
            current_trade.date(db[i][date_col])

            # current_contracts = db[i][q_col]
            # current_price = db[i][p_col]
            # current_date = db[i][date_col]
            # float_line = [current_date, current_contracts, current_price]

            float_line = [current_trade.date(), current_trade.quantity(), current_trade.price()]    
            symbol_trades.enqueue(float_line)
            
            i += 1

            # Here you need to dequeue as well and produce the new 

            if i >= len(db):
                print(f'Total number of transactions: {i}')
                break
        
        trade_dict[symbol] = symbol_trades.items
    
    return(trade_dict)

def symbol_pnl(symbol, list, q_col= 1):
    trades_q = Queue()

    balance = existing_balance(list)
    print(balance)
    queue_list = []

    first_trade = list[q_col]


    
    ##########################################
    # first_trade = db[i][q_col]

    # entry = []
    # exit = []
    # # Evaluate the sign of the first trade to determine your strategy: either long or short
    # if same_signs(first_trade, current_contracts):
    #     entry.append(float_line)
    # else:
    #     exit.append(float_line)    
    ###########################################
    pass

def existing_balance(list, q_col= 1):
    sum = 0
    for item in list:
        sum += item[q_col]

    return sum

def first_entry(list, q_col= 1):
    return list[q_col]


def fill_symbol_pnl(symbol, q, p_entry, d_entry, p_exit, d_exit):
    cost = q * p_entry
    income = q * p_exit
    profit = income - cost
    
    return [symbol, q, p_entry, cost, d_entry, p_exit, income, d_exit, profit]

def main():
    symbol_col = 6 + 1
    date_col = 7 + 1
    q_col = 8 + 1
    p_col = 10 + 1

    raw_db = sort_ib_file()
    db = compress_db(raw_db, symbol_col, date_col, q_col, p_col)
    trade_dict = unique_symbols(db, symbol_col=0, date_col=1, q_col=2, p_col=3)

    for key, value in trade_dict.items():
        print(f'{key} : {value}')

    for i in trade_dict['BABA']:
        print(i)

if __name__ == "__main__": main()