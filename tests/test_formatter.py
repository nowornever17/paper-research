"""格式化模块测试"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from formatter import format_result


def test_format_result():
    result = {
        "background": "测试背景",
        "decisions": "测试决策",
        "lessons": "测试启示",
        "model": "Test AI",
    }
    output = format_result(result, "测试标题")
    assert "测试标题" in output
    assert "测试背景" in output
    assert "Test AI" in output
