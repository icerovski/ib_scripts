import csv

from yfinance import Ticker

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
        self._items = {}

    def ticker(self, s=None):
        if s:
            self._items['ticker'] = s
        return self._items['ticker']

    def quantity(self, q=None):
        if q:
            if is_option(self._items['ticker']):
                self._items['q'] = int(comma_cleanup(q)) * 100
            else:
                self._items['q'] = int(comma_cleanup(q))
        return self._items['q']

    def price(self, p=None):
        if p:
            self._items['p'] = float(comma_cleanup(p))
        return self._items['p']
    
    def date(self, d=None):
        if d:
            self._items['d'] = comma_break(d)
        return self._items['d']
    
    def items(self):
        return self._items

    def __str__(self) -> str:
        return self._items

class tradeLedger(tradeTicket):

    pass

def comma_break(line):
    D = ''
    for char in line:
        if char != ',': D += char
        else: break

    return(D)

def comma_cleanup(line):
    D = ''
    for char in line:
        if char != ',': D += char
        else: continue
    
    return(D)

def is_option(ticker):
    if ' ' in ticker:
        return True
    else:
        return False

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

# loop through database and list all unique tickers at index[0] skip lines when the same ticker
def unique_tickers(db, ticker_col, date_col, q_col, p_col):
    i = 0
    ledger = {}
    while i < len(db):
        # Sort out unique tickers and their trades
        ticker = db[i][ticker_col]
        ticker_trades = Queue()

        while db[i][ticker_col] == ticker:
            current_trade = tradeTicket()

            current_trade.ticker(ticker)
            current_trade.quantity(db[i][q_col])
            current_trade.price(db[i][p_col])
            current_trade.date(db[i][date_col])

            ticker_trades.enqueue(current_trade.items())
            
            i += 1

            # Here you need to dequeue as well and produce the new 

            if i >= len(db):
                print(f'Total number of transactions: {i}')
                break
        
        ledger[ticker] = ticker_trades.items

        for key, value in ledger.items():
            print(f'{key} : {value}')

    
    return(ledger)

def main():
    ticker_col = 6 + 1
    date_col = 7 + 1
    q_col = 8 + 1
    p_col = 10 + 1

    raw_db = sort_ib_file()
    ledger = unique_tickers(raw_db, ticker_col, date_col, q_col, p_col)

    for key, value in ledger.items():
        print(f'{key} : {value}')

if __name__ == "__main__": main()