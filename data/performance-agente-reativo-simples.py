#!/usr/bin/env python3
"""Calcula as métricas de performance do agente definidas no agent-spec.md (PEAS).

Métrica Principal:
    F = A / T (Taxa de captura de falhas / Recall)
    - A: Casos em que (risco == "alto" OU bloqueio == Sim) E Machine failure == 1
    - T: Total de falhas reais (Machine failure == 1)
    - Limiar de sucesso: F >= 97.35%

Métrica Secundária:
    FP = B / S (Taxa de falsos positivos)
    - B: Casos em que (risco == "alto" OU bloqueio == Sim) E Machine failure == 0
    - S: Total de máquinas saudáveis (Machine failure == 0)
    - Limiar de sucesso: FP <= 7.02%

Uso:
    python performance-agente-reativo-simples.py               # usa amostra/ai4i2020.csv por padrão
    python performance-agente-reativo-simples.py outro.csv     # usa outro arquivo csv
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd

# Limiares de telemetria do domínio de manufatura (linha de base do agente)
LIMITE_DIF_TEMP = 8.6       # K (dissipação de calor - HDF)
LIMITE_ROTACAO_HDF = 1380   # rpm
POTENCIA_MIN = 3500         # W (potência - PWF)
POTENCIA_MAX = 9000         # W
LIMITE_DESGASTE_TWF = 200   # min (desgaste de ferramenta)
LIMITE_OSF = {"L": 11000, "M": 12000, "H": 13000}  # Sobrecarga (torque * desgaste)


def agente_reativo_simples_decidir(row: pd.Series) -> tuple[str, bool]:
    """Atuador do agente: percebe os sensores e decide (risco, requer_bloqueio).

    Restrição de Percepção: O agente NÃO tem acesso ao rótulo 'Machine failure'.
    """
    tipo = str(row["Type"])
    temp_ar = float(row["Air temperature [K]"])
    temp_proc = float(row["Process temperature [K]"])
    rotacao = float(row["Rotational speed [rpm]"])
    torque = float(row["Torque [Nm]"])
    desgaste = float(row["Tool wear [min]"])

    # Potência mecânica: P = Torque * w = Torque * (rpm * 2 * pi / 60)
    potencia = torque * rotacao * (2 * math.pi) / 60

    hdf = (temp_proc - temp_ar < LIMITE_DIF_TEMP) and (rotacao < LIMITE_ROTACAO_HDF)
    pwf = (potencia < POTENCIA_MIN) or (potencia > POTENCIA_MAX)
    twf = desgaste >= LIMITE_DESGASTE_TWF
    osf = (desgaste * torque) > LIMITE_OSF.get(tipo, 12000)

    if hdf or pwf or twf or osf:
        return ("alto", True)  # risco == "alto" OU bloqueio == Sim
    return ("baixo", False)


def main() -> None:
    if len(sys.argv) > 1:
        caminho_csv = Path(sys.argv[1])
    else:
        caminho_csv = Path(__file__).resolve().parent / "amostra" / "ai4i2020.csv"

    if not caminho_csv.is_file():
        sys.exit(f"Arquivo não encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv)

    coluna_falha = "Machine failure"
    if coluna_falha not in df.columns:
        sys.exit(f"Coluna obrigatória '{coluna_falha}' não encontrada no dataset.")

    # 1. Agente avalia cada registro usando apenas os sensores
    decisoes = df.apply(agente_reativo_simples_decidir, axis=1)
    df["risco_agente"] = [d[0] for d in decisoes]
    df["bloqueio_agente"] = [d[1] for d in decisoes]

    # Intervenção recomendada pelo agente conforme o agent-spec.md:
    # (risco == "alto" OU bloqueio == Sim)
    intervencao = (df["risco_agente"] == "alto") | (df["bloqueio_agente"] == True)
    falha_real = df[coluna_falha] == 1
    sem_falha = df[coluna_falha] == 0

    # 2. Métrica Principal: F = A / T
    total_falhas_reais = int(falha_real.sum())          # T
    falhas_capturadas = int((intervencao & falha_real).sum())  # A
    recall = falhas_capturadas / total_falhas_reais if total_falhas_reais > 0 else 0.0

    # 3. Métrica Secundária: FP = B / S
    total_saudaveis = int(sem_falha.sum())              # S
    falsos_positivos = int((intervencao & sem_falha).sum())    # B
    taxa_fp = falsos_positivos / total_saudaveis if total_saudaveis > 0 else 0.0

    total_casos = len(df)

    print("=" * 60)
    print("AVALIAÇÃO DE PERFORMANCE DO AGENTE (agent-spec.md - PEAS)")
    print("=" * 60)
    print(f"Dataset avaliado:          {caminho_csv.name} ({total_casos} casos)")
    print("-" * 60)
    print("MÉTRICA PRINCIPAL: TAXA DE CAPTURA DE FALHAS (F = A / T)")
    print(f"  • Falhas reais (T):      {total_falhas_reais}")
    print(f"  • Falhas capturadas (A): {falhas_capturadas}")
    print(f"  • Resultado F:           {recall:.2%} (Limiar de sucesso: >= 97.35%)")
    status_f = "ATINGIDO" if round(recall, 4) >= 0.9735 else "NÃO ATINGIDO"
    print(f"  • Status:                [{status_f}]")
    print("-" * 60)
    print("MÉTRICA SECUNDÁRIA: TAXA DE FALSOS POSITIVOS (FP = B / S)")
    print(f"  • Casos saudáveis (S):   {total_saudaveis}")
    print(f"  • Falsos positivos (B):  {falsos_positivos}")
    print(f"  • Resultado FP:          {taxa_fp:.2%} (Limiar de sucesso: <= 7.02%)")
    status_fp = "ATINGIDO" if round(taxa_fp, 4) <= 0.0702 else "NÃO ATINGIDO"
    print(f"  • Status:                [{status_fp}]")
    print("=" * 60)


if __name__ == "__main__":
    main()

