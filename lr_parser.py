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
        
        # LR分析表
        self.action = {}
        self.goto = {}
        
    def construct_table(self):
        """
        构造LR分析表（简化版）
        直接硬编码表，而非动态构建
        """
        # 初始化ACTION和GOTO表
        self.action = {
            0: {'(': ('shift', 4), 'num': ('shift', 5)},
            1: {'+': ('shift', 6), '-': ('shift', 7), '$': ('accept', None)},
            2: {'+': ('reduce', 3), '-': ('reduce', 3), '*': ('shift', 8), '/': ('shift', 9), 
                ')': ('reduce', 3), '$': ('reduce', 3)},
            3: {'+': ('reduce', 6), '-': ('reduce', 6), '*': ('reduce', 6), '/': ('reduce', 6), 
                ')': ('reduce', 6), '$': ('reduce', 6)},
            4: {'(': ('shift', 4), 'num': ('shift', 5)},
            5: {'+': ('reduce', 8), '-': ('reduce', 8), '*': ('reduce', 8), '/': ('reduce', 8), 
                ')': ('reduce', 8), '$': ('reduce', 8)},
            6: {'(': ('shift', 4), 'num': ('shift', 5)},
            7: {'(': ('shift', 4), 'num': ('shift', 5)},
            8: {'(': ('shift', 4), 'num': ('shift', 5)},
            9: {'(': ('shift', 4), 'num': ('shift', 5)},
            10: {'+': ('reduce', 3), '-': ('reduce', 3), ')': ('shift', 15), '$': ('reduce', 3)},
            11: {'+': ('shift', 6), '-': ('shift', 7), ')': ('shift', 13)},
            12: {'+': ('reduce', 1), '-': ('reduce', 1), '*': ('shift', 8), '/': ('shift', 9), 
                 ')': ('reduce', 1), '$': ('reduce', 1)},
            13: {'+': ('reduce', 7), '-': ('reduce', 7), '*': ('reduce', 7), '/': ('reduce', 7), 
                 ')': ('reduce', 7), '$': ('reduce', 7)},
            14: {'+': ('reduce', 4), '-': ('reduce', 4), '*': ('reduce', 4), '/': ('reduce', 4), 
                 ')': ('reduce', 4), '$': ('reduce', 4)},
            15: {'+': ('reduce', 7), '-': ('reduce', 7), '*': ('reduce', 7), '/': ('reduce', 7), 
                 ')': ('reduce', 7), '$': ('reduce', 7)},
            16: {'+': ('reduce', 5), '-': ('reduce', 5), '*': ('reduce', 5), '/': ('reduce', 5), 
                 ')': ('reduce', 5), '$': ('reduce', 5)},
        }
        
        self.goto = {
            0: {'E': 1, 'T': 2, 'F': 3},
            4: {'E': 11, 'T': 2, 'F': 3},
            6: {'T': 12, 'F': 3},
            7: {'T': 13, 'F': 3},
            8: {'F': 14},
            9: {'F': 16},
            10: {'E': 11, 'T': 2, 'F': 3},
            11: {},
            12: {},
        }
        
        # 补充缺失的状态转换
        # 状态6和状态7需要添加对非终结符T的处理
        self.goto[6] = {'T': 12, 'F': 3}
        self.goto[7] = {'T': 13, 'F': 3}
        
        # 补充E->E+T产生式对应的状态
        # 当识别E+T后，需要规约为E
        self.action[12] = {'+': ('reduce', 1), '-': ('reduce', 1), '*': ('shift', 8), '/': ('shift', 9), 
                           ')': ('reduce', 1), '$': ('reduce', 1)}
        
        # 补充E->E-T产生式对应的状态
        # 当识别E-T后，需要规约为E
        self.action[13] = {'+': ('reduce', 2), '-': ('reduce', 2), '*': ('reduce', 2), '/': ('reduce', 2), 
                           ')': ('reduce', 2), '$': ('reduce', 2)}
        
        print("LR分析表构造完成")
    
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
            
            # 查询动作表
            if token_type not in self.action.get(state, {}):
                print(f"语法错误: 状态 {state} 没有对 {token_type} 的动作定义")
                return False
                
            action_entry = self.action[state][token_type]
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
                
                # 查找GOTO表
                if lhs not in self.goto.get(top_state, {}):
                    print(f"语法错误: GOTO[{top_state},{lhs}]未定义")
                    return False
                
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
