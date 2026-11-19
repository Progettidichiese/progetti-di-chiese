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
- Testi fissi del convegno (titolo, date, organizzatori con bio, luogo e indicazioni, contatti, Instagram): `data/sito.json`.
  Foto degli organizzatori (non riservate): `src/pubblici/organizzatori/<file>` + campo `foto`.
- Ordine della home: apertura · presentazione · Organizzatori (responsabili scientifici con foto, poi Comitato scientifico e Comitato organizzativo come elenchi di soli nomi) · Relatori · Programma · Come arrivare · piede.
- Pagina separata `iscrizione/` (voce di menu "Iscrizione" evidenziata): architetti con crediti (portale Ordine), pubblico esterno (sito Polimi, sezione convegni), studenti senza iscrizione.
  Link e numero di crediti in `data/sito.json` → `iscrizione`; finché sono vuoti i pulsanti mostrano "link in arrivo".
- Mappa Google caricata solo al clic su "Mostra la mappa" (niente dati a Google senza azione del visitatore).
  Luogo verificato: Aula De Donato = Campus Leonardo, Edificio 3, piano terra, Piazza Leonardo da Vinci 32.
  Coordinate esatte dell aula (45.4776016, 9.2275393) e link Google Maps fornito dagli organizzatori in `data/sito.json` → `luogo`.
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
- Segno: croce formata da barra verticale viola e barra orizzontale lime. Nella home la croce si scompone scorrendo (viola verso l alto, lime verso sinistra) e si ricompone tornando su; disattivata con prefers-reduced-motion.
- Apertura: sotto la data solo "Politecnico di Milano" in grassetto (l aula compare in Come arrivare).
- Al passaggio del mouse foto e testi delle schede, link e pulsanti si ingrandiscono leggermente (solo dispositivi con mouse, mai con riduci movimento).
- Pagina relatore: in alto copertina orizzontale grande = immagine del progetto con ordine 1 (con didascalia). Sotto, barra lime che passa sotto il ritratto (piccolo, sovrapposto alla copertina) e scorrendo esce verso destra; nessuna barra viola su questa pagina.
- Comparsa morbida allo scorrimento (dissolvenza + leggero sollevamento, a cascata) per schede relatori, organizzatori, progetti e titoli di sezione; classe "anima" aggiunta in <head> per evitare lampeggi.
- La pagina relatore si apre sempre dall alto (scrollTo + scrollIntoView anche dentro finestre/iframe).
- style.css è richiamato con ?v=<hash> perché GitHub Pages fa tenere ai browser copie vecchie per circa 10 minuti (non in ANTEPRIMA).
- Titolo "Progetti di chiese": interlinea >= 1.16 (1.24 su telefono) perché la g di Progetti non tocchi la h di chiese.
- Font ufficiali: Bodoni 72 / Bodoni URW (titoli), ITC Avant Garde Gothic Pro (testo), Neue Haas Grotesk (maiuscoletti, etichette).
  Per ora sostituti open source ospitati sul sito (src/pubblici/fonts, licenza OFL): Bodoni Moda, Questrial, Inter Tight. Quando arriva il kit Adobe Fonts
  (use.typekit.net) sostituire il preload in `build.py` → `testa()`, le @font-face e le variabili `--serif/--geo/--grot` in `style.css`.

## Da fare
- Logo Politecnico ufficiale (ora segnaposto "[Logo Polimi]").
- Kit Adobe Fonts.
- Dominio proprio: file `CNAME` nella radice + DNS presso il registrar.
- Programma delle giornate, email, account Instagram (`data/sito.json`).
- Attenzione: GitHub sospende i workflow pianificati dopo 60 giorni senza attività sul repository.
