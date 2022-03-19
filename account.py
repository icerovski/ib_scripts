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

    def remove_item(self, item):
        '''Remove the item from the array'''
        
        self.items.remove(item)

    def replace_last_items(self):
        '''Replaces the last two values in the list'''

        # return list(map(lambda x: x.replace(self.peek(), self.peek_2()), self.items))
        i = self.items.index(self.peek_2())
        self.items.insert(i, self.peek())
        self.dequeue()

    def peek(self):
        """Returns the last item in the list, which represents the front-most
        item in the Queue.

        The runtime is constant because we're just indexing to the last item of
        the list and returning the value found there.
        """

        if self.items:
            return self.items[-1]
        return None
    
    def peek_2(self):
        """Returns the one before the last item in the list, which represents the one behind the front-most
        item in the Queue.

        The runtime is constant because we're just indexing to the last item of
        the list and returning the value found there.
        """

        if self.items:
            return self.items[-2]
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

    def instrumet_type(self, it=None):
        if it:
            self._items['type'] = it
        return self._items['type']

    def quantity(self, q=None):
        if q:
            if self.instrumet_type() == 'Stocks':
                self._items['q'] = int(comma_cleanup(q))
            else:
                self._items['q'] = int(comma_cleanup(q)) * 100
        return self._items['q']

    def price(self, p=None):
        if p:
            self._items['p'] = float(comma_cleanup(p))
        return self._items['p']
    
    def date(self, d=None):
        if d:
            self._items['d'] = comma_break(d)
        return self._items['d']
    
    def populate(self, t, it, q, p, d):
        self.ticker(t)
        self.instrumet_type(it)
        self.quantity(q)
        self.price(p)
        self.date(d)
    
    def items(self):
        return self._items

    def __str__(self) -> str:
        return self._items


class tradeSummary (tradeTicket):
    '''Produced by one or maximum two trades. Consists of the following items:
    Stock, Quantity, Date Entry, Price Entry, Date Exit, Price Exit, Cost, Income, Profit'''

    def __init__(self) -> None:
        super().__init__()

    def case_1(self, front=None, rear=None):
        if front and rear:
            if equal_signs(front, rear) and self.size < 2:
                return front + rear
    
    def case_2(self, front=None, rear=None):
        if front and rear:
            if equal_signs(front, rear) and self.size > 2:
                pass
    
    def case_3(self, front=None, rear=None):
        if front and rear:
            if not equal_signs(front, rear):
                pass


class tickerSummary (tradeSummary):
    '''Consists of all tradeSummary Objects for a ticker.'''

    def __init__(self) -> None:
        super().__init__()
        
     
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
    

def data_to_string(data_set):
    data_string = ''
    for item in data_set:
        for i in range(len(item)):
            data_string += str(i)
        

    pass

def write(data_set):
    with open('tax_statement.csv', 'w') as f:
        fieldnames = ['Ticker', 'Date entry', 'Quantity', 'Price entry', 'Expense', 'Date exit', 'Quantity', 'Price exit', 'Income', 'Profit']
        writer = csv.writer(f)

        writer.writerow(fieldnames)

        for list in data_set:
            line = []
            for item in list:
                line.append(str(item))
            
            writer.writerow(line)
    
def unique_tickers(db, type_col, ticker_col, date_col, q_col, p_col):
    i = 0
    ledger = []
    
    script_ended = False
    while i < len(db):
        # Iterate through a NEW TICKER
        instrument_type = db[i][type_col]
        ticker = db[i][ticker_col]
        ticker_PNL = Queue()
        tax_ledger = []

        while db[i][ticker_col] == ticker:
            current_trade = tradeTicket()
            current_trade.populate(ticker, instrument_type, db[i][q_col], db[i][p_col], db[i][date_col])
            ticker_PNL.enqueue(current_trade.items())
            
            i += 1
            if i >= len(db):
                print(f'Total number of transactions: {i}')
                script_ended = True
                break
        
        if script_ended:
            break
        
        print(ticker)
        while not ticker_PNL.is_empty():
            first_q = ticker_PNL.peek()['q']
            obj_last_index = ticker_PNL.size() - 1
    
            current_item = {}
            all_same_sign = True
            for j in range(obj_last_index, -1, -1):
                if not equal_signs(ticker_PNL.items[j]['q'], first_q):
                    current_item = ticker_PNL.items[j]
                    current_q = current_item['q']
                    second_q = ticker_PNL.peek_2()['q']
                    all_same_sign = False
                    break

            if all_same_sign:
                for j in range(obj_last_index, -1, -1):
                    trade_q = ticker_PNL.items[j]['q']
                    first_date = ticker_PNL.items[j]['d']
                    first_price = ticker_PNL.items[j]['p']

                    # Case 1: If you sold short an option and it expired without being excercised, you keep the profit.
                    # Case 2: If you bought an option and it expires worthless, you book the cost.
                    # Case 3: If you sold short a stock, it does not expire until you buy it back. So, it is unrealized profit/ expense and goes to the balance.
                    if ticker_PNL.items[j]['type'] != 'Stocks':
                        trade_profit = -1 * trade_q * first_price
                    else:
                        trade_profit = None

                    float_line = [ticker, first_date, trade_q, first_price, trade_profit, None, None, None, None, trade_profit]

                    tax_ledger.append(float_line)
                    ledger.append(float_line)
                    print(float_line)

                break
            
            if equal_signs(first_q, second_q):
                if abs(first_q) > abs(current_q):
                    trade_q = -1 * current_q
                    ticker_PNL.peek()['q'] -= trade_q # decrease the first_q with the second_q
                    # ticker_PNL.peek_2 = ticker_PNL.peek # Replace the second object with the first object

                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = current_item['d']
                    second_price = current_item['p']

                    ticker_PNL.remove_item(current_item)
                    # ticker_PNL.replace_last_items() # Replace the second object with the first object [DOES NOT WORK!!]
                    # ticker_PNL.dequeue() # Delete the first object                    

                elif abs(first_q) < abs(current_q):
                    trade_q = first_q
                    current_item['q'] += trade_q
                    
                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = current_item['d']
                    second_price = current_item['p']

                    ticker_PNL.dequeue() # Delete the first object
                elif abs(first_q) == abs(current_q):
                    trade_q = -1 * first_q

                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = ticker_PNL.peek_2()['d']
                    second_price = ticker_PNL.peek_2()['p']

                    ticker_PNL.dequeue()
                    ticker_PNL.dequeue()
            
            elif not equal_signs(first_q, second_q):
                # THIS HERE DOESN'T CALCULATE PROPERLY. CHECK OUT 'T'
                if abs(first_q) > abs(second_q):
                    trade_q = -1 * second_q
                    ticker_PNL.peek()['q'] -= trade_q # decrease the first_q with the second_q

                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = ticker_PNL.peek_2()['d']
                    second_price = ticker_PNL.peek_2()['p']

                    ticker_PNL.replace_last_items() # Replace the second object with the first object [DOES NOT WORK!!]
                    ticker_PNL.dequeue() # Delete the first object

                elif abs(first_q) < abs(second_q):
                    trade_q = -1 * first_q
                    ticker_PNL.peek_2()['q'] -= trade_q # decrease the second_q with the first_q

                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = ticker_PNL.peek_2()['d']
                    second_price = ticker_PNL.peek_2()['p']

                    ticker_PNL.dequeue() # Delete the first object

                elif abs(first_q) == abs(second_q):
                    trade_q = first_q

                    first_date = ticker_PNL.peek()['d']
                    first_price = ticker_PNL.peek()['p']
                    second_date = ticker_PNL.peek_2()['d']
                    second_price = ticker_PNL.peek_2()['p']

                    ticker_PNL.dequeue()
                    ticker_PNL.dequeue()
            
             
            trade_expense = trade_q * first_price
            trade_income = -1 * trade_q * second_price
            trade_profit = trade_income + trade_expense
            float_line = [ticker, first_date, trade_q, first_price, trade_expense, second_date, -1 * trade_q, second_price, trade_income, trade_profit]

            tax_ledger.append(float_line)
            ledger.append(float_line)
            print(float_line)

    return(ledger)

def main():
    type_col = 3 + 1
    ticker_col = 6 + 1
    date_col = 7 + 1
    q_col = 8 + 1
    p_col = 9 + 1

    raw_db = sort_ib_file()
    ledger = unique_tickers(raw_db, type_col, ticker_col, date_col, q_col, p_col)
    print(*ledger, sep = '\n')
    write(ledger)

    # for key, value in ledger.items():
    #     print(f'{key} : {value}')

if __name__ == "__main__": main()