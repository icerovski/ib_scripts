import csv

class TaxStatement:
    type_col = 3 + 1
    ticker_col = 5 + 1
    date_col = 6 + 1
    q_col = 7 + 1
    p_col = 8 + 1

    @classmethod
    def sort_ib_file(cls):
        data = []
        counter = 0
        with open("ib_statement.csv", "r") as source_file:
            reader = csv.reader(source_file, delimiter=",")
            for row in reader:
                if row[0] == "Trades" and row[1] == "Data":
                    counter += 1  # used to count the transactions
                    row = [
                        counter,
                        *row,
                    ]  # using unpack insert an item in the begining of the list
                    data.append(row)  # append the newly created row to the data

        return data

    @classmethod
    def equal_signs(cls, num_1, num_2):
        return ((num_1 == num_2) & (num_1 == 0)) | (num_1 * num_2 > 0)

    @classmethod
    def get_unique_tickers(cls):
        sort_ib_data = cls.sort_ib_file()
        i = 0
        ledger = []

        # Improved this part!!!!!
        script_ended = False
        while i < len(sort_ib_data):
            # Iterate through a NEW TICKER
            instrument_type = sort_ib_data[i][cls.type_col]
            ticker = sort_ib_data[i][cls.ticker_col]
            tax_ledger = []

            ticker_ledger = Ticker(ticker=ticker)
            single_trade = Trade(instrument_type=instrument_type)

            # Build up the ledger for the ticker
            while sort_ib_data[i][cls.ticker_col] == ticker:
                single_trade.populate(
                    sort_ib_data[i][cls.q_col],
                    sort_ib_data[i][cls.p_col],
                    sort_ib_data[i][cls.date_col],
                )
                ticker_ledger.filltrades(single_trade.getitems())

                i += 1
                if i >= len(sort_ib_data):
                    print(f"Total number of transactions: {i}")
                    script_ended = True
                    break

            if script_ended:
                break

            # Pair entry and exits
            ticker_pnl = ticker_ledger.getitems()
            print(ticker)
            while not ticker_pnl.is_empty():
                first_q = ticker_pnl.peek()["q"]
                obj_last_index = ticker_pnl.size() - 1

                current_item = {}
                all_same_sign = True
                for j in range(obj_last_index, -1, -1):
                    if not cls.equal_signs(ticker_pnl.items[j]["q"], first_q):
                        current_item = ticker_pnl.items[j]
                        current_q = current_item["q"]
                        second_q = ticker_pnl.peek_2()["q"]
                        all_same_sign = False
                        break

                if all_same_sign:
                    for j in range(obj_last_index, -1, -1):
                        trade_q = ticker_pnl.items[j]["q"]
                        first_date = ticker_pnl.items[j]["d"]
                        first_price = ticker_pnl.items[j]["p"]

                        # Case 1: If you sold short an option and it expired without getting
                        #           excercised, you keep the profit.
                        # Case 2: If you bought an option and it expires worthless, you book
                        #           the cost.
                        # Case 3: If you sold short a stock, it does not expire until you buy
                        #           it back. So, it is unrealized profit/ expense and goes to
                        #           the balance.
                        if single_trade.is_stock():
                            trade_profit = -1 * trade_q * first_price
                        else:
                            trade_profit = None

                        float_line = [
                            ticker,
                            first_date,
                            trade_q,
                            first_price,
                            trade_profit,
                            None,
                            None,
                            None,
                            None,
                            trade_profit,
                        ]

                        tax_ledger.append(float_line)
                        ledger.append(float_line)
                        print(float_line)

                    break

                if cls.equal_signs(first_q, second_q):
                    if abs(first_q) > abs(current_q):
                        trade_q = -1 * current_q
                        ticker_pnl.peek()[
                            "q"
                        ] -= trade_q  # decrease the first_q with the second_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = current_item["d"]
                        second_price = current_item["p"]

                        ticker_pnl.remove_item(current_item)

                    elif abs(first_q) < abs(current_q):
                        trade_q = first_q
                        current_item["q"] += trade_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = current_item["d"]
                        second_price = current_item["p"]

                        ticker_pnl.dequeue()  # Delete the first object
                    elif abs(first_q) == abs(current_q):
                        trade_q = -1 * first_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = ticker_pnl.peek_2()["d"]
                        second_price = ticker_pnl.peek_2()["p"]

                        ticker_pnl.dequeue()
                        ticker_pnl.dequeue()

                elif not cls.equal_signs(first_q, second_q):
                    # THIS HERE DOESN'T CALCULATE PROPERLY. CHECK OUT 'T'
                    if abs(first_q) > abs(second_q):
                        trade_q = -1 * second_q
                        ticker_pnl.peek()[
                            "q"
                        ] -= trade_q  # decrease the first_q with the second_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = ticker_pnl.peek_2()["d"]
                        second_price = ticker_pnl.peek_2()["p"]

                        ticker_pnl.replace_last_items()
                        # Replace the second object with the first object [DOES NOT WORK!!]
                        ticker_pnl.dequeue()
                        # Delete the first object

                    elif abs(first_q) < abs(second_q):
                        trade_q = -1 * first_q
                        ticker_pnl.peek_2()[
                            "q"
                        ] -= trade_q  # decrease the second_q with the first_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = ticker_pnl.peek_2()["d"]
                        second_price = ticker_pnl.peek_2()["p"]

                        ticker_pnl.dequeue()  # Delete the first object

                    elif abs(first_q) == abs(second_q):
                        trade_q = first_q

                        first_date = ticker_pnl.peek()["d"]
                        first_price = ticker_pnl.peek()["p"]
                        second_date = ticker_pnl.peek_2()["d"]
                        second_price = ticker_pnl.peek_2()["p"]

                        ticker_pnl.dequeue()
                        ticker_pnl.dequeue()

                trade_expense = trade_q * first_price
                trade_income = -1 * trade_q * second_price
                trade_profit = trade_income + trade_expense
                float_line = [
                    ticker,
                    first_date,
                    trade_q,
                    first_price,
                    trade_expense,
                    second_date,
                    -1 * trade_q,
                    second_price,
                    trade_income,
                    trade_profit,
                ]

                tax_ledger.append(float_line)
                ledger.append(float_line)
                print(float_line)

        return ledger

    @classmethod
    def write_tax_statement_csv(cls, data_set):
        with open("tax_statement.csv", "w") as destination_file:
            fieldnames = [
                "Ticker",
                "Date entry",
                "Quantity",
                "Price entry",
                "Expense",
                "Date exit",
                "Quantity",
                "Price exit",
                "Income",
                "Profit",
            ]
            writer = csv.writer(destination_file)

            writer.writerow(fieldnames)

            for single_list in data_set:
                line = []
                for item in single_list:
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
        """Remove the item from the array"""

        self.items.remove(item)

    def replace_last_items(self):
        """Replaces the last two values in the list"""

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
        """Returns the one before the last item in the list, which represents
        the one behind the front-most item in the Queue.

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
        # return self.items == []
        return not self.items


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


class Trade:
    INSTRUMENT_TYPES = ("Stocks", "Equity and Index Options")

    @classmethod
    def comma_break(cls, line):
        digit = ""
        for char in line:
            if char != ",":
                digit += char
            else:
                break

        return digit

    @classmethod
    def comma_cleanup(cls, line):
        digit = ""
        for char in line:
            if char != ",":
                digit += char
            else:
                continue

        return digit

    def __init__(self, instrument_type):
        if not instrument_type in self.INSTRUMENT_TYPES:
            raise ValueError(f"{instrument_type} is not a valid instrument type.")
        else:
            self._instrumet_type = instrument_type
        self._items = {}

    def quantity(self, qty=None):
        if qty:
            quantity = int(self.comma_cleanup(qty))
            if self.is_stock():
                self._items["q"] = quantity
            else:
                self._items["q"] = quantity * 100
        return self._items["q"]

    def price(self, num=None):
        if num:
            price = float(self.comma_cleanup(num))
            self._items["p"] = price
        return self._items["p"]

    def date(self, date=None):
        if date:
            self._items["d"] = self.comma_break(date)
        return self._items["d"]

    def populate(self, quantity, price, date):
        self._items = {}
        self.quantity(quantity)
        self.price(price)
        self.date(date)

    def getitems(self):
        return self._items

    def is_stock(self):
        return self._instrumet_type == self.INSTRUMENT_TYPES[0]


def main():
    tax_statement = TaxStatement
    unique_tickers_data = tax_statement.get_unique_tickers()
    tax_statement.write_tax_statement_csv(unique_tickers_data)


if __name__ == "__main__":
    main()
