import pytest

def test_basic():
    """基础测试"""
    assert 1 + 1 == 2

def test_string():
    """字符串测试"""
    assert "hello" in "hello world"

def test_list():
    """列表测试"""
    items = [1, 2, 3]
    assert len(items) == 3
    assert 2 in items
