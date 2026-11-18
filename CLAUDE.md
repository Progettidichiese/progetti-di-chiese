# Progetti di chiese — sito del convegno

Convegno internazionale «Progetti di chiese. Architetture Testimonianze Prospettive»,
Politecnico di Milano, 18–19 marzo 2027, Aula “Osvaldo De Donato”.
A cura di Francesca Daprà, Emilio Faroldi, Maria Pilar Vettori.
Il sito lavora in coppia con una pagina Instagram: ogni settimana viene svelato un relatore.
Chi lavora al sito: comunica in italiano, gli utenti non sono sviluppatori.

## Come funziona
- `build.py` (Python, solo libreria standard) genera il sito statico in `_site/`.
- Pubblica SOLO i relatori con `data_svelamento <= oggi` (fuso Europe/Rome).
  Anteprima di un altro giorno: `OGGI=2027-01-15 python3 build.py`.
- Dati: `data/privato/relatori.json` + `data/privato/immagini/` se esistono, altrimenti `data/demo.json` (prova).
- Testi fissi del convegno (titolo, date, curatori, contatti, Instagram): `data/sito.json`.
- Stile: `src/style.css`. File statici extra (favicon, logo): `src/pubblici/` (copiati nella radice del sito).
- Pubblicazione: `.github/workflows/pubblica.yml` → GitHub Pages, a ogni push su `main`
  e ogni giorno alle 05:05 UTC (06:05 in Italia). Si può lanciare a mano da Actions → "Run workflow".

## Fase di costruzione
- `data/sito.json` → `"in_costruzione": true` aggiunge noindex e un robots.txt che blocca i motori di ricerca.
  Al lancio: mettere `false` e collegare il dominio (CNAME). Il dominio NON va collegato prima del lancio.
- Anteprima privata per gli organizzatori: artifact claude.ai "Progetti di chiese — anteprima privata del sito",
  generato con `ANTEPRIMA=1 python3 build.py` (link espliciti a index.html) e ripubblicato a ogni modifica.

## Riservatezza dei relatori futuri (IMPORTANTE)
Il repository è pubblico (GitHub Pages gratuito). I dati veri non vanno MAI committati in chiaro:
- `data/privato/` è in `.gitignore`.
- Si committa solo `data/dati.enc`, creato con `CHIAVE_DATI=… bash tools/cifra.sh cifra`.
- La chiave sta solo nel secret del repository `CHIAVE_DATI`; il workflow decifra prima della build.
- Le immagini di un relatore vengono copiate nel sito solo dal giorno del suo svelamento.

## Schema dati (dal foglio Excel "Progetti_di_chiese_relatori_MODELLO")
`relatori`: id, data_svelamento (YYYY-MM-DD), nome, cognome, ruolo, qualifica, bio_it,
titolo_intervento_it, giorno_intervento, orario, foto, credito_foto, sito_web,
link_post_instagram, qualifica_en, bio_en, titolo_intervento_en.
`progetti`: id_relatore, ordine, titolo, luogo, anno, descrizione_it, immagine, credito_immagine, descrizione_en.
La riga con id "00" è l'esempio del modello e viene ignorata.

## Grafica (dal save the date)
- Colori: carta #FCFBF8, inchiostro #111111, viola #7B2560, lime #B2CC2A, malva #D3B6C9 (sottolineature).
- Segno: croce formata da barra verticale viola e barra orizzontale lime.
- Font ufficiali: Bodoni 72 / Bodoni URW (titoli), ITC Avant Garde Gothic Pro (testo), Neue Haas Grotesk (maiuscoletti, etichette).
  Per ora sostituti Google Fonts: Bodoni Moda, Questrial, Inter Tight. Quando arriva il kit Adobe Fonts
  (use.typekit.net) sostituire il <link> in `build.py` → `testa()` e le variabili `--serif/--geo/--grot` in `style.css`.

## Da fare
- Logo Politecnico ufficiale (ora segnaposto "[Logo Polimi]").
- Kit Adobe Fonts.
- Dominio proprio: file `CNAME` nella radice + DNS presso il registrar.
- Programma delle giornate, email, account Instagram (`data/sito.json`).
- Attenzione: GitHub sospende i workflow pianificati dopo 60 giorni senza attività sul repository.
