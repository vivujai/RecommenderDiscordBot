import os
from dotenv import load_dotenv
from openai import OpenAI
import random
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands import Context

load_dotenv()

API_KEY = os.getenv("API_KEY")


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=f"{API_KEY}",
)
  

class AI(commands.Cog, name="ai"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.response = ""


    async def AiSession(self, message):
        try:
            completions = await asyncio.to_thread(
                client.chat.completions.create,  # pass not call
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {
                        "role": "user",
                        "content": f"{message}"
                    }
                ]
            )
            
            self.response = completions.choices[0].message.content
            if "deepseek-r1" in self.response.lower() or "deepseek" in self.response.lower():
                self.response = self.response.replace("DeepSeek-R1", "Monkey Bot")
                self.response = self.response.replace("DeepSeek", "Monkey Bot")
            self.response = self.response + "\n (Powered by DeepSeek-R1)"
        except Exception as e:
            self.response = f"An error occurred: {str(e)}"

    @commands.hybrid_command(name="askai", description="Ask the AI a question.")
    async def AskAi(self, context: Context, message: str) -> None:
        # Defer the response to avoid timeout
        if context.interaction:
            await context.interaction.response.defer()
        await self.AiSession(message=message)
        # Send the response after processing
        await context.send(self.response)


async def setup(bot) -> None:
    await bot.add_cog(AI(bot))