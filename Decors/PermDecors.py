import functools
import disnake
import EmbedPalette


def check_permissions(*perms):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: disnake.ApplicationCommandInteraction, *args, **kwargs):
            if not any([value for name, value in ctx.user.guild_permissions if name in perms]):
                await ctx.send(embed=disnake.Embed(
                    title="Ошибка выполнения команды",
                    description="Недостаточно прав!",
                    color=EmbedPalette.IMPORTANT
                ), ephemeral=True, delete_after=15)
                return
            await ctx.send(embed=disnake.Embed(
                title="Успешно выполнено!",
                color=EmbedPalette.SUCCESS
            ), ephemeral=True, delete_after=15)
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def check_roles(*roles):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx: disnake.ApplicationCommandInteraction, *args, **kwargs):
            if not [role for role in ctx.user.roles if role.id in roles]:
                await ctx.send(embed=disnake.Embed(
                    title="Ошибка выполнения команды",
                    description="Недостаточно прав!",
                    color=EmbedPalette.IMPORTANT
                ), ephemeral=True, delete_after=15)
                return
            await ctx.send(embed=disnake.Embed(
                title="Успешно выполнено!",
                color=EmbedPalette.SUCCESS
            ), ephemeral=True, delete_after=15)
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator
