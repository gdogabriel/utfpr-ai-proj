"""Testes do Laboratório 06 — a prova de que o baseline e a medição estão de pé.

Como usar (da pasta do laboratório):
    python -m pytest teste.py -q

Quatro famílias:

  1. AS REGRAS — cada condição de `decidir` dispara no caso que a define,
     e a ORDEM das condições importa (a primeira que casa decide);
  2. O ESTADO INTERNO — falhas contam dentro da janela e envelhecem fora
     dela; sem desfecho, o estado não muda;
  3. O GABARITO DOS 30 CASOS — as 30 decisões do `esqueleto.py` sobre
     `casos-ams.csv`, caso a caso, e as métricas finais;
  4. A TROCA — o mesmo medidor rodando sobre OUTRO arquivo de casos, sem
     tocar em código: a troca do conjunto é uma linha (slide 29).
"""

from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

from medir import medir

_AQUI = Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("esqueleto", _AQUI / "esqueleto.py")
esqueleto = importlib.util.module_from_spec(_spec)
sys.modules["esqueleto"] = esqueleto
_spec.loader.exec_module(esqueleto)  # type: ignore[union-attr]

ESPERADO = {
    "UDI-1": ("baixo", False),
    "UDI-11": ("baixo", False),
    "UDI-21": ("baixo", False),
    "UDI-31": ("baixo", False),
    "UDI-41": ("baixo", False),
    "UDI-51": ("alto", True),
    "UDI-52": ("baixo", False),
    "UDI-70": ("alto", True),
    "UDI-72": ("medio", True),
    "UDI-73": ("medio", True),
    "UDI-74": ("alto", True),
    "UDI-78": ("alto", True),
    "UDI-87": ("baixo", False),
    "UDI-97": ("baixo", False),
    "UDI-107": ("baixo", False),
    "UDI-117": ("baixo", False),
    "UDI-157": ("alto", True),
    "UDI-161": ("alto", True),
    "UDI-162": ("alto", True),
    "UDI-169": ("alto", True),
    "UDI-1088": ("alto", True),
    "UDI-1222": ("baixo", False),
    "UDI-1325": ("alto", True),
    "UDI-1438": ("baixo", False),
    "UDI-1493": ("alto", True),
    "UDI-1997": ("medio", True),
    "UDI-3237": ("alto", True),
    "UDI-3761": ("alto", True),
    "UDI-4045": ("baixo", False),
    "UDI-4685": ("baixo", False),
}
ERROS_ESPERADOS = [
    "UDI-72",
    "UDI-73",
    "UDI-74",
    "UDI-157",
    "UDI-1438",
    "UDI-4045",
    "UDI-4685",
]


def _registro(**mudancas) -> dict:
    base = {
        "UDI": 1,
        "Product ID": "M14860",
        "Type": "M",
        "Air temperature [K]": 298.1,
        "Process temperature [K]": 308.6,
        "Rotational speed [rpm]": 1551.0,
        "Torque [Nm]": 42.8,
        "Tool wear [min]": 100.0,
        "Machine failure": 0,
    }
    base.update(mudancas)
    return base


# --- 1. as regras -----------------------------------------------------------

def test_condicao_reativa_para_com_desgaste_critico():
    estado = esqueleto.EstadoDaFrota()
    decisao = esqueleto.decidir(_registro(**{"Tool wear [min]": 205.0}), estado)
    assert decisao == ("alto", True)


def test_condicao_reativa_para_com_falha_dissipacao_calor():
    estado = esqueleto.EstadoDaFrota()
    decisao = esqueleto.decidir(
        _registro(**{
            "Air temperature [K]": 302.0,
            "Process temperature [K]": 310.0,  # dif = 8.0 < 8.6
            "Rotational speed [rpm]": 1350.0,  # < 1380
        }),
        estado,
    )
    assert decisao == ("alto", True)


def test_estado_interno_bloqueia_apos_duas_falhas_da_familia_com_desgaste_fronteira():
    estado = esqueleto.EstadoDaFrota()
    estado.registrar_desfecho(_registro(**{"Machine failure": 1}))  # 1ª falha
    assert esqueleto.decidir(_registro(**{"Tool wear [min]": 195.0}), estado) == ("baixo", False)
    estado.registrar_desfecho(_registro(**{"Machine failure": 1}))  # 2ª falha
    decisao = esqueleto.decidir(_registro(**{"Tool wear [min]": 195.0}), estado)
    assert decisao == ("medio", True)


def test_a_ordem_das_condicoes_importa():
    estado = esqueleto.EstadoDaFrota()
    for _ in range(2):
        estado.registrar_desfecho(_registro(**{"Machine failure": 1}))
    critico = _registro(**{"Tool wear [min]": 210.0})
    assert esqueleto.decidir(critico, estado) == ("alto", True), (
        "com leitura crítica, classifica risco alto — a condição reativa vem primeiro"
    )


def test_familia_diferente_nao_herda_as_falhas():
    estado = esqueleto.EstadoDaFrota()
    estado.registrar_desfecho(_registro(**{"Type": "L", "Machine failure": 1}))
    estado.registrar_desfecho(_registro(**{"Type": "L", "Machine failure": 1}))
    decisao = esqueleto.decidir(
        _registro(**{"Type": "H", "Tool wear [min]": 195.0}),
        estado,
    )
    assert decisao == ("baixo", False)


# --- 2. o estado interno e a janela -----------------------------------------

def test_falha_envelhece_fora_da_janela():
    estado = esqueleto.EstadoDaFrota()
    estado.registrar_desfecho(_registro(**{"Machine failure": 1}))
    estado.registrar_desfecho(_registro(**{"Machine failure": 1}))
    # Avança JANELA_CASOS registros sem falha para expirar as falhas antigas
    for _ in range(esqueleto.JANELA_CASOS):
        estado.registrar_desfecho(_registro(**{"Machine failure": 0}))
    decisao = esqueleto.decidir(_registro(**{"Tool wear [min]": 195.0}), estado)
    assert decisao == ("baixo", False)


def test_sem_desfecho_o_estado_nao_muda():
    estado = esqueleto.EstadoDaFrota()
    estado.registrar_desfecho(_registro(**{"Machine failure": 0}))
    assert estado.falhas_recentes("M") == 0


# --- 3. o gabarito dos 30 casos ---------------------------------------------

def test_as_trinta_decisoes_batem_com_o_gabarito():
    casos = esqueleto.carregar_casos(_AQUI / esqueleto.CAMINHO_DOS_CASOS)
    estado = esqueleto.EstadoDaFrota()
    divergentes = []
    for registro in casos:
        decisao = esqueleto.decidir(registro, estado)
        if decisao != ESPERADO[registro["id_caso"]]:
            divergentes.append((registro["id_caso"], decisao))
        estado.registrar_desfecho(registro)
    assert not divergentes, f"decisões divergentes do gabarito: {divergentes}"


def test_as_metricas_finais_dos_trinta_casos():
    resultado = medir(_AQUI / esqueleto.CAMINHO_DOS_CASOS)
    assert resultado["total"] == 30
    assert (resultado["falhas_capturadas"], resultado["total_falhas_reais"]) == (12, 15)
    assert round(resultado["recall"], 4) == 0.8000
    assert (resultado["acertos"], round(resultado["valor"], 4)) == (23, 0.7667)
    assert [e["id_caso"] for e in resultado["erros"]] == ERROS_ESPERADOS


# --- 4. a troca do conjunto é uma linha -------------------------------------

def test_o_medidor_roda_sobre_outro_arquivo_sem_tocar_em_codigo(tmp_path):
    casos_novos = tmp_path / "meus_casos.csv"
    with casos_novos.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            "UDI", "Product ID", "Type", "Air temperature [K]",
            "Process temperature [K]", "Rotational speed [rpm]",
            "Torque [Nm]", "Tool wear [min]", "Machine failure",
            "TWF", "HDF", "PWF", "OSF", "RNF",
        ])
        escritor.writerow([
            1, "M14860", "M", 298.1, 308.6, 1551, 42.8, 210, 1, 1, 0, 0, 0, 0,
        ])
        escritor.writerow([
            2, "L47181", "L", 298.2, 308.7, 1408, 46.3, 10, 0, 0, 0, 0, 0, 0,
        ])
    resultado = medir(casos_novos)
    assert resultado["total"] == 2
    assert resultado["acertos"] == 2
    assert resultado["recall"] == 1.0
