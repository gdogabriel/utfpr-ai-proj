# Linha de Base de Performance: Agente Reativo Simples

Este documento registra a medição de desempenho do **Agente Reativo Simples** sobre a base de dados do projeto, servindo como referência para as fórmulas de performance do [agent-spec.md](../agent-spec.md).

Os valores obtidos na base completa estabelecem a régua empírica contra a qual qualquer agente futuro mais complexo (baseado em modelo, aprendizado de máquina ou LLM) será avaliado.

---

## 1. Configuração do Teste

* **Arquivo de Medição:** [`performance-agente-reativo-simples.py`](performance-agente-reativo-simples.py)
* **Comando de Execução:** `npm run d2:lab1:formula-performance-agente-reativo-simples:completa`
* **Base Completa:** [`raw/ai4i2020.csv`](raw/ai4i2020.csv) (10.000 registros)
* **Base de Amostra:** [`amostra/ai4i2020.csv`](amostra/ai4i2020.csv) (200 registros)
* **Restrição de Observabilidade:** O agente decide estritamente por regras sobre a percepção do instante (telemetria), sem acesso ao rótulo real (`Machine failure`) ou aos modos de falha.

---

## 2. Fórmulas de Performance (PEAS)

### Métrica Principal: Taxa de Captura de Falhas (Recall)

Avalia a segurança operacional: a capacidade do agente de identificar risco e recomendar parada/bloqueio antes que ocorra um acidente ou quebra catastrófica.

$$F = \frac{A}{T}$$

* **$T$ (Total de Falhas Reais):** Ocorrências em que `Machine failure == 1`.
* **$A$ (Falhas Capturadas):** Casos em que o agente atuou `(risco == "alto" OU bloqueio == True)` E a máquina realmente falhou (`Machine failure == 1`).

### Métrica Secundária: Taxa de Falsos Positivos

Avalia o impacto na produtividade: o contrapeso que pune o agente por bloquear indevidamente máquinas sadias.

$$FP = \frac{B}{S}$$

* **$S$ (Total de Máquinas Saudáveis):** Ocorrências em que `Machine failure == 0`.
* **$B$ (Falsos Positivos):** Casos em que o agente atuou `(risco == "alto" OU bloqueio == True)` E a máquina estava saudável (`Machine failure == 0`).

---

## 3. Resultados Obtidos

| Componente / Métrica | Base de Amostra (200 casos) | Base Completa (10.000 casos) | Limiar de Sucesso no `agent-spec.md` |
| :--- | :---: | :---: | :---: |
| **Total de Registros** | 200 | 10.000 | — |
| **Falhas Reais ($T$)** | 8 | 339 | — |
| **Falhas Capturadas ($A$)** | 8 | 330 | — |
| **Métrica Principal ($F = A / T$)** | **100.00%** | **97.35%** | **$F \ge 97.35\%$** |
| **Máquinas Saudáveis ($S$)** | 192 | 9.661 | — |
| **Falsos Positivos ($B$)** | 19 | 678 | — |
| **Métrica Secundária ($FP = B / S$)** | **9.90%** | **7.02%** | **$FP \le 7.02\%$** |

---

## 4. Análise dos Desvios e Justificativa dos Limiares

Na base completa (10.000 registros), os resultados explicam por que esses limiares representam o teto do agente reativo simples:

### 1. Omissões ($T - A = 9$ falhas não capturadas $\implies F = 97.35\%$)
O agente deixou passar 9 falhas reais:
* **1 caso de desgaste de ferramenta (UDI 1997):** Apresentou $TWF = 1$ com desgaste de 198 min, logo abaixo do limiar conservador adotado pela regra ($\ge 200\text{ min}$).
* **8 casos de anomalias sem modo registrado (UDIs 1438, 2750, 4045, 4685, 5537, 5942, 6479, 8507):** Falhas que ocorreram sem qualquer alteração prévia nos sensores ($TWF=HDF=PWF=OSF=RNF=0$). Como o agente reativo simples só enxerga os sensores, essas falhas estocásticas não puderam ser capturadas.

Portanto, **$F = 97.35\%$** é a máxima capacidade de captura que um conjunto de regras puras sobre os sensores consegue atingir neste dataset.

### 2. Falsos Positivos ($B = 678$ paradas indevidas $\implies FP = 7.02\%$)
O agente recomendou bloqueio em 678 máquinas que não falhariam naquele ciclo:
* No processo de fabricação, as ferramentas falham aleatoriamente entre 200 e 240 minutos. Ao determinar a parada preventiva em 200 minutos, o agente garante a proteção da máquina, mas assume o custo de parar 678 máquinas saudáveis.

Portanto, **$FP = 7.02\%$** é o custo operacional mínimo que esse conjunto de regras impõe à fábrica.

---

## 5. Conclusão

Os resultados experimentais da base completa ajudam a definir o que é sucesso para o [agent-spec.md](../agent-spec.md):
* **Meta Principal:** $F \ge 97.35\%$
* **Meta Secundária:** $FP \le 7.02\%$

Qualquer implementação futura terá essa referência: um novo agente, mais complexo, só justificará sua viabilidade se conseguir melhorar esses índices.
