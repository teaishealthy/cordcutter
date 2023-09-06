from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable, Iterable
from datetime import timedelta
from logging import getLogger
from typing import Any, Generic, TypeVar, Type

from nextcord import (
    ApplicationError,
    BaseApplicationCommand,
    Client,
    Interaction,
    SlashApplicationSubcommand,
)

TClient = TypeVar("TClient", bound="Client")

ApplicationCommand = SlashApplicationSubcommand | BaseApplicationCommand

Callback = Callable[[Interaction[Client]], Any]
TCallback = TypeVar("TCallback", bound=Callback)

logger = getLogger(__name__)


class Cordcutter(Generic[TClient]):
    """Cordcutter implements the circuit breaker design pattern for nextcord bot using application commands."""  # noqa: E501

    def __init__(
        self,
        client: TClient,
        *,
        threshold: int = 3,
        reset_after: timedelta | None = None,
        ignore_exceptions: Iterable[Type[Exception]] | None = None
    ) -> None:
        """Create a new Cordcutter instance.

        Args:
            client (Client): The nextcord client to use.
            threshold (int, optional): How many errors may occur before the command breaker trips.
            Defaults to 3.
            reset_after (timedelta, optional): After what time the command breaker should reset.
            Defaults to timedelta(minutes=1).
            ignore_exceptions (Iterable): Exceptions that cordcutter should ignore
        """
        client.on_application_command_error = self._on_application_command_error

        self.threshold: int = threshold
        self.reset_after: timedelta = reset_after or timedelta(minutes=1)
        self.errors: defaultdict[ApplicationCommand, int] = defaultdict(int)
        self.ignore_exceptions: Iterable[Type[Exception]] | None = ignore_exceptions

        self._on_tripped_call: Callback | None = None

    async def _on_application_command_error(
        self,
        interaction: Interaction[TClient],
        exception: ApplicationError,  # noqa: ARG002
    ) -> None:
        if interaction.application_command is None:
            return

        # Breaker has already tripped
        if self.errors.get(interaction.application_command, 0) >= self.threshold:
            return

        if self.ignore_exceptions:
            original_exception: Exception = getattr(exception, "original", exception)

            if isinstance(original_exception, tuple(self.ignore_exceptions)):
                command: str = interaction.application_command.qualified_name
                logger.warning("🔌 Ignoring exception: %s for command /%s", type(original_exception), command)
                return

        self.errors[interaction.application_command] += 1

        if self.errors[interaction.application_command] >= self.threshold:
            await self.tripped_breaker(interaction.application_command)

    async def tripped_breaker(self, command: ApplicationCommand) -> None:
        """Trips a command breaker.

        Args:
            command (ApplicationCommand): The command to trip the breaker for.
        """
        logger.warning("🔌 Breaker tripped for %s!", command.qualified_name)

        original_callback: Any = command.callback  # pyright: ignore[reportUnknownMemberType=false]
        command.callback = self._on_tripped_call

        asyncio.get_event_loop().call_later(
            self.reset_after.total_seconds(),
            self.reset_breaker,
            command,
            original_callback,
        )

    def reset_breaker(self, command: ApplicationCommand, original_callback: Any) -> None:
        """Reset the breaker for a command.

        Args:
            command (ApplicationCommand): The command to reset the breaker for.
            original_callback (Any): The original callback of the command.
        """
        logger.warning("🔌 Breaker reset for %s!", command.qualified_name)

        command.callback = original_callback
        self.errors.pop(command, None)

    def on_tripped_call(self, callback: TCallback) -> TCallback:
        """The callback to call when a command breaker trips.

        Args:
            callback (Callback): The callback to call.

        Returns:
            Callback: The callback.
        """
        self._on_tripped_call = callback
        return callback
