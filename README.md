### Purpose of this project:

In Ukraine due to power outages a lot of people use internet from their cellphones.
Yesterday i figured out that my friend lost 20GB of available traffic without noticing.
I'm also often times visit Vodafone iOS app to check the available data. But it's very slow (up to 20 each time, since in order to see the interned traffic available one has to wait for the entire app to load which takes time).

Also I wanted to explore raw Telegram Bot API without using any frameworks. Just out of curiosity and for fun.

I know getting headers for non-technical user might be complicated, but I can help you – reach out to me in Telegram @kopyl.

I might record the video on how to set this thing up for a non-technical people, but maybe later.

### Prerequisites:

You have to know how to create your own Telegram with Botfather and exctract headers from Vodafone dashboard logged in (https://my.vodafone.ua/primary/main/home).

### Do before launching this:

1. Launch bot that you want to send you updates. Send at least /start.

### Run with Docker:

You can find already built Docker image at https://hub.docker.com/repository/docker/kopyl/vodafone-traffic-monitor/general, so you don't need to build (or download) to run it, just run the `docker run...` command from the steps below and enjoy:

1. Prepare headers string to put between `HEADERS='` and `'`
2. Prepare Telegram bot token to put between `BOT_TOKEN='` and `'`
3. Prepare your Telegram user ID
   `docker run --env HEADERS='' --env BOT_TOKEN='' --name vodafone-traffic-monitor -d kopyl/vodafone-traffic-monitor`
   (you can replace the image name from `kopyl/vodafone-traffic-monitor` to whatever you want)

You might want to specify the amount of seconds the bot is going to wait between fetching the data from Vodafone with `SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS` environment variable. The default is 300 seconds.

### If you want to build it yourself:

`docker build -t kopyl/vodafone-traffic-monitor .`
(you can replace the image name from `kopyl/vodafone-traffic-monitor` to whatever you want)

### Example docker run command:

```
docker run --env HEADERS='{
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en",
    "Authorization": "Bearer ...",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Origin": "https://my.vodafone.ua",
    "Pragma": "no-cache",
    "Referer": "https://my.vodafone.ua/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "X-APP-VERSION": "1.0.0",
    "X-DEVICE-SOURCE": "MacOS",
    "profile": "COUNTERS-DATA",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}' --env BOT_TOKEN='...' --name vodafone-traffic-monitor -d kopyl/vodafone-traffic-monitor
```

(... shall be your own data)
