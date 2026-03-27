import pytest
from nya_result import Maybe


def test_some():
	v = 1234

	maybe = Maybe.new_some(v)

	assert maybe.is_some
	assert not maybe.is_none

	assert maybe.unwrap() == v
	assert maybe.unwrap_or(-42) == v
	assert maybe.unwrap_or_else(lambda: -42) == v


def test_none():
	maybe = Maybe.new_none()

	assert not maybe.is_some
	assert maybe.is_none

	with pytest.raises(ValueError):
		maybe.unwrap()

	assert maybe.unwrap_or(-42) == -42
	assert maybe.unwrap_or_else(lambda: -42) == -42
