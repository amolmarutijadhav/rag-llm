import pytest

def test_basic_math():
    """Basic test to verify pytest works."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert "hello" + " world" == "hello world"

def test_list_operations():
    """Test basic list operations."""
    my_list = [1, 2, 3, 4, 5]
    assert len(my_list) == 5
    assert sum(my_list) == 15
    assert my_list[0] == 1

def test_dict_operations():
    """Test basic dictionary operations."""
    my_dict = {"a": 1, "b": 2, "c": 3}
    assert len(my_dict) == 3
    assert my_dict["a"] == 1
    assert "b" in my_dict

class TestBasicClass:
    """Basic test class."""
    
    def test_class_method(self):
        """Test method in a class."""
        assert True
        
    def test_another_method(self):
        """Another test method."""
        assert 10 > 5 