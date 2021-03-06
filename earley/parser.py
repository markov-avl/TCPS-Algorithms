from .row import Row
from .table import Table


class Parser:
    def __init__(self, grammar):
        grammar.productions['GAMMA'] = [[grammar.start]]
        self.grammar = grammar
        self.tables = []
        self.words = []

    def add_table(self, k):
        self.tables.append(Table(k))

    def run(self, words):
        self.words = [[word] for word in words]
        self.init()

        for i in range(len(self.words) + 1):
            for row in self.tables[i].get_rows():
                if not row.is_complete():
                    if self.grammar.is_nonterminal(row.get_next()):
                        self.predict(row)
                    else:
                        self.scan(row)
                else:
                    self.complete(row)

    def init(self):
        # creates a GAMMA starting production and n+1 tables
        self.tables = []
        for i in range(len(self.words) + 1):
            self.add_table(i)
        self.tables[0].add_row(Row(0, '', ['GAMMA'], (0, 0)))

    def scan(self, row):
        # creates a new row and copies the production that triggered this op
        # from the table[k-1] to the current table, advacing the pointer
        next_symbol = row.get_next()
        if row.end < len(self.words):
            atual = self.words[row.end][0]
            if next_symbol == atual:
                nrow = Row(1, next_symbol, [atual], (row.end, (row.end+1)))
                self.tables[row.end+1].add_row(nrow)

    def predict(self, row):
        # copies the productions from the nonterminal that triggered this op
        # with the new pointer in the begining of the right side
        next_row = row.get_next()
        if next_row in self.grammar.productions:
            for rule in self.grammar.productions[next_row]:
                self.tables[row.end].add_row(Row(0, next_row, rule, (row.end, row.end)))

    def complete(self, row):
        # advances all rows that were waiting for the current word
        for old_row in self.tables[row.start].get_rows():
            if not old_row.is_complete() and old_row.right[old_row.dot] == row.left:
                nrow = Row((old_row.dot+1), old_row.left, old_row.right,
                           (old_row.start, row.end), old_row.completes[:])
                self.tables[row.end].add_row(nrow, row)

    def show_tables(self):
        for table in self.tables:
            for row in table.rows:
                row.show()

    def make_node(self, row, relatives=None):
        if relatives is None:
            relatives = []
        nodo = {'a': row.left, 'children': [self.make_node(row, []) for row in row.completes]}
        if not row.completes:
            relatives += [row]
        if row.left == 'GAMMA':
            nodo['children'] += [{'a': self.words[row.start]} for row in relatives if row.start < len(self.words)]
        return nodo

    def get_completes(self):
        # returns all rows that are in the GAMMA nonterminal
        completes = []
        for row in self.tables[-1].get_rows():
            if row.left == 'GAMMA':
                completes.append(row)
        del self.grammar.productions['GAMMA']
        return completes
