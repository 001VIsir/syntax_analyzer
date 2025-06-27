class LL1Parser:
    def __init__(self):
        # 初始化文法
        self.grammar = {
            'E': [['E', '+', 'T'], ['E', '-', 'T'], ['T']],
            'T': [['T', '*', 'F'], ['T', '/', 'F'], ['F']],
            'F': [['(', 'E', ')'], ['num']]
        }
        
        # 消除左递归
        self.eliminate_left_recursion()
        
        # 初始化FIRST集和FOLLOW集
        self.first = {}
        self.follow = {}
        self.terminals = set(['+', '-', '*', '/', '(', ')', 'num', '$'])
        self.non_terminals = set(self.grammar.keys())
        
        # 构造预测分析表
        self.parse_table = {}
        
    def eliminate_left_recursion(self):
        # 消除直接左递归
        new_grammar = {}
        
        for nt, productions in self.grammar.items():
            alpha_prods = []  # 形如 Aα
            beta_prods = []   # 形如 β (不以A开头)
            
            for prod in productions:
                if prod[0] == nt:
                    alpha_prods.append(prod[1:])  # 去掉A
                else:
                    beta_prods.append(prod)
            
            if not alpha_prods:  # 没有左递归
                new_grammar[nt] = productions
            else:
                # 引入新的非终结符 A'
                new_nt = nt + "'"
                
                # 对于每个β, 添加 A -> βA'
                new_prods = []
                for beta in beta_prods:
                    new_prod = beta.copy()
                    new_prod.append(new_nt)
                    new_prods.append(new_prod)
                
                new_grammar[nt] = new_prods
                
                # 对于每个α, 添加 A' -> αA'
                new_prods = []
                for alpha in alpha_prods:
                    new_prod = alpha.copy()
                    new_prod.append(new_nt)
                    new_prods.append(new_prod)
                
                # 添加 A' -> ε
                new_prods.append(['ε'])
                new_grammar[new_nt] = new_prods
        
        self.grammar = new_grammar
        print("消除左递归后的文法:")
        for nt, prods in self.grammar.items():
            for prod in prods:
                print(f"{nt} -> {' '.join(prod)}")
    
    def compute_first(self):
        # 初始化FIRST集
        for symbol in self.terminals:
            self.first[symbol] = set([symbol])
        
        for nt in self.non_terminals:
            self.first[nt] = set()
        
        # 特殊处理空字符
        self.first['ε'] = set(['ε'])
        
        # 计算FIRST集
        while True:
            updated = False
            
            for nt, productions in self.grammar.items():
                for prod in productions:
                    # 当产生式为 A -> ε
                    if prod[0] == 'ε':
                        if 'ε' not in self.first[nt]:
                            self.first[nt].add('ε')
                            updated = True
                        continue
                    
                    # 依次计算产生式右部各符号的FIRST
                    k = 0
                    can_derive_epsilon = True
                    
                    while k < len(prod) and can_derive_epsilon:
                        symbol = prod[k]
                        can_derive_epsilon = False
                        
                        # 如果是终结符，直接加入
                        if symbol in self.terminals:
                            if symbol not in self.first[nt]:
                                self.first[nt].add(symbol)
                                updated = True
                            break
                        
                        # 如果是非终结符，将其FIRST中除ε外的所有元素加入
                        for term in self.first[symbol] - set(['ε']):
                            if term not in self.first[nt]:
                                self.first[nt].add(term)
                                updated = True
                        
                        # 检查是否可以推导出ε
                        if 'ε' in self.first[symbol]:
                            can_derive_epsilon = True
                        
                        k += 1
                    
                    # 如果所有符号都可以推导出ε，则将ε加入FIRST(A)
                    if can_derive_epsilon and k == len(prod):
                        if 'ε' not in self.first[nt]:
                            self.first[nt].add('ε')
                            updated = True
            
            if not updated:
                break
        
        print("\nFIRST集:")
        for symbol, first_set in self.first.items():
            if symbol in self.non_terminals:
                print(f"FIRST({symbol}) = {first_set}")
    
    def compute_follow(self):
        # 初始化FOLLOW集
        for nt in self.non_terminals:
            self.follow[nt] = set()
        
        # 将$加入起始符号的FOLLOW集
        start_symbol = list(self.grammar.keys())[0]  # 假设第一个非终结符是起始符号
        self.follow[start_symbol].add('$')
        
        # 计算FOLLOW集
        while True:
            updated = False
            
            for nt, productions in self.grammar.items():
                for prod in productions:
                    for i, symbol in enumerate(prod):
                        # 只关心非终结符
                        if symbol not in self.non_terminals:
                            continue
                        
                        # 如果是产生式最后一个符号，则将FOLLOW(A)加入FOLLOW(B)
                        if i == len(prod) - 1:
                            for term in self.follow[nt]:
                                if term not in self.follow[symbol]:
                                    self.follow[symbol].add(term)
                                    updated = True
                            continue
                        
                        # 计算FIRST(βi+1...βn)
                        first_of_remain = set()
                        can_derive_epsilon = True
                        
                        for j in range(i + 1, len(prod)):
                            next_symbol = prod[j]
                            
                            # 如果是终结符，直接加入并退出
                            if next_symbol in self.terminals:
                                first_of_remain.add(next_symbol)
                                can_derive_epsilon = False
                                break
                            
                            # 如果是非终结符，加入其FIRST集中除ε外的所有元素
                            for term in self.first[next_symbol] - set(['ε']):
                                first_of_remain.add(term)
                            
                            # 如果不能导出ε，则停止
                            if 'ε' not in self.first[next_symbol]:
                                can_derive_epsilon = False
                                break
                        
                        # 将FIRST(βi+1...βn)添加到FOLLOW(B)
                        for term in first_of_remain:
                            if term not in self.follow[symbol]:
                                self.follow[symbol].add(term)
                                updated = True
                        
                        # 如果FIRST(βi+1...βn)包含ε，则将FOLLOW(A)加入FOLLOW(B)
                        if can_derive_epsilon:
                            for term in self.follow[nt]:
                                if term not in self.follow[symbol]:
                                    self.follow[symbol].add(term)
                                    updated = True
            
            if not updated:
                break
        
        print("\nFOLLOW集:")
        for nt, follow_set in self.follow.items():
            print(f"FOLLOW({nt}) = {follow_set}")
    
    def construct_table(self):
        # 计算FIRST和FOLLOW集
        self.compute_first()
        self.compute_follow()
        
        # 初始化分析表
        for nt in self.non_terminals:
            self.parse_table[nt] = {}
            for term in self.terminals:
                self.parse_table[nt][term] = None
        
        # 构造预测分析表
        for nt, productions in self.grammar.items():
            for i, prod in enumerate(productions):
                # 计算FIRST(α)
                first_of_prod = set()
                can_derive_epsilon = True
                
                for symbol in prod:
                    if symbol == 'ε':
                        first_of_prod.add('ε')
                        break
                    
                    if symbol in self.terminals:
                        first_of_prod.add(symbol)
                        can_derive_epsilon = False
                        break
                    
                    # 将FIRST(X)中除ε外的所有符号加入FIRST(α)
                    for term in self.first[symbol] - set(['ε']):
                        first_of_prod.add(term)
                    
                    # 如果X不能推导出ε，则停止
                    if 'ε' not in self.first[symbol]:
                        can_derive_epsilon = False
                        break
                
                # 对于FIRST(α)中的每个终结符a，将产生式A->α加入M[A,a]
                for term in first_of_prod - set(['ε']):
                    if term != '$':  # 排除$
                        if self.parse_table[nt][term] is None:
                            self.parse_table[nt][term] = (i, prod)
                        else:
                            print(f"文法不是LL(1)文法! 冲突在 M[{nt},{term}]")
                
                # 如果ε在FIRST(α)中，对于FOLLOW(A)中的每个终结符b，将A->α加入M[A,b]
                if 'ε' in first_of_prod or can_derive_epsilon:
                    for term in self.follow[nt]:
                        actual_term = term if term != '$' else '$'
                        if actual_term in self.terminals and self.parse_table[nt][actual_term] is None:
                            self.parse_table[nt][actual_term] = (i, prod)
                        elif actual_term in self.terminals:
                            print(f"文法不是LL(1)文法! 冲突在 M[{nt},{actual_term}]")
        
        print("\n预测分析表:")
        for nt in self.non_terminals:
            for term in self.terminals:
                if term != '$' and self.parse_table[nt][term] is not None:
                    prod_idx, prod = self.parse_table[nt][term]
                    print(f"M[{nt},{term}] = {nt} -> {' '.join(prod)}")
    
    def tokenize(self, expr):
        tokens = []
        i = 0
        while i < len(expr):
            # 跳过空白
            if expr[i].isspace():
                i += 1
                continue
            
            # 检查数字
            if expr[i].isdigit():
                start = i
                while i < len(expr) and expr[i].isdigit():
                    i += 1
                tokens.append(('num', expr[start:i]))
                continue
            
            # 检查符号
            if expr[i] in ['+', '-', '*', '/', '(', ')']:
                tokens.append((expr[i], expr[i]))
            
            i += 1
        
        tokens.append(('$', '$'))  # 结束符号
        return tokens
    
    def parse(self, expr):
        tokens = self.tokenize(expr)
        token_index = 0
        stack = ['$', list(self.grammar.keys())[0]]  # 栈底添加$和起始符号
        productions_used = []
        
        print("\n分析过程:")
        print(f"{'步骤':<5}{'符号栈':<20}{'输入串':<20}{'产生式':<30}")
        
        step = 1
        while stack[-1] != '$':
            top = stack[-1]
            token_type, token_value = tokens[token_index]
            
            # 打印当前状态
            stack_str = ' '.join(stack)
            input_str = ' '.join([t[0] for t in tokens[token_index:]])
            
            # 如果栈顶是终结符
            if top in self.terminals:
                if top == token_type:
                    stack.pop()
                    token_index += 1
                    print(f"{step:<5}{stack_str:<20}{input_str:<20}匹配终结符: {top}")
                else:
                    print(f"语法错误: 期望 {top}, 得到 {token_type}")
                    return False
            # 如果栈顶是非终结符
            elif top in self.non_terminals:
                entry = self.parse_table[top][token_type]
                
                if entry is not None:
                    prod_idx, production = entry
                    production_str = f"{top} -> {' '.join(production)}"
                    productions_used.append(production_str)
                    
                    stack.pop()  # 弹出非终结符
                    
                    # 反向压入产生式右部（除了ε）
                    if production[0] != 'ε':
                        for symbol in reversed(production):
                            stack.append(symbol)
                    
                    print(f"{step:<5}{stack_str:<20}{input_str:<20}{production_str:<30}")
                else:
                    print(f"语法错误: 在 M[{top},{token_type}] 中没有产生式")
                    return False
            else:
                print(f"未知符号: {top}")
                return False
            
            step += 1
        
        # 检查输入是否全部处理完
        if tokens[token_index][0] == '$':
            print("\n分析成功!")
            print("\n使用的产生式序列:")
            for i, prod in enumerate(productions_used):
                print(f"{i+1}. {prod}")
            return True
        else:
            print("\n语法错误: 输入未完全处理")
            return False
