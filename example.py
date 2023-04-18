from logging import INFO, basicConfig
from typing import TYPE_CHECKING

from nextcord import Client, Color, Embed, Interaction

from cordcutter import Cordcutter

basicConfig(level=INFO)

if TYPE_CHECKING:
    Interaction = Interaction[Client]

client = Client()

# By default a command breaker will pop after three errors and reset after one minute.
cordcutter = Cordcutter(client)


@client.slash_command(name="test")
async def test_command(interaction: Interaction) -> None:  # noqa: ARG001
    raise RuntimeError("This command always fails!")


@cordcutter.on_tripped_call
async def on_tripped(interaction: Interaction) -> None:
    # In a classic circuit breaker, this is where you would show the user a message,
    # that lets them know that the command is temporarily disabled.

    # You should avoid accessing a database or any other external resources here,
    # as that might be the reason why the breaker tripped in the first place.

    await interaction.response.send_message(
        embed=Embed(
            title="⚡ Breaker tripped!",
            description="This command is temporarily disabled due to encountering too many errors.",
            color=Color.red(),
        ),
    )


client.run("")
