import sys
from recursive_descent import RecursiveDescentParser
from ll1_parser import LL1Parser
from lr_parser import LRParser
from simple_test import run_simple_test

def main():
    while True:
        print("\n语法分析程序 - 算术表达式分析器")
        print("============================")
        print("支持的文法:")
        print("E -> E+T | E-T | T")
        print("T -> T*F | T/F | F")
        print("F -> (E) | num")
        print("\n请选择功能:")
        print("1. 递归下降分析")
        print("2. LL(1)分析")
        print("3. LR分析")
        print("4. 运行简单测试")
        print("0. 退出程序")
        
        choice = input("\n请输入选择(0-4): ")
        
        if choice == '1':
            expr = input("请输入算术表达式: ")
            parser = RecursiveDescentParser(expr)
            parser.parse()
        elif choice == '2':
            expr = input("请输入算术表达式: ")
            parser = LL1Parser()
            parser.construct_table()  # 构造预测分析表
            parser.parse(expr)
        elif choice == '3':
            expr = input("请输入算术表达式: ")
            parser = LRParser()
            parser.construct_table()  # 构造LR分析表
            parser.parse(expr)
        elif choice == '4':
            run_simple_test()
        elif choice == '0':
            print("\n程序已退出")
            sys.exit(0)
        else:
            print("无效的选择!")
        
        input("\n按Enter键继续...")
            
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
