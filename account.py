import csv

# from yfinance import Ticker

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
    
    def __str__(self) -> str:
        return self.items


class tradeTicket(Queue):

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


class transactionConstructor(Queue):
    '''All methods and cases that involve the transition from raw data to transactionPNL Object'''

    def __init__(self) -> None:
        super().__init__()
    

class transactionPNL(tradeTicket):
    '''Build each row in the summary table. It consists of the following items:
    Stock, Quantity, Date Entry, Price Entry, Date Exit, Price Exit, Cost, Income, Profit'''

    def __init__(self) -> None:
        super().__init__()
        

class transactionSummaryTable (transactionPNL):
    '''Full summary of all transactions, which consits  of transactionPNL Objects.'''

    def __init__(self) -> None:
        super().__init__()
        


class dealPipe(Queue):
    '''Track each entry and act depending on the sign and the size of the entry. Enqueue entries with the same sign, until you get
    an entry with a different sign. In that case you dequeue it from the enqueued entries (FIFO). You do that until you either
    get to zero, or switch signs from the remaining entry. Keep entries IDs, which you can link to the built up database to obtain
    prices and dates of the transaction.'''
    def __init__(self) -> None:
        super().__init__()
    
    def enqueue(self, item_id, item):
        '''Definitions:
        id- the trade number in the sequence of trades as shown in the IB Trade table.
        item- the number of contracts for the current row.'''
        new_item = {'id':item_id, 'item':item}      
        return super().enqueue(new_item)
     
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

def equal_signs(a, b):
    return ((a == b) & (a == 0)) | (a * b > 0)

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
        ticker_PNL = Queue()
        current_pipe = dealPipe()
        tax_ledger = []
        
        # j iteration wouldn't work. The pipe will only have two positions:
        # ONE where trade_q piles up because it is of the same sign
        # TWO, which is temporary, where you save the incoming trade_q of a different sign, 
        # so that you can subtract it from ONE, remove the smaller of the two, and leave the result as the new ONE.
        
        j = 0
        while db[i][ticker_col] == ticker:
            current_trade = tradeTicket()
            current_trade.ticker(ticker)
            current_trade.quantity(db[i][q_col])
            current_trade.price(db[i][p_col])
            current_trade.date(db[i][date_col])
            current_q = current_trade.quantity()
            # first_q_correct = ticker_PNL.peek_first()['q']

            if current_pipe.is_empty():
                current_pipe.enqueue(j, current_q)
                ticker_PNL.enqueue(current_trade.items())
            elif equal_signs(current_trade.quantity(), ticker_PNL.peek()['q']):
                # compare the current (latest) item, with the 'first item' in the queue
                # if different signs, check if this item is not the second one, i.e. there's no other items ahead of you (other than the 'first item')
                # if there is another item ahead of you, do these two things: (1) add current row at the back of the queue and (2) subtract the second item and the first item
                # Then remove the smaller of the two, and leave the result as the new 'first item'.
                ticker_PNL.enqueue(current_trade.items())
                print(ticker_PNL.items)
                # consider the case when there is only one entry
            else:
                first_q = current_pipe.peek()['item']
                first_q_id = current_pipe.peek()['id']

                if equal_signs(current_q, first_q):
                    current_pipe.enqueue(j, current_q)
                else:
                    yEn = ticker_PNL.items[j] 
                    en_date = yEn['d']
                    entry_q = yEn['q']
                    en_price = yEn['p']
                    yEx = ticker_PNL.items[first_q_id]
                    ex_date = yEx['d']
                    exit_q = yEx['q']
                    ex_price = yEx['p']
                    
                    if abs(entry_q) > abs(exit_q):
                        transaction_q = - 1 * exit_q
                        # first_q -= transaction_q # decrease the first quantity with the one that we are booking now
                        current_pipe.dequeue()
                        current_pipe.enqueue(j, entry_q - transaction_q)
                        ticker_PNL.dequeue()
                        ticker_PNL.items[j - 1]['q'] -= transaction_q                    
                    elif abs(entry_q) < abs(exit_q):
                        transaction_q = - 1 * entry_q
                        # first_q -= transaction_q
                        current_pipe.dequeue()
                        current_pipe.enqueue(j, exit_q - transaction_q)
                        ticker_PNL.dequeue()
                        ticker_PNL.items[j - 1]['q'] -= transaction_q
                    elif abs(entry_q) == abs(exit_q):
                        transaction_q = entry_q
                        current_pipe.dequeue()
                        ticker_PNL.dequeue()

                    tax_ledger.append([ticker, transaction_q, en_date, en_price, -1 * transaction_q, ex_date, ex_price])
                       
                    # print(tax_ledger)
            
            print(ticker_PNL.items)
            j += 1            
            i += 1
        
            if i >= len(db):
                print(f'Total number of transactions: {i}')
                break

        ledger[ticker] = ticker_PNL.items
                
    return(ledger)

def main():
    ticker_col = 6 + 1
    date_col = 7 + 1
    q_col = 8 + 1
    p_col = 10 + 1

    raw_db = sort_ib_file()
    ledger = unique_tickers(raw_db, ticker_col, date_col, q_col, p_col)

    # for key, value in ledger.items():
    #     print(f'{key} : {value}')

if __name__ == "__main__": main()