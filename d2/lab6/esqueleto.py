"""Laboratório 06 — o agente de linha de base do seu domínio.

O agente mais simples que resolve uma fatia do problema, SEM modelo de
linguagem: percepção (o registro), decisão (regras explícitas), ação (a
recomendação) e medida (a métrica primária do `agent-spec.md`, sobre 30
casos). O número que sai daqui é a linha de base contra a qual o agente de
D10 vai ser comparado — sem ela, "melhorou" é opinião.

Estrutura do slide 22 do D2-E4: uma função `decidir(registro, estado)` com
duas condições — a primeira REATIVA (só a percepção do instante) e a
segunda consultando ESTADO INTERNO (o que o agente já observou do mundo).
Quem caracterizou o ambiente como totalmente observável pode APAGAR a
segunda condição e ficar com um reativo simples — e registra a escolha na
análise, porque o tipo de agente é parte do que a rubrica avalia.

Como usar:
    1. adapte as regras (os TODOs) e os limiares ao SEU domínio;
    2. aponte CAMINHO_DOS_CASOS para o seu conjunto de 30 casos rotulados
       (ou deixe no conjunto de reserva — ver COMO-USAR-A-RESERVA.pdf);
    3. rode:  python medir.py
    4. quando o baseline estiver pronto, copie as funções para
       `src/<projeto>/baseline.py` — é o caminho que a entrega final cobra.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

# --------------------------------------------------------------------------
# Configuração — a troca do dataset é UMA LINHA aqui (slide 29).
# --------------------------------------------------------------------------
CAMINHO_DOS_CASOS = "casos-ams.csv"
# Conjunto de reserva original do pacote:
# CAMINHO_DOS_CASOS = "casos-de-reserva.csv"

# --------------------------------------------------------------------------
# Os limiares das regras — Domínio: Assistente de Manutenção Segura (AMS)
# Baseados no AI4I 2020 Predictive Maintenance Dataset (ai4i2020.csv).
# --------------------------------------------------------------------------
LIMITE_DIF_TEMP = 8.6              # K — abaixo disso (com baixa rotação), HDF
LIMITE_ROTACAO_HDF = 1380          # rpm — abaixo disso (com baixa dif. temp.), HDF
POTENCIA_MIN = 3500.0              # W — abaixo disso, falha de potência (PWF)
POTENCIA_MAX = 9000.0              # W — acima disso, falha de potência (PWF)
LIMITE_DESGASTE_TWF = 200          # min — a partir disso, desgaste crítico (TWF)
LIMITE_OSF = {                     # min * Nm — acima disso, sobrecarga (OSF)
    "L": 11000.0,
    "M": 12000.0,
    "H": 13000.0,
}

# Limiares do estado interno (observabilidade parcial):
LIMITE_DESGASTE_INSPECAO = 190     # min — zona de fronteira antes de 200 min
FALHAS_PARA_INSPECAO = 2           # falhas recentes do mesmo Type → bloquear
JANELA_CASOS = 5                   # janela de observações recentes na linha

# --------------------------------------------------------------------------
# Estado interno — a memória do que o agente JÁ OBSERVOU do ambiente.
# O agente não sabe o futuro: ele acumula os desfechos que o ambiente
# revelou até agora, com política de esquecimento por janela (slide 24 do E2).
# --------------------------------------------------------------------------


class EstadoDaFrota:
    """O que o agente já observou: falhas por tipo de máquina, dentro da janela."""

    def __init__(self, janela_casos: int = JANELA_CASOS) -> None:
        self._janela = janela_casos
        self._falhas: list[tuple[str, int]] = []
        self._passo_atual: int = 0

    def falhas_recentes(self, familia: str) -> int:
        """Quantas falhas desta família (Type) o agente viu dentro da janela."""
        if self._passo_atual == 0:
            return 0
        limite = self._passo_atual - self._janela
        return sum(
            1 for familia_vista, passo in self._falhas
            if familia_vista == familia and passo > limite
        )

    def registrar_desfecho(self, registro: dict) -> None:
        """O ambiente revela o desfecho do caso — a percepção do próximo
        ciclo é maior do que a do anterior (parcialmente observável)."""
        self._passo_atual += 1
        falhou = int(registro.get("Machine failure", registro.get("falhou_depois", 0)))
        familia = str(registro.get("Type", registro.get("tipo_maquina", "")))
        if falhou == 1:
            self._falhas.append((familia, self._passo_atual))


# --------------------------------------------------------------------------
# A decisão — o coração do agente (slide 22)
# --------------------------------------------------------------------------

def _condicao_reativa_critica(registro: dict) -> bool:
    """Avalia os 4 modos de falha determinísticos sobre os sensores do instante."""
    tipo = str(registro["Type"])
    temp_ar = float(registro["Air temperature [K]"])
    temp_proc = float(registro["Process temperature [K]"])
    rotacao = float(registro["Rotational speed [rpm]"])
    torque = float(registro["Torque [Nm]"])
    desgaste = float(registro["Tool wear [min]"])

    potencia = torque * rotacao * (2 * math.pi) / 60.0

    hdf = (temp_proc - temp_ar < LIMITE_DIF_TEMP) and (rotacao < LIMITE_ROTACAO_HDF)
    pwf = (potencia < POTENCIA_MIN) or (potencia > POTENCIA_MAX)
    twf = desgaste >= LIMITE_DESGASTE_TWF
    osf = (desgaste * torque) > LIMITE_OSF.get(tipo, 12000.0)
    return hdf or pwf or twf or osf


def decidir(registro: dict, estado: EstadoDaFrota) -> tuple[str, bool]:
    """Uma rodada: percepção entra, ação `(risco, requer_bloqueio)` sai.

    Condição 1 (reativa): limiares físicos sobre o REGISTRO atual.
    Condição 2 (estado interno): histórico recente de falhas do mesmo Type
    combinado com desgaste na zona de fronteira (>= 190 min).
    A ordem importa: a primeira que casar decide.
    """
    if _condicao_reativa_critica(registro):
        return ("alto", True)
    if (estado.falhas_recentes(str(registro["Type"])) >= FALHAS_PARA_INSPECAO
            and float(registro["Tool wear [min]"]) >= LIMITE_DESGASTE_INSPECAO):
        return ("medio", True)
    return ("baixo", False)


def carregar_casos(caminho: str | Path) -> list[dict]:
    """Lê o CSV de casos do domínio (ai4i2020) na ordem sequencial de UDI."""
    with Path(caminho).open(encoding="utf-8-sig", newline="") as arquivo:
        casos = list(csv.DictReader(arquivo))
    casos.sort(key=lambda registro: int(registro["UDI"]))
    for registro in casos:
        registro["UDI"] = int(registro["UDI"])
        registro["id_caso"] = f"UDI-{registro['UDI']}"
        registro["Air temperature [K]"] = float(registro["Air temperature [K]"])
        registro["Process temperature [K]"] = float(registro["Process temperature [K]"])
        registro["Rotational speed [rpm]"] = float(registro["Rotational speed [rpm]"])
        registro["Torque [Nm]"] = float(registro["Torque [Nm]"])
        registro["Tool wear [min]"] = float(registro["Tool wear [min]"])
        registro["Machine failure"] = int(registro["Machine failure"])
        registro["falhou_depois"] = registro["Machine failure"]
        registro["acao_correta"] = (
            ("alto", True)
            if registro["Machine failure"] == 1
            else ("baixo", False)
        )
    return casos


if __name__ == "__main__":
    from medir import medir_e_imprimir

    medir_e_imprimir(CAMINHO_DOS_CASOS, decidir, EstadoDaFrota)
