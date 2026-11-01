#!/usr/bin/env python3
"""Genera la copia de respaldo del catálogo de RadioGuasa a partir de Radio Browser.

Para cada país descarga las emisoras más escuchadas que funcionan y las guarda en docs/XX.json,
con el mismo formato que la API de Radio Browser (la app las lee con el mismo código).
También crea docs/seed.json (lista inicial para incluir en la app) y docs/index.json.
Solo usa la biblioteca estándar de Python. Se ejecuta a diario con GitHub Actions.
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

COUNTRIES = (
    "AR AU AT BE BO BR CA CL CN CO KR CR CU DK EC EG AE SK ES US PH FI FR GR GT NL IN ID IR IE IL IT "
    "JP MA MX NG NO NZ PK PA PY PE PL PT GB DO RO RU SA SE CH TH TR UA UY VE VN DE ZA DZ"
).split()
LIMIT = 500          # emisoras por país
SEED_COUNTRY = "ES"  # país de la lista inicial que se incluye dentro de la app
SEED_SIZE = 150
HOSTS = ["de1", "de2", "nl1", "fi1", "at1"]
USER_AGENT = "RadioGuasa-catalog/1.0 (daily snapshot; github.com/radioguasa-catalog)"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
KEEP = ("stationuuid", "name", "url", "url_resolved", "countrycode", "tags", "favicon", "clickcount")


def get(path, params):
    last = None
    for host in HOSTS:
        url = f"https://{host}.api.radio-browser.info/json/{path}?" + urllib.parse.urlencode(params)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2)
    raise RuntimeError(f"sin servidores: {last}")


def clean(stations):
    out, seen = [], set()
    for s in stations:
        name = (s.get("name") or "").strip()
        stream = (s.get("url_resolved") or s.get("url") or "").strip()
        if not name or not stream.startswith("http") or name.lower() in seen:
            continue
        if s.get("lastcheckok") == 0:
            continue
        seen.add(name.lower())
        out.append({k: s.get(k, "") for k in KEEP})
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    ok, failed, index = 0, [], {}
    seed_src = []
    for code in COUNTRIES:
        try:
            raw = get("stations/search", {
                "countrycode": code, "order": "clickcount", "reverse": "true",
                "hidebroken": "true", "limit": LIMIT,
            })
            stations = clean(raw)
            if len(stations) < 5:
                raise RuntimeError("muy pocas emisoras")
            with open(os.path.join(OUT, f"{code}.json"), "w", encoding="utf-8") as f:
                json.dump(stations, f, ensure_ascii=False, separators=(",", ":"))
            index[code] = len(stations)
            if code == SEED_COUNTRY:
                seed_src = stations
            ok += 1
        except Exception as e:  # noqa: BLE001
            failed.append(f"{code}: {e}")
            # Se conserva el fichero anterior si existía.
        time.sleep(2)  # una petición cada 2 s: trato amable con el servicio
    if seed_src:
        seed = [{
            "id": s["stationuuid"] or s["url_resolved"], "name": s["name"],
            "streamUrl": s["url_resolved"] or s["url"], "country": s["countrycode"],
            "tags": " · ".join([t.strip() for t in s["tags"].split(",") if t.strip()][:3]),
            "logoUrl": s["favicon"], "custom": False,
            "altUrl": s["url"] if s["url_resolved"] and s["url"] != s["url_resolved"] else "",
        } for s in seed_src[:SEED_SIZE]]
        with open(os.path.join(OUT, "seed.json"), "w", encoding="utf-8") as f:
            json.dump(seed, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump({"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "countries": index}, f)
    print(f"{ok} países correctos, {len(failed)} fallidos")
    for line in failed:
        print("  ", line)
    if ok == 0:
        sys.exit(1)  # Radio Browser caído: no se cambia nada y la tarea se marca como fallida


if __name__ == "__main__":
    main()
