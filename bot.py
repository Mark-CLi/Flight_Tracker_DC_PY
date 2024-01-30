import os
import discord
from discord.ext import commands
import requests


# Discord Token Location
with open('Project_Location/Discord_Token.txt','r') as file:
    DISCORD_TOKEN = file.read().strip()

# Oly API Token Location
with open('Project_Location/Aeroapi_Token.txt','r') as file:
    aeroapi_key = file.read().strip()


# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable message content intent


# Initialize the Discord bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def flight(ctx, flight_number):
    try:
        # API URL
        env = 'aeroapi'
        url = f'https://{env}.flightaware.com/aeroapi/flights/{flight_number}'
        headers = {'x-apikey': aeroapi_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if 'flights' in data and data['flights']:
                # Prioritize current or recent flights
                current_flights = [flight for flight in data['flights'] if flight.get('actual_off')]
                flight_data = current_flights[0] if current_flights else data['flights'][0]

                # Create an embedded message
                embed = discord.Embed(title="Flight Information", color=0x1a1aff)

                # Flight Status and Aircraft Type
                embed.add_field(name="Flight Status", value=flight_data.get('status', 'No status info'), inline=False)
                embed.add_field(name="Aircraft Type", value=flight_data.get('aircraft_type', 'No aircraft type info'), inline=False)
                embed.add_field(name="Aircraft Registration", value=flight_data.get('registration', 'No Registration info found'), inline=False)

                # Origin and Destination
                origin_info = flight_data.get('origin', {})
                destination_info = flight_data.get('destination', {})
                origin_name = origin_info.get('name', 'No origin info')
                destination_name = destination_info.get('name', 'No destination info')
                origin_icao = origin_info.get('code_icao', 'No origin ICAO')
                destination_icao = destination_info.get('code_icao', 'No destination ICAO')
                embed.add_field(name="Origin", value=f"{origin_name} (ICAO: {origin_icao})", inline=True)
                embed.add_field(name="Destination", value=f"{destination_name} (ICAO: {destination_icao})", inline=True)

                # Departure and Arrival Times
                departure_time = flight_data.get('actual_off') if flight_data.get('actual_off') is not None else flight_data.get('scheduled_off', 'No departure info')
                arrival_time = flight_data.get('actual_on') if flight_data.get('actual_on') is not None else flight_data.get('scheduled_on', 'No arrival info')
                embed.add_field(name="Departure Time", value=departure_time, inline=True)
                embed.add_field(name="Arrival Time", value=arrival_time, inline=True)

                # Route
                route = flight_data.get('route', 'No route info')
                embed.add_field(name="Route", value=route, inline=False)

                await ctx.send(embed=embed)
            else:
                await ctx.send("No flight information found for this number.")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
async def metar(ctx, icao_id):
    try:
        # Constructing the API URL with specified options
        base_url = 'https://aviationweather.gov/data/api'
        endpoint = '/dataserver'
        url = f'{base_url}{endpoint}?requestType=retrieve&dataSource=metars&stationString={icao_id}&format=xml&mostRecent=true'
        response = requests.get(url)

        if response.status_code == 200:
            metar_data = response.text
            # Send the METAR data as a message
            await ctx.send(f"METAR Data for {icao_id}:\n```{metar_data}```")
        else:
            await ctx.send(f"Failed to retrieve METAR data for {icao_id}. Status Code: {response.status_code}")

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")




# Run the bot
bot.run(bot_token)
