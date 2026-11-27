"""Profil commun au menu, à la boutique et aux parties terminées."""
import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from reglages_boutique import CODE_ADMIN, SKINS
from settings import ROOT


def lire(chemin):
    return json.loads(chemin.read_text(encoding="utf-8-sig"))


class Profil:
    def __init__(self, fichier=ROOT / "sauvegarde.json"):
        self.fichier = Path(fichier)
        data = lire(self.fichier) if self.fichier.exists() else {}
        if data.get("version") != 1:
            # Le JSON fourni porte version 0 : il permet l'import au premier lancement.
            ancien = self.fichier.with_name("boutique.json")
            if ancien.exists() and (not data or data.get("version") == 0):
                boutique = lire(ancien)
                data.update(wallet=boutique["pieces"], owned=boutique["acquis"],
                            selected=boutique["equipe"])
            scores = list(data.get("scores", []))
            record = self.fichier.with_name("record.json")
            if record.exists():
                meilleur = lire(record).get("best", 0)
                if meilleur > 0 and meilleur not in scores:
                    scores.append(meilleur)
            data.update(version=1, scores=sorted(scores, reverse=True)[:5])
        self.data = {
            "wallet": 0, "owned": ["classic"], "selected": "classic",
            "scores": [], "last_score": None, "last_run": "", "sound": True,
            "admin": False, "admin_skin": None, **data,
        }
        if "classic" not in self.data["owned"]:
            self.data["owned"].append("classic")
        if self.data["selected"] not in self.data["owned"] or self.data["selected"] not in SKINS:
            self.data["selected"] = "classic"
        if not self.fichier.exists() or self.data != lire(self.fichier):
            self._enregistrer()

    def _enregistrer(self, **changements):
        nouveau = {**self.data, **changements}
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.fichier.parent,
                                suffix=".tmp", delete=False) as fichier:
            temporaire = Path(fichier.name)
            try:
                json.dump(nouveau, fichier, indent=2, ensure_ascii=False)
                fichier.write("\n")
            except Exception:
                fichier.close()
                temporaire.unlink(missing_ok=True)
                raise
        try:
            temporaire.replace(self.fichier)
        finally:
            temporaire.unlink(missing_ok=True)
        self.data = nouveau

    @property
    def pieces(self):
        return self.data["wallet"]

    @property
    def admin(self):
        return self.data["admin"]

    @property
    def equipe(self):
        demo = self.data["admin_skin"]
        return demo if self.admin and demo in SKINS else self.data["selected"]

    @property
    def record(self):
        return max(self.data["scores"], default=0)

    @property
    def dernier_score(self):
        return self.data["last_score"]

    @property
    def son(self):
        return self.data["sound"]

    def modifier_son(self, active):
        self._enregistrer(sound=active)

    def disponible(self, skin):
        return skin in SKINS and (self.admin or skin in self.data["owned"])

    def acheter(self, skin):
        if self.disponible(skin):
            return ""
        prix = SKINS[skin]["prix"]
        if self.pieces < prix:
            return f"Need {prix - self.pieces:,} more coins"
        self._enregistrer(wallet=self.pieces - prix, owned=self.data["owned"] + [skin])
        return "Skin unlocked!"

    def equiper(self, skin):
        if self.disponible(skin) and skin != self.equipe:
            if self.admin:
                self._enregistrer(admin_skin=skin)
            else:
                self._enregistrer(selected=skin)

    def debloquer(self, code):
        if code != CODE_ADMIN:
            return "Incorrect code"
        self._enregistrer(admin=True, admin_skin=self.equipe)
        return "Admin mode"

    def sortir_admin(self):
        self._enregistrer(admin=False, admin_skin=None)

    def fin_partie(self, run_id, pieces, score):
        if run_id == self.data["last_run"]:
            return
        meilleurs = sorted([*self.data["scores"], score], reverse=True)[:5]
        self._enregistrer(wallet=self.pieces + pieces, scores=meilleurs,
                          last_score=score, last_run=run_id)
