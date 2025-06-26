class Grammar:
    def __init__(self):
        self.rules = {
            "E": [["T", "E'"]],
            "E'": [["+", "T", "E'"], ["-", "T", "E'"], []],
            "T": [["F", "T'"]],
            "T'": [["*", "F", "T'"], ["/", "F", "T'"], []],
            "F": [["(", "E", ")"], ["num"]]
        }
        self.start_symbol = "E"

class RecursiveDescentParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.current_token = None
        self.tokens = []
        self.productions_used = []

    def parse(self, expression):
        self.tokens = self.tokenize(expression)
        self.current_token = self.tokens[0]
        self.E()
        return self.productions_used

    def tokenize(self, s):
        tokens = []
        i = 0
        while i < len(s):
            if s[i] in '+-*/()':
                tokens.append(s[i])
                i += 1
            elif s[i].isalpha():
                # 收集连续字母作为num
                start = i
                while i < len(s) and s[i].isalpha():
                    i += 1
                tokens.append('num')
            else:
                i += 1
        tokens.append('EOF')
        return tokens

    def E(self):
        self.productions_used.append("E -> T E'")
        self.T()
        while self.current_token in ('+', '-'):
            op = self.current_token
            self.consume()
            self.T()
            self.productions_used.append(f"E' -> {op} T E'")
        self.productions_used.append("E' -> ε")

    def T(self):
        self.productions_used.append("T -> F T'")
        self.F()
        while self.current_token in ('*', '/'):
            op = self.current_token
            self.consume()
            self.F()
            self.productions_used.append(f"T' -> {op} F T'")
        self.productions_used.append("T' -> ε")

    def F(self):
        if self.current_token == '(':
            self.productions_used.append("F -> ( E )")
            self.consume('(')
            self.E()
            self.consume(')')
        else:
            self.productions_used.append("F -> num")
            self.consume('num')

    def consume(self, expected=None):
        if expected and self.current_token != expected:
            raise SyntaxError(f"Expected {expected} got {self.current_token}")
        self.tokens.pop(0)
        self.current_token = self.tokens[0] if self.tokens else None

class LL1Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.parsing_table = self.build_parsing_table()

    def build_parsing_table(self):
        first = self.compute_first()
        follow = self.compute_follow(first)
        terminals = {'+', '-', '*', '/', '(', ')', 'num', 'EOF'}

        for non_terminal in self.grammar.rules:
            for production in self.grammar.rules[non_terminal]:
                first_set = self.get_production_first(production, first)
                for terminal in first_set - {'ε'}:
                    self.parsing_table[(non_terminal, terminal)] = production
                if 'ε' in first_set:
                    for terminal in follow[non_terminal]:
                        self.parsing_table[(non_terminal, terminal)] = production

    def compute_first(self):
        first = {nt: set() for nt in self.grammar.rules}
        changed = True
        while changed:
            changed = False
            for nt in self.grammar.rules:
                for production in self.grammar.rules[nt]:
                    for symbol in production:
                        if symbol in self.grammar.rules:
                            prev_size = len(first[nt])
                            first[nt] |= first[symbol] - {'ε'}
                            if 'ε' not in first[symbol]:
                                break
                            if len(first[nt]) != prev_size:
                                changed = True
                        else:
                            prev_size = len(first[nt])
                            first[nt].add(symbol)
                            if len(first[nt]) != prev_size:
                                changed = True
                            break
        return first

    def compute_follow(self, first):
        # 补充FOLLOW集计算逻辑
        while changed:
            changed = False
            for nt in self.grammar.rules:
                for production in self.grammar.rules[nt]:
                    trailer = follow[nt].copy()
                    for symbol in reversed(production):
                        if symbol in self.grammar.rules:
                            if symbol not in follow:
                                follow[symbol] = set()
                            prev_size = len(follow[symbol])
                            follow[symbol] |= trailer
                            if prev_size != len(follow[symbol]):
                                changed = True
                            if 'ε' in first[symbol]:
                                trailer |= first[symbol] - {'ε'}
                            else:
                                trailer = first[symbol]
                        else:
                            trailer = {symbol}

    def parse(self, input_str):
        # 实现算法4.1
        stack = ['EOF', self.grammar.start_symbol]
        pointer = 0
        while stack:
            top = stack[-1]
            current = input_str[pointer] if pointer < len(input_str) else 'EOF'
            if top == current:
                stack.pop()
                pointer += 1
            else:
                production = self.parsing_table.get((top, current))
                if production:
                    stack.pop()
                    stack.extend(reversed(production))
                else:
                    raise SyntaxError(f"Syntax error at {current}")

class LRParser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.action_table, self.goto_table = self.build_lr_tables()

    def build_lr_tables(self):
        items = []
        start_production = (self.grammar.start_symbol, self.grammar.rules[self.grammar.start_symbol][0])
        initial_item = (start_production, 0)

        states = [self.closure({initial_item})]
        transitions = {}

        for i, state in enumerate(states):
            for item in state:
                prod, pos = item
                if pos < len(prod[1]):
                    next_symbol = prod[1][pos]
                    new_state = self.goto(state, next_symbol)
                    if new_state and new_state not in states:
                        states.append(new_state)
                        transitions[(i, next_symbol)] = len(states)-1

            for symbol in self.grammar.rules.keys() | {'num','+','-','*','/','(',')','EOF'}:
                if (i, symbol) in transitions:
                    state_idx = transitions[(i, symbol)]
                    if symbol in self.grammar.rules:
                        self.goto_table[(i, symbol)] = state_idx
                    else:
                        self.action_table[(i, symbol)] = ('s', state_idx)

        for i, state in enumerate(states):
            for item in state:
                prod, pos = item
                if pos == len(prod[1]):
                    if prod[0] == self.grammar.start_symbol:
                        self.action_table[(i, 'EOF')] = ('acc',)
                    else:
                        for t in self.follow[prod[0]]:
                            self.action_table[(i, t)] = ('r', self.grammar.rules[prod[0]].index(prod[1]))

        return self.action_table, self.goto_table

    def closure(self, items):
        closure = set(items)
        changed = True
        while changed:
            changed = False
            for item in list(closure):
                prod, pos = item
                if pos < len(prod[1]):
                    B = prod[1][pos]
                    if B in self.grammar.rules:
                        for production in self.grammar.rules[B]:
                            new_item = ((B, production), 0)
                            if new_item not in closure:
                                closure.add(new_item)
                                changed = True
        return frozenset(closure)

    def goto(self, state, symbol):
        new_state = set()
        for item in state:
            prod, pos = item
            if pos < len(prod[1]) and prod[1][pos] == symbol:
                new_state.add((prod, pos+1))
        return self.closure(new_state) if new_state else None

    def parse(self, input_str):
        stack = [0]
        input = list(input_str) + ['EOF']
        while True:
            state = stack[-1]
            current = input[0]
            action = self.action_table.get((state, current))
            if action[0] == 's':
                stack.append(int(action[1:]))
                input.pop(0)
            elif action[0] == 'r':
                prod_num = int(action[1:])
                # 执行规约操作
                stack = stack[:-2*prod_num]
                stack.append(self.goto_table[stack[-1], 'E'])
            elif action == 'acc':
                return True
            else:
                raise SyntaxError(f"Syntax error at {current}")

# 测试用例
if __name__ == "__main__":
    g = Grammar()
    print("测试递归下降分析器:")
    print(RecursiveDescentParser(g).parse("num+num*num"))
    print("\n测试LL(1)分析器:")
    print(LL1Parser(g).parse(["num", "+", "num", "*", "num"]))

    print("\n测试LR分析器:")
    print(LRParser(g).parse("num+num*num"))
    print(LRParser(g).parse("num*num+num"))