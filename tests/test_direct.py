import pytest
from nya_result import ResultDirect as _RD
from nya_result._base import ResultUnwrappedErrOnValueError, ResultUnwrappedOnErrorError


def test_unwrap_on_ok_returns_value():
	result = _RD.new_ok(42)
	# unwrap() should behave like unwrap_direct()
	assert result.unwrap() == 42


def test_unwrap_on_err_raises_underlying_error():
	error = ValueError("boom")
	result = _RD.new_err(error)

	# unwrap() should behave like unwrap_direct(), raising the underlying error
	with pytest.raises(ValueError) as exc:
		result.unwrap()

	assert exc.value is error
