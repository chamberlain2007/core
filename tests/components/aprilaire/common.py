from collections.abc import Awaitable, Callable

from typing_extensions import Generator

# Typing helpers
type PlatformSetup = Callable[[], Awaitable[None]]
type YieldFixture[_T] = Generator[_T]
