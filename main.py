import sys
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class GrammarSymbol:
    """文法符号基类"""
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return self.name == other.name if isinstance(other, GrammarSymbol) else self.name == other
    
    def __hash__(self):
        return hash(self.name)


class Terminal(GrammarSymbol):
    """终结符"""
    pass


class NonTerminal(GrammarSymbol):
    """非终结符"""
    pass


class Production:
    """产生式"""
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __str__(self):
        return f"{self.left} -> {' '.join(str(s) for s in self.right)}"
    
    def __repr__(self):
        return self.__str__()


class Grammar:
    """文法定义"""
    def __init__(self):
        # 定义终结符
        self.NUM = Terminal("num")
        self.PLUS = Terminal("+")
        self.MINUS = Terminal("-")
        self.TIMES = Terminal("*")
        self.DIV = Terminal("/")
        self.LPAREN = Terminal("(")
        self.RPAREN = Terminal(")")
        self.END = Terminal("$")
        self.EPSILON = Terminal("ε")
        
        # 定义非终结符
        self.E = NonTerminal("E")
        self.E_PRIME = NonTerminal("E'")
        self.T = NonTerminal("T")
        self.T_PRIME = NonTerminal("T'")
        self.F = NonTerminal("F")
        
        self.non_terminals = {self.E, self.E_PRIME, self.T, self.T_PRIME, self.F}
        self.terminals = {self.NUM, self.PLUS, self.MINUS, self.TIMES, self.DIV, self.LPAREN, self.RPAREN, self.END, self.EPSILON}
        
        # 原始文法产生式1
        self.original_productions = [
            Production(self.E, [self.E, self.PLUS, self.T]),
            Production(self.E, [self.E, self.MINUS, self.T]),
            Production(self.E, [self.T]),
            Production(self.T, [self.T, self.TIMES, self.F]),
            Production(self.T, [self.T, self.DIV, self.F]),
            Production(self.T, [self.F]),
            Production(self.F, [self.LPAREN, self.E, self.RPAREN]),
            Production(self.F, [self.NUM])
        ]
        
        # 消除左递归后的文法
        self.productions = [
            Production(self.E, [self.T, self.E_PRIME]),
            Production(self.E_PRIME, [self.PLUS, self.T, self.E_PRIME]),
            Production(self.E_PRIME, [self.MINUS, self.T, self.E_PRIME]),
            Production(self.E_PRIME, [self.EPSILON]),
            Production(self.T, [self.F, self.T_PRIME]),
            Production(self.T_PRIME, [self.TIMES, self.F, self.T_PRIME]),
            Production(self.T_PRIME, [self.DIV, self.F, self.T_PRIME]),
            Production(self.T_PRIME, [self.EPSILON]),
            Production(self.F, [self.LPAREN, self.E, self.RPAREN]),
            Production(self.F, [self.NUM])
        ]
        
        self.start_symbol = self.E
        
    def get_production_by_index(self, index):
        """根据索引获取产生式"""
        if 0 <= index < len(self.productions):
            return self.productions[index]
        return None


class Lexer:
    """词法分析器"""
    def __init__(self, grammar):
        self.grammar = grammar
        
    def tokenize(self, expression):
        """将表达式转换为符号流"""
        tokens = []
        i = 0
        while i < len(expression):
            if expression[i].isspace():
                i += 1
            elif expression[i].isdigit():
                num = ''
                while i < len(expression) and expression[i].isdigit():
                    num += expression[i]
                    i += 1
                tokens.append(self.grammar.NUM)
            elif expression[i] == '+':
                tokens.append(self.grammar.PLUS)
                i += 1
            elif expression[i] == '-':
                tokens.append(self.grammar.MINUS)
                i += 1
            elif expression[i] == '*':
                tokens.append(self.grammar.TIMES)
                i += 1
            elif expression[i] == '/':
                tokens.append(self.grammar.DIV)
                i += 1
            elif expression[i] == '(':
                tokens.append(self.grammar.LPAREN)
                i += 1
            elif expression[i] == ')':
                tokens.append(self.grammar.RPAREN)
                i += 1
            else:
                raise ValueError(f"无效字符: {expression[i]}")
        tokens.append(self.grammar.END)
        return tokens


class RecursiveDescentParser:
    """递归下降分析器"""
    def __init__(self, grammar):
        self.grammar = grammar
        
    def parse(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.productions_used = []
        
        try:
            result = self.parse_E()
            if self.pos == len(self.tokens) - 1 and self.tokens[self.pos] == self.grammar.END:
                print("\n递归下降分析成功！")
                print("使用的产生式：")
                for prod in self.productions_used:
                    print(f"  {prod}")
                return True
            else:
                print("\n递归下降分析失败：未能解析完整表达式")
                return False
        except Exception as e:
            print(f"\n递归下降分析失败：{e}")
            return False
    
    def lookahead(self):
        """获取当前符号"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def match(self, expected):
        """匹配当前符号"""
        if self.lookahead() == expected:
            self.pos += 1
            return True
        raise SyntaxError(f"语法错误：期望 {expected}，得到 {self.lookahead()}")
    
    def parse_E(self):
        """E -> T E'"""
        prod = f"E -> T E'"
        self.productions_used.append(prod)
        print(f"应用产生式: {prod}")
        
        self.parse_T()
        self.parse_E_prime()
        return True
    
    def parse_E_prime(self):
        """E' -> + T E' | - T E' | ε"""
        if self.lookahead() == self.grammar.PLUS:
            prod = f"E' -> + T E'"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.PLUS)
            self.parse_T()
            self.parse_E_prime()
        elif self.lookahead() == self.grammar.MINUS:
            prod = f"E' -> - T E'"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.MINUS)
            self.parse_T()
            self.parse_E_prime()
        else:
            prod = f"E' -> ε"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
        return True
    
    def parse_T(self):
        """T -> F T'"""
        prod = f"T -> F T'"
        self.productions_used.append(prod)
        print(f"应用产生式: {prod}")
        
        self.parse_F()
        self.parse_T_prime()
        return True
    
    def parse_T_prime(self):
        """T' -> * F T' | / F T' | ε"""
        if self.lookahead() == self.grammar.TIMES:
            prod = f"T' -> * F T'"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.TIMES)
            self.parse_F()
            self.parse_T_prime()
        elif self.lookahead() == self.grammar.DIV:
            prod = f"T' -> / F T'"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.DIV)
            self.parse_F()
            self.parse_T_prime()
        else:
            prod = f"T' -> ε"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
        return True
    
    def parse_F(self):
        """F -> ( E ) | num"""
        if self.lookahead() == self.grammar.LPAREN:
            prod = f"F -> ( E )"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.LPAREN)
            self.parse_E()
            self.match(self.grammar.RPAREN)
        elif self.lookahead() == self.grammar.NUM:
            prod = f"F -> num"
            self.productions_used.append(prod)
            print(f"应用产生式: {prod}")
            
            self.match(self.grammar.NUM)
        else:
            raise SyntaxError(f"语法错误：期望 ( 或 num，得到 {self.lookahead()}")
        
        return True


class LL1Parser:
    """LL(1)分析器"""
    def __init__(self, grammar):
        self.grammar = grammar
        self.first_sets = {nt: set() for nt in self.grammar.non_terminals}
        self.follow_sets = {nt: set() for nt in self.grammar.non_terminals}
        self.parse_table = {}
        
    def calculate_first_sets(self):
        """计算FIRST集"""
        # 初始化：对于所有终结符a，FIRST(a) = {a}
        for terminal in self.grammar.terminals:
            if terminal != self.grammar.EPSILON:
                self.first_sets[terminal] = {terminal}
        
        # 对于所有产生式A -> ε，将ε加入FIRST(A)
        for prod in self.grammar.productions:
            if len(prod.right) == 1 and prod.right[0] == self.grammar.EPSILON:
                self.first_sets[prod.left].add(self.grammar.EPSILON)
        
        # 迭代计算，直到FIRST集不再变化
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                A = prod.left
                alpha = prod.right
                
                # 处理A -> X1 X2 ... Xn
                k = 0
                continue_next = True
                
                while k < len(alpha) and continue_next:
                    X = alpha[k]
                    
                    # 将FIRST(X) - {ε}加入FIRST(A)
                    if X in self.first_sets:
                        old_size = len(self.first_sets[A])
                        for symbol in self.first_sets[X]:
                            if symbol != self.grammar.EPSILON:
                                self.first_sets[A].add(symbol)
                        
                        if len(self.first_sets[A]) != old_size:
                            changed = True
                        
                        # 如果FIRST(X)不包含ε，则停止计算
                        if self.grammar.EPSILON not in self.first_sets[X]:
                            continue_next = False
                    else:
                        # X是终结符，将X加入FIRST(A)
                        old_size = len(self.first_sets[A])
                        self.first_sets[A].add(X)
                        if len(self.first_sets[A]) != old_size:
                            changed = True
                        continue_next = False
                    
                    k += 1
                
                # 如果所有符号都可推导出ε，则将ε加入FIRST(A)
                if continue_next:
                    old_size = len(self.first_sets[A])
                    self.first_sets[A].add(self.grammar.EPSILON)
                    if len(self.first_sets[A]) != old_size:
                        changed = True
    
    def calculate_follow_sets(self):
        """计算FOLLOW集"""
        # 初始化：将$加入FOLLOW(S)，其中S是开始符号
        self.follow_sets[self.grammar.start_symbol].add(self.grammar.END)
        
        # 迭代计算，直到FOLLOW集不再变化
        changed = True
        while changed:
            changed = False
            
            for prod in self.grammar.productions:
                A = prod.left
                beta = prod.right
                
                for i in range(len(beta)):
                    B = beta[i]
                    
                    # 只处理非终结符
                    if B not in self.grammar.non_terminals:
                        continue
                    
                    # 计算FIRST(β_{i+1}...β_n)
                    first_rest = self.calculate_first_of_string(beta[i+1:])
                    
                    # 将FIRST(β_{i+1}...β_n) - {ε}加入FOLLOW(B)
                    old_size = len(self.follow_sets[B])
                    for symbol in first_rest:
                        if symbol != self.grammar.EPSILON:
                            self.follow_sets[B].add(symbol)
                    
                    if len(self.follow_sets[B]) != old_size:
                        changed = True
                    
                    # 如果FIRST(β_{i+1}...β_n)包含ε或i=n，将FOLLOW(A)加入FOLLOW(B)
                    if self.grammar.EPSILON in first_rest or i == len(beta) - 1:
                        old_size = len(self.follow_sets[B])
                        for symbol in self.follow_sets[A]:
                            self.follow_sets[B].add(symbol)
                        if len(self.follow_sets[B]) != old_size:
                            changed = True
    
    def calculate_first_of_string(self, string):
        """计算符号串的FIRST集"""
        if not string:
            return {self.grammar.EPSILON}
        
        first_set = set()
        all_have_epsilon = True
        
        for symbol in string:
            if symbol not in self.first_sets:
                first_set.add(symbol)
                all_have_epsilon = False
                break
            
            # 将FIRST(symbol) - {ε}加入结果
            for s in self.first_sets[symbol]:
                if s != self.grammar.EPSILON:
                    first_set.add(s)
            
            # 如果FIRST(symbol)不包含ε，则停止计算
            if self.grammar.EPSILON not in self.first_sets[symbol]:
                all_have_epsilon = False
                break
        
        # 如果所有符号都可推导出ε，则将ε加入结果
        if all_have_epsilon:
            first_set.add(self.grammar.EPSILON)
        
        return first_set
    
    def build_parse_table(self):
        """构建LL(1)分析表"""
        # 初始化分析表
        for nt in self.grammar.non_terminals:
            self.parse_table[nt] = {}
            for t in self.grammar.terminals:
                if t != self.grammar.EPSILON:
                    self.parse_table[nt][t] = None
        
        # 根据算法4.2填充分析表
        for i, prod in enumerate(self.grammar.productions):
            A = prod.left
            alpha = prod.right
            
            # 计算FIRST(alpha)
            first_alpha = self.calculate_first_of_string(alpha)
            
            # 对于FIRST(alpha)中的每个终结符a，填充M[A, a]
            for a in first_alpha:
                if a != self.grammar.EPSILON:
                    if self.parse_table[A][a] is None:
                        self.parse_table[A][a] = i
                    else:
                        print(f"警告：文法不是LL(1)，{A}和{a}冲突")
            
            # 如果ε在FIRST(alpha)中，则对于FOLLOW(A)中的每个b，填充M[A, b]
            if self.grammar.EPSILON in first_alpha:
                for b in self.follow_sets[A]:
                    if b != self.grammar.EPSILON:
                        if self.parse_table[A][b] is None:
                            self.parse_table[A][b] = i
                        else:
                            print(f"警告：文法不是LL(1)，{A}和{b}冲突")
    
    def print_first_follow_sets(self):
        """打印FIRST和FOLLOW集合"""
        print("\nFIRST集合:")
        for symbol in sorted(self.first_sets.keys(), key=lambda s: str(s)):
            if symbol in self.grammar.non_terminals:
                print(f"  FIRST({symbol}) = {{{', '.join(str(s) for s in sorted(self.first_sets[symbol], key=lambda s: str(s)))}}}")
        
        print("\nFOLLOW集合:")
        for symbol in sorted(self.follow_sets.keys(), key=lambda s: str(s)):
            if symbol in self.grammar.non_terminals:
                print(f"  FOLLOW({symbol}) = {{{', '.join(str(s) for s in sorted(self.follow_sets[symbol], key=lambda s: str(s)))}}}")
    
    def print_parse_table(self):
        """打印分析表"""
        print("\nLL(1)预测分析表:")
        terminals = [t for t in self.grammar.terminals if t != self.grammar.EPSILON]
        
        # 打印表头
        print(f"{'非终结符':<8}", end="")
        for t in sorted(terminals, key=lambda t: str(t)):
            print(f"{t}:{'':<5}", end="")
        print()
        
        # 打印表内容
        for nt in sorted(self.grammar.non_terminals, key=lambda nt: str(nt)):
            print(f"{nt}:{'':<5}", end="")
            for t in sorted(terminals, key=lambda t: str(t)):
                if t in self.parse_table[nt] and self.parse_table[nt][t] is not None:
                    prod = self.grammar.productions[self.parse_table[nt][t]]
                    print(f"{prod.left}->{' '.join(str(s) for s in prod.right):<5}", end="")
                else:
                    print(f"{'error':<7}", end="")
            print()
    
    def parse(self, tokens):
        """LL(1)语法分析"""
        stack = [self.grammar.END, self.grammar.start_symbol]
        input_buffer = tokens[:]
        ip = 0
        productions_used = []
        
        print("\nLL(1)分析过程:")
        print(f"{'步骤':<4} {'栈':<25} {'输入':<25} {'动作'}")
        print("-" * 70)
        
        step = 1
        while stack:
            X = stack[-1]
            a = input_buffer[ip]
            
            stack_str = ' '.join(str(s) for s in stack)
            input_str = ' '.join(str(s) for s in input_buffer[ip:])
            print(f"{step:<4} {stack_str:<25} {input_str:<25}", end=" ")
            
            if X == self.grammar.END and a == self.grammar.END:
                print("接受")
                print("\nLL(1)分析成功！")
                print("使用的产生式：")
                for i, prod in enumerate(productions_used):
                    print(f"  {i+1}. {prod}")
                return True
            
            if X in self.grammar.terminals:
                if X == a:
                    stack.pop()
                    ip += 1
                    print(f"匹配 {a}")
                else:
                    print(f"错误：期望 {X}，得到 {a}")
                    return False
            else:  # X是非终结符
                if a in self.parse_table[X] and self.parse_table[X][a] is not None:
                    prod_index = self.parse_table[X][a]
                    prod = self.grammar.productions[prod_index]
                    productions_used.append(prod)
                    
                    stack.pop()
                    if prod.right != [self.grammar.EPSILON]:
                        for symbol in reversed(prod.right):
                            stack.append(symbol)
                    
                    print(f"使用 {prod}")
                else:
                    print(f"错误：表中M[{X}, {a}]未定义")
                    return False
            
            step += 1
        
        return False


class LRParser:
    """LR分析器"""
    def __init__(self, grammar):
        self.grammar = grammar
        
        # 扩展文法
        self.augmented_start = NonTerminal("S'")  # 新的开始符号
        self.augmented_production = Production(self.augmented_start, [self.grammar.start_symbol])
        
        # 预设的LR分析表（简化实现）
        self.action_table = {
            0: {'num': ('s', 5), '(': ('s', 4)},
            1: {'+': ('s', 6), '-': ('s', 7), '$': ('accept', None)},
            2: {'*': ('s', 8), '/': ('s', 9), '+': ('r', 2), '-': ('r', 2), ')': ('r', 2), '$': ('r', 2)},
            3: {'+': ('r', 4), '-': ('r', 4), '*': ('r', 4), '/': ('r', 4), ')': ('r', 4), '$': ('r', 4)},
            4: {'num': ('s', 5), '(': ('s', 4)},
            5: {'+': ('r', 6), '-': ('r', 6), '*': ('r', 6), '/': ('r', 6), ')': ('r', 6), '$': ('r', 6)},
            6: {'num': ('s', 5), '(': ('s', 4)},
            7: {'num': ('s', 5), '(': ('s', 4)},
            8: {'num': ('s', 5), '(': ('s', 4)},
            9: {'num': ('s', 5), '(': ('s', 4)},
            10: {'+': ('s', 6), '-': ('s', 7), ')': ('s', 15)},
            11: {'*': ('s', 8), '/': ('s', 9), '+': ('r', 1), '-': ('r', 1), ')': ('r', 1), '$': ('r', 1)},
            12: {'*': ('s', 8), '/': ('s', 9), '+': ('r', 3), '-': ('r', 3), ')': ('r', 3), '$': ('r', 3)},
            13: {'+': ('r', 5), '-': ('r', 5), '*': ('r', 5), '/': ('r', 5), ')': ('r', 5), '$': ('r', 5)},
            14: {'+': ('r', 7), '-': ('r', 7), '*': ('r', 7), '/': ('r', 7), ')': ('r', 7), '$': ('r', 7)}
        }
        
        self.goto_table = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 10, 'T': 2, 'F': 3},
            6: {'T': 11, 'F': 3},
            7: {'T': 12, 'F': 3},
            8: {'F': 13},
            9: {'F': 14}
        }
        
        # 产生式映射
        self.productions = [
            Production(self.augmented_start, [self.grammar.start_symbol]),  # S' -> E
            Production(self.grammar.E, [self.grammar.T, self.grammar.E_PRIME]),  # E -> T E'
            Production(self.grammar.E_PRIME, [self.grammar.PLUS, self.grammar.T, self.grammar.E_PRIME]),  # E' -> + T E'
            Production(self.grammar.E_PRIME, [self.grammar.MINUS, self.grammar.T, self.grammar.E_PRIME]),  # E' -> - T E'
            Production(self.grammar.E_PRIME, [self.grammar.EPSILON]),  # E' -> ε
            Production(self.grammar.T, [self.grammar.F, self.grammar.T_PRIME]),  # T -> F T'
            Production(self.grammar.T_PRIME, [self.grammar.TIMES, self.grammar.F, self.grammar.T_PRIME]),  # T' -> * F T'
            Production(self.grammar.T_PRIME, [self.grammar.DIV, self.grammar.F, self.grammar.T_PRIME]),  # T' -> / F T'
            Production(self.grammar.T_PRIME, [self.grammar.EPSILON]),  # T' -> ε
            Production(self.grammar.F, [self.grammar.LPAREN, self.grammar.E, self.grammar.RPAREN]),  # F -> ( E )
            Production(self.grammar.F, [self.grammar.NUM])  # F -> num
        ]
    
    def parse(self, tokens):
        """LR语法分析"""
        state_stack = [0]  # 状态栈
        symbol_stack = []  # 符号栈
        inputs = tokens[:]  # 输入缓冲区
        
        print("\nLR分析过程:")
        print(f"{'步骤':<4} {'状态栈':<25} {'符号栈':<25} {'输入':<25} {'动作'}")
        print("-" * 80)
        
        step = 1
        productions_used = []
        
        while True:
            state = state_stack[-1]
            symbol = inputs[0]
            
            state_str = ' '.join(str(s) for s in state_stack)
            symbol_str = ' '.join(str(s) for s in symbol_stack)
            input_str = ' '.join(str(s) for s in inputs)
            
            print(f"{step:<4} {state_str:<25} {symbol_str:<25} {input_str:<25}", end=" ")
            
            if symbol.name in self.action_table[state]:
                action, value = self.action_table[state][symbol.name]
                
                if action == 's':  # 移进
                    state_stack.append(value)
                    symbol_stack.append(symbol)
                    inputs.pop(0)
                    print(f"移进，进入状态 {value}")
                
                elif action == 'r':  # 归约
                    production = self.productions[value]
                    
                    # 如果产生式右部不是ε，弹出相应数量的符号和状态
                    if production.right != [self.grammar.EPSILON]:
                        for _ in range(len(production.right)):
                            if symbol_stack:  # 确保栈不为空
                                symbol_stack.pop()
                            if len(state_stack) > 1:  # 保留至少一个状态
                                state_stack.pop()
                    
                    # 压入归约后的非终结符
                    symbol_stack.append(production.left)
                    
                    # 查找GOTO表
                    new_state = self.goto_table[state_stack[-1]][production.left.name]
                    state_stack.append(new_state)
                    
                    productions_used.append(production)
                    print(f"按 {production} 归约，进入状态 {new_state}")
                
                elif action == 'accept':  # 接受
                    print("接受")
                    print("\nLR分析成功！")
                    print("使用的产生式：")
                    for i, prod in enumerate(productions_used):
                        print(f"  {i+1}. {prod}")
                    return True
            else:
                print(f"错误：ACTION[{state}, {symbol}]未定义")
                return False
            
            step += 1


def main():
    # 设置较大的递归深度限制
    sys.setrecursionlimit(10000)
    
    # 创建文法
    grammar = Grammar()
    
    # 创建词法分析器
    lexer = Lexer(grammar)
    
    # 创建三种分析器
    recursive_descent_parser = RecursiveDescentParser(grammar)
    ll1_parser = LL1Parser(grammar)
    lr_parser = LRParser(grammar)
    
    # 预先计算FIRST和FOLLOW集合
    ll1_parser.calculate_first_sets()
    ll1_parser.calculate_follow_sets()
    
    # 构建LL(1)分析表
    ll1_parser.build_parse_table()
    
    # 测试表达式
    test_expressions = [
        "3+4*5",
        "(2+3)*4",
        "1+2+3",
        "8/2/2"
    ]
    
    for expr in test_expressions:
        print("=" * 80)
        print(f"分析表达式: {expr}")
        print("=" * 80)
        
        try:
            tokens = lexer.tokenize(expr)
            token_names = [token.name for token in tokens]
            print(f"词法分析结果: {token_names}")
            
            # 打印FIRST和FOLLOW集合
            ll1_parser.print_first_follow_sets()
            ll1_parser.print_parse_table()
            
            # 方法1：递归下降分析
            print("\n" + "=" * 30)
            print("方法1：递归下降分析")
            print("=" * 30)
            recursive_descent_parser.parse(tokens[:])
            
            # 方法2：LL(1)分析
            print("\n" + "=" * 30)
            print("方法2：LL(1)分析")
            print("=" * 30)
            ll1_parser.parse(tokens[:])
            
            # 方法3：LR分析
            print("\n" + "=" * 30)
            print("方法3：LR分析")
            print("=" * 30)
            lr_parser.parse(tokens[:])
            
        except Exception as e:
            import traceback
            print(f"分析过程中出现错误: {e}")
            traceback.print_exc()
        
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
