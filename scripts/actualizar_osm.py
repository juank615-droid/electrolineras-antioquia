"""Copia diaria de las estaciones de OpenStreetMap a 60 km de Medellin (osm.json)."""
import json, urllib.parse, urllib.request

Q = '[out:json][timeout:60];nwr["amenity"="charging_station"](around:60000,6.2442,-75.5812);out center tags;'
for base in ("https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"):
    try:
        req = urllib.request.Request(base + "?data=" + urllib.parse.quote(Q),
                                     headers={"User-Agent": "ElectrolinerasAntioquia/1.0", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=90) as r:
            d = json.load(r)
        with open("osm.json", "w", encoding="utf-8") as f:
            json.dump({"elements": d["elements"]}, f, ensure_ascii=False)
        print("OSM OK", len(d["elements"]))
        break
    except Exception as e:
        print("OSM fallo", base, e)
