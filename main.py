import os
import json
import requests
from keep_alive import keep_alive
import discord

API_URL = "https://api-inference.huggingface.co/models/"

intents=discord.Intents.default()
intents.message_content=True #NOQA 
client = discord.Client(intents=intents)
api_endpoint = API_URL + 'wizaye/DialoGPT-small-Rick-V1'

# Retrieve the secret API token from the system environment
huggingface_token = os.environ['HUGGINGFACE_TOKEN']
# Format the header in our request to Hugging Face
request_headers = {'Authorization': 'Bearer {}'.format(huggingface_token)}


def query(payload):
    """
    Make a request to the Hugging Face model API
    """
    data = json.dumps(payload)
    response = requests.post(api_endpoint, headers=request_headers, data=data)
    ret = json.loads(response.content.decode('utf-8'))
    return ret


@client.event
async def on_ready():
    # Print out information when the bot wakes up
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    # Send a request to the model without caring about the response
    # Just so that the model wakes up and starts loading
    query({'inputs': {'text': 'Hello!'}})


@client.event
async def on_message(message):
    """
    This function is called whenever the bot sees a message in a channel
    """

    # Ignore the message if it comes from the bot itself
    if message.author.id == client.user.id:
        return

    # Check if the message content is empty or just whitespace
    # if not message.content.strip():
    #     await message.channel.send("Please provide a non-empty input.")
    #     return

    # Form query payload with the content of the message
    payload = {'inputs': {'text': message.content}}

    # While the bot is waiting on a response from the model,
    # Set its status as typing for user-friendliness
    async with message.channel.typing():
        response = query(payload)

    bot_response = response.get('generated_text',[])

    # Check if bot_response is empty or ill-formed
    if not bot_response:
        if 'error' in response:
            bot_response = f'Error: {response["error"]}'
        else:
            bot_response = 'Hmm... something is not right.'

    # Send the model's response to the Discord channel
    await message.channel.send(bot_response)


def main():
    # DialoGPT
    keep_alive()
    client.run(os.environ['DISCORD_TOKEN'])


if __name__ == '__main__':
    main()
