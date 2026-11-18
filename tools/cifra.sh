#!/usr/bin/env bash
# Cifra / decifra i dati privati dei relatori (testi + immagini).
#   CHIAVE_DATI=... bash tools/cifra.sh cifra     data/privato/  ->  data/dati.enc
#   CHIAVE_DATI=... bash tools/cifra.sh decifra   data/dati.enc  ->  data/privato/
# La chiave NON va mai scritta nel repository: sta solo nel secret GitHub "CHIAVE_DATI".
set -euo pipefail
cd "$(dirname "$0")/.."
: "${CHIAVE_DATI:?Imposta la variabile CHIAVE_DATI}"

case "${1:-}" in
  cifra)
    test -f data/privato/relatori.json || { echo "Manca data/privato/relatori.json"; exit 1; }
    tar -C data -czf - privato | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt \
      -pass env:CHIAVE_DATI -out data/dati.enc
    echo "Creato data/dati.enc"
    ;;
  decifra)
    rm -rf data/privato
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:CHIAVE_DATI -in data/dati.enc \
      | tar -C data -xzf -
    echo "Decifrato in data/privato/"
    ;;
  *)
    echo "Uso: bash tools/cifra.sh cifra|decifra"; exit 1 ;;
esac
