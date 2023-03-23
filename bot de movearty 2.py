import discord
from discord.ext import commands
import json

with open("config.json") as f:
    config = json.load(f)

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

servers = []

def is_owner(ctx):
    return ctx.author.id == config["owner_id"]

def is_server_added(ctx):
    return ctx.guild.id in servers

def is_valid_message(message):
    return "pub" not in message.content.lower()

def get_admission_request_message(ctx):
    server_name = ctx.guild.name
    invite_link = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(send_messages=True))
    return f"{server_name} souhaite être ajouté à la liste des serveurs. Invitation : {invite_link}"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def send(ctx, *, message):
    if is_owner(ctx):
        if is_valid_message(ctx.message):
            for channel in ctx.guild.text_channels:
                if channel != ctx.channel:
                    await channel.send(message)
        else:
            await ctx.send("Le message ne doit pas contenir de pub.")
    else:
        await ctx.send("Seul l'owner du serveur peut exécuter cette commande.")

@bot.command()
async def addserver(ctx):
    if ctx.author.id == config["my_id"]:
        if not is_server_added(ctx):
            servers.append(ctx.guild.id)
            await ctx.send(f"{ctx.guild.name} a été ajouté à la liste des serveurs autorisés.")
        else:
            await ctx.send("Ce serveur est déjà autorisé à envoyer des messages.")
    else:
        await ctx.send("Vous n'êtes pas autorisé à exécuter cette commande.")

@bot.command()
async def demande_admission(ctx):
    admission_request_message = get_admission_request_message(ctx)
    author = await bot.fetch_user(config["my_id"])
    await author.send(admission_request_message)
    await ctx.send("Votre demande d'admission a été envoyée.")

@bot.command()
async def cochannel(ctx, channel_id: int):
    if is_server_added(ctx):
        with open("channels.json") as f:
            channels = json.load(f)
        if channel_id not in channels:
            channels.append(channel_id)
            with open("channels.json", "w") as f:
                json.dump(channels, f)
            await ctx.send(f"Le salon <#{channel_id}> a été ajouté à la liste des salons.")
        else:
            await ctx.send("Ce salon est déjà ajouté à la liste.")
    else:
        await ctx.send("Ce serveur n'est pas autorisé à utiliser cette commande.")

bot.run(config["token"])
