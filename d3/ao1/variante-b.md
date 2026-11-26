# Variante B do Agente AMS — Mudanças no Código

Este documento explica o que muda no código da **Variante B** ([`src/ams/variante_b.py`](../../src/ams/variante_b.py#L67-L122)) em relação à **linha de base** (`Variante A`, [`src/ams/baseline.py`](../../src/ams/baseline.py#L75-L106)).

## 1. Estrutura geral

A Variante B reutiliza a classe `EstadoDaFrota`, os limiares base e as funções de leitura de [`src/ams/baseline.py`](../../src/ams/baseline.py). A mudança real de comportamento ocorre em duas funções:

1. `_condicao_reativa_variante_b(registro)` substitui `_condicao_reativa_critica(registro)`.
2. `decidir_variante_b(registro, estado)` substitui `decidir(registro, estado)`.

## 2. O que permanece igual

As regras de potência e de sobrecarga mecânica continuam idênticas às da linha de base:

- **`pwf`:** `potencia < POTENCIA_MIN` (`3500.0 W`) ou `potencia > POTENCIA_MAX` (`9000.0 W`).
- **`osf`:** `(desgaste * torque) > LIMITE_OSF[tipo]`.
- **Saídas:** `("alto", True)` na condição reativa, `("medio", True)` no estado interno e `("baixo", False)` quando nenhuma regra dispara.

## 3. O que muda nas regras de decisão

| Bloco de código | Linha de base (`baseline.py`) | Variante B (`variante_b.py`) |
|---|---|---|
| **Condição térmica** | Avalia apenas `hdf`: `dif_temp < LIMITE_DIF_TEMP` (`8.6 K`) e `rotacao < LIMITE_ROTACAO_HDF` (`1380 rpm`). | Mantém `hdf_classico` e adiciona `estresse_termico`: quando `temp_proc >= LIMITE_TEMP_PROC_ALTA` (`311.5 K`), retorna `True` se `dif_temp < 8.6 K` ou se `rotacao < 1380 rpm` e `torque >= LIMITE_TORQUE_ESTRESSE` (`50.0 Nm`). |
| **Desgaste da ferramenta** | Avalia corte único `twf`: `desgaste >= LIMITE_DESGASTE_TWF` (`200 min`). | Divide em dois estágios: `twf_severo` (`desgaste >= 205 min`) dispara direto; `twf_fronteira_confirmado` (`desgaste >= 200 min`) exige `dif_temp < LIMITE_DIF_TEMP_FRONTEIRA` (`9.5 K`) ou `rotacao >= LIMITE_ROTACAO_ALTA_DESGASTE` (`1800 rpm`). |
| **Estado interno (`EstadoDaFrota`)** | Em `decidir`, bloqueia quando `estado.falhas_recentes(tipo) >= 2` e `desgaste >= 190 min`. | Em `decidir_variante_b`, exige `estado.falhas_recentes(tipo) >= 2`, `desgaste >= 190 min` e `dif_temp < LIMITE_DIF_TEMP_FROTA` (`10.0 K`). |

## 4. Funções adicionais para avaliação pareada

O arquivo [`src/ams/variante_b.py`](../../src/ams/variante_b.py#L125-L172) inclui duas funções que não existem em `baseline.py`:

- `avaliar_pareado(caminho)`: executa `decidir` e `decidir_variante_b` sobre os mesmos casos na mesma ordem, usando instâncias separadas de `EstadoDaFrota`.
- `gerar_acertos_csv(caminho_casos, destinos)`: grava os resultados binários (`0` e `1`) nas colunas `variante_a` e `variante_b`.

## 5. Como verificar no código

1. Execute a suíte de testes unitários da Variante B:
   `npm run d3:ao1:testes`
2. Resultado esperado: todos os `6` testes de [`tests/test_variante_b.py`](../../tests/test_variante_b.py) passam com código `0`.
