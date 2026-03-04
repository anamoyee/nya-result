from typing import Any

import pytest
from nya_result import ResultDirect as _RD
from nya_result import ResultIndirect as _RI
from nya_result._base import (
	ResultUnwrappedErrOnValueError,
	ResultUnwrappedOnErrorError,
	_ResultBase,
)


@pytest.fixture(params=[_RD, _RI])
def Result(request) -> type[_ResultBase]:
	return request.param


@pytest.mark.parametrize(
	("inner_value",),
	(
		(1,),
		([1, 2, 3],),
		(type,),
		(None,),
	),
)
def test_containing_doesnt_corrupt_value(Result, inner_value: Any) -> None:
	result = Result.new_ok(inner_value)
	assert result.unwrap() is inner_value


def test_new_err_sets_error_state(Result):
	err = ValueError("boom")
	result = Result.new_err(err)

	assert result.is_err
	assert not result.is_ok
	assert result.unwrap_err() is err


def test_new_ok_sets_value_state(Result):
	result = Result.new_ok(123)

	assert result.is_ok
	assert not result.is_err
	assert result.unwrap() == 123


def test_unwrap_err_on_value_raises(Result):
	result = Result.new_ok(1)

	with pytest.raises(ResultUnwrappedErrOnValueError):
		result.unwrap_err()


def test_unwrap_or(Result):
	ok = Result.new_ok(10)
	err = Result.new_err(ValueError())

	assert ok.unwrap_or(999) == 10
	assert err.unwrap_or(999) == 999


def test_unwrap_err_or(Result):
	error = ValueError("x")
	ok = Result.new_ok(10)
	err = Result.new_err(error)

	assert ok.unwrap_err_or("fallback") == "fallback"
	assert err.unwrap_err_or("fallback") is error


def test_unwrap_or_else(Result):
	error = ValueError("x")
	ok = Result.new_ok(10)
	err = Result.new_err(error)

	assert ok.unwrap_or_else(lambda e: 999) == 10
	assert err.unwrap_or_else(lambda e: str(e)) == "x"


def test_unwrap_err_or_else(Result):
	error = ValueError("x")
	ok = Result.new_ok(10)
	err = Result.new_err(error)

	assert ok.unwrap_err_or_else(lambda v: v * 2) == 20
	assert err.unwrap_err_or_else(lambda v: None) is error


def test_raise_if_possible_ok(Result):
	result = Result.new_ok(1)
	result.raise_if_possible()


def test_raise_if_possible_err(Result):
	error = ValueError("boom")
	result = Result.new_err(error)

	with pytest.raises(ValueError) as exc:
		result.raise_if_possible()

	assert exc.value is error


def test_map_ok(Result):
	result = Result.new_ok(2)
	returned = result.map_ok(lambda v: v * 3)

	assert returned is result
	assert result.unwrap() == 6


def test_map_ok_noop_on_err(Result):
	error = ValueError("x")
	result = Result.new_err(error)

	result.map_ok(lambda v: 999)

	assert result.unwrap_err() is error


def test_map_err(Result):
	error = ValueError("x")
	result = Result.new_err(error)

	result.map_err(lambda e: TypeError(str(e)))

	err = result.unwrap_err()
	assert isinstance(err, TypeError)
	assert str(err) == "x"


def test_map_err_noop_on_ok(Result):
	result = Result.new_ok(5)

	result.map_err(lambda e: RuntimeError())

	assert result.unwrap() == 5


def test_equality_ok_equals_ok(Result):
	result_ok_one1 = Result.new_ok(1)
	result_ok_one2 = Result.new_ok(1)
	assert result_ok_one1 == result_ok_one2


def test_equality_ok_not_equals_different_ok(Result):
	result_ok_one1 = Result.new_ok(1)
	result_ok_two = Result.new_ok(2)
	assert result_ok_one1 != result_ok_two


def test_equality_err_not_equals_err(Result):
	# due to:
	# > >>> ValueError('x') == ValueError('x')
	# > False
	result_err1 = Result.new_err(ValueError("x"))
	result_err2 = Result.new_err(ValueError("x"))
	assert result_err1 != result_err2


def test_equality_ok_not_equals_err(Result):
	result_ok_one1 = Result.new_ok(1)
	result_err1 = Result.new_err(ValueError("x"))
	assert result_ok_one1 != result_err1


def test_new_err_rejects_non_exception(Result):
	with pytest.raises(ValueError):
		Result(is_error=True, value=123)  # type: ignore


# ------------------------
# Test unwrap_direct and unwrap_indirect explicitly
# ------------------------


def test_unwrap_direct_raises_on_error(Result):
	err = ValueError("boom")
	result = Result.new_err(err)

	if result.is_err:
		# unwrap_direct always raises underlying error
		with pytest.raises(ValueError) as exc:
			result.unwrap_direct()
		assert exc.value is err
	else:
		# ok case returns value
		assert result.unwrap_direct() == result._value


def test_unwrap_indirect_raises_on_error(Result):
	err = ValueError("boom")
	result = Result.new_err(err)

	if result.is_err:
		with pytest.raises(ResultUnwrappedOnErrorError) as exc:
			result.unwrap_indirect()
		assert exc.value.__cause__ is err
	else:
		assert result.unwrap_indirect() == result._value
