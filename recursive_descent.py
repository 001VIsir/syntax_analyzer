class RecursiveDescentParser:
    def __init__(self, expr):
        self.expr = expr
        self.pos = 0
        self.current_token = None
        self.productions = []
    
    def get_next_token(self):
        if self.pos >= len(self.expr):
            return None
        
        # 跳过空白字符
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1
            
        if self.pos >= len(self.expr):
            return None
            
        # 检查数字
        if self.expr[self.pos].isdigit():
            start = self.pos
            while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                self.pos += 1
            return ('num', self.expr[start:self.pos])
            
        # 检查其他符号
        c = self.expr[self.pos]
        self.pos += 1
        return (c, c)
    
    def parse(self):
        self.current_token = self.get_next_token()
        result = self.parse_E()
        
        if self.current_token is None and result:
            print("分析成功!")
            print("使用的产生式序列:")
            for prod in self.productions:
                print(prod)
            return True
        else:
            print("语法错误!")
            return False
    
    def match(self, expected_token):
        if self.current_token and self.current_token[0] == expected_token:
            self.current_token = self.get_next_token()
            return True
        return False
    
    def parse_E(self):
        # E -> T E'
        # 其中 E' -> +T E' | -T E' | ε
        self.productions.append("E -> T")
        if not self.parse_T():
            return False
            
        while self.current_token and self.current_token[0] in ['+', '-']:
            op = self.current_token[0]
            self.match(op)
            
            if op == '+':
                self.productions.append("E -> E+T")
            else:
                self.productions.append("E -> E-T")
                
            if not self.parse_T():
                return False
                
        return True
    
    def parse_T(self):
        # T -> F T'
        # 其中 T' -> *F T' | /F T' | ε
        self.productions.append("T -> F")
        if not self.parse_F():
            return False
            
        while self.current_token and self.current_token[0] in ['*', '/']:
            op = self.current_token[0]
            self.match(op)
            
            if op == '*':
                self.productions.append("T -> T*F")
            else:
                self.productions.append("T -> T/F")
                
            if not self.parse_F():
                return False
                
        return True
    
    def parse_F(self):
        # F -> (E) | num
        if self.current_token:
            if self.current_token[0] == '(':
                self.match('(')
                self.productions.append("F -> (E)")
                if not self.parse_E():
                    return False
                if not self.match(')'):
                    print("错误：缺少右括号")
                    return False
                return True
            elif self.current_token[0] == 'num':
                self.match('num')
                self.productions.append("F -> num")
                return True
        
        print("语法错误：期望 '(' 或 'num'")
        return False
