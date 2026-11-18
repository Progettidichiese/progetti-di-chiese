#!/usr/bin/env python3
"""Genera il sito statico in _site/.

Dati:
  - data/privato/relatori.json + data/privato/immagini/  (decifrati dal robot, mai in chiaro su GitHub)
  - altrimenti data/demo.json (relatori di prova)
Pubblica solo i relatori con data_svelamento <= oggi (fuso Europe/Rome).
Per vedere il sito "come sarà" in un altro giorno: OGGI=2027-01-15 python3 build.py
"""
import datetime as dt
import html
import json
import os
import shutil
import urllib.parse
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
PRIV = ROOT / "data" / "privato"
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]

e = lambda s: html.escape(str(s or ""), quote=True)
# ANTEPRIMA=1: link espliciti a index.html, per l'anteprima privata su claude.ai
IDX = "index.html" if os.environ.get("ANTEPRIMA") else ""


def data_it(d):
    return f"{d.day} {MESI[d.month - 1]}"


def oggi():
    if os.environ.get("OGGI"):
        return dt.date.fromisoformat(os.environ["OGGI"])
    return dt.datetime.now(ZoneInfo("Europe/Rome")).date()


def carica():
    sito = json.loads((ROOT / "data" / "sito.json").read_text("utf-8"))
    sorgente = PRIV / "relatori.json"
    demo = not sorgente.exists()
    dati = json.loads((ROOT / "data" / "demo.json" if demo else sorgente).read_text("utf-8"))
    relatori = []
    for r in dati["relatori"]:
        rid = str(r.get("id", "")).strip().zfill(2)
        if not rid or rid == "00":
            continue  # riga di esempio
        r["id"] = rid
        r["data"] = dt.date.fromisoformat(str(r["data_svelamento"])[:10])
        r["progetti"] = sorted(
            (p for p in dati.get("progetti", []) if str(p.get("id_relatore", "")).strip().zfill(2) == rid),
            key=lambda p: float(p.get("ordine") or 0))
        relatori.append(r)
    relatori.sort(key=lambda r: (r["data"], r["id"]))
    return sito, relatori, demo


def testa(sito, titolo, base, descrizione=""):
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titolo)}</title>
<meta name="description" content="{e(descrizione or sito['sottotitolo'])}">
<meta property="og:title" content="{e(titolo)}">
<meta property="og:description" content="{e(descrizione or sito['sottotitolo'])}">
{'<meta name="robots" content="noindex, nofollow">' if sito.get('in_costruzione') else ''}
<link rel="preload" href="{base}fonts/bodoni-moda-latin-standard-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}style.css">
</head>
<body>
<header class="testata">
<div class="wrap">
<a class="marchio" href="{base}{IDX}"><span class="logo-polimi">[Logo Polimi]</span><span class="serif">{e(sito['titolo'])}</span></a>
<nav class="menu" aria-label="Principale">
<a href="{base}{IDX}#organizzatori">Organizzatori</a>
<a href="{base}{IDX}#relatori">Relatori</a>
<a href="{base}{IDX}#programma">Programma</a>
<a href="{base}{IDX}#come-arrivare">Come arrivare</a>
<a href="{base}{IDX}#info">Info</a>
{f'<a class="ig" href="{e(sito["instagram_url"])}">Instagram ↗</a>' if sito.get('instagram_url') else ''}
</nav>
</div>
</header>
<main>
"""


def piede(sito):
    ig = (f'<a href="{e(sito["instagram_url"])}">{e(sito.get("instagram_nome") or "Instagram")} ↗</a>'
          if sito.get("instagram_url") else '<span class="segnaposto-testo">[account Instagram]</span>')
    mail = (f'<a href="mailto:{e(sito["email"])}">{e(sito["email"])}</a>'
            if sito.get("email") else '<span class="segnaposto-testo">[email di contatto]</span>')
    return f"""</main>
<footer class="piede" id="info">
<div class="wrap">
<div class="col"><span class="serif">{e(sito['titolo'])}</span><span class="geo">{e(sito['sottotitolo'])}</span></div>
<div class="col geo"><span>{e(sito['date'])} · {e(sito['sede'])}</span><span>{e(sito['aula'])}</span>{mail}{ig}</div>
</div>
</footer>
</body>
</html>
"""


def img_tag(nome, alt, base):
    if not nome:
        return ""
    return f'<img src="{base}img/{e(nome)}" alt="{e(alt)}" loading="lazy">'


def scheda(r, aperto, base):
    num = r["id"]
    if not aperto:
        return f"""<li class="scheda chiusa" aria-label="Relatore {num}, annunciato il {data_it(r['data'])}">
<div class="ritratto"><svg aria-hidden="true" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg><span class="num">{num}</span></div>
<div class="filo"></div>
<div class="scheda-testo"><span class="etichetta">In arrivo</span><span class="nome">Svelato il {data_it(r['data'])}</span></div>
</li>"""
    nome = f"{r.get('nome', '')} {r.get('cognome', '')}".strip()
    foto = img_tag(r.get("foto"), f"Ritratto di {nome}", base) or \
        f'<div class="segnaposto"><span class="etichetta segnaposto-testo">[Foto]</span><span class="num">{num}</span></div>'
    return f"""<li><a class="scheda" href="{base}relatori/{num}/{IDX}">
<div class="ritratto">{foto}</div>
<div class="filo"></div>
<div class="scheda-testo"><span class="etichetta">{e(r.get('ruolo'))}</span><span class="nome">{e(nome)}</span><span class="geo">Progetti e intervento →</span></div>
</a></li>"""


def scheda_organizzatore(o, base):
    foto = (f'<img src="{base}organizzatori/{e(o["foto"])}" alt="Ritratto di {e(o["nome"])}" loading="lazy">' if o.get("foto")
            else '<div class="segnaposto"><span class="etichetta segnaposto-testo">[Foto]</span></div>')
    return f"""<li class="organizzatore">
<div class="ritratto">{foto}</div>
<div class="filo"></div>
<div class="organizzatore-testo">
<span class="etichetta">{e(o.get('ruolo')) or '[Ruolo, dipartimento]'}</span>
<h3 class="serif">{e(o['nome'])}</h3>
<p class="geo">{e(o.get('bio')) or '[Biografia breve, 4–6 righe.]'}</p>
</div>
</li>"""


def home(sito, relatori, svelati, oggi_):
    base = "./"
    prossimo = next((r for r in relatori if r["data"] > oggi_), None)
    organizzatori = "\n".join(scheda_organizzatore(o, base) for o in sito.get("organizzatori", []))
    luogo = sito.get("luogo", {})
    coord = f'{luogo.get("lat")},{luogo.get("lng")}'
    url_mappa = luogo.get("maps_url") or f"https://www.google.com/maps/search/?api=1&query={coord}"
    schede = "\n".join(scheda(r, r in svelati, base) for r in relatori)
    box = (f'<span class="serif">{data_it(prossimo["data"])}</span>' if prossimo
           else '<span class="serif">Tutti annunciati</span>')
    return testa(sito, f"{sito['titolo']} — {sito['sottotitolo']}", base, sito["presentazione"][:155]) + f"""
<section class="apertura" aria-label="Presentazione">
<div class="barra-v" aria-hidden="true"></div>
<div class="apertura-corpo">
<p class="occhiello">{'<span class="sep" aria-hidden="true"> · </span>'.join(f'<span>{e(t)}</span>' for t in sito['tipo'])}</p>
<p class="data-grande"><span class="evidenzia">{e(sito['date'])}</span></p>
<p class="luogo"><strong>{e(sito['sede'])}</strong></p>
<h1>Progetti<br>di chiese</h1>
<div class="barra-o" aria-hidden="true"></div>
<p class="sottotitolo">{e(sito['sottotitolo'])}</p>
<a class="scorri" href="{base}{IDX}#relatori">Scopri i relatori <span aria-hidden="true">↓</span></a>
</div>
</section>
<section class="wrap presentazione" aria-label="Il convegno">
<div class="presentazione-testo">
<h2 class="etichetta">Il convegno</h2>
<p>{e(sito['presentazione'])}</p>
</div>
<aside class="presentazione-lato">
<div class="prossimo"><span class="etichetta">{'Prossimo relatore' if prossimo else 'Relatori'}</span>{box}<span class="geo">{len(svelati)} di {len(relatori)} relatori annunciati</span></div>
</aside>
</section>
<section class="wrap sezione" id="organizzatori">
<div class="sezione-testa"><h2>Organizzatori</h2><p>Il convegno è a cura di</p></div>
<ul class="organizzatori">
{organizzatori}
</ul>
</section>
<section class="wrap sezione" id="relatori">
<div class="sezione-testa"><h2>Relatori</h2><p>Un nuovo nome ogni settimana, insieme al post su Instagram</p></div>
<ul class="griglia">
{schede}
</ul>
</section>
<section class="wrap sezione" id="programma">
<div class="sezione-testa"><h2>Programma</h2></div>
<p class="in-arrivo">[Il programma delle due giornate sarà pubblicato qui.]</p>
</section>
<section class="wrap sezione" id="come-arrivare">
<div class="sezione-testa"><h2>Come arrivare</h2><p>{e(sito['date'])}</p></div>
<div class="arrivo">
<div class="arrivo-testo">
<p class="arrivo-aula serif">{e(sito['aula'])}</p>
<p class="arrivo-dove"><strong>{e(sito['sede'])}</strong><br>{e(luogo.get('campus'))} · {e(luogo.get('edificio'))}<br>{e(luogo.get('indirizzo'))}</p>
<div class="arrivo-mezzi">
<span class="etichetta">In metropolitana</span>
<p>{e(luogo.get('metro'))}</p>
</div>
<div class="collegamenti">
<a href="https://www.google.com/maps/dir/?api=1&amp;destination={coord}">Indicazioni stradali ↗</a>
<a href="{e(url_mappa)}">Apri in Google Maps ↗</a>
</div>
</div>
<div class="mappa" data-src="https://www.google.com/maps?q={coord}&amp;z=18&amp;output=embed">
<div class="mappa-copertina">
<svg aria-hidden="true" width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/></svg>
<span class="serif">Piazza Leonardo da Vinci 32</span>
<button type="button" class="mappa-carica">Mostra la mappa</button>
<span class="mappa-nota">La mappa è fornita da Google: caricandola, Google riceve alcuni dati di navigazione.</span>
</div>
</div>
</div>
</section>
<script>
(function () {{
  var m = document.querySelector(".mappa");
  if (!m) return;
  m.querySelector(".mappa-carica").addEventListener("click", function () {{
    var f = document.createElement("iframe");
    f.src = m.getAttribute("data-src");
    f.title = "Mappa: {e(sito['aula'])}, {e(sito['sede'])}";
    f.loading = "lazy";
    f.referrerPolicy = "no-referrer-when-downgrade";
    m.innerHTML = "";
    m.appendChild(f);
  }});
}})();
</script>
<script>
(function () {{
  var ap = document.querySelector(".apertura");
  if (!ap || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var v = ap.querySelector(".barra-v"), o = ap.querySelector(".barra-o"), att = false;
  function aggiorna() {{
    att = false;
    var p = Math.min(1, Math.max(0, window.scrollY / (ap.offsetHeight * 0.7)));
    var k = p * p * (3 - 2 * p);
    v.style.transform = "translate3d(0," + (-k * 100) + "%,0)";
    o.style.transform = "translate3d(" + (-k * 100) + "%,0,0)";
  }}
  window.addEventListener("scroll", function () {{ if (!att) {{ att = true; requestAnimationFrame(aggiorna); }} }}, {{ passive: true }});
  window.addEventListener("resize", aggiorna);
  aggiorna();
}})();
</script>
""" + piede(sito)


def pagina_relatore(sito, r, svelati):
    base = "../../"
    nome = f"{r.get('nome', '')} {r.get('cognome', '')}".strip()
    i = svelati.index(r)
    prec = svelati[i - 1] if i > 0 else None
    succ = svelati[i + 1] if i < len(svelati) - 1 else None
    foto = img_tag(r.get("foto"), f"Ritratto di {nome}", base) or \
        '<div class="segnaposto"><span class="etichetta segnaposto-testo">[Foto del relatore]</span></div>'
    # copertina: immagine del primo progetto (ordine 1); senza immagine, un segnaposto
    p1 = r["progetti"][0] if r["progetti"] else {}
    cop_img = img_tag(p1.get("immagine"), p1.get("titolo") or nome, base)
    didascalia = " · ".join(x for x in [str(p1.get("titolo") or ""), ", ".join(y for y in [str(p1.get("luogo") or ""), str(p1.get("anno") or "")] if y)] if x)
    credito_cop = f' <span class="credito">{e(p1["credito_immagine"])}</span>' if p1.get("credito_immagine") else ""
    didasc_html = f'<figcaption class="wrap"><span>{e(didascalia)}</span>{credito_cop}</figcaption>' if didascalia else ""
    segnaposto_cop = '<span class="etichetta segnaposto-testo">[Immagine di copertina: il primo progetto della lista]</span>'
    copertina = f"""<figure class="copertina">
<div class="copertina-img">{cop_img or segnaposto_cop}</div>
<div class="copertina-barra" aria-hidden="true"></div>
{didasc_html}
</figure>"""
    quando = " · ".join(x for x in [r.get("giorno_intervento"), r.get("orario")] if x)
    link = []
    if r.get("sito_web"):
        link.append(f'<a href="{e(r["sito_web"])}">Sito web ↗</a>')
    if r.get("link_post_instagram"):
        link.append(f'<a href="{e(r["link_post_instagram"])}">Il post su Instagram ↗</a>')
    progetti = "\n".join(f"""<li class="progetto">
<div class="foto">{img_tag(p.get('immagine'), p.get('titolo'), base) or '<span class="etichetta segnaposto-testo">[Immagine progetto]</span>'}</div>
<h3>{e(p.get('titolo'))}</h3>
<span class="luogo">{e(', '.join(x for x in [str(p.get('luogo') or ''), str(p.get('anno') or '')] if x))}</span>
{f'<p>{e(p["descrizione_it"])}</p>' if p.get('descrizione_it') else ''}
{f'<span class="credito">{e(p["credito_immagine"])}</span>' if p.get('credito_immagine') else ''}
</li>""" for p in r["progetti"])
    return testa(sito, f"{nome} — {sito['titolo']}", base, f"{r.get('qualifica', '')}. {sito['titolo']}, {sito['date']}.") + f"""
<div class="wrap"><a class="indietro" href="{base}{IDX}#relatori">← Tutti i relatori</a></div>
{copertina}
<div class="wrap sezione">
<article>
<div class="profilo">
<div class="profilo-foto"><div class="ritratto">{foto}</div><div class="filo"></div>{f'<p class="credito">{e(r["credito_foto"])}</p>' if r.get('credito_foto') else ''}</div>
<div class="profilo-testo">
<span class="etichetta">Relatore {r['id']} · {e(r.get('ruolo'))}</span>
<h1>{e(nome)}</h1>
{f'<p class="qualifica">{e(r["qualifica"])}</p>' if r.get('qualifica') else ''}
<p class="bio">{e(r.get('bio_it'))}</p>
<div class="intervento">
<span class="etichetta">Al convegno</span>
<span class="serif">{e(r.get('titolo_intervento_it'))}</span>
<span class="geo">{f'<span class="evidenzia">{e(quando)}</span> · ' if quando else ''}{e(sito['aula'])}</span>
</div>
{f'<div class="collegamenti">{"".join(link)}</div>' if link else ''}
</div>
</div>
{f'<section class="progetti"><div class="sezione-testa"><h2>Progetti</h2></div><ul class="progetti-griglia">{progetti}</ul></section>' if r['progetti'] else ''}
</article>
<nav class="naviga" aria-label="Altri relatori">
{f'<a href="{base}relatori/{prec["id"]}/{IDX}">← {e(prec.get("nome"))} {e(prec.get("cognome"))}</a>' if prec else '<span></span>'}
{f'<a href="{base}relatori/{succ["id"]}/{IDX}">{e(succ.get("nome"))} {e(succ.get("cognome"))} →</a>' if succ else '<span></span>'}
</nav>
</div>
<script>
(function () {{
  var c = document.querySelector(".copertina"), b = c && c.querySelector(".copertina-barra");
  if (!b || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var att = false;
  function aggiorna() {{
    att = false;
    var fine = c.offsetTop + c.offsetHeight;
    var p = Math.min(1, Math.max(0, window.scrollY / (fine * 0.75)));
    var k = p * p * (3 - 2 * p);
    b.style.transform = "translate3d(" + (k * window.innerWidth) + "px,0,0)";
  }}
  window.addEventListener("scroll", function () {{ if (!att) {{ att = true; requestAnimationFrame(aggiorna); }} }}, {{ passive: true }});
  window.addEventListener("resize", aggiorna);
  aggiorna();
}})();
</script>
""" + piede(sito)


def main():
    sito, relatori, demo = carica()
    oggi_ = oggi()
    svelati = [r for r in relatori if r["data"] <= oggi_]
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    # sito in costruzione: niente motori di ricerca
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n" if sito.get("in_costruzione") else "User-agent: *\nAllow: /\n")
    if (ROOT / "CNAME").exists():
        shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    if (ROOT / "src" / "pubblici").exists():
        shutil.copytree(ROOT / "src" / "pubblici", OUT, dirs_exist_ok=True)
    (OUT / "index.html").write_text(home(sito, relatori, svelati, oggi_), "utf-8")
    immagini = PRIV / "immagini"
    for r in svelati:
        d = OUT / "relatori" / r["id"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(pagina_relatore(sito, r, svelati), "utf-8")
        # copia SOLO le immagini dei relatori già svelati
        for nome in [r.get("foto")] + [p.get("immagine") for p in r["progetti"]]:
            if nome and (immagini / nome).exists():
                shutil.copy(immagini / nome, OUT / "img" / Path(nome).name)
    print(f"Oggi {oggi_}: {len(svelati)}/{len(relatori)} relatori pubblicati"
          f"{' (DATI DI PROVA)' if demo else ''}.")


if __name__ == "__main__":
    main()
