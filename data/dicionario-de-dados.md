# Dicionário do Dataset AI4I 2020: Estrutura para Agentes Inteligentes

Este documento descreve o conjunto de dados de manutenção preditiva industrial (AI4I 2020). Ele separa as variáveis entre **dados percebidos pelo agente** e **dados de avaliação externa**.

> **Fonte:** https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset

> **Nota:** Versão adaptada para o português (Brasil) para fins de estudo no curso de Especialização em Desenvolvimento de Agentes Inteligentes.

## 1\. Visão Geral do Conjunto de Dados

- **Total de registros:** 10.000 pontos de dados (linhas).
- **Total de atributos:** 14 colunas.
- **Aplicação no agente:** Base de dados para a execução da função de decisão e medição do desempenho.

## 2\. Entradas do Agente: Percepção e Sensores (S)

Estas colunas representam o ambiente que o agente percebe. A função de decisão do agente lê estes dados em tempo de execução para avaliar a máquina.

### Identificadores e Variantes de Produção

- **UID:** Identificador único do registro. Varia de 1 a 10.000.
- **Product ID (ID do Produto):** Identificador do produto. Contém a variante de qualidade e o número de série:
  - **L (Low):** Variante de baixa qualidade. Representa 50% dos produtos.
  - **M (Medium):** Variante de média qualidade. Representa 30% dos produtos.
  - **H (High):** Variante de alta qualidade. Representa 20% dos produtos.
- **Type (Tipo):** Letra indicadora da variante de qualidade (`L`, `M` ou `H`).

### Leituras dos Sensores da Máquina

- **Air temperature \[K\] (Temperatura do ar):** Medição em Kelvin. O dado usa passeio aleatório normalizado com desvio padrão de 2 K em torno de 300 K.
- **Process temperature \[K\] (Temperatura do processo):** Medição em Kelvin. O dado usa passeio aleatório com desvio padrão de 1 K, somado à temperatura do ar mais 10 K.
- **Rotational speed \[rpm\] (Velocidade de rotação):** Medição em RPM. O valor é calculado a partir de uma potência de 2.860 W com ruído de distribuição normal.
- **Torque \[Nm\]:** Medição de torque em Nm. Os valores seguem distribuição normal em torno de 40 Nm com desvio padrão \=10Nm. Não possui valores negativos.
- **Tool wear \[min\] (Desgaste da ferramenta):** Tempo de uso acumulado em minutos. Cada processo adiciona tempo ao desgaste conforme a variante do produto:
  - Variante **H:** adiciona 5 minutos.
  - Variante **M:** adiciona 3 minutos.
  - Variante **L:** adiciona 2 minutos.

## 3\. Dados Ocultos ao Agente: Gabarito e Análise Externa (P)

Estes dados **não estão acessíveis** à lógica do agente no momento da decisão. O arcabouço de teste usa estas colunas apenas externamente para calcular a **medida de desempenho (**P**)** do agente.

### Rótulo Principal (Target)

- **Machine failure (Falha da Máquina):** Indica o desfecho real da operação na fábrica.
  - **0:** A máquina operou normalmente.
  - **1:** A máquina falhou.
  - **Regra de definição:** O valor é `1` quando ao menos um dos 5 modos de falha for verdadeiro.
  - **Restrição do Agente:** O agente não lê este rótulo ao decidir. O modelo de decisão recebe apenas as medições dos sensores e não conhece a causa da falha.

### Rótulos dos Modos de Falha Independentes

O script de avaliação compara a recomendação do agente com os 5 modos de falha reais registrados na fábrica:

1. **TWF (Tool Wear Failure \- Falha por Desgaste da Ferramenta):**
   - **Regra:** A ferramenta falha ou é substituída em um tempo de desgaste aleatório entre 200 e 240 minutos.
   - **Ocorrências no dataset:** 120 registros (69 substituições planejadas e 51 falhas aleatórias).
2. **HDF (Heat Dissipation Failure \- Falha por Dissipação de Calor):**
   - **Regra:** A diferença entre a temperatura do ar e a do processo é menor que 8,6 K **e** a velocidade de rotação é menor que 1.380 rpm.
   - **Ocorrências no dataset:** 115 registros.
3. **PWF (Power Failure \- Falha de Potência):**
   - **Regra:** A potência necessária (TorqueVelocidadeemrad/s) fica abaixo de 3.500 W ou acima de 9.000 W.
   - **Ocorrências no dataset:** 95 registros.
4. **OSF (Overstrain Failure \- Falha por Sobrecarga):**
   - **Regra:** O produto do desgaste da ferramenta pelo torque excede o limite da variante:
     - Variante **L:** excede 11.000 minNm.
     - Variante **M:** excede 12.000 minNm.
     - Variante **H:** excede 13.000 minNm.
   - **Ocorrências no dataset:** 98 registros.
5. **RNF (Random Failures \- Falhas Aleatórias):**
   - **Regra:** Falha aleatória com probabilidade fixa de 0,1% em cada processo, independente dos sensores.
   - **Ocorrências no dataset:** 5 registros.
