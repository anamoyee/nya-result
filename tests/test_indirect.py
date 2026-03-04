from math import e

import pytest
from nya_result import ResultIndirect as _RI
from nya_result._base import ResultUnwrappedOnErrorError


def test_unwrap_on_ok_returns_value():
	result = _RI.new_ok(99)
	# unwrap() should behave like unwrap_indirect()
	assert result.unwrap() == 99


def test_unwrap_on_err_raises_wrapper_error():
	error = RuntimeError("fail")
	result = _RI.new_err(error)

	# unwrap() should behave like unwrap_indirect(), raising ResultUnwrappedOnErrorError
	with pytest.raises(ResultUnwrappedOnErrorError) as exc:
		result.unwrap()

	# the original error should be the __cause__
	assert exc.value.__cause__ is error
