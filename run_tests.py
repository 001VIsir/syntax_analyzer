import sys
from test_parser import ParserTest
import unittest

def run_tests():
    print("语法分析器测试程序")
    print("==================")
    print("\n请选择测试类型:")
    print("1. 测试所有分析器")
    print("2. 只测试递归下降分析器")
    print("3. 只测试LL(1)分析器")
    print("4. 只测试LR分析器")
    print("5. 测试错误处理")
    print("0. 退出")
    
    choice = input("\n请输入选择(0-5): ")
    
    suite = unittest.TestSuite()
    
    if choice == '1':
        suite.addTest(ParserTest('test_recursive_descent'))
        suite.addTest(ParserTest('test_ll1_parser'))
        suite.addTest(ParserTest('test_lr_parser'))
    elif choice == '2':
        suite.addTest(ParserTest('test_recursive_descent'))
    elif choice == '3':
        suite.addTest(ParserTest('test_ll1_parser'))
    elif choice == '4':
        suite.addTest(ParserTest('test_lr_parser'))
    elif choice == '5':
        suite.addTest(ParserTest('test_error_cases'))
    elif choice == '0':
        sys.exit(0)
    else:
        print("无效的选择!")
        return
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
    
    print("\n测试完成!")
    input("\n按Enter键返回主菜单...")
    run_tests()

if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n程序已退出")
