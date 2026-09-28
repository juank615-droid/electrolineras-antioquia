"""Estado en vivo por conector (Terpel Voltex, Mubon, Voltop, Celsia, Ergenia...) desde electrolineras.co
y copia del mapa oficial EPM. Genera vivo.json y estaciones_epm.json. Lo corre GitHub Actions cada 5 min.
"""
import json, math, urllib.request

CENTRO = (6.2442, -75.5812)   # Medellin
RADIO_KM = 60
ECO = "https://electrolineras.co/api/stations/nearby?lat=%s&lng=%s&limit=200" % CENTRO
EPM = ("https://services1.arcgis.com/lHSB5M3vxFT82S7P/arcgis/rest/services/"
       "Estaciones_de_carga_el%C3%A9ctrica/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json")


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def km(lat, lon):
    a, b = map(math.radians, CENTRO)
    c, d = math.radians(lat), math.radians(lon)
    h = math.sin((c - a) / 2) ** 2 + math.cos(a) * math.cos(c) * math.sin((d - b) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


try:
    d = bajar(ECO)
    est = [s for s in d["stations"] if km(s["latitude"], s["longitude"]) <= RADIO_KM]
    for s in est:
        s.pop("distanceKm", None)
    with open("vivo.json", "w", encoding="utf-8") as f:
        json.dump({"sincronizado": d.get("providerSyncTimes", {}), "stations": est}, f, ensure_ascii=False)
    print("vivo OK", len(est))
except Exception as e:
    print("vivo FALLO", e)

try:
    d = bajar(EPM)
    if "features" in d:
        with open("estaciones_epm.json", "w", encoding="utf-8") as f:
            json.dump({"features": d["features"]}, f, ensure_ascii=False)
        print("EPM OK", len(d["features"]))
except Exception as e:
    print("EPM FALLO", e)
