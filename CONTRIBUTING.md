# Contribution Guidelines

Before committing, please make sure your contributions meet our requirements.

# Code Style

## Imports

We organize imports like this:
```py
# Imports without from
import asyncio
import discord

# Imports with from, we prefer these
from discord import app_commands
from discord.ext import commands

# Local imports
from utils import Cog
from utils.config import cfg
from utils.services import guild_service
```

Avoid using comments in the imports section.

## If Statements

Avoid keeping if statements over 120 characters.
```py
if (message.channel.id != guild_service.get_guild().channel_chatgpt or message.author.bot or message.content.startswith(("--", "–", "—", "<@"))):
    return
```
Would be changed to:
```py
if (
    message.channel.id != guild_service.get_guild().channel_chatgpt
    or message.author.bot
    or message.content.startswith(("--", "–", "—", "<@"))
):
    return
```

## Classes

There should be 2 spaces between classes.
```py
# Imports here


class A(Cog):
    pass


class B(Cog):
    pass
```

Cogs should always use the `Cog` class from `utils`.

## Functions

Your functions should have always have a return type. Interactions will always return `None`. Every variable should also have a type if known.
```py
async def say(self, ctx: discord.Interaction, message: str, channel: Optional[discord.TextChannel]) -> None:
```

```py
def format_number(number: int) -> str:
    return f"{number:,}"
```

If there are multiple possible types, Union should be used.
```py
def __eq__(self, other: Union[int, discord.Member, discord.interactions.Interaction]) -> bool:
        if isinstance(other, discord.interactions.Interaction):
            other = other.user

        if isinstance(other, discord.Member):
            # ...
        
        assert isinstance(other, self.__class__)
        return self.value == other.value
```

Functions should have 1 space between each other:
```py
def a(text: str) -> str:
    return text

def b(number: int) -> int:
    return number
```

## Files

Every file should have an empty line at the end. They do not show on GitHub, however.
