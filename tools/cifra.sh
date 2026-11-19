#!/usr/bin/env bash
# Cifratura dei dati privati dei relatori (testi + immagini) con una coppia di chiavi.
#   bash tools/cifra.sh cifra     data/privato/ -> data/dati.enc + data/dati.chiave.enc
#                                 usa SOLO la chiave pubblica (data/chiave_pubblica.pem): non serve nessun segreto
#   CHIAVE_PRIVATA_DATI="$(cat chiave.pem)" bash tools/cifra.sh decifra    -> data/privato/
#                                 la chiave privata sta SOLO nel secret GitHub "CHIAVE_PRIVATA_DATI"
set -euo pipefail
cd "$(dirname "$0")/.."
PUB=data/chiave_pubblica.pem

case "${1:-}" in
  cifra)
    test -f data/privato/relatori.json || { echo "Manca data/privato/relatori.json"; exit 1; }
    TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
    openssl rand -hex 32 > "$TMP/k"                                  # chiave casuale usa-e-getta
    tar -C data -czf - privato | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt \
      -pass file:"$TMP/k" -out data/dati.enc
    openssl pkeyutl -encrypt -pubin -inkey "$PUB" -pkeyopt rsa_padding_mode:oaep \
      -pkeyopt rsa_oaep_md:sha256 -in "$TMP/k" -out data/dati.chiave.enc
    echo "Creati data/dati.enc e data/dati.chiave.enc"
    ;;
  decifra)
    : "${CHIAVE_PRIVATA_DATI:?Manca la chiave privata (secret CHIAVE_PRIVATA_DATI)}"
    TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
    printf '%s\n' "$CHIAVE_PRIVATA_DATI" > "$TMP/priv.pem"; chmod 600 "$TMP/priv.pem"
    openssl pkeyutl -decrypt -inkey "$TMP/priv.pem" -pkeyopt rsa_padding_mode:oaep \
      -pkeyopt rsa_oaep_md:sha256 -in data/dati.chiave.enc -out "$TMP/k"
    rm -rf data/privato
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass file:"$TMP/k" -in data/dati.enc | tar -C data -xzf -
    echo "Decifrato in data/privato/"
    ;;
  *)
    echo "Uso: bash tools/cifra.sh cifra|decifra"; exit 1 ;;
esac
