import requests
import json
from discord_webhook import DiscordWebhook, DiscordEmbed
import pyfiglet
import time
import os

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}


def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


def get_server_data(code):
    url = f"https://servers-frontend.fivem.net/api/servers/single/{code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        
        data_bytes = response.content

        
        with open("server_data.json", "wb") as file:
            file.write(data_bytes)

        return data_bytes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None


def extract_important_data(data_bytes):
    try:
        data = json.loads(data_bytes.decode("utf-8"))
        data_info = data.get("Data", {})
        vars_info = data_info.get("vars", {})

        important_data = {
            "server": data_info.get("server", "N/A"),
            "discord_link": vars_info.get("Discord", "N/A"),
            "ownerName": data_info.get("ownerName", "N/A"),
            "ownerProfile": data_info.get("ownerProfile", "N/A"),
            "ownerAvatar": data_info.get("ownerAvatar", "N/A"),
            "lastSeen": data_info.get("lastSeen", "N/A"),
            "iconVersion": data_info.get("iconVersion", "N/A"),
            "connectEndPoints": ", ".join(data_info.get("connectEndPoints", [])),
            "upvotePower": data_info.get("upvotePower", "N/A"),
            "burstPower": data_info.get("burstPower", "N/A"),
            "support_status": data_info.get("support_status", "N/A"),
            "svMaxclients": data_info.get("svMaxclients", "N/A"),
            "hostname": data_info.get("hostname", "N/A"),
        }

        return important_data
    except (KeyError, ValueError) as e:
        print(f"Error extracting important data: {e}")
        return None


def extract_players_data(data_bytes):
    try:
        data = json.loads(data_bytes.decode("utf-8"))
        players = data.get("Data", {}).get("players", [])

        print("Raw players data:", players)  

        player_data = []
        for player in players:
            player_info = {
                "name": player.get("name", "N/A"),
                "discord_id": next(
                    (
                        id
                        for id in player.get("identifiers", [])
                        if id.startswith("discord:")
                    ),
                    "N/A",
                ).replace("discord:", ""),
                "steam_id": next(
                    (
                        id
                        for id in player.get("identifiers", [])
                        if id.startswith("steam:")
                    ),
                    "N/A",
                ).replace("steam:", ""),
            }
            player_data.append(player_info)

        return player_data
    except (KeyError, ValueError) as e:
        print(f"Error extracting player data: {e}")
        return None


def send_to_discord(data, webhook_url):
    webhook = DiscordWebhook(url=webhook_url)
    embed = DiscordEmbed(
        title="Server Information",
        description=f"Owner: {data.get('ownerName', 'N/A')}",
        color="03b2f8",
    )

    embed.add_embed_field(name="Server", value=data.get("server", "N/A"))
    embed.add_embed_field(name="Discord Link", value=data.get("discord_link", "N/A"))
    embed.add_embed_field(name="Owner Name", value=data.get("ownerName", "N/A"))
    embed.add_embed_field(name="Owner Profile", value=data.get("ownerProfile", "N/A"))
    embed.add_embed_field(name="Owner Avatar", value=data.get("ownerAvatar", "N/A"))
    embed.add_embed_field(name="Last Seen", value=data.get("lastSeen", "N/A"))
    embed.add_embed_field(name="Icon Version", value=data.get("iconVersion", "N/A"))
    embed.add_embed_field(
        name="Connect Endpoints", value=data.get("connectEndPoints", "N/A")
    )
    embed.add_embed_field(name="Upvote Power", value=data.get("upvotePower", "N/A"))
    embed.add_embed_field(name="Burst Power", value=data.get("burstPower", "N/A"))
    embed.add_embed_field(
        name="Support Status", value=data.get("support_status", "N/A")
    )
    embed.add_embed_field(name="Max Clients", value=data.get("svMaxclients", "N/A"))
    embed.add_embed_field(name="Hostname", value=data.get("hostname", "N/A"))

    webhook.add_embed(embed)
    response = webhook.execute()
    return response

def send_players_to_discord(players, webhook_url):
    for player in players:
        print(f"Sending player data for {player['name']} to Discord")

        
        webhook = DiscordWebhook(url=webhook_url)

        embed = DiscordEmbed(
            title=f"Player Information - {player['name']}", color="03b2f8"
        )
        embed.add_embed_field(name="Name", value=player["name"])
        embed.add_embed_field(name="Discord ID", value=player["discord_id"])
        embed.add_embed_field(name="Steam ID", value=player["steam_id"])

        webhook.add_embed(embed)
        response = webhook.execute()

        # Remove or comment out the following lines to stop printing the status code and response
        # if response.status_code != 204:
        #     print(f"Webhook status code {response.status_code}: {response.text}")

        # Delay to avoid hitting rate limits
        time.sleep(2)  # Adjust this as needed to avoid rate limiting

    return response



if __name__ == "__main__":
    
    fivem_sniper_banner = pyfiglet.figlet_format("FiveM Sniper", font="slant")
    print(f"\033[91m{fivem_sniper_banner}\033[0m")
    print("#lfillaz ~ https://github.com/lfillaz ")

    config = load_config()
    webhook_url = config.get("webhook_url", "")

    while True:
        
        choice = input("Choose data type to send (1: Server Info, 2: Player Info): ")

        
        code = input("Please enter the server code: ")

        
        print("-------------------------")
        time.sleep(3)
        print("\033[F" + " " * 25 + "\033[F")  

        
        if not webhook_url:
            webhook_url = input("Please enter the Discord webhook URL: ")
            config["webhook_url"] = webhook_url
            save_config(config)

        
        try:
            data_bytes = get_server_data(code)
            if data_bytes:
                if choice == "1":
                    
                    important_data = extract_important_data(data_bytes)
                    if important_data:
                        response = send_to_discord(important_data, webhook_url)
                        print("Data sent to the webhook successfully.")
                    else:
                        print("No important data was found.")
                elif choice == "2":
                    
                    players_data = extract_players_data(data_bytes)
                    if players_data:
                        num_players = len(players_data)
                        print(f"Found {num_players} players.")
                        send = input("Do you want to send the player data to the webhook? (y/n): ")
                        if send.lower() == "y":
                            send_players_to_discord(players_data, webhook_url)
                        else:
                            print("Player data sending canceled.")
                    else:
                        print("No player data found.")
                else:
                    print("Invalid choice. Please select 1 or 2.")
            else:
                print("No data found for the provided code.")
        except Exception as e:
            print(f"An error occurred while fetching data: {e}")

        
        new_code = input("Please enter a new server code or type 'exit' to quit: ")
        if new_code.lower() == "exit":
            break
        else:
            code = new_code
