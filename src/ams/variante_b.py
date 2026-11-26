"""Variante B do Assistente de Manutenção Segura (AMS) — D3 (AO1 e N2).

Implementa uma mudança real de comportamento sobre a linha de base (Variante A),
adicionando passos de verificação cruzada determinística para resolver os dois
padrões sistemáticos de erro diagnosticados na D2:

1. Verificação de Estresse Térmico Combinado:
   Captura falhas térmicas em alta temperatura de processo (>= 311.5 K) quando
   combinadas com baixa margem de dissipação (dif_temp < 8.6 K, ex.: UDI-4685)
   ou baixa rotação com alto torque (RPM < 1380 e Torque >= 50 Nm, ex.: UDI-5537).

2. Desgaste de Ferramenta em Dois Estágios (Severidade Operacional):
   Substitui o corte cego de 200 min por dois níveis:
   - Desgaste severo (>= 205 min): intervenção imediata.
   - Fronteira (200 a 204 min): exige confirmação de estresse adicional
     (margem térmica < 9.5 K ou alta rotação >= 1800 rpm). Evita falsos
     positivos em regime leve e frio (ex.: UDI-74 e UDI-157).

3. Estado Interno com Confirmação de Margem Térmica:
   Quando a família acumula >= 2 falhas recentes e desgaste >= 190 min, exige
   que a diferença térmica já apresente estreitamento (dif_temp < 10.0 K) antes
   de recomendar bloqueio. Preserva a captura de UDI-1997 e elimina os falsos
   positivos da família L em operação fria (UDI-72, UDI-73 e UDI-1241).

Uso:
    python src/ams/variante_b.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

from ams.baseline import (
    FALHAS_PARA_INSPECAO,
    LIMITE_DESGASTE_INSPECAO,
    LIMITE_DIF_TEMP,
    LIMITE_OSF,
    LIMITE_ROTACAO_HDF,
    POTENCIA_MAX,
    POTENCIA_MIN,
    RAIZ_DO_PACOTE,
    EstadoDaFrota,
    _intervencao,
    carregar_casos,
    decidir,
    medir_e_imprimir,
)

CAMINHO_CASOS_60 = RAIZ_DO_PACOTE / "d3" / "ao1" / "casos-ams-60.csv"
CAMINHO_ACERTOS_AO1 = RAIZ_DO_PACOTE / "d3" / "ao1" / "acertos.csv"

# --------------------------------------------------------------------------
# Limiares específicos da Variante B (Verificação Cruzada Multi-Critério)
# --------------------------------------------------------------------------
LIMITE_TEMP_PROC_ALTA = 311.5          # K — teto de alerta de temperatura de processo
LIMITE_TORQUE_ESTRESSE = 50.0          # Nm — torque elevado em baixa rotação
LIMITE_DESGASTE_SEVERO = 205           # min — desgaste crítico incondicional
LIMITE_DESGASTE_FRONTEIRA = 200        # min — início da fronteira de desgaste
LIMITE_DIF_TEMP_FRONTEIRA = 9.5        # K — estreitamento térmico na fronteira
LIMITE_ROTACAO_ALTA_DESGASTE = 1800    # rpm — velocidade severa para ferramenta gasta
LIMITE_DIF_TEMP_FROTA = 10.0           # K — confirmação térmica para alerta de frota


def _condicao_reativa_variante_b(registro: dict) -> bool:
    """Avalia modos físicos com verificação cruzada de estresse térmico e desgaste."""
    tipo = str(registro["Type"])
    temp_ar = float(registro["Air temperature [K]"])
    temp_proc = float(registro["Process temperature [K]"])
    rotacao = float(registro["Rotational speed [rpm]"])
    torque = float(registro["Torque [Nm]"])
    desgaste = float(registro["Tool wear [min]"])

    dif_temp = temp_proc - temp_ar
    potencia = torque * rotacao * (2 * math.pi) / 60.0

    # 1. Falha de dissipação de calor clássica + estresse térmico severo
    hdf_classico = (dif_temp < LIMITE_DIF_TEMP) and (rotacao < LIMITE_ROTACAO_HDF)
    estresse_termico = (temp_proc >= LIMITE_TEMP_PROC_ALTA) and (
        (dif_temp < LIMITE_DIF_TEMP)
        or (rotacao < LIMITE_ROTACAO_HDF and torque >= LIMITE_TORQUE_ESTRESSE)
    )

    # 2. Falha de potência e sobrecarga mecânica (OSF)
    pwf = (potencia < POTENCIA_MIN) or (potencia > POTENCIA_MAX)
    osf = (desgaste * torque) > LIMITE_OSF.get(tipo, 12000.0)

    # 3. Verificação de desgaste em dois estágios
    twf_severo = desgaste >= LIMITE_DESGASTE_SEVERO
    twf_fronteira_confirmado = (desgaste >= LIMITE_DESGASTE_FRONTEIRA) and (
        dif_temp < LIMITE_DIF_TEMP_FRONTEIRA or rotacao >= LIMITE_ROTACAO_ALTA_DESGASTE
    )

    return (
        hdf_classico
        or estresse_termico
        or pwf
        or osf
        or twf_severo
        or twf_fronteira_confirmado
    )


def decidir_variante_b(registro: dict, estado: EstadoDaFrota) -> tuple[str, bool]:
    """Decisão da Variante B: percepção + estado interno com confirmação física."""
    if _condicao_reativa_variante_b(registro):
        return ("alto", True)

    tipo = str(registro["Type"])
    desgaste = float(registro["Tool wear [min]"])
    dif_temp = float(registro["Process temperature [K]"]) - float(registro["Air temperature [K]"])

    if (
        estado.falhas_recentes(tipo) >= FALHAS_PARA_INSPECAO
        and desgaste >= LIMITE_DESGASTE_INSPECAO
        and dif_temp < LIMITE_DIF_TEMP_FROTA
    ):
        return ("medio", True)

    return ("baixo", False)


def avaliar_pareado(caminho: str | Path = CAMINHO_CASOS_60) -> list[dict]:
    """Avalia Variante A e Variante B sobre os mesmos casos na mesma ordem."""
    casos = carregar_casos(caminho)
    estado_a = EstadoDaFrota()
    estado_b = EstadoDaFrota()
    resultados: list[dict] = []

    for registro in casos:
        falha_real = int(registro.get("Machine failure", registro.get("falhou_depois", 0))) == 1

        decisao_a = decidir(registro, estado_a)
        interveio_a = _intervencao(decisao_a)
        acerto_a = int((falha_real and interveio_a) or (not falha_real and not interveio_a))
        estado_a.registrar_desfecho(registro)

        decisao_b = decidir_variante_b(registro, estado_b)
        interveio_b = _intervencao(decisao_b)
        acerto_b = int((falha_real and interveio_b) or (not falha_real and not interveio_b))
        estado_b.registrar_desfecho(registro)

        resultados.append({
            "id_caso": registro["id_caso"],
            "udi": int(registro["UDI"]),
            "falha_real": int(falha_real),
            "decisao_a": decisao_a,
            "decisao_b": decisao_b,
            "variante_a": acerto_a,
            "variante_b": acerto_b,
        })

    return resultados


def gerar_acertos_csv(
    caminho_casos: str | Path = CAMINHO_CASOS_60,
    destinos: tuple[str | Path, ...] = (CAMINHO_ACERTOS_AO1,),
) -> list[dict]:
    """Gera o arquivo acertos.csv (uma linha por caso, colunas variante_a e variante_b)."""
    pares = avaliar_pareado(caminho_casos)
    for destino in destinos:
        caminho_saida = Path(destino)
        caminho_saida.parent.mkdir(parents=True, exist_ok=True)
        with caminho_saida.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(["variante_a", "variante_b"])
            for item in pares:
                escritor.writerow([item["variante_a"], item["variante_b"]])
    return pares


if __name__ == "__main__":
    caminho = CAMINHO_CASOS_60 if CAMINHO_CASOS_60.is_file() else None
    if caminho:
        medir_e_imprimir(caminho=caminho, decidir_fn=decidir_variante_b)
        gerar_acertos_csv(caminho_casos=caminho)
    else:
        medir_e_imprimir(decidir_fn=decidir_variante_b)


