class LRParser:
    def __init__(self):
        # 初始化文法
        self.grammar = [
            ("S'", ["E"]),             # 扩展的起始产生式
            ("E", ["E", "+", "T"]),    # E -> E+T
            ("E", ["E", "-", "T"]),    # E -> E-T
            ("E", ["T"]),              # E -> T
            ("T", ["T", "*", "F"]),    # T -> T*F
            ("T", ["T", "/", "F"]),    # T -> T/F
            ("T", ["F"]),              # T -> F
            ("F", ["(", "E", ")"]),    # F -> (E)
            ("F", ["num"])             # F -> num
        ]
        
        self.non_terminals = {"S'", "E", "T", "F"}
        self.terminals = {"+", "-", "*", "/", "(", ")", "num", "$"}
        
        # LR项集和DFA
        self.items = []
        self.goto_table = {}
        
        # LR分析表
        self.action = {}
        self.goto = {}
        
        # 规范LR(1)项集族
        self.canonical_collection = []
        
    def closure(self, item_set):
        """计算LR(0)项集的闭包"""
        result = item_set.copy()
        
        while True:
            added = False
            for item in list(result):
                nt, rhs, dot_pos = item
                
                # 如果点不在最后且点后面是非终结符
                if dot_pos < len(rhs) and rhs[dot_pos] in self.non_terminals:
                    next_symbol = rhs[dot_pos]
                    
                    # 查找所有以该非终结符为左部的产生式
                    for g_nt, g_rhs in self.grammar:
                        if g_nt == next_symbol:
                            new_item = (g_nt, g_rhs, 0)
                            if new_item not in result:
                                result.add(new_item)
                                added = True
            
            if not added:
                break
                
        return result
    
    def goto(self, item_set, symbol):
        """计算GOTO函数"""
        result = set()
        
        for item in item_set:
            nt, rhs, dot_pos = item
            
            if dot_pos < len(rhs) and rhs[dot_pos] == symbol:
                result.add((nt, rhs, dot_pos + 1))
                
        return self.closure(result) if result else set()
    
    def build_dfa(self):
        """构建识别文法活前缀的DFA"""
        # 初始项集 - S' -> .E
        initial_item = ("S'", ["E"], 0)
        initial_set = self.closure({initial_item})
        
        # 初始化规范族和转换表
        self.canonical_collection = [initial_set]
        self.goto_table = {}
        
        i = 0
        while i < len(self.canonical_collection):
            item_set = self.canonical_collection[i]
            
            # 获取所有可能的下一个符号
            next_symbols = set()
            for nt, rhs, dot_pos in item_set:
                if dot_pos < len(rhs):
                    next_symbols.add(rhs[dot_pos])
            
            # 计算每个符号的GOTO
            for symbol in next_symbols:
                next_set = self.goto(item_set, symbol)
                
                if next_set:
                    # 检查是否已存在该项集
                    if next_set in self.canonical_collection:
                        j = self.canonical_collection.index(next_set)
                    else:
                        self.canonical_collection.append(next_set)
                        j = len(self.canonical_collection) - 1
                    
                    self.goto_table[(i, symbol)] = j
            
            i += 1
        
        print(f"共构造 {len(self.canonical_collection)} 个LR(0)项集:")
        for i, item_set in enumerate(self.canonical_collection):
            print(f"I{i}:")
            for nt, rhs, dot_pos in sorted(item_set, key=lambda x: (x[0], ''.join(x[1]))):
                rhs_str = ' '.join(rhs[:dot_pos] + ['.'] + rhs[dot_pos:])
                print(f"    {nt} -> {rhs_str}")
        
        print("\nGOTO函数:")
        for (i, symbol), j in sorted(self.goto_table.items()):
            print(f"GOTO(I{i}, {symbol}) = I{j}")
    
    def construct_table(self):
        """构造LR分析表"""
        # 首先构建DFA
        self.build_dfa()
        
        # 初始化分析表
        for i in range(len(self.canonical_collection)):
            self.action[i] = {}
            self.goto[i] = {}
            
            for term in self.terminals:
                self.action[i][term] = None
            
            for nt in self.non_terminals - {"S'"}:  # 排除扩展的开始符号
                self.goto[i][nt] = None
        
        # 填充ACTION和GOTO表
        for i, item_set in enumerate(self.canonical_collection):
            # 对于每个项 [A -> α.aβ]，若 (I_i, a) -> I_j，则置ACTION[i, a] = shift j
            for symbol in self.terminals:
                if (i, symbol) in self.goto_table:
                    j = self.goto_table[(i, symbol)]
                    self.action[i][symbol] = ('shift', j)
            
            # 对于每个项 [A -> α.]，若A != S'，则对FOLLOW(A)中的所有a, 置ACTION[i, a] = reduce j
            for nt, rhs, dot_pos in item_set:
                if dot_pos == len(rhs) and nt != "S'":
                    # 查找该产生式在文法中的索引
                    for j, (g_nt, g_rhs) in enumerate(self.grammar):
                        if g_nt == nt and g_rhs == rhs:
                            for term in self.terminals:  # 简化版：使用所有终结符作为FOLLOW集
                                if self.action[i][term] is None:
                                    self.action[i][term] = ('reduce', j)
                                # 检测并报告冲突
                                elif self.action[i][term][0] != 'reduce' or self.action[i][term][1] != j:
                                    print(f"警告: 状态{i}对于终结符{term}存在冲突!")
                                    print(f"已有: {self.action[i][term]}")
                                    print(f"新增: ('reduce', {j})")
            
            # 对于项 [S' -> E.]，置ACTION[i, $] = accept
            if ("S'", ["E"], 1) in item_set:
                self.action[i]['$'] = ('accept', None)
            
            # 填充GOTO表
            for nt in self.non_terminals - {"S'"}:
                if (i, nt) in self.goto_table:
                    j = self.goto_table[(i, nt)]
                    self.goto[i][nt] = j
        
        print("\nACTION表:")
        terminal_list = sorted(self.terminals)
        header = "状态 | " + " | ".join(terminal_list)
        print(header)
        print("-" * len(header))
        
        for i in range(len(self.canonical_collection)):
            row = f"{i:4d} | "
            for term in terminal_list:
                action_entry = self.action[i][term]
                if action_entry is None:
                    row += f"{'':8} | "
                elif action_entry[0] == 'shift':
                    row += f"s{action_entry[1]:7} | "
                elif action_entry[0] == 'reduce':
                    row += f"r{action_entry[1]:7} | "
                else:  # accept
                    row += f"{'acc':8} | "
            print(row)
        
        print("\nGOTO表:")
        nt_list = sorted(self.non_terminals - {"S'"})
        header = "状态 | " + " | ".join(nt_list)
        print(header)
        print("-" * len(header))
        
        for i in range(len(self.canonical_collection)):
            row = f"{i:4d} | "
            for nt in nt_list:
                goto_entry = self.goto[i][nt]
                if goto_entry is None:
                    row += f"{'':5} | "
                else:
                    row += f"{goto_entry:5d} | "
            print(row)
    
    def tokenize(self, expr):
        """词法分析，将表达式转换为token序列"""
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
        """LR语法分析过程"""
        tokens = self.tokenize(expr)
        token_index = 0
        stack = [(0, '$')]  # 状态栈初始化为状态0和栈底标记
        productions_used = []
        
        print("\n分析过程:")
        print(f"{'步骤':<5}{'状态栈':<20}{'符号栈':<20}{'输入串':<20}{'动作':<30}")
        
        step = 1
        while True:
            state = stack[-1][0]
            token_type, token_value = tokens[token_index]
            
            # 打印当前状态
            state_stack = ' '.join([str(s[0]) for s in stack])
            symbol_stack = ' '.join([str(s[1]) for s in stack])
            input_str = ' '.join([t[0] for t in tokens[token_index:]])
            
            action_entry = self.action[state][token_type]
            
            if action_entry is None:
                print(f"语法错误: 状态 {state} 没有对 {token_type} 的动作定义")
                return False
            
            action_type, action_value = action_entry
            
            if action_type == 'shift':
                print(f"{step:<5}{state_stack:<20}{symbol_stack:<20}{input_str:<20}移进，转到状态 {action_value}")
                stack.append((action_value, token_type))
                token_index += 1
            
            elif action_type == 'reduce':
                # 获取要规约的产生式
                prod_idx = action_value
                lhs, rhs = self.grammar[prod_idx]
                
                # 弹出|β|个符号
                for _ in range(len(rhs)):
                    stack.pop()
                
                # 查看栈顶状态
                top_state = stack[-1][0]
                
                # 将[A, GOTO[top_state, A]]入栈
                goto_state = self.goto[top_state][lhs]
                stack.append((goto_state, lhs))
                
                # 记录使用的产生式
                prod_str = f"{lhs} -> {' '.join(rhs)}"
                productions_used.append(prod_str)
                
                print(f"{step:<5}{state_stack:<20}{symbol_stack:<20}{input_str:<20}规约: {prod_str}")
            
            elif action_type == 'accept':
                print(f"{step:<5}{state_stack:<20}{symbol_stack:<20}{input_str:<20}接受!")
                break
            
            else:
                print(f"未知动作: {action_type}")
                return False
            
            step += 1
        
        print("\n分析成功!")
        print("\n使用的产生式序列:")
        for i, prod in enumerate(productions_used):
            print(f"{i+1}. {prod}")
        
        return True
