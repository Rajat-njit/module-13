# tests/unit/test_calculation_model.py

from uuid import uuid4
from app.models.calculation import Calculation, Addition, Subtraction, Multiplication, Division


def test_factory_creates_correct_subclass():
    user_id = uuid4()
    calc = Calculation.create("addition", user_id=user_id, inputs=[1, 2])
    assert isinstance(calc, Addition)

    calc = Calculation.create("subtraction", user_id=user_id, inputs=[3, 1])
    assert isinstance(calc, Subtraction)

    calc = Calculation.create("multiplication", user_id=user_id, inputs=[2, 3])
    assert isinstance(calc, Multiplication)

    calc = Calculation.create("division", user_id=user_id, inputs=[10, 2])
    assert isinstance(calc, Division)


def test_addition_result():
    user_id = uuid4()
    calc = Calculation.create("addition", user_id=user_id, inputs=[1, 2, 3])
    assert calc.get_result() == 6.0


def test_division_by_zero_raises():
    user_id = uuid4()
    calc = Calculation.create("division", user_id=user_id, inputs=[10, 0])
    try:
        calc.get_result()
        assert False, "Expected ValueError when dividing by zero"
    except ValueError:
        assert True
