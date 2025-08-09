import discord
from discord.ext import commands
from discord.ext.commands import Context
import random
import math


class Earn(commands.Cog, name="earn"):
    def __init__(self, bot): 
        self.bot = bot
        self.data_cog = self.bot.get_cog("user")


    async def gamble(self, user_id: int, amount: int) -> str:
        """Gamble a certain amount of balance"""
        if amount <= 0:
            return "You cannot gamble a non-positive amount."
        balance = await self.data_cog.get_balance(user_id)
        level = await self.data_cog.get_level(user_id)
        if level < 5:
            return "You need to be at least level 5 to gamble."
        if balance < int(amount):
            return "You do not have enough balance to gamble this amount."
        if int(amount) > math.floor(5000 * ((level*level*level) - level * level)/2):
            return "You cannot gamble more than 5000 coins at once."
        
        win = random.choice([True, False, False])

        if win:
            winnings = amount * 2
            await self.data_cog.add_balance(user_id, winnings)
            return f"You won {winnings} coins!"
        
        else:
            await self.data_cog.add_balance(user_id, -amount)
            return f"You lost {amount} coins. Better luck next time!"
        
    async def work(self, user_id: int) -> str:
        """Work to earn money"""
        level = await self.data_cog.get_level(user_id)
        print(level)
        earnings = random.randint(30 * level, 40 * level)

        await self.data_cog.add_balance(user_id, earnings)
        return f"You worked hard and earned {earnings} coins!"
    
    async def crime(self, user_id: int) -> str:
        """Commit a crime or get caught"""
        level = await self.data_cog.get_level(user_id)
        success_number = 245 * (1.5 ** level)
        success = random.randint(1, 1000) <= success_number

        if success:
            earnings = random.randint(200 * level, 289 * level)
            await self.data_cog.add_balance(user_id, earnings)
            return f"You successfully committed a crime and earned {earnings} coins!"
        else:
            penalty = random.randint(150 * level, 400 * level)
            await self.data_cog.add_balance(user_id, -penalty)
            return f"You got caught committing a crime and lost {penalty} coins!"
        
    @commands.hybrid_command(name="gamble", description="Gamble with a 1/3 chance to double your money.")
    async def Gamble(self,context:Context, amount) -> None:
        await context.send(await self.gamble(context.author.id, amount=amount))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))

    @commands.hybrid_command(name="work", description="Work to earn money.")
    async def Work(self, context: Context) -> None:
        await context.send(await self.work(context.author.id))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))

    @commands.hybrid_command(name="crime", description="Commit a crime to earn money, but you might get caught.")
    async def Crime(self,context:Context) -> None:
        await context.send(await self.crime(context.author.id))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))


async def setup(bot) -> None:
    # Load the UserData cog first if it's not already loaded
    if not bot.get_cog("user"):
        await bot.load_extension("cogs.user")  # Adjust if your path is different

    # Now safely add the Earn cog
    await bot.add_cog(Earn(bot))
