# 🔌 Cordcutter

Cordcutter is a nextcord extension that implements the circuit breaker design pattern for application commands.

Cordcutter works by watching for errors in your application commands and once the error threshold is reached _(breaker tripped)_, it will disable the command for a set period of time. Once the cool-down period is over, the command will be re-enabled _(breaker reset)_.

Cordcutter currently does not implement an semi-stable circuit breaker (half-open / half-tripped state), but this is a planned feature.

For more information on the circuit breaker design pattern, see [this wikipedia article](https://en.wikipedia.org/wiki/Circuit_breaker_design_pattern).

## Installation

Cordcutter is currently in development and is not yet available on PyPI. You can install it from Git using pip:

```bash
pip install git+https://github.com/teaishealthy/cordcutter.git
```

## Usage

Simply import the `Cordcutter` class from `cordcutter` and pass your `nextcord.Client` instance to it.

```py
from cordcutter import Cordcutter
# <snip>
cordcutter = Cordcutter(client)
```

### Configuration

You can configure when the breaker trips and how long it stays tripped by passing the `threshold` and `reset_after` parameters to the `Cordcutter` constructor:

```py
Cordcutter(
    client,
    threshold = 3,
    reset_after = timedelta(minutes=5)
)
```
