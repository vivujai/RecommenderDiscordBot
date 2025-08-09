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
  api_key=f"{API_KEY}"
)
  

class AI(commands.Cog, name="ai"):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.response = ""


    async def AiSession(self, message):
        try:
            # Run the streaming call in a thread
            self.response = await asyncio.to_thread(
                client.chat.completions.create,
                model="deepseek/deepseek-r1-0528:free",
                messages=[
                    {
                        "role": "user",
                        "content": f"{message}, \n ONLY USE ENGLIHS",
                    }
                ],
                stream=False
            )

            # Replace deepseek with Monkey Bot
            if "deepseek-r1" in self.response.lower() or "deepseek" in self.response.lower():
                self.response = self.response.replace("DeepSeek-R1", "Monkey Bot")
                self.response = self.response.replace("DeepSeek", "Monkey Bot")

            self.response = self.response.strip()
            if len(self.response) <= 20:
                self.response = "My name is Monkey Bot! (Powered by DeepSeek-R1)"
            else:
                self.response = (
                    f"___**You**___:\n {message}\n\n"
                    + "##**MonkeyBot**##: \n"
                    + self.response
                    + "\n\n (Powered by DeepSeek-R1)"
                )
        except Exception as e:
            self.response = f"An error occurred: {str(e)}"

        print("AI Session completed.")

    @commands.hybrid_command(name="askai", description="Ask the AI a question.")
    async def AskAi(self, context: Context, message: str) -> None:
        if context.interaction:
            await context.interaction.response.defer()
        # Send initial message
        sent = await context.send("MonkeyBot is thinking...")

        try:
            response = ""
            chunk_size = 15
            chunk_list =[self.response[chunk_start:chunk_start+chunk_size] for chunk_start in range(0, len(self.response), chunk_size)]
            for chunk in chunk_list:
                    response += chunk
                    await sent.edit(content=response)
        except Exception as e:
            await sent.edit(content=f"An error occurred: {str(e)}")


async def setup(bot) -> None:
    await bot.add_cog(AI(bot))