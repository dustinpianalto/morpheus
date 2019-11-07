import inspect
from argparse import ArgumentParser
from typing import Optional


class Command:
    def __init__(self, function: callable, extension: str = None):
        if not callable(function):
            raise RuntimeError('The function to make a command from must be a callable')

        if not inspect.iscoroutinefunction(function):
            raise RuntimeError('The function to make a command from must be a coroutine')

        self.extension = extension
        self.signature = inspect.signature(function)
        self.parser: ArgumentParser = self.process_parameters(self.signature.parameters)
        self.function: callable = function

    def process_parameters(self, params: dict) -> ArgumentParser:
        iterator = iter(params.items())

        if self.extension:
            try:
                next(iterator)
            except StopIteration:
                raise RuntimeError('self is missing from signature')

        try:
            next(iterator)  # the next param should be ctx
        except StopIteration:
            raise RuntimeError('ctx is missing from signature')

        parser = ArgumentParser()
        for name, param in iterator:
            param: inspect.Parameter
            if param.kind == param.VAR_POSITIONAL:
                nargs = '+'
            else:
                nargs = 1

            if param.annotation == param.empty:
                param_type = str
            else:
                param_type = param.annotation

            if param.kind == param.KEYWORD_ONLY:
                name = '--' + name

            if param.default == param.empty:
                parser.add_argument(name, nargs=nargs, type=param_type)
            else:
                parser.add_argument(name, nargs=nargs, type=param_type, default=param.default)

        return parser

    async def invoke(self, ctx, args_list):
        iterator = iter(self.signature.parameters.items())

        if self.extension:
            try:
                next(iterator)
            except StopIteration:
                raise RuntimeError('self is missing from signature')

        try:
            next(iterator)  # the next param should be ctx
        except StopIteration:
            raise RuntimeError('ctx is missing from signature')

        args = []
        kwargs = {}
        if args_list:
            params, ctx.extra_params = self.parser.parse_known_args(args_list)

            for key, value in iterator:
                value: inspect.Parameter
                if value.kind == value.VAR_POSITIONAL or value.kind == value.POSITIONAL_OR_KEYWORD:
                    args.extend(params.__dict__[key])
                else:
                    kwargs[key] = params.__dict__[key]
            await self.function(ctx, *args, **kwargs)
        else:
            await self.function(ctx)
