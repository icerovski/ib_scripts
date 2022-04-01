import csv

class TaxStatement:
    type_col = 3 + 1
    ticker_col = 6 + 1
    date_col = 7 + 1
    q_col = 8 + 1
    p_col = 9 + 1

    @classmethod
    def sort_ib_file(self):
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

    @classmethod
    def equal_signs(self, a, b):
        return ((a == b) & (a == 0)) | (a * b > 0)

    @classmethod
    def get_unique_tickers(self):
        sort_ib_data = self.sort_ib_file()
        i = 0
        ledger = []
        
        # Improved this part!!!!!
        script_ended = False
        while i < len(sort_ib_data):
            # Iterate through a NEW TICKER
            type = sort_ib_data[i][self.type_col]
            ticker = sort_ib_data[i][self.ticker_col]
            tax_ledger = []

            ticker_ledger = Ticker(ticker=ticker)
            single_trade = Trade(type=type)

            # Build up the ledger for the ticker
            while sort_ib_data[i][self.ticker_col] == ticker:
                single_trade.populate(sort_ib_data[i][self.q_col], sort_ib_data[i][self.p_col], sort_ib_data[i][self.date_col])
                ticker_ledger.filltrades(single_trade.getitems())
                
                i += 1
                if i >= len(sort_ib_data):
                    print(f'Total number of transactions: {i}')
                    script_ended = True
                    break
            
            if script_ended:
                break
            
            # Pair entry and exits
            ticker_PNL = ticker_ledger.getitems()
            print(ticker)
            while not ticker_PNL.is_empty():
                first_q = ticker_PNL.peek()['q']
                obj_last_index = ticker_PNL.size() - 1
        
                current_item = {}
                all_same_sign = True
                for j in range(obj_last_index, -1, -1):
                    if not self.equal_signs(ticker_PNL.items[j]['q'], first_q):
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
                        if single_trade.is_instrument_type():
                            trade_profit = -1 * trade_q * first_price
                        else:
                            trade_profit = None

                        float_line = [ticker, first_date, trade_q, first_price, trade_profit, None, None, None, None, trade_profit]

                        tax_ledger.append(float_line)
                        ledger.append(float_line)
                        print(float_line)

                    break
                
                if self.equal_signs(first_q, second_q):
                    if abs(first_q) > abs(current_q):
                        trade_q = -1 * current_q
                        ticker_PNL.peek()['q'] -= trade_q # decrease the first_q with the second_q

                        first_date = ticker_PNL.peek()['d']
                        first_price = ticker_PNL.peek()['p']
                        second_date = current_item['d']
                        second_price = current_item['p']

                        ticker_PNL.remove_item(current_item)                

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
                
                elif not self.equal_signs(first_q, second_q):
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

    @classmethod
    def write_tax_statement_csv(self, data_set):
        with open('tax_statement.csv', 'w') as f:
            fieldnames = ['Ticker', 'Date entry', 'Quantity', 'Price entry', 'Expense', 'Date exit', 'Quantity', 'Price exit', 'Income', 'Profit']
            writer = csv.writer(f)

            writer.writerow(fieldnames)

            for list in data_set:
                line = []
                for item in list:
                    line.append(str(item))
                
                writer.writerow(line)

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


class Ticker:
    
    def __init__(self, ticker):

        # Instance variables
        self._ticker = ticker
        self._tradelist = Queue()
    
    def filltrades(self, singletrade):
        self._tradelist.enqueue(singletrade)

    def getticker(self):
        return self._ticker

    def getitems(self):
        return self._tradelist

    def __str__(self) -> str:
        return self._tradelist

class Trade:
    INSTRUMENT_TYPES = ('Stocks', 'Equity and Index Options')

    @classmethod
    def comma_break(self, line):
        D = ''
        for char in line:
            if char != ',': D += char
            else: break

        return(D)

    @classmethod
    def comma_cleanup(self, line):
        D = ''
        for char in line:
            if char != ',': D += char
            else: continue
        
        return(D)

    def __init__(self, type):
        if (not type in self.INSTRUMENT_TYPES):
            raise ValueError(f'{type} is not a valid instrument type.')
        else:
            self._instrumet_type = type
        self._items = {}

    def quantity(self, q=None):
        if q:
            if self.is_instrument_type():
                self._items['q'] = int(self.comma_cleanup(q))
            else:
                self._items['q'] = int(self.comma_cleanup(q)) * 100
        return self._items['q']

    def price(self, p=None):
        if p:
            self._items['p'] = float(self.comma_cleanup(p))
        return self._items['p']
    
    def date(self, d=None):
        if d:
            self._items['d'] = self.comma_break(d)
        return self._items['d']
    
    def populate(self, q, p, d):
        self._items = {}
        self.quantity(q)
        self.price(p)
        self.date(d)

    def getitems(self):
        return self._items


    def is_instrument_type(self):
        return self._instrumet_type == self.INSTRUMENT_TYPES[0]


def main():
    tax_statement = TaxStatement
    unique_tickers_data = tax_statement.get_unique_tickers()
    tax_statement.write_tax_statement_csv(unique_tickers_data)

if __name__ == "__main__": main()
