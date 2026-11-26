# Comparação de Dados — Linha de Base vs. Variante B

Este documento analisa os resultados medidos da **linha de base** (`Variante A`) e da **Variante B** sobre os `60` casos de [`casos-ams-60.csv`](casos-ams-60.csv), registrados em [`acertos.csv`](acertos.csv). As mudanças de código estão descritas em [`variante-b.md`](variante-b.md).

## 1. Métricas observadas nos 60 casos

| Métrica | Linha de base (`Variante A`) | Variante B | Diferença |
|---|---:|---:|---:|
| **Acertos totais** | `49/60` (`81,7%`) | `56/60` (`93,3%`) | `+7` casos (`+11,7` p.p.) |
| **Métrica primária: taxa de captura de falhas** | `25/30` (`83,3%`) | `27/30` (`90,0%`) | `+2` falhas (`+6,7` p.p.) |
| **Falsos positivos** | `6/30` (`20,0%`) | `1/30` (`3,33%`) | `-5` alarmes falsos (`-16,7` p.p.) |

## 2. Cruzamento de acertos nos 60 casos (`acertos.csv`)

A tabela abaixo resume os acertos das duas variantes avaliadas sobre os mesmos `60` casos de [`acertos.csv`](acertos.csv):

| | Variante B acertou (`1`) | Variante B errou (`0`) | Total |
|---|---:|---:|---:|
| **Linha de base acertou (`1`)** | `49` | `0` | `49` |
| **Linha de base errou (`0`)** | `7` | `4` | `11` |
| **Total** | `56` | `4` | `60` |

As variantes concordam em `53` casos (`49` acertos e `4` erros) e divergem em `7` casos, todos favoráveis à Variante B (`7` contra `0`).

## 3. Os 7 casos em que as decisões divergem

| Caso | Falha real | Linha de base (`Variante A`) | Variante B | Dados observados em [`casos-ams-60.csv`](casos-ams-60.csv) |
|---|---|---|---|---|
| `UDI-72` | `0` (Normal) | `('medio', True)` (erro) | `('baixo', False)` (acerto) | `Type = L`, `Tool wear = 196 min`, `dif_temp = 10.2 K` |
| `UDI-73` | `0` (Normal) | `('medio', True)` (erro) | `('baixo', False)` (acerto) | `Type = L`, `Tool wear = 198 min`, `dif_temp = 10.2 K` |
| `UDI-74` | `0` (Normal) | `('alto', True)` (erro) | `('baixo', False)` (acerto) | `Type = L`, `Tool wear = 200 min`, `dif_temp = 10.1 K`, `rotacao = 1592 rpm` |
| `UDI-157` | `0` (Normal) | `('alto', True)` (erro) | `('baixo', False)` (acerto) | `Type = M`, `Tool wear = 203 min`, `dif_temp = 9.7 K`, `rotacao = 1495 rpm` |
| `UDI-1241` | `0` (Normal) | `('medio', True)` (erro) | `('baixo', False)` (acerto) | `Type = L`, `Tool wear = 192 min`, `dif_temp = 11.4 K` |
| `UDI-4685` | `1` (Falha) | `('baixo', False)` (erro) | `('alto', True)` (acerto) | `Type = M`, `Process temperature = 311.8 K`, `dif_temp = 8.2 K`, `rotacao = 1421 rpm` |
| `UDI-5537` | `1` (Falha) | `('baixo', False)` (erro) | `('alto', True)` (acerto) | `Type = M`, `Process temperature = 311.8 K`, `dif_temp = 9.5 K`, `rotacao = 1363 rpm`, `Torque = 54.0 Nm` |

## 4. Os 4 casos em que ambas erram

Conforme a saída de `npm run d3:ao1:variante-b`, as duas variantes erram os mesmos `4` casos:

- **Falsos negativos (`3` casos):** `UDI-1438`, `UDI-2750` e `UDI-4045` (decidiram `('baixo', False)` em casos com `Machine failure = 1`).
- **Falso positivo (`1` caso):** `UDI-6668` (decidiu `('alto', True)` em caso normal com `Machine failure = 0`).

## 5. Comandos para reproduzir os números

1. Execute a medição da linha de base sobre os `60` casos:
   `.venv/bin/python -c "from ams.baseline import medir_e_imprimir; medir_e_imprimir('d3/ao1/casos-ams-60.csv')"`
2. Execute a medição da Variante B e grave [`acertos.csv`](acertos.csv):
   `npm run d3:ao1:variante-b`
