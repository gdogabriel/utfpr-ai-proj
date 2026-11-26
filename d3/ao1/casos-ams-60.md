# Conjunto Ampliado de Avaliação — 60 Casos do Domínio AMS

Este documento descreve a construção e a distribuição do arquivo [`casos-ams-60.csv`](casos-ams-60.csv), utilizado na Atividade Orientada 1 (AO1) e na N2 da disciplina D3.

---

## 1. Visão Geral e Objetivo

- **Origem dos dados:** Extraídos do *AI4I 2020 Predictive Maintenance Dataset* ([`data/raw/ai4i2020.csv`](../../data/raw/ai4i2020.csv)).
- **Objetivo:** Ampliar o conjunto de avaliação de `30` para `60` casos rotulados para avaliar a **linha de base** (`Variante A`) e a **Variante B** sobre os mesmos casos (reconhecendo que, segundo `D3-AO1, p. 1`, `60` casos distinguem do acaso apenas diferenças acima de `10` a `12` pontos percentuais).
- **Balanceamento do conjunto ($n = 60$):**
  - **30 casos de falha real** (`Machine failure == 1`)
  - **30 casos normais/saudáveis** (`Machine failure == 0`)

---

## 2. Estrutura dos 60 Casos

### Bloco 1: Os 30 casos originais da D2 (Linhas 1 a 30)
- Mantidos de forma idêntica ao arquivo [`d2/lab6/casos-ams.csv`](../../d2/lab6/casos-ams.csv).
- Preserva a continuidade histórica e permite comparar o agente de **linha de base** diretamente sobre a mesma base.
- Contém:
  - 15 falhas reais da D2.
  - 15 casos normais da D2 (incluindo os 4 falsos positivos de fronteira e o caso atípico de falha aleatória).

### Bloco 2: Os 30 novos casos adicionados na D3 (Linhas 31 a 60)
Gerados de forma reprodutível pelo script [`casos-ams-60.py`](casos-ams-60.py) a partir de [`data/raw/ai4i2020.csv`](../../data/raw/ai4i2020.csv) (excluindo os 30 `UDI`s da D2) com semente fixa (`SEMENTE = 42`) e filtros explícitos por estrato.

#### A. 15 Novas Falhas Reais (`Machine failure == 1`):
1. **Falha de ferramenta (`TWF` puro):** 3 casos (`UDI`s `2245`, `8610`, `9175`).
2. **Dissipação de calor (`HDF` puro):** 3 casos (`UDI`s `4250`, `4537`, `4545`).
3. **Falha de potência (`PWF` puro):** 3 casos (`UDI`s `443`, `1017`, `4003`).
4. **Sobrecarga mecânica (`OSF` puro):** 2 casos (`UDI`s `587`, `4815`).
5. **Falha combinada (`soma_modos >= 2`):** 2 casos — `UDI 1497` (`PWF` + `OSF`) e `UDI 5395` (`PWF` + `OSF`).
6. **Falha geral sem modo específico marcado (`soma_modos == 0`):** 2 casos (`UDI 2750` e `UDI 5537`), preservando a inconsistência registrada na D1.

#### B. 15 Novos Casos Normais (`Machine failure == 0`):
1. **Desgaste alto (`175 <= Tool wear <= 210` min):** 5 casos (`UDI`s `404`, `1241`, `5053`, `6574`, `6668`).
2. **Fronteira térmica ou de potência (`Tool wear < 175` min com `dif_temp < 9.0 K`, `potencia < 3800 W` ou `potencia > 8200 W`):** 5 casos (`UDI`s `2103`, `2836`, `4159`, `4353`, `4915`).
3. **Operação de rotina (`Tool wear < 175` min, `dif_temp >= 9.0 K` e `3800 <= potencia <= 8200 W`):** 5 casos estratificados por tipo — `2` `H` (`1847`, `6100`), `2` `M` (`5165`, `8700`) e `1` `L` (`3917`).

---

## 3. Lista de UDIs Selecionados

### Casos da D2 (1 a 30):
`[1, 11, 21, 31, 41, 51, 52, 70, 72, 73, 74, 78, 87, 97, 107, 117, 157, 161, 162, 169, 1088, 1222, 1325, 1438, 1493, 1997, 3237, 3761, 4045, 4685]`

### Novos Casos Adicionados na D3 (31 a 60):
`[404, 443, 587, 1017, 1241, 1497, 1847, 2103, 2245, 2750, 2836, 3917, 4003, 4159, 4250, 4353, 4537, 4545, 4815, 4915, 5053, 5165, 5395, 5537, 6100, 6574, 6668, 8610, 8700, 9175]`

---

## 4. Relevância para a AO1 (Etapa 1)

- **Mesmos casos:** As duas variantes do agente (`Variante A` e `Variante B`) são avaliadas estritamente sobre estes mesmos `60` casos.
- **Arquivo de acertos:** A execução sobre este conjunto gera [`acertos.csv`](acertos.csv) com `60` linhas e valores binários (`1` para acerto, `0` para erro), alimentando a análise exploratória e a medição desta entrega.

