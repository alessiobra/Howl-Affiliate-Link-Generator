import interactions
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from interactions import slash_command, SlashContext
import sys
import random

# Replace these with your actual tokens and keys
DISCORD_TOKEN = ''
HOWL_API_KEY = ''
HOWL_API_URL = 'https://api.narrativ.com/api/v1/smart_links/'
one_user = False
ALLOWED_USER_ID = 99999999999  # Replace with your role ID

bot = interactions.Client(token=DISCORD_TOKEN)

@interactions.listen
async def on_ready():
    print(f'Logged in as {bot.me.name}')

@interactions.slash_command(
    name="generate_link",
    description="Generate an affiliate link",
    options=[
        interactions.SlashCommandOption(
            name="link",
            description="The link to convert",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ]
)

async def generate_link(ctx: interactions.SlashContext, link: str):
    # Check if the user has the required ID
    if one_user and ctx.author.id != ALLOWED_USER_ID:
        await ctx.send('You do not have permission to use this command.', ephemeral=True)
        return
    print(f'Received link: {link}')  # Log the received link
    affiliate_link = generate_affiliate_link(link)
    if affiliate_link:
        await ctx.send(f'{affiliate_link}')
    else:
        await ctx.send('Failed to generate affiliate link.')

def generate_affiliate_link(link):
    random_float_range = random.uniform(1, 9999999999)
    url = HOWL_API_URL
    headers = {
        'Authorization': f'NRTV-API-KEY {HOWL_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'url': link,
        'article_name': f'{random_float_range}',  # Replace with your actual article name
        'article_url': 'http://www.google.com',  # Replace with your actual article URL
        'article_publication_date': '2017-08-02T17:00:00Z',  # Current date and time in ISO format with timezone
        'exclusive_match_requested': True  # Optional, set to True if needed
    }
    
    # Setting up retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        print(f'Sending request to URL: {url} with data: {data}')  # Log the request details
        response = http.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f'Response received: {response.json()}')  # Log the response

        # Check for the correct field in the response
        response_data = response.json()
        smart_link_url = response_data['data'][0].get('smart_link_url')
        howl_link_url = response_data['data'][0].get('howl_link_url')

        # Return the correct URL
        if howl_link_url:
            return howl_link_url
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')
        if e.response is not None:
            print(e.response.json())  # Log detailed error response
        return None

bot.start()
