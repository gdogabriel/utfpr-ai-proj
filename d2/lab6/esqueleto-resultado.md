# Resultado — Laboratório 06 (Agente de Linha de Base)

## 1. Medição sobre os 30 casos (`python medir.py`)

```text
Métrica primária (PEAS): Taxa de captura de falhas / Recall (F = A / T: (risco == 'alto' OU bloqueio == True) sobre o total de falhas reais)
Valor (F = A / T): 12/15 = 0.8 (80.00%)
Métrica secundária (FP = B / S): 4/15 = 0.2667 (26.67%)
Acerto global (modelo original): 23/30 = 0.7667 (76.67%)
Conjunto: casos-ams.csv — 30 casos rotulados {('baixo', False): 15, ('alto', True): 15}
Onde erra (o rótulo que o agente não deu):
  caso UDI-72: decidiu ('medio', True), correto era ('baixo', False)
  caso UDI-73: decidiu ('medio', True), correto era ('baixo', False)
  caso UDI-74: decidiu ('alto', True), correto era ('baixo', False)
  caso UDI-157: decidiu ('alto', True), correto era ('baixo', False)
  caso UDI-1438: decidiu ('baixo', False), correto era ('alto', True)
  caso UDI-4045: decidiu ('baixo', False), correto era ('alto', True)
  caso UDI-4685: decidiu ('baixo', False), correto era ('alto', True)
```

---

## 2. Análise dos erros (duas frases)

> **Onde erra:** O agente erra por excesso de cautela em 4 máquinas saudáveis na fronteira de desgaste (`UDI-72` e `UDI-73` por bloqueio preventivo do estado interno; `UDI-74` e `UDI-157` por desgaste $\ge 200\text{ min}$ sem quebra) e deixa passar 3 falhas reais que ocorrem fora dos limiares fixos (`UDI-1438`, `UDI-4045` e `UDI-4685`).
>
> **Por que erra:** O erro é sistemático porque regras determinísticas de corte e contagem simples de falhas recentes não capturam interações não lineares entre variáveis contínuas (como $\Delta T = 8{,}2\text{ K}$ com rotação de $1421\text{ rpm}$ no `UDI-4685`) nem separam desgaste crítico sem quebra de falha iminente, o que exige combinar verificações especializadas e inferência probabilística.

---

## 3. Código do Agente de Linha de Base (`esqueleto.py` / `src/ams/baseline.py`)

```python
from __future__ import annotations

import csv
import math
from pathlib import Path

CAMINHO_DOS_CASOS = "casos-ams.csv"

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

LIMITE_DESGASTE_INSPECAO = 190     # min — zona de fronteira antes de 200 min
FALHAS_PARA_INSPECAO = 2           # falhas recentes do mesmo Type → bloquear
JANELA_CASOS = 5                   # janela de observações recentes na linha


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
    """Uma rodada: percepção entra, ação `(risco, requer_bloqueio)` sai."""
    if _condicao_reativa_critica(registro):
        return ("alto", True)
    if (estado.falhas_recentes(str(registro["Type"])) >= FALHAS_PARA_INSPECAO
            and float(registro["Tool wear [min]"]) >= LIMITE_DESGASTE_INSPECAO):
        return ("medio", True)
    return ("baixo", False)
```

