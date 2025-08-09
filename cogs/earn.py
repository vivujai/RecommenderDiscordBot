import json
import discord
from discord.ext import commands
from discord.ext.commands import Context
import random
import math

class UserData(commands.Cog, name="user"):
    def __init__(self, bot):
        self.bot = bot
        

    async def add_user_data(self, user_id: int):
        """Add a user to the data file"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
        with open("UserData/data.json", "w") as datafile:
            if str(user_id) not in data:
                profile = {
                    "inventory": [],
                    "balance": 0,
                    "xp": 0,
                    "level": 1
                }
                data.update({str(user_id): profile})
                json.dump(data, datafile, indent=4)
    
    async def add_balance(self, user_id: int, amount: int):
        """Add balance to a user"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
        with open("UserData/data.json", "w") as datafile:
            if str(user_id) in data:
                data[str(user_id)]["balance"] += amount
                json.dump(data, datafile, indent=4)
    
    async def get_balance(self, user_id: int) -> int:
        """Get the balance of a user"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
            if str(user_id) in data:
                return data[str(user_id)]["balance"]
            else:
                return 0
            
    async def get_inventory(self, user_id: int) -> int:
        """Get the inventory of a user"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
            if str(user_id) in data:
                return data[str(user_id)]["inventory"]
            else:
                return 0
            
    async def get_level(self, user_id: int) -> int:
        """Get the level of a user"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
            if str(user_id) in data:
                return data[str(user_id)]["level"]
            else:
                return 0
            
    async def get_xp(self, user_id: int) -> int:
        """Get the xp of a user"""
        with open("UserData/data.json", "r") as datafile:
            data = json.load(datafile)
            if str(user_id) in data:
                return data[str(user_id)]["xp"]
            else:
                return 0
            
    async def profile_embed(self, user_id: int, pfp) -> discord.Embed:
        """Create an embed for the user's profile"""
        balance = f"{await self.get_balance(user_id)} :coin:"
        inventory = await self.get_inventory(user_id)
        status = f"Level: {await self.get_level(user_id)} :credit_card:\nXp: {await self.get_xp(user_id)} :credit_card:"
        embed = discord.Embed(
            title="Profile", color=0xBEBEFE
        )    
        embed.add_field(
            name="Status".capitalize(), value=status, inline=False
        )
        embed.add_field(
            name="Balance".capitalize(), value=balance, inline=False
        )
        inventory_text = ""
        for item in inventory:
            if inventory.index(item) != len(inventory) - 1:
                inventory_text += f"{item}"
            else:
                inventory_text += f"{item}\n"
        if not inventory_text:
            inventory_text = "No items in inventory."
        embed.add_field(
            name="Inventory".capitalize(), value=inventory_text, inline=False
        )
        embed.set_thumbnail(url=pfp)
        embed.set_footer(text=f"ID: {user_id}")

        return embed
            
    @commands.hybrid_command(name="register", description="Register yourself with a profile.")
    async def Register(self,context:Context) -> None:
        await self.add_user_data(context.author.id)
        embed = await self.profile_embed(context.author.id, context.author.display_avatar.url) 
        await context.send("You have been registered!")
        await context.send(embed=embed)

    @commands.hybrid_command(name="profile", description="View your profile.")
    async def Profile(self, context: Context) -> None:
        embed = await self.profile_embed(context.author.id, context.author.display_avatar.url)

        await context.send(embed=embed)

class Earn(commands.Cog, name="earn"):
    def __init__(self, bot): 
        self.bot = bot


    async def gamble(self, user_id: int, amount: int) -> str:
        """Gamble a certain amount of balance"""
        if amount <= 0:
            return "You cannot gamble a non-positive amount."
        balance = self.data_cog.get_balance(user_id)
        level = self.data_cog.get_level(user_id)
        if level < 5:
            return "You need to be at least level 5 to gamble."
        if balance < amount:
            return "You do not have enough balance to gamble this amount."
        if amount > math.floor(5000 * ((level*level*level) - level * level)/2):
            return "You cannot gamble more than 5000 coins at once."
        
        win = random.choice([True, False, False])

        if win:
            winnings = amount * 2
            self.data_cog.add_balance(user_id, winnings)
            return f"You won {winnings} coins!"
        
    async def work(self, user_id: int) -> str:
        """Work to earn money"""
        level = self.data_cog.get_level(user_id)
        earnings = random.randint(30 * level, 40 * level)

        self.data_cog.add_balance(user_id, earnings)
        return f"You worked hard and earned {earnings} coins!"
    
    async def crime(self, user_id: int) -> str:
        """Commit a crime or get caught"""
        level = self.data_cog.get_level(user_id)
        success_number = 245 * (1.5 ** level)
        success = random.randint(1, 1000) <= success_number

        if success:
            earnings = random.randint(200 * level, 289 * level)
            self.data_cog.add_balance(user_id, earnings)
            return f"You successfully committed a crime and earned {earnings} coins!"
        
    @commands.hybrid_command(name="gamble", description="Gamble with a 1/3 chance to double your money.")
    async def Gamble(self,context:Context, amount) -> None:
        await context.send(self.gamble(context.author.id, amount=amount))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))

    @commands.hybrid_command(name="work", description="Work to earn money.")
    async def Work(self, context: Context) -> None:
        await context.send(await self.work(context.author.id))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))

    @commands.hybrid_command(name="crime", description="Commit a crime to earn money, but you might get caught.")
    async def Crime(self,context:Context) -> None:
        await context.send(self.crime(context.author.id))
        await context.send(embed=await self.data_cog.profile_embed(context.author.id, context.author.display_avatar.url))

async def setup(bot) -> None:
    await bot.add_cog(UserData(bot))

async def setup(bot) -> None:
    await bot.add_cog(Earn(bot))
