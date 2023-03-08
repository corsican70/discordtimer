import datetime, discord, logging, os, sys, time
from timeit import default_timer as timer
from discord.ext import tasks

if len(sys.argv) < 2:
    print('Usage: %s TOKEN' % sys.argv[0])
    sys.exit()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

max_hours = 12
sTime = None
eTime = None
offset = 0
timerChannel = None

discord.utils.setup_logging(level=logging.INFO, root=False)

@client.event
async def on_ready():
    check_autostop.start()

@client.event
async def on_message(message):
    global sTime
    global eTime
    global offset
    global timerChannel
    print("MESSAGE: %s" % message.content)
    if message.content.startswith('~set '):
        params = message.content.split()
        if len(params) != 3:
            await message.channel.send("USAGE: ~set [timername] [timestamp], timestamp is HH:MM:SS, MM:SS or number of seconds")
            return
        timestamp = params[2]
        if ':' in timestamp:
            try:
                x = time.strptime(timestamp,'%H:%M:%S')
                offset = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
            except ValueError:
                try:
                    x = time.strptime(timestamp,'%M:%S')
                    offset = datetime.timedelta(hours=0,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
                except ValueError:
                    await message.channel.send("USAGE: ~set [timername] [timestamp], timestamp is HH:MM:SS, MM:SS or number of seconds")
                    return
        else:
            offset = int(timestamp)
        response = '{} has started with {} seconds already elapsed.'.format(params[1].capitalize(), offset)
        await message.channel.send(response)
        sTime = timer()
        timerChannel = message.channel.id

    if message.content.startswith('~start'):
        param = message.content[7:]
        if timerChannel:
            response = '{} already running. Stop {} and try again.'.format(param.capitalize(), param)
            await message.channel.send(response)
        else:
            response = 'COUNTDOWN HAS STARTED. HIT PLAY AT 🚨  🇬   🇴  🚨'
            await message.channel.send(response)
            time.sleep(1)
            response = '5️⃣'
            await message.channel.send(response)
            time.sleep(1)
            response = '4️⃣'
            await message.channel.send(response)
            time.sleep(1)
            response = '3️⃣'
            await message.channel.send(response)
            time.sleep(1)
            response = '2️⃣'
            await message.channel.send(response)
            time.sleep(1)
            response = '1️⃣'
            await message.channel.send(response)
            time.sleep(1)
            response = '🚨  🇬  🇴    🚨'
            await message.channel.send(response)
            response = '{} has started.'.format(param.capitalize())
            await message.channel.send(response)
            sTime = timer()
            offset = 0
            timerChannel = message.channel.id

    if message.content.startswith('~stop'):
        param = message.content[6:]
        eTime = timer() + offset
        elapsedSeconds = eTime - sTime
        elapsed = str(datetime.timedelta(seconds=int(elapsedSeconds)))
        response = '{} has stopped after {} elapsed'.format(param.capitalize(), elapsed)
        await message.channel.send(response)
        sTime = time.perf_counter()
        offset = 0
        timerChannel = None

    if message.content.startswith('~check'):
        param = message.content[7:]
        if not timerChannel:
            response = 'No {} is currently running.'.format(param)
            await message.channel.send(response)
        else:
            eTime = timer() + offset
            elapsedSeconds = eTime - sTime
            elapsed = str(datetime.timedelta(seconds=int(elapsedSeconds)))
            response = 'Current elapsed time {}'.format(elapsed)
            await message.channel.send(response)

@tasks.loop(minutes=30.0)
async def check_autostop():
    global sTime
    global eTime
    global offset
    global timerChannel
    if not timerChannel:
        return
    eTime = timer() + offset
    elapsedSeconds = eTime - sTime
    print("elapsedSeconds: %s" % str(elapsedSeconds))
    if elapsedSeconds >= (max_hours * 3600):
        channel = client.get_channel(timerChannel)
        response = 'Timer automatically stopped after {} hours elapsed'.format(int(elapsedSeconds/3600))
        await channel.send(response)
        sTime = time.perf_counter()
        offset = 0
        timerChannel = None

client.run(sys.argv[1])

