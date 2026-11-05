"""Agente de linha de base do Assistente de Manutenção Segura (AMS).

Implementa o agente sem modelo de linguagem (Laboratório 06 — D2) sobre 30
casos rotulados do dataset AI4I 2020 (`d2/lab6/casos-ams.csv`):
  - Percepção: leitura do registro de sensores da máquina (`carregar_casos`).
  - Estado interno: memória das falhas recentes por família (`EstadoDaFrota`).
  - Decisão: condição reativa + condição com estado interno (`decidir`).
  - Ação: tupla `(risco, requer_bloqueio)` alinhada aos atuadores do PEAS.
  - Medida: cálculo da métrica primária do PEAS ($F = A / T$, Recall) e da
    métrica secundária ($FP = B / S$) sobre os 30 casos (`medir`).

Uso:
    python src/ams/baseline.py
"""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path

RAIZ_DO_PACOTE = Path(__file__).resolve().parent.parent.parent
CAMINHO_DOS_CASOS = RAIZ_DO_PACOTE / "d2" / "lab6" / "casos-ams.csv"

# --------------------------------------------------------------------------
# Limiares das regras — Domínio: Assistente de Manutenção Segura (AMS)
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


def carregar_casos(caminho: str | Path = CAMINHO_DOS_CASOS) -> list[dict]:
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


def _intervencao(decisao: tuple[str, bool]) -> bool:
    """Critério de intervenção do PEAS (`agent-spec.md`):
    `(risco == "alto" OU bloqueio == Sim)`.
    """
    risco, requer_bloqueio = decisao
    return risco == "alto" or requer_bloqueio is True


def medir(caminho: str | Path = CAMINHO_DOS_CASOS, decidir_fn=None, classe_estado=None) -> dict:
    """Roda o agente sobre os 30 casos e devolve o resultado da medição."""
    decidir_fn = decidir_fn or decidir
    classe_estado = classe_estado or EstadoDaFrota
    casos = carregar_casos(caminho)
    estado = classe_estado()
    acertos = 0
    erros: list[dict] = []

    total_falhas_reais = 0      # T (Machine failure == 1)
    falhas_capturadas = 0       # A ((risco == "alto" OU bloqueio == True) E Machine failure == 1)
    total_saudaveis = 0         # S (Machine failure == 0)
    falsos_positivos = 0        # B ((risco == "alto" OU bloqueio == True) E Machine failure == 0)

    for registro in casos:
        decisao = decidir_fn(registro, estado)
        correta = registro["acao_correta"]
        falha_real = int(registro.get("Machine failure", registro.get("falhou_depois", 0))) == 1
        interveio = _intervencao(decisao)

        if falha_real:
            total_falhas_reais += 1
            if interveio:
                falhas_capturadas += 1
        else:
            total_saudaveis += 1
            if interveio:
                falsos_positivos += 1

        acertou_caso = (falha_real and interveio) or (not falha_real and not interveio)
        if acertou_caso:
            acertos += 1
        else:
            erros.append({
                "id_caso": registro["id_caso"],
                "decidiu": decisao,
                "correta": correta,
            })
        estado.registrar_desfecho(registro)

    total = len(casos)
    rotulos = Counter(registro["acao_correta"] for registro in casos)
    recall = falhas_capturadas / total_falhas_reais if total_falhas_reais else 0.0
    taxa_fp = falsos_positivos / total_saudaveis if total_saudaveis else 0.0

    return {
        "caminho": str(Path(caminho).name),
        "total": total,
        "acertos": acertos,
        "valor": acertos / total if total else 0.0,
        "falhas_capturadas": falhas_capturadas,
        "total_falhas_reais": total_falhas_reais,
        "recall": recall,
        "falsos_positivos": falsos_positivos,
        "total_saudaveis": total_saudaveis,
        "taxa_fp": taxa_fp,
        "distribuicao": dict(rotulos),
        "erros": erros,
    }


def imprimir(resultado: dict, nome_da_metrica: str) -> None:
    """Imprime as informações obrigatórias do slide 28 e a lista de erros (slide 30)."""
    print(f"Métrica primária (PEAS): {nome_da_metrica}")
    print(f"Valor (F = A / T): {resultado['falhas_capturadas']}/{resultado['total_falhas_reais']} = "
          f"{round(resultado['recall'], 4)} ({resultado['recall']:.2%})")
    print(f"Métrica secundária (FP = B / S): {resultado['falsos_positivos']}/{resultado['total_saudaveis']} = "
          f"{round(resultado['taxa_fp'], 4)} ({resultado['taxa_fp']:.2%})")
    print(f"Acerto global (modelo original): {resultado['acertos']}/{resultado['total']} = "
          f"{round(resultado['valor'], 4)} ({resultado['valor']:.2%})")
    print(f"Conjunto: {resultado['caminho']} — {resultado['total']} casos "
          f"rotulados {resultado['distribuicao']}")
    if resultado["erros"]:
        print("Onde erra (o rótulo que o agente não deu):")
        for erro in resultado["erros"]:
            print(f"  caso {erro['id_caso']}: decidiu "
                  f"{erro['decidiu']}, correto era {erro['correta']}")
    else:
        print("Onde erra: em nenhum dos casos — cuidado com um conjunto só "
              "de casos fáceis (slide 24: número bonito e inútil).")


def medir_e_imprimir(caminho: str | Path = CAMINHO_DOS_CASOS, decidir_fn=None, classe_estado=None) -> None:
    resultado = medir(caminho, decidir_fn, classe_estado)
    imprimir(resultado, "Taxa de captura de falhas / Recall "
                        "(F = A / T: (risco == 'alto' OU bloqueio == True) sobre o total de falhas reais)")


if __name__ == "__main__":
    medir_e_imprimir()

