from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URL = os.getenv("DB_URL")
ROLE_REWARD = {"1316232347816955964": ["zenMiner | Zenrock", 1000],
               "1268395930499944539": ["zenDisciple | Zenrock", 2500],
               "1268396133236084766": ["zenMaster | Zenrock", 10000],
               "1268396272855941224": [".zen | Zenrock", 20000],
               "1362246524066861267": ["ROCK 1 | Zenrock", 30000]}
RUNNER = [1226891544334700667]
