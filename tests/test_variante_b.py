"""Testes da Variante B (`src/ams/variante_b.py`) — D3 (AO1 e N2).

Valida as mudanças reais de comportamento da Variante B sobre a Variante A:
  1. Verificação de estresse térmico combinado (alta temperatura de processo);
  2. Desgaste de ferramenta em dois estágios (200-204 min exige estresse, >= 205 min direto);
  3. Estado interno (`EstadoDaFrota`) com confirmação de margem térmica (< 10.0 K);
  4. Medição pareada sobre o conjunto ampliado de 60 casos (`d3/ao1/casos-ams-60.csv`).
"""

from __future__ import annotations

from ams import baseline, variante_b


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


def test_estresse_termico_captura_falha_com_alta_temp_processo_e_dif_baixa():
    """Captura UDI-4685 (TProc=311.8 K, DifT=8.2 K, mesmo com RPM=1421 >= 1380)."""
    estado = baseline.EstadoDaFrota()
    reg = _registro(**{
        "Air temperature [K]": 303.6,
        "Process temperature [K]": 311.8,
        "Rotational speed [rpm]": 1421.0,
        "Torque [Nm]": 44.8,
        "Tool wear [min]": 101.0,
    })
    assert baseline.decidir(reg, estado) == ("baixo", False)
    assert variante_b.decidir_variante_b(reg, estado) == ("alto", True)


def test_desgaste_em_dois_estagios_evita_falso_positivo_em_regime_frio():
    """Evita falso positivo em UDI-74 (Wear=200 min, DifT=10.1 K, RPM=1592)."""
    estado = baseline.EstadoDaFrota()
    reg = _registro(**{
        "Type": "L",
        "Air temperature [K]": 299.0,
        "Process temperature [K]": 309.1,
        "Rotational speed [rpm]": 1592.0,
        "Torque [Nm]": 35.0,
        "Tool wear [min]": 200.0,
    })
    assert baseline.decidir(reg, estado) == ("alto", True)
    assert variante_b.decidir_variante_b(reg, estado) == ("baixo", False)


def test_desgaste_fronteira_dispara_quando_acompanhado_de_alta_rotacao():
    """Captura UDI-9175 (Wear=200 min, RPM=1871 >= 1800)."""
    estado = baseline.EstadoDaFrota()
    reg = _registro(**{
        "Type": "L",
        "Air temperature [K]": 297.8,
        "Process temperature [K]": 308.9,
        "Rotational speed [rpm]": 1871.0,
        "Torque [Nm]": 25.6,
        "Tool wear [min]": 200.0,
    })
    assert variante_b.decidir_variante_b(reg, estado) == ("alto", True)


def test_estado_interno_exige_confirmacao_termica_para_bloquear():
    """Evita falso positivo em UDI-72/73 (DifT=10.2 K >= 10.0 K) e mantém captura de UDI-1997 (DifT=9.6 K)."""
    estado = baseline.EstadoDaFrota()
    estado.registrar_desfecho(_registro(**{"Type": "M", "Machine failure": 1}))
    estado.registrar_desfecho(_registro(**{"Type": "M", "Machine failure": 1}))

    # Máquina saudável com folga térmica (DifT = 10.5 K >= 10.0 K)
    reg_frio = _registro(**{
        "Type": "M",
        "Air temperature [K]": 298.0,
        "Process temperature [K]": 308.5,
        "Tool wear [min]": 196.0,
    })
    assert baseline.decidir(reg_frio, estado) == ("medio", True)
    assert variante_b.decidir_variante_b(reg_frio, estado) == ("baixo", False)

    # Máquina com margem térmica estreita (DifT = 9.6 K < 10.0 K, caso UDI-1997)
    reg_quente = _registro(**{
        "Type": "M",
        "Air temperature [K]": 298.4,
        "Process temperature [K]": 308.0,
        "Tool wear [min]": 198.0,
    })
    assert variante_b.decidir_variante_b(reg_quente, estado) == ("medio", True)


def test_medicao_sobre_60_casos_supera_baseline():
    res_a = baseline.medir(variante_b.CAMINHO_CASOS_60, decidir_fn=baseline.decidir)
    res_b = baseline.medir(variante_b.CAMINHO_CASOS_60, decidir_fn=variante_b.decidir_variante_b)

    assert res_a["total"] == 60
    assert res_b["total"] == 60
    assert res_b["acertos"] == 56
    assert res_a["acertos"] == 49
    assert res_b["recall"] == 27 / 30
    assert res_b["taxa_fp"] == 1 / 30


def test_geracao_acertos_csv_formato_e_valores(tmp_path):
    saida_temp = tmp_path / "acertos.csv"
    pares = variante_b.gerar_acertos_csv(destinos=(saida_temp,))

    assert len(pares) == 60
    assert sum(p["variante_a"] for p in pares) == 49
    assert sum(p["variante_b"] for p in pares) == 56

    linhas = saida_temp.read_text(encoding="utf-8").strip().splitlines()
    assert linhas[0] == "variante_a,variante_b"
    assert len(linhas) == 61
    for linha in linhas[1:]:
        partes = linha.split(",")
        assert len(partes) == 2
        assert partes[0] in {"0", "1"}
        assert partes[1] in {"0", "1"}


