from sys import platform
BOT_TOKEN = "NzQ1NzU3Nzk5ODAzMzg4MDM2.G63LcA.nImnva0qn9FZ30Zkv20xr1LIkaAPZj5Eymr6Xc"

TEST_BOT_TOKEN = "OTg4MjAwMDU4NTY4NzM2Nzg5.GGTR8i.C6sOLi9OVlDnPOtJlUxBR9TZ4LgUwpsIY0WUgw"

CID = "d763fd8215284c9cb33b5ce4f194c939"
SECRET = "060b957fc06740c4af3847a95ef22eec"
YANDEX_TOKEN = "AgAAAAAGeV9IAAG8XjTHJs48bkgLqBiEv-Ln7Gs"


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
