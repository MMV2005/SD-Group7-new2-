from settings import ASSETS

CODE_ADMIN = "admin"
SKINS = {
    "classic": {"nom": "Classic Leprechaun", "prix": 0},
    "gold": {"nom": "Gold Leprechaun", "prix": 100000},
    "stone": {"nom": "Stone Leprechaun", "prix": 1000},
    "mcgregor": {"nom": "McGregor", "prix": 5000, "mystere": True},
    "jensen": {"nom": "Jensen Huang", "dossier": "jensen huang", "prix": 10000, "mystere": True},
}


def dossier_skin(skin):
    return ASSETS / "Skins" / SKINS[skin].get("dossier", skin)
