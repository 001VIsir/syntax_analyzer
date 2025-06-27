from recursive_descent import RecursiveDescentParser
from ll1_parser import LL1Parser
from lr_parser import LRParser

def run_simple_test():
    """
    简单测试函数，测试各种语法分析器是否能正确分析给定的表达式
    """
    print("\n===== 语法分析器简单测试 =====")
    
    # 测试表达式列表，包含有效和无效的表达式
    test_expressions = [
        # 有效表达式
        ("3+4*5", True, "基本混合运算，测试运算符优先级"),
        ("2*(3+4)", True, "带括号表达式，测试括号优先级"),
        ("(1+2)*(3+4)", True, "复杂表达式，测试嵌套括号"),
        ("5/(2+3)-1", True, "带除法的表达式，测试多种运算符"),
        ("1", True, "单一数字表达式，测试最简单情况"),
        ("(((1+2)+3)+4)", True, "多层嵌套括号，测试复杂嵌套"),
        # 无效表达式
        ("3+", False, "不完整的表达式，缺少右操作数"),
        ("3++4", False, "连续的操作符，违反语法规则"),
        ("3+4)", False, "右括号不匹配，缺少左括号"),
        ("(3+4", False, "左括号不匹配，缺少右括号"),
        ("*3+4", False, "表达式以运算符开头，违反语法规则"),
    ]
    
    # 选择分析方法
    print("\n请选择要测试的分析器:")
    print("1. 递归下降分析器")
    print("2. LL(1)分析器")
    print("3. LR分析器")
    print("4. 所有分析器")
    
    choice = input("请输入选择(1-4): ")
    
    # 预先初始化分析器
    ll1_parser = None
    lr_parser = None
    
    if choice in ['2', '4']:
        print("\n正在初始化LL(1)分析器...")
        ll1_parser = LL1Parser()
        ll1_parser.construct_table()
    
    if choice in ['3', '4']:
        print("\n正在初始化LR分析器...")
        lr_parser = LRParser()
        lr_parser.construct_table()
    
    print("\n===== 测试结果 =====")
    print(f"{'表达式':<20} | {'预期结果':<10} | {'递归下降':<10} | {'LL(1)':<10} | {'LR':<10} | {'说明'}")
    print("-" * 90)
    
    for expr, expected, description in test_expressions:
        # 初始化结果
        rd_result = "未测试"
        ll1_result = "未测试"
        lr_result = "未测试"
        
        # 测试递归下降分析器
        if choice in ['1', '4']:
            print(f"\n测试递归下降分析: {expr}")
            parser = RecursiveDescentParser(expr)
            rd_result = "成功" if parser.parse() else "失败"
            print("----------------------------------------")
        
        # 测试LL(1)分析器
        if choice in ['2', '4'] and ll1_parser:
            print(f"\n测试LL(1)分析: {expr}")
            ll1_result = "成功" if ll1_parser.parse(expr) else "失败"
            print("----------------------------------------")
        
        # 测试LR分析器
        if choice in ['3', '4'] and lr_parser:
            print(f"\n测试LR分析: {expr}")
            lr_result = "成功" if lr_parser.parse(expr) else "失败"
            print("----------------------------------------")
        
        # 打印结果
        expected_str = "成功" if expected else "失败"
        print(f"{expr:<20} | {expected_str:<10} | {rd_result:<10} | {ll1_result:<10} | {lr_result:<10} | {description}")
    
    print("\n测试完成！")
    
    # 打印结果分析
    print("\n===== 结果分析 =====")
    success_count = {'rd': 0, 'll1': 0, 'lr': 0}
    total_valid = sum(1 for _, expected, _ in test_expressions if expected)
    total_invalid = sum(1 for _, expected, _ in test_expressions if not expected)
    
    for expr, expected, _ in test_expressions:
        if choice in ['1', '4']:
            parser = RecursiveDescentParser(expr)
            result = parser.parse()
            if (result and expected) or (not result and not expected):
                success_count['rd'] += 1
                
        if choice in ['2', '4'] and ll1_parser:
            result = ll1_parser.parse(expr)
            if (result and expected) or (not result and not expected):
                success_count['ll1'] += 1
                
        if choice in ['3', '4'] and lr_parser:
            result = lr_parser.parse(expr)
            if (result and expected) or (not result and not expected):
                success_count['lr'] += 1
    
    if choice in ['1', '4']:
        print(f"递归下降分析器: {success_count['rd']}/{len(test_expressions)} 正确 "
              f"({success_count['rd']/len(test_expressions)*100:.1f}%)")
    
    if choice in ['2', '4']:
        print(f"LL(1)分析器: {success_count['ll1']}/{len(test_expressions)} 正确 "
              f"({success_count['ll1']/len(test_expressions)*100:.1f}%)")
    
    if choice in ['3', '4']:
        print(f"LR分析器: {success_count['lr']}/{len(test_expressions)} 正确 "
              f"({success_count['lr']/len(test_expressions)*100:.1f}%)")
    
    print(f"\n共测试 {len(test_expressions)} 个表达式 ({total_valid} 个有效, {total_invalid} 个无效)")

if __name__ == "__main__":
    run_simple_test()
