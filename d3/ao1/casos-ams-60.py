"""Gera de forma reprodutível o conjunto ampliado de 60 casos (AO1 e N2).

Mantém os 30 casos originais da D2 (`d2/lab6/casos-ams.csv`) nas linhas 1 a 30
e seleciona 30 novos casos estratificados a partir de `data/raw/ai4i2020.csv`
com semente fixa (`SEMENTE = 42`).

Saídas geradas:
    - `d3/ao1/casos-ams-60.csv`: CSV com 60 linhas e 14 colunas (30 falhas e 30 normais).
    - `data/casos-ams-60.csv`: cópia idêntica na pasta `data/` do projeto.
    - Terminal (stdout): resumo da quantidade de casos, falhas/normais e novos UDIs.

Uso:
    .venv/bin/python d3/ao1/casos-ams-60.py
    npm run d3:ao1:casos-60
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
CAMINHO_BRUTO = RAIZ / "data" / "raw" / "ai4i2020.csv"
CAMINHO_D2 = RAIZ / "d2" / "lab6" / "casos-ams.csv"
DESTINOS = (
    RAIZ / "d3" / "ao1" / "casos-ams-60.csv",
    RAIZ / "data" / "casos-ams-60.csv",
)

SEMENTE = 42
MODOS = ("TWF", "HDF", "PWF", "OSF", "RNF")


def _sortear(df: pd.DataFrame, n: int, semente: int = SEMENTE) -> pd.DataFrame:
    if len(df) < n:
        raise ValueError(f"Estrato possui apenas {len(df)} linhas; precisa de {n}.")
    return df.sample(n=n, random_state=semente)


def gerar_casos_60(
    caminho_bruto: Path = CAMINHO_BRUTO,
    caminho_d2: Path = CAMINHO_D2,
    destinos: tuple[Path, ...] = DESTINOS,
    semente: int = SEMENTE,
) -> pd.DataFrame:
    """Constrói e grava os 60 casos (30 da D2 + 30 novos estratificados)."""
    bruto = pd.read_csv(caminho_bruto)
    d2 = pd.read_csv(caminho_d2)

    pool = bruto[~bruto["UDI"].isin(d2["UDI"])].copy()
    pool["dif_temp"] = pool["Process temperature [K]"] - pool["Air temperature [K]"]
    pool["potencia"] = pool["Torque [Nm]"] * pool["Rotational speed [rpm]"] * (2 * math.pi) / 60.0
    pool["soma_modos"] = pool[list(MODOS)].sum(axis=1)

    falhas = pool[pool["Machine failure"] == 1]
    normais = pool[pool["Machine failure"] == 0]

    # --- 15 novas falhas reais ---
    twf_puro = _sortear(falhas[(falhas["TWF"] == 1) & (falhas["soma_modos"] == 1)], 3, semente)
    hdf_puro = _sortear(falhas[(falhas["HDF"] == 1) & (falhas["soma_modos"] == 1)], 3, semente)
    pwf_puro = _sortear(falhas[(falhas["PWF"] == 1) & (falhas["soma_modos"] == 1)], 3, semente)
    osf_puro = _sortear(falhas[(falhas["OSF"] == 1) & (falhas["soma_modos"] == 1)], 2, semente)
    combinadas = _sortear(falhas[falhas["soma_modos"] >= 2], 2, semente)
    sem_modo = _sortear(falhas[falhas["soma_modos"] == 0], 2, semente)

    # --- 15 novos casos normais ---
    desgaste_alto = _sortear(
        normais[(normais["Tool wear [min]"] >= 175) & (normais["Tool wear [min]"] <= 210)],
        5,
        semente,
    )
    normais_restantes = normais[normais["Tool wear [min]"] < 175]
    cond_fronteira = (
        (normais_restantes["dif_temp"] < 9.0)
        | (normais_restantes["potencia"] < 3800.0)
        | (normais_restantes["potencia"] > 8200.0)
    )
    fronteira_tp = _sortear(normais_restantes[cond_fronteira], 5, semente)
    rotina_pool = normais_restantes[~cond_fronteira]
    rotina = pd.concat(
        [
            _sortear(rotina_pool[rotina_pool["Type"] == "H"], 2, semente),
            _sortear(rotina_pool[rotina_pool["Type"] == "M"], 2, semente),
            _sortear(rotina_pool[rotina_pool["Type"] == "L"], 1, semente),
        ]
    )

    novos = pd.concat(
        [
            twf_puro,
            hdf_puro,
            pwf_puro,
            osf_puro,
            combinadas,
            sem_modo,
            desgaste_alto,
            fronteira_tp,
            rotina,
        ]
    )[list(d2.columns)].sort_values("UDI")

    resultado = pd.concat([d2, novos], ignore_index=True)
    if len(resultado) != 60 or resultado["UDI"].nunique() != 60:
        raise AssertionError("O conjunto final deve ter exatamente 60 UDIs únicos.")

    for destino in destinos:
        destino.parent.mkdir(parents=True, exist_ok=True)
        resultado.to_csv(destino, index=False)

    return resultado


if __name__ == "__main__":
    df_60 = gerar_casos_60()
    novos_udis = [int(u) for u in df_60["UDI"].iloc[30:]]
    print(f"Gerados {len(df_60)} casos (30 D2 + 30 novos, semente={SEMENTE}).")
    print(f"Falhas: {int(df_60['Machine failure'].sum())} | Normais: {int((df_60['Machine failure'] == 0).sum())}")
    print(f"Novos UDIs: {novos_udis}")
