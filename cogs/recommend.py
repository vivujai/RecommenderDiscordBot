import pandas as pd
from surprise import Dataset, Reader, SVD
import discord
from discord.ext import commands
from fuzzywuzzy import process
import os
from openai import OpenAI
import asyncio


OPEN_AI_API_KEY = "YOUR OPENAI API KEY HERE!"
OPEN_AI_ASSISTANTS_ID = "YOUR OPENAI ASSISTANTS ID HERE!"




client = OpenAI(
    api_key=OPEN_AI_API_KEY, 
)
# Main recommend COG class
class Recommend(commands.Cog, name="recommend"):
    def __init__(self, bot) -> None:
        self.bot = bot

        # Initialize data
        self.data_file = 'ml-100k/u.data'
        self.user_file = 'ml-100k/u.user'
        self.item_file = 'ml-100k/u.item'

        # Load data
        self.user_id_mapping, self.username_mapping = self.load_users()
        self.movie_titles = self.load_movie_titles()
        self.data = self.load_data()
        
        # Initialize and train model
        self.algo = SVD()
        self.retrain_model()

    # Init function to load all registered users with the bot
    def load_users(self):
        if not os.path.exists(self.user_file):
            return {}, {}

        column_names = ['user_id', 'age', 'gender', 'occupation', 'discord_username', 'discord_user_id']
        user_data = pd.read_csv(self.user_file, delimiter='|', names=column_names)
        id_mapping = {str(row['discord_user_id']): str(row['user_id']) for _, row in user_data.iterrows() if pd.notna(row['discord_user_id'])}
        name_mapping = {row['discord_username']: str(row['user_id']) for _, row in user_data.iterrows() if pd.notna(row['discord_username'])}
        return id_mapping, name_mapping


    # Loads all movie titles from the data file
    def load_movie_titles(self):
        item_data = pd.read_csv(self.item_file, delimiter='|', encoding='ISO-8859-1', 
                                usecols=[0, 1], names=['movie_id', 'title'])
        return dict(zip(item_data['title'], item_data['movie_id']))

    # Loads all of the total data from the dataset
    def load_data(self):
        reader = Reader(line_format='user item rating timestamp', sep='\t', rating_scale=(1, 5))
        return Dataset.load_from_file(self.data_file, reader=reader)

    # Used to retrain the model when new data is added by users.
    def retrain_model(self):
        trainset = self.data.build_full_trainset()
        self.algo.fit(trainset)

    # Function to add a user to the data
    async def add_user(self, discord_user):
        discord_user_id = str(discord_user.id)
        discord_username = discord_user.name

        if discord_username in self.username_mapping:
            return False, f"Discord username '{discord_username}' is already registered with ID {self.username_mapping[discord_username]}."

        new_user_id = max([int(uid) for uid in self.user_id_mapping.values() if uid.isdigit()], default=0) + 1
        self.user_id_mapping[discord_user_id] = str(new_user_id)
        self.username_mapping[discord_username] = str(new_user_id)

        # Format the new user data to match the existing structure of the u.user file
        new_user_data = f"\n{new_user_id}|M|other|00000|{discord_username}|{discord_user_id}\n"

        with open(self.user_file, 'a') as f:
            f.write(new_user_data)

        return True, f"Discord username '{discord_username}' added with ID {new_user_id}."

    # Function to add a rating to a given movie name, requires a user to already be added to the database
    async def add_rating(self, discord_user, partial_movie_title: str, rating: float):
        discord_username = discord_user.name

        if discord_username not in self.username_mapping:
            return False, "Discord user not found. Please register first."

        user_id = self.username_mapping[discord_username]

        # Find the closest match for the movie title
        closest_match = process.extractOne(partial_movie_title, self.movie_titles.keys(), score_cutoff=70)
        if not closest_match:
            return False, "No close match found for the movie title. Please try again."

        movie_title, movie_id = closest_match[0], self.movie_titles[closest_match[0]]

        with open(self.data_file, 'a') as f:
            f.write(f"{user_id}\t{movie_id}\t{rating}\t0\n")

        # Update the data and retrain the model
        self.data = self.load_data()
        self.retrain_model()

        return True, f"Rating added for Discord user '{discord_username}' on movie '{movie_title}'."

    # Executes the discord command to add a user
    @commands.hybrid_command(
        name="add_user",
        description="Register the Discord user in the recommendation system.",
    )
    async def add_user_command(self, ctx: commands.Context):
        success, message = await self.add_user(ctx.author)
        await ctx.send(message)

    # Executes the discord command to add a rating, requires user to already be added
    @commands.hybrid_command(
        name="add_rating",
        description="Add a movie rating for a Discord user.",
    )
    async def add_rating_command(self, ctx: commands.Context, movie_title: str, rating: float):
        success, message = await self.add_rating(ctx.author, movie_title, rating)
        await ctx.send(message)

    # Executes the discord command to provide a recommendation to the user based on a movie they appear to be asking about, requires user to already be registered via the add_user command
    @commands.hybrid_command(
        name="recommend",
        description="Get recommendations based on username and partial movie name.",
    )
    async def recommend(self, ctx: commands.Context, *, partial_movie_name: str):
        discord_username = ctx.author.name

        if discord_username not in self.username_mapping:
            await ctx.send("Discord user not found. Please register first.")
            return

        user_id = self.username_mapping[discord_username]


        client = OpenAI(
            api_key=OPEN_AI_API_KEY, 
        )

        # Create a thread with the initial user message
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": partial_movie_name
                }
            ]
        )

        # Start a run with the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=OPEN_AI_ASSISTANTS_ID,
        )

        # Wait for the assistant's response
        assistant_response = await self.wait_for_response(thread.id)

        if not assistant_response:
            await ctx.send("No response from the assistant. Please try again later.")
            return


        print("OpenAI's response from the bot: ", assistant_response[0].text.value)
        
        # Process the assistant's response
        closest_match = process.extractOne(assistant_response[0].text.value, self.movie_titles.keys(), score_cutoff=70)
        if not closest_match:
            embed = discord.Embed(
                title="No close match found for the movie name. Please try again.",
                color=0xE02B2B,
            )
            await ctx.send(embed=embed)
            return

        movie_name, movie_id = closest_match[0], self.movie_titles[closest_match[0]]
        prediction = self.algo.predict(str(user_id), str(movie_id))

        embed = discord.Embed(
            title=f"Closest match: '{movie_name}'",
            description=f"Prediction for User '{discord_username}' on Movie '{movie_name}':\nRating Prediction: {prediction.est}",
            color=0x57F287,
        )

        await ctx.send(embed=embed)

    async def wait_for_response(self, thread_id):
        """Wait for the assistant's response in the given thread."""
        for _ in range(30):  # Wait up to 30 seconds for a response
            await asyncio.sleep(1)  # Correctly await the sleep
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            if len(messages.data) > 1:  # Assuming the first message is the user's and the second is the assistant's
                return messages.data[0].content  # Return the assistants content


async def setup(bot) -> None:
    await bot.add_cog(Recommend(bot))
