from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")
ROLE_REWARD = {"1316232347816955964": ["zenMiner | Zenrock", 1000],
               "1268395930499944539": ["zenDisciple | Zenrock", 2500],
               "1289437312136122500": ["zenContent Creators | Zenrock", 5000],
               "1268396133236084766": ["zenMaster | Zenrock", 10000],
               "1268396272855941224": [".zen | Zenrock", 20000],
               "1362246524066861267": ["ROCK 1 | Zenrock", 30000],
               "1362246632661323920": ["ROCK 2 | Zenrock", 30000]}
RUNNER = [1226891544334700667]

MAIN_COLOR = 0x060f42
GREEN = 0x66FF00
RED = 0xFF6666

