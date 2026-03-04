from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from ._base import _ResultBase


class ResultDirect[Ok, Err: BaseException = BaseException](_ResultBase[Ok, Err]):
	def unwrap(self) -> Ok:
		"""If the result contains an error, raise it, else return the value."""
		return self.unwrap_direct()


def aresultify_direct[**P, R](f: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, ResultDirect[R, Exception]]]:
	@wraps(f)
	async def wrapper(*args, **kwargs):
		try:
			return ResultDirect.new_ok(await f(*args, **kwargs))
		except Exception as e:
			return ResultDirect.new_err(e)

	return wrapper


def resultify_direct[**P, R](f: Callable[P, R]) -> Callable[P, ResultDirect[R, Exception]]:
	@wraps(f)
	def wrapper(*args, **kwargs):
		try:
			return ResultDirect.new_ok(f(*args, **kwargs))
		except Exception as e:
			return ResultDirect.new_err(e)

	return wrapper
