# Relatório de desempenho da linha de base — modelo

<!--
Item 3 da N2. Este relatório tem as quatro informações que o slide 28 do
E4 cobra, mais a leitura de onde erra (slide 30) — a saída do medir.py já
traz quase tudo pronto: rode `python medir.py` na pasta do D2-06 (ou do
seu projeto) e cole no lugar marcado. Responda NOS COLCHETES, apagando
nada das seções.
-->

**Projeto:** Assistente de Manutenção Segura (AMS) · **Data:** 05/11/2026

## 1. A métrica primária

- **Métrica primária — Taxa de captura de falhas (`Recall`, $F = A / T$):** mede a proporção de falhas reais que o agente bloqueia antes do acidente. O script divide as falhas reais bloqueadas ($A$, onde `(risco == "alto" OU requer_bloqueio == true) E Machine failure == 1`) pelo total de falhas reais do conjunto ($T$, onde `Machine failure == 1`).
- **Métrica secundária — Taxa de falsos positivos ($FP = B / S$):** mede a proporção de máquinas saudáveis que o agente bloqueia sem necessidade. O script divide as máquinas saudáveis bloqueadas ($B$, onde `(risco == "alto" OU requer_bloqueio == true) E Machine failure == 0`) pelo total de máquinas saudáveis ($S$, onde `Machine failure == 0`).
- **Acerto global (`acertos / 30`):** mede o total de decisões idênticas ao rótulo esperado sobre os 30 casos.

## 2. O valor

```text
Métrica primária (PEAS): Taxa de captura de falhas / Recall (F = A / T: (risco == 'alto' OU bloqueio == True) sobre o total de falhas reais)
Valor (F = A / T): 12/15 = 0.8 (80.00%)
Métrica secundária (FP = B / S): 4/15 = 0.2667 (26.67%)
Acerto global (modelo original): 23/30 = 0.7667 (76.67%)
Conjunto: casos-ams.csv — 30 casos rotulados {('baixo', False): 15, ('alto', True): 15}
```

## 3. O conjunto

**Arquivo:** `d2/lab6/casos-ams.csv`. O conjunto contém 30 casos reais extraídos de `data/raw/ai4i2020.csv` (**AI4I 2020 Predictive Maintenance Dataset**), ordenados por `UDI`. O projeto não usa o conjunto de reserva. Os 30 casos têm distribuição balanceada entre 15 máquinas com falha (`('alto', True)`) e 15 máquinas saudáveis (`('baixo', False)`):

- **20 casos fáceis:** 10 máquinas saudáveis longe dos limiares (`UDI` `1`, `11`, `21`, `31`, `41`, `52`, `87`, `97`, `107`, `117`) e 10 falhas claras nos 4 modos físicos (`HDF`: `3237`, `3761`; `PWF`: `51`, `70`, `169`, `1325`, `1493`; `OSF`: `161`, `162`; `TWF`: `78`, `1088`).
- **7 casos difíceis (zona de fronteira):** 4 máquinas saudáveis no limite de desgaste (`UDI-72`, `UDI-73`, `UDI-74` e `UDI-157`), 1 falha por desgaste em `198 min` (`UDI-1997`, capturada por `EstadoDaFrota`) e 1 falha térmica na fronteira (`UDI-4685`).
- **3 casos atípicos:** 1 máquina saudável com flag de falha aleatória (`UDI-1222`, onde `RNF=1` e `Machine failure=0`) e 2 quebras reais com sensores normais (`UDI-1438` e `UDI-4045`).

## 4. Onde o agente erra

```text
Onde erra (o rótulo que o agente não deu):
  caso UDI-72: decidiu ('medio', True), correto era ('baixo', False)
  caso UDI-73: decidiu ('medio', True), correto era ('baixo', False)
  caso UDI-74: decidiu ('alto', True), correto era ('baixo', False)
  caso UDI-157: decidiu ('alto', True), correto era ('baixo', False)
  caso UDI-1438: decidiu ('baixo', False), correto era ('alto', True)
  caso UDI-4045: decidiu ('baixo', False), correto era ('alto', True)
  caso UDI-4685: decidiu ('baixo', False), correto era ('alto', True)
```

**Padrão dos erros:** Os 7 erros da linha de base formam dois grupos. O primeiro grupo tem **4 falsos positivos na fronteira de desgaste (`Tool wear`)**. Nos casos `UDI-72` e `UDI-73`, o estado interno (`EstadoDaFrota`) bloqueia a máquina com `('medio', True)` porque o tipo `L` acumula duas falhas recentes (`UDI-51` e `UDI-70`). Já nos casos `UDI-74` e `UDI-157`, a regra reativa bloqueia a máquina com `('alto', True)` porque o desgaste chega a `200 min`, mas a ferramenta não quebra naquele ciclo. O segundo grupo tem **3 falsos negativos (falhas não capturadas)**. No caso `UDI-4685`, a máquina sofre falha térmica (`HDF=1`) logo abaixo do corte fixo de temperatura e rotação. Nos casos `UDI-1438` e `UDI-4045`, a máquina quebra com todas as leituras em faixa normal.

**Hipótese do porquê:** O agente de linha de base erra porque avalia cada sensor com cortes fixos e independentes. Na usinagem, o desgaste acima de `190 min` aumenta a chance de falha, mas não define o minuto exato da quebra sem medir variáveis ocultas, como vibração ou microfissuras. Além disso, no caso `UDI-4685`, a regra fixa (`dif_temp < 8.6 and rotacao < 1380`) ignora o efeito combinado de temperatura, rotação e torque elevado. Portanto, casos de fronteira exigem um modelo que combine múltiplas variáveis contínuas.

## 5. A tabela comparativa de busca (item 4 da N2)

Formulação: `diagnostico.py:AMS`

| Busca | Custo | Ações | Nós expandidos | Nós gerados | Prof. máx. | Segundos |
|---|---:|---:|---:|---:|---:|---:|
| largura | 26.0 | 6 | 299 | 402 | 6 | 0.0006 |
| custo_uniforme | 26.0 | 6 | 368 | 431 | 8 | 0.0008 |
| profundidade_limitada(limite=32) | 26.0 | 6 | 7 | 6 | 6 | 0.0 |
| aprofundamento_iterativo(limite=32) | 26.0 | 6 | 219 | 524 | 6 | 0.0009 |
| gulosa[admissivel] | 26.0 | 6 | 7 | 27 | 6 | 0.0001 |
| a_estrela[admissivel] | 26.0 | 6 | 78 | 144 | 6 | 0.0003 |
| gulosa[inadmissivel] | 30.0 | 7 | 8 | 29 | 7 | 0.0001 |
| a_estrela[inadmissivel] | 26.0 | 6 | 7 | 27 | 6 | 0.0001 |

**Dominância e economia no espaço de estados (`a_estrela[admissivel]` vs. `custo_uniforme`):** Sim. A busca `a_estrela[admissivel]` mantém o custo ótimo (`26.0 ms` com `6` ações) e expande `78` nós, contra `368` nós da busca `custo_uniforme` (economia de `290` nós expandidos). A busca `custo_uniforme` equivale ao A\* com heurística zero. Já a heurística admissível de `diagnostico.py` soma o custo das verificações essenciais que ainda faltam. Como essa estimativa é sempre maior que zero antes do objetivo, a heurística admissível domina a busca `custo_uniforme`. No espaço de estados do `AMS`, a verificação essencial `ml-failure-probability` custa `15.0 ms`, enquanto as checagens de rotina custam `1.0 ms` e `4.0 ms`. Sem heurística, `custo_uniforme` testa combinações baratas de rotina até a profundidade `8`. Com heurística, `a_estrela[admissivel]` sabe que as rotinas não reduzem o custo restante das verificações essenciais e foca nos ramos de profundidade `6`.

**Ressalva de contagem da busca em profundidade limitada (`7` nós expandidos):** A busca `profundidade_limitada` mostra apenas `7` nós expandidos por dois motivos. Primeiro, as 6 verificações essenciais estão no início da tupla em `CASO_AMS`, então o primeiro ramo visitado já atinge o objetivo sem retrocesso. Segundo, `profundidade_limitada` usa recursão sem fila de fronteira: a métrica `nos_expandidos` conta apenas as chamadas recursivas (`1` estado inicial + `6` ações = `7`), e por isso não é diretamente comparável à contagem do `a_estrela[admissivel]` e do `custo_uniforme`.
