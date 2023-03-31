# Description

Bing chat Telegram bot implemented in Python that utilizes unofficial [EdgeChat](https://github.com/acheong08/EdgeGPT) API

## Known issues

- Different people will use the same conversation

## Screenshot

![](assets/screenshot.png)

# Setup

## Requirements

- python 3.8+
- A Microsoft Account with early access to http://bing.com/chat (Required)

  ## Checking access (Required)

- Install the latest version of Microsoft Edge
- Open http://bing.com/chat
- If you see a chat feature, you are good to go

 ## Getting authentication (Required)

- Install the cookie editor extension for [Chrome](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)
- Go to `bing.com`
- Open the extension
- Click "Export" on the bottom right (This saves your cookies to clipboard)
- Paste your cookies into a file `cookies.json`. The format of json refers to `cookie.exaple.json`(The middle field is omitted)

## Install requirements

```shell
pip install -r requirements.txt
```

## Set environment variables

```shell
export BOT_TOKEN='REPLACE YOUR BOT TOKEN'
export ALLOWED_USER_IDS='XXXXXXXXX,XXXXXXXX,XXXXXXXX'
```

## Run

```shell
python bing.py
```






