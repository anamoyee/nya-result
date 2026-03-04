from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from ._base import _ResultBase


class ResultIndirect[Ok, Err: BaseException = BaseException](_ResultBase[Ok, Err]):
	def unwrap(self) -> Ok:
		"""If the result contains an error, raise `ResultUnwrappedOnErrorError()`, else return the value (On `Result` alias to `.unwrap_indirect()`)."""
		return self.unwrap_indirect()


def aresultify_indirect[**P, R](f: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, ResultIndirect[R, Exception]]]:
	@wraps(f)
	async def wrapper(*args, **kwargs):
		try:
			return ResultIndirect.new_ok(await f(*args, **kwargs))
		except Exception as e:
			return ResultIndirect.new_err(e)

	return wrapper


def resultify_indirect[**P, R](f: Callable[P, R]) -> Callable[P, ResultIndirect[R, Exception]]:
	@wraps(f)
	def wrapper(*args, **kwargs):
		try:
			return ResultIndirect.new_ok(f(*args, **kwargs))
		except Exception as e:
			return ResultIndirect.new_err(e)

	return wrapper
