"""Descarga el historico de tarifas URV (carga publica) de EPM y genera precios.json.

Lo ejecuta GitHub Actions todos los dias (ver .github/workflows/precios.yml).
EPM publica un PDF por mes con todo el historico; se prueba el mes actual y hacia atras.
"""
import datetime, io, json, re, sys, urllib.request
from pypdf import PdfReader

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
BASE = "https://www.epm.com.co/content/dam/epm/clientes-y-usuarios/energia/hogar/movilidad-electrica/tarifas-anos/{a}/"
NOMBRES = ["tarifas-movilidad-electrica-{m}.pdf", "tarifas-movilidad_electrica-{m}.pdf"]


def bajar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def num(s):
    # EPM ha usado "1,213.0" y "1.331,2"
    if re.search(r",\d{1,2}$", s):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    return float(s)


def parsear(texto):
    datos = {}
    anios = []
    NUM = r"(\d[\d.,]*\d)"
    for linea in texto.splitlines():
        a = re.findall(r"(20\d\d) Carga Lenta", linea)
        if a:
            anios = [int(x) for x in a]
            continue
        partes = re.findall(r"([A-Za-z]+) " + NUM + " " + NUM, linea)
        for i, (mes, lenta, rapida) in enumerate(partes):
            if mes.lower() in MESES and i < len(anios):
                clave = "%d-%02d" % (anios[i], MESES.index(mes.lower()) + 1)
                datos[clave] = {"lenta": num(lenta), "rapida": num(rapida)}
    return dict(sorted(datos.items()))


def main():
    hoy = datetime.date.today()
    y, m = hoy.year, hoy.month
    for _ in range(14):
        for nombre in NOMBRES:
            url = BASE.format(a=y) + nombre.format(m=MESES[m - 1])
            try:
                pdf = bajar(url)
            except Exception:
                continue
            texto = "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(pdf)).pages)
            hist = parsear(texto)
            if not hist:
                continue
            out = {
                "fuente": "EPM - Unidad de Recarga Vehicular (URV), carga publica",
                "url": url,
                "consultado": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "unidad": "COP/kWh",
                "historico": hist,
            }
            with open("precios.json", "w", encoding="utf-8") as f:
                json.dump(out, f, ensure_ascii=False, indent=1)
            ultimo = list(hist)[-1]
            print("OK", url, ultimo, hist[ultimo], len(hist), "meses")
            return
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    sys.exit("No se encontro PDF de tarifas")


if __name__ == "__main__":
    main()
