### Purpose of this project:

In Ukraine due to power outages a lot of people use internet from their cellphones.
Yesterday i figured out that my friend lost 20GB of available traffic without noticing.
I'm also often times visit Vodafone iOS app to check the available data. But it's very slow (up to 20 each time, since in order to see the interned traffic available one has to wait for the entire app to load which takes time).

Also I wanted to explore raw Telegram Bot API without using any frameworks. Just out of curiosity and for fun.

I know getting headers for non-technical user might be complicated, but I can help you – reach out to me in Telegram @kopyl.

I might record the video on how to set this thing up for a non-technical people, but maybe later.

### Prerequisites:

You have to know how to create your own Telegram bot with Botfather and exctract headers from Vodafone dashboard logged in (https://my.vodafone.ua/primary/main/home).

### Do before launching this:

1. Launch bot that you want to send you updates. Send at least /start.

### Run with Docker:

You can find already built Docker image at https://hub.docker.com/repository/docker/kopyl/vodafone-traffic-monitor/general, so you don't need to build (or download) to run it, just run the `docker run...` command from the steps below and enjoy:

1. Prepare headers string in base64 to put between `HEADERS='` and `'`
2. Prepare Telegram bot token to put between `BOT_TOKEN='` and `'`
3. Prepare your Telegram user ID
4. Run the build command:
   `docker run --env HEADERS='' --env BOT_TOKEN='' --name vodafone-traffic-monitor -d kopyl/vodafone-traffic-monitor`
   (you can replace the image name from `kopyl/vodafone-traffic-monitor` to whatever you want)

You might want to specify the amount of seconds the bot is going to wait between fetching the data from Vodafone with `SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS` environment variable. The default is 300 seconds.

Here is an example of how you can that base64 string in Python:

```
import base64


headers = {
    "Sec-Fetch-Site": "same-site",
}
json_bytes = base64.encodebytes(json.dumps(headers).encode())
json_bytes.decode()
```

### If you want to build it yourself:

`docker build --platform=linux/amd64 -t kopyl/vodafone-traffic-monitor .`
(you can replace the image name from `kopyl/vodafone-traffic-monitor` to whatever you want)

### Example docker run command:

```
docker run --env HEADERS='...' --env BOT_TOKEN='...' --name vodafone-traffic-monitor -d kopyl/vodafone-traffic-monitor
```

(... shall be your own data)

---

### How to deploy it on Azure:

##### 1. Create Azure container registry

(you might want to use Dockerhub for that, but i've been facing some rate limiting from either Dockerhub or Azure or both, so I decided that it's better to stick to Azure)

```
az acr create --resource-group test_group \
  --name vodafonetrafficmonitorregistry --sku Basic
```

(you might want to replace the name `vodafonetrafficmonitorregistry` with yours and make sure you specify the resource group you have here and in all the places below)

##### 2. Push the image to the registry

1. Login with `az acr login --name vodafonetrafficmonitorregistry` (keep the same name)
2. Tag with `docker tag kopyl/vodafone-traffic-monitor vodafonetrafficmonitorregistry.azurecr.io/vodafone-traffic-monitor` (to ensure stable versions each deployment, tag each new build with the new version like `vodafonetrafficmonitorregistry.azurecr.io/vodafone-traffic-monitor:4`)
3. And finally push to the registry: `doker push vodafonetrafficmonitorregistry.azurecr.io/vodafone-traffic-monitor`

##### 3. Now you need credentials for deploying the container to Azure Container instances service

```
az acr update -n vodafonetrafficmonitorregistry --admin-enabled true
az acr credential show --name vodafonetrafficmonitorregistry
```

##### 4. Now let's create a container:

```
az container create \
    --resource-group test_group \
    --name vodafone-traffic-monitor \
    --image vodafonetrafficmonitorregistry.azurecr.io/vodafone-traffic-monitor:6 \
    --os-type Linux \
    --cpu 1 \
    --memory 2 \
    --registry-username vodafonetrafficmonitorregistry \
    --registry-password ... \
    --environment-variables HEADERS='...' BOT_TOKEN='...' PYTHONUNBUFFERED=1
```

(Replace all ... with real data)

##### 5. Verify container is created

```
az container show \
    --resource-group test_group \
    --name vodafone-traffic-monitor \
    --query "{FQDN:ipAddress.fqdn,ProvisioningState:provisioningState}" \
    --out table
```

##### 6. Make sure you have all your environment variables set:

Verify it with

```
az container show \
    --resource-group test_group \
    --name vodafone-traffic-monitor \
    --query "containers[0].environmentVariables"
```

##### Now let's sit back end watch the logs:

```
az container attach \
    --resource-group test_group
    --name vodafone-traffic-monitor
```

##### If you ever want to delete it, feel free:

`az container delete --resource-group test_group --name vodafone-traffic-monitor`
