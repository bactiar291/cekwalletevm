import json
import os
import requests
import time
from rich.console import Console
from rich.style import Style
from rich.text import Text
from random import choice
from time import sleep

console = Console()

def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def display_neon_title():
    clear_terminal()
    title = " BACTIAR 291 "
    colors = ["#FF00FF", "#00FFFF", "#FFFF00", "#FF4500", "#00FF00", "#00BFFF"]
    styled_text = Text()
    
    for char in title:
        styled_text.append(char, style=Style(bold=True, color=choice(colors)))

    console.print("\n" * 2, end="")
    for i in range(len(styled_text)):
        console.print(styled_text[:i + 1], style="bold", justify="center", end="\r")
        sleep(0.1)

display_neon_title()

with open('config.json') as f:
    config = json.load(f)

required_keys = ["ETHERSCAN_KEY", "BSCSCAN_KEY", "POLYGONSCAN_KEY"]
for key in required_keys:
    if not config.get(key):
        console.print("❌ [red]Please provide valid API keys in config.json.[/red]")
        exit(1)

def get_wallet_info(address, api_key, network_name, api_url):
    try:
        response = requests.get(f"{api_url}{address}&apikey={api_key}")
        response_json = response.json()

        if response_json.get("status") == "1":
            return response_json["result"]
        else:
            console.print(f"❌ [red]Error: Unable to retrieve balance from {network_name}: {response_json['message']}[/red]")
            return None
    except Exception as e:
        console.print(f"❌ [red]Error fetching wallet info from {network_name}: {str(e)}[/red]")
        return None

def get_balances(wallet_address):
    eth_balance = get_wallet_info(wallet_address, config["ETHERSCAN_KEY"], "Etherscan", 
                                  "https://api.etherscan.io/api?module=account&action=balance&address=")
    bnb_balance = get_wallet_info(wallet_address, config["BSCSCAN_KEY"], "BscScan", 
                                  "https://api.bscscan.com/api?module=account&action=balance&address=")
    matic_balance = get_wallet_info(wallet_address, config["POLYGONSCAN_KEY"], "PolygonScan", 
                                    "https://api.polygonscan.com/api?module=account&action=balance&address=")

    eth_tokens = get_wallet_info(wallet_address, config["ETHERSCAN_KEY"], "Etherscan", 
                                 "https://api.etherscan.io/api?module=account&action=tokentx&address=")
    bnb_tokens = get_wallet_info(wallet_address, config["BSCSCAN_KEY"], "BscScan", 
                                 "https://api.bscscan.com/api?module=account&action=tokentx&address=")
    matic_tokens = get_wallet_info(wallet_address, config["POLYGONSCAN_KEY"], "PolygonScan", 
                                   "https://api.polygonscan.com/api?module=account&action=tokentx&address=")

    return {
        "eth": eth_balance,
        "bnb": bnb_balance,
        "matic": matic_balance,
        "eth_tokens": eth_tokens,
        "bnb_tokens": bnb_tokens,
        "matic_tokens": matic_tokens
    }

if __name__ == "__main__":
    wallet_address = input("🔑 Enter the wallet address to check: ").strip()

    balances = get_balances(wallet_address)
    if balances:
        console.print(f"🔍 Wallet Address: [cyan]{wallet_address}[/cyan]")
        eth_balance = int(balances['eth']) / 10**18 if balances['eth'] and balances['eth'].isdigit() else 0
        bnb_balance = int(balances['bnb']) / 10**18 if balances['bnb'] and balances['bnb'].isdigit() else 0
        matic_balance = int(balances['matic']) / 10**18 if balances['matic'] and balances['matic'].isdigit() else 0
        console.print(f"💰 [yellow]ETH Balance: {eth_balance} ETH[/yellow]")
        console.print(f"💵 [green]BNB Balance: {bnb_balance} BNB[/green]")
        console.print(f"🪙 [magenta]MATIC Balance: {matic_balance} MATIC[/magenta]")
        
        if balances["eth_tokens"]:
            for token in balances["eth_tokens"]:
                console.print(f"📈 ETH Token: [blue]{token['tokenName']}[/blue] - [cyan]{token['value']}[/cyan]")
        
        if balances["bnb_tokens"]:
            for token in balances["bnb_tokens"]:
                console.print(f"📈 BNB Token: [blue]{token['tokenName']}[/blue] - [cyan]{token['value']}[/cyan]")
        
        if balances["matic_tokens"]:
            for token in balances["matic_tokens"]:
                console.print(f"📈 MATIC Token: [blue]{token['tokenName']}[/blue] - [cyan]{token['value']}[/cyan]")
    else:
        console.print("❌ [red]No information available to display.[/red]")
