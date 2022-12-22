from sys import platform
BOT_TOKEN = "?"

TEST_BOT_TOKEN = "?"

CID = "?"
SECRET = "?"
YANDEX_TOKEN = "?"


PATH_TO_SERVERS = ""
PATH_TO_COGS = ""
PATH_TO_PREFIXES = ""
PATH_TO_MEM = ""
PATH_TO_LEVELS_DB = ""
if platform == 'win32':
    PATH_TO_SERVERS = "D:/Python/Umi-Pycharm/bot/cogs/servers/"
    PATH_TO_COGS = "bot/cogs/*.py"
    PATH_TO_PREFIXES = "bot/cogs/prefixes.json"
    PATH_TO_MEM = "D:/Python/Umi-Pycharm/bot/cogs/what_mem/"
    PATH_TO_LEVELS_DB = "D:/Python/Umi-Pycharm/bot/cogs/levels.db"
else:
    PATH_TO_SERVERS = "/home/ubuntu/umi/bot/cogs/servers/"
    PATH_TO_COGS = "./home/ubuntu/umi/bot/cogs/*.py"
    PATH_TO_PREFIXES = "/home/ubuntu/umi/bot/cogs/prefixes.json"
    PATH_TO_MEM = "/home/ubuntu/umi/bot/cogs/what_mem/"
    PATH_TO_LEVELS_DB = "/home/ubuntu/umi/bot/cogs/levels.db"


GUILDS = []
