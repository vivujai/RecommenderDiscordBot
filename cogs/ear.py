import json
import discord
from discord.ext import commands
from discord.ext.commands import Context

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


async def setup(bot) -> None:
    await bot.add_cog(UserData(bot))