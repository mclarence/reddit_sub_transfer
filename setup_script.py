#!/usr/bin/env python

"""This example demonstrates the flow for retrieving a refresh token.

In order for this example to work your application's redirect URI must be set to
http://localhost:8080.

This tool can be used to conveniently create refresh tokens for later use with your web
application OAuth2 credentials.

"""
import random
import socket
import sys
import configparser
import praw
import os
import time

def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()

def check_config():
    global config
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini'):
        return False
    config.read('config.ini')
    if config.has_section('REDDIT_AUTH'):
        if not config.has_option('REDDIT_AUTH', 'client_id'):
            return False
        if not config.has_option('REDDIT_AUTH', 'client_secret'):
            return False
    else:
        return False
    return True

def main():
    scopes = ["*"]
    if not check_config():
        """Provide the program's entry point when directly executed."""
        print(
            "Go here while logged into the account you want to create a token for: "
            "https://www.reddit.com/prefs/apps/"
        )
        print(
            "Click the create an app button. Put something in the name field and select the"
            " script radio button."
        )
        print("Put http://localhost:8080 in the redirect uri field and click create app")
        client_id = input(
            "Enter the client ID, it's the line just under Personal use script at the top: "
        )
        client_secret = input("Enter the client secret, it's the line next to secret: ")
        

    else:
        client_id=config['REDDIT_AUTH']['client_id']
        client_secret=config['REDDIT_AUTH']['client_secret']
        
        

    reddit = praw.Reddit(
        client_id=client_id.strip(),
        client_secret=client_secret.strip(),
        redirect_uri="http://localhost:8080",
        user_agent="praw_refresh_token_example",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")
    print(f"Now open this url in your browser and sign in with the account you want to transfer from: {url}")
    sys.stdout.flush()

    client, params = init_callback_server(state)

    refresh_token_one = reddit.auth.authorize(params["code"])
    send_message(client, f"1st Refresh token: {refresh_token_one}")

    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")
    print(f"Now open this url in your browser and sign in with the account you want to transfer to: {url}")
    sys.stdout.flush()

    time.sleep(2)
    client, params = init_callback_server(state)

    refresh_token_two = reddit.auth.authorize(params["code"])
    send_message(client, f"2nd Refresh token: {refresh_token_two}")

    config['REDDIT_AUTH'] = {
        'client_id': client_id.strip(),
        'client_secret': client_secret.strip(),
        'refreshtoken_one': refresh_token_one,
        'refreshtoken_two': refresh_token_two
    }
    with open ('config.ini', 'w') as configfile:
        config.write(configfile)

    print ("Done!")
    return 0

def init_callback_server(state):
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }

    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1
    return client, params

if __name__ == "__main__":
    sys.exit(main())