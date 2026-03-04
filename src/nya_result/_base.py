import abc
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Self, TypeVar, overload

Default = TypeVar("Default")


@dataclass
class ResultUnwrappedOnErrorError(Exception):
	"""An unwrap() was called on a Result containing an error."""


@dataclass
class ResultUnwrappedErrOnValueError(Exception):
	"""An unwrap_err() was called on a Result contaning a value."""


class _ResultBase[OkT, ErrT: BaseException = BaseException](abc.ABC):
	_value: OkT | ErrT
	_is_err: bool

	@overload
	def __init__(self, *, is_error: Literal[False] = False, value: OkT): ...

	@overload
	def __init__(self, *, is_error: Literal[True] = ..., value: ErrT): ...

	@overload
	def __init__(self, *, is_error: bool = False, value: ErrT | OkT): ...

	def __init__(
		self,
		*,
		is_error: bool = False,
		value: OkT | ErrT,
	):
		self._is_err = bool(is_error)

		if is_error and not isinstance(value, BaseException):
			raise ValueError(f"If is_error=True, value must be an {'**INSTANCE**' if isinstance(value, type) else 'instance'} of BaseException")

		self._value = value

	@classmethod
	def new_ok(cls, value: OkT) -> Self:
		return cls(is_error=False, value=value)  # type: ignore # <- mypy, i have no idea how do i tell you that this method is supposed to be used on subclasses only...

	@classmethod
	def new_err(cls, error: ErrT) -> Self:
		return cls(is_error=True, value=error)  # type: ignore # <- mypy, i have no idea how do i tell you that this method is supposed to be used on subclasses only...

	@property
	def is_ok(self) -> bool:
		return not self._is_err

	@property
	def is_err(self) -> bool:
		return self._is_err

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return NotImplemented

		return self._is_err == other._is_err and self._value == other._value

	def unwrap_err(self) -> ErrT:
		"""If the result contains a value, raise `ResultUnwrappedErrOnValueError()`, else return the error."""
		if not self._is_err:
			raise ResultUnwrappedErrOnValueError()

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_or(self, default: Default) -> OkT | Default:
		"""If the result contains an error, return default, else return the value."""
		if self.is_err:
			return default

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_err_or(self, default: Default) -> ErrT | Default:
		"""If the result contains a value, return default, else return the error."""
		if not self.is_err:
			return default

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_or_else(self, default_factory: Callable[[ErrT], Default]) -> OkT | Default:
		"""If the result contains an error, return `default_factory(that_error)`, else return the value."""
		if self.is_err:
			return default_factory(self._value)  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_err_or_else(self, default_factory: Callable[[OkT], Default]) -> ErrT | Default:
		"""If the result contains a value, return `default_factory(that_value)`, else return the error."""
		if not self.is_err:
			return default_factory(self._value)  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee

	def raise_if_possible(self) -> None:
		"""If the result contains a value, do nothing, otherwise raise the error."""

		if self.is_err:
			raise self._value  # type: ignore # <- due to `if` guarantee

	def map_err(self, f: Callable[[ErrT], ErrT]) -> Self:
		"""If the result contains an error, set it to `f(current_error)`, else do nothing."""
		if self.is_err:
			self._value = f(self._value)  # type: ignore # <- due to `if` guarantee

		return self

	def map_ok(self, f: Callable[[OkT], OkT]) -> Self:
		"""If the result contains a value (Ok), set it to `f(current_value)`, else do nothing."""
		if self.is_ok:
			self._value = f(self._value)  # type: ignore # <- due to `if` guarantee

		return self

	def __tcr_fmt__(self=None, *, fmt_iterable, syntax_highlighting, **kwargs):
		if self is None:
			raise NotImplementedError

		return fmt_iterable(self.__class__) + fmt_iterable(696969.696969).replace("696969", "") + fmt_iterable(bool(self.is_ok)).replace("True", "Ok").replace("False", "Err") + fmt_iterable((self._value,))

	@abc.abstractmethod
	def unwrap(self) -> OkT: ...  # subclass must choose either direct, indirect or custom impl as the default.

	def unwrap_direct(self) -> OkT:
		"""If the result contains an error, raise it, else return the value."""
		if self._is_err:
			raise self._value  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_indirect(self) -> OkT:
		"""If the result contains an error, raise `ResultUnwrappedOnErrorError()`, else return the value."""
		if self._is_err:
			raise ResultUnwrappedOnErrorError() from self._value  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee
