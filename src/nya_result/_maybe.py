from collections.abc import Callable
from enum import Enum, auto
from typing import Self, TypeVar

Default = TypeVar("Default")


class _ArgNotPassedType(Enum):
	ARG_NOT_PASSED = auto()


class Maybe[T]:
	_value: T
	_is_some: bool

	def __init__(
		self,
		value: T | _ArgNotPassedType = _ArgNotPassedType.ARG_NOT_PASSED,
	):
		self._is_some = value is not _ArgNotPassedType.ARG_NOT_PASSED

		if self._is_some:
			self._value = value  # type: ignore # <- due to `if` guarantee

	@classmethod
	def new_some(cls, value: T) -> Self:
		return cls(value)

	@classmethod
	def new_none(cls) -> Self:
		return cls()

	@property
	def is_some(self) -> bool:
		return self._is_some

	@property
	def is_none(self) -> bool:
		return not self._is_some

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return NotImplemented

		return self._is_some == other._is_some and self._value == other._value

	def unwrap_or(self, default: Default) -> T | Default:
		"""If the result contains a none, return default, else return the value."""
		if self.is_none:
			return default

		return self._value  # type: ignore # <- due to `if` guarantee

	def unwrap_or_else(self, default_factory: Callable[[], Default]) -> T | Default:
		"""If the result contains a none, return `default_factory()`, else return the value."""
		if self.is_none:
			return default_factory()  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee

	def map(self, f: Callable[[T], T]) -> Self:
		"""If the result contains a Some, set it to `f(current_value)`, else do nothing."""
		if self.is_some:
			self._value = f(self._value)  # type: ignore # <- due to `if` guarantee

		return self

	def __tcr_fmt__(self=None, *, fmt_iterable, syntax_highlighting, **kwargs):
		if self is None:
			raise NotImplementedError

		return fmt_iterable(self.__class__) + fmt_iterable(696969.696969).replace("696969", "") + fmt_iterable(bool(self.is_some)).replace("True", "Some").replace("False", "None_") + fmt_iterable((self._value,))

	def unwrap(self) -> T:
		"""If the result contains a none, raise `ValueError()`, else return the value."""
		if self.is_none:
			raise ValueError(f"{self.__class__.__name__!r}.unwrap() called on instance of the none variant")  # type: ignore # <- due to `if` guarantee

		return self._value  # type: ignore # <- due to `if` guarantee
