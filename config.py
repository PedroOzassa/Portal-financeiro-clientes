import configparser
from pathlib import Path

_config = configparser.ConfigParser()
_config.read(Path(__file__).parent / "variaveis.ini", encoding="utf-8")

ProjetoPucc = _config["ProjetoPucc"]
Cores = _config["Cores"]
FlaskCfg = _config["Flask"]
