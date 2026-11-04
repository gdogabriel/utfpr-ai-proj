# agent-spec.md — modelo do meu agente

<!--
Este arquivo é para preencher, não para ler e devolver. As perguntas de cada
seção estão em comentário como este: elas não aparecem na pré-visualização,
aparecem no editor. Responda ABAIXO de cada seção, apagando nada delas.

As seções que ainda não foram vistas em aula ficam de pé, com a linha
"quando se preenche" dizendo o encontro em que isso acontece. O documento
cresce a cada laboratório — o de hoje é o primeiro.

Preencha com exemplos concretos do SEU domínio. Uma linha que funcionaria
para qualquer empresa é uma linha genérica — o exemplo do seu segmento
(agente-spec-exemplo.pdf, no mesmo pacote) mostra o contraste.
-->

**Domínio:** Assistente de Manutenção Segura
**Autor(a):** Gabriel Duarte · **Última revisão:** 04/11/2026

---

## 1. PEAS

<!-- Perguntas que guiam o preenchimento:
  - Performance: o que conta como sucesso, em uma fórmula? Sobre o quê se
    conta, sobre qual conjunto, quanto é sucesso? Qual termo impede a
    trapaça mais óbvia (fechar rápido sem resolver)?
  - Environment: onde o agente opera? O que existe lá — sistemas, pessoas,
    documentos, ruído? Cite elementos concretos.
  - Actuators: o que o agente pode FAZER? Inclua comunicar e escalar:
    informar a decisão é uma ação, e passar adiante também é.
  - Sensors: o que o agente consegue PERCEBER? Só o que ele enxerga existe
    para ele.
  Um PEAS que menciona tecnologia de solução (banco vetorial, nome de modelo)
  está descrevendo a solução — o PEAS descreve o problema.
-->

**Quando se preenche:** no Laboratório 01, hoje. Refinado na Atividade Orientada.

### Performance:

#### Considerações do domínio

- Parada não planejada (falha) gera alto custo de produção, perda de insumos e afeta a qualidade.
- Parada preventiva indevida gera custo de oportunidade e consome capacidade limitada da equipe técnica.

#### Métrica Principal: Taxa de Captura de Falhas (Recall)

Mede a capacidade do agente de identificar e recomendar intervenção (bloqueio) em máquinas com risco real de quebra.

- **Fórmula:** F = A / T
  - **F:** Taxa de captura de falhas (recall).
  - **A:** Número de casos que identificou risco alto ou recomendou intervenção e teve falha, isto é, `( risco == "alto" OU bloqueio == Sim ) E Machine failure == 1`.
  - **T:** Número total de casos com falha real, isto é, `Machine failure == 1`.
- **Conjunto de casos:** o dataset AI4I 2020 (`ai4i2020.csv`).
- **Limiar de sucesso:** F >= 97.35% de captura de falhas (referência obtida pelo [agente reativo simples](data/performance-agente-reativo-simples.md) na base completa de 10.000 casos).

#### Métrica Secundária: Taxa de Falsos Positivos

Mede o impacto do agente na produção, evitando paradas e bloqueios indevidos em máquinas saudáveis. É esperado que ocorram paradas para manutenção preventiva. Esta métrica é um contrapeso de performance do agente.

- **Fórmula:** FP = B / S
  - **FP:** Taxa de falsos positivos.
  - **B:** Número de casos que identificou risco alto ou recomendou intervenção e não teve falha, isto é, `( risco == "alto" OU bloqueio == Sim ) E Machine failure == 0`.
  - **S:** Número total de casos sem falha, isto é, `Machine failure == 0`.
- **Conjunto de casos:** o dataset AI4I 2020 (`ai4i2020.csv`).
- **Limiar de sucesso:** FP <= 7.02% (referência obtida pelo [agente reativo simples](data/performance-agente-reativo-simples.md) na base completa de 10.000 casos).

### Environment:

O agente opera em uma planta industrial de manufatura. O ambiente contém os seguintes elementos:

- **Físico:** Máquinas de usinagem em operação e variações de temperatura ambiente.
- **Sensores e Telemetria:** Fluxo de dados operacionais (temperatura do ar e do processo, velocidade, torque e desgaste da ferramenta).
- **Documentos:** Normas de segurança do trabalho (NR-10, NR-12 e NR-35) e manuais de manutenção.
- **Pessoas:** Técnico de manutenção (usuário principal) e operadores da produção.
- **Incertezas:** Ruídos de medição nos sensores e ocorrência de falhas aleatórias.

### Actuators:

Os atuadores definem as informações de apoio que o agente apresenta na tela do técnico:

- **Informar Nível de Risco e Confiança:** Apresentar a classificação do risco de falha (`baixo`, `médio` ou `alto`), a justificativa técnica e o percentual de confiança.
- **Indicar Normas Aplicáveis:** Apontar as normas de segurança necessárias para a intervenção (`NR-10`, `NR-12`, `NR-35` ou `NENHUMA`).
- **Recomendar Bloqueio de Segurança:** Indicar se a intervenção exige bloqueio físico e etiquetagem (`requer_bloqueio = true | false`).

### Sensors:

Os sensores definem os canais de entrada percebidos pelo agente a cada chamada:

- **Entrada da Ordem de Serviço:** Texto da solicitação e identificadores da máquina (\`Product ID\` e \`Type\`).
- **Telemetria de Sensores Físicos:**
  - Temperatura do ar (`Air temperature [K]`).
  - Temperatura do processo (`Process temperature [K]`).
  - Velocidade de rotação (`Rotational speed [rpm]`).
  - Torque (`Torque [Nm]`).
  - Tempo de desgaste da ferramenta (`Tool wear [min]`).

> **Nota de Restrição de Percepção:** O indicador de falha real (`Machine failure`) e os rótulos de modos de falha **não são visíveis** para o agente.

---

## 2. O ambiente em sete dimensões

<!--
Perguntas que guiam o preenchimento (uma por dimensão):
  - Observabilidade: existe algo que muda a decisão e o agente não mede?
  - Número de agentes: existe alguém cujas ações mudam o seu resultado?
    Um humano que reage ao agente conta.
  - Determinismo: a mesma ação no mesmo estado dá sempre o mesmo efeito?
  - Episódico ou sequencial: a decisão de agora afeta as decisões seguintes?
  - Estático ou dinâmico: o ambiente muda enquanto o agente delibera?
  - Discreto ou contínuo: estados e ações são contáveis?
  - Conhecido ou desconhecido: o agente sabe de antemão as regras? (Trata do
    que ele SABE, não do que ele VÊ.)
  Cada classificação vem com uma frase de justificativa — a etiqueta sozinha
  não vale nada.
-->

**Quando se preenche:** no Laboratório 02, no sábado (encontro 2).

| Dimensão | Minha classificação | Justificativa (uma frase) |
|----------|---------------------|---------------------------|
| Observabilidade | Parcial | Os sensores medem variáveis físicas do instante, mas não capturam ruídos de medição, histórico de manutenção nem desgastes internos ocultos da máquina. |
| Número de agentes | Único | Considerando o escopo de deliberar sobre a OS, o agente processa cada ordem de serviço de forma isolada e autônoma antes de entregar a recomendação, sem interação com outros agentes. |
| Determinismo | Estocástico | A mesma leitura de sensores pode resultar em falha ou não no mundo físico, e as chamadas ao modelo de linguagem possuem resposta probabilística. |
| Episódico ou sequencial | Episódico | A avaliação de uma ordem de serviço é independente e não altera o estado nem o resultado das solicitações seguintes. |
| Estático ou dinâmico | Dinâmico | As variáveis telemétricas da máquina continuam mudando na fábrica durante a deliberação, tornando inválidas as respostas atrasadas. |
| Discreto ou contínuo | Contínuo | As medições físicas de telemetria variam em escalas numéricas contínuas, exigindo a discretização dos valores para a tomada de decisão. |
| Conhecido ou desconhecido | Conhecido | As regras de decisão e os critérios de risco são estabelecidos previamente a partir do histórico de dados e das normas de segurança (NRs). |

---

## 3. Tipo de agente pretendido

<!--
Perguntas que guiam o preenchimento:
  - O tipo mais simples que resolve: reativo simples, baseado em modelo,
    baseado em objetivos, baseado em utilidade, ou um deles com aprendizagem?
  - A caracterização do ambiente (seção 2) é que decide — parcialmente
    observável elimina o reativo simples.
  - Justifique com a dimensão do ambiente que obriga a escolha.
-->

**Quando se preenche:** no sábado (encontro 2, manhã).

**Tipo escolhido:** Agente baseado em objetivos.

**Justificativa:**

1. **A Observabilidade Parcial elimina o Tipo 1 (Reativo simples).** Os sensores medem variáveis físicas do instante, mas sofrem ruídos de medição e não capturam desgastes internos ocultos da máquina.
2. **O Tipo 2 (Baseado em modelo) é insuficiente pois controla apenas o estado interno dos passos já executados.** Saber quais verificações já rodaram (e seus resultados) evita repetir etapas na OS, mas o Tipo 2 não avalia qual sequência de ações chega mais rápido ao laudo final.
3. **O ambiente Conhecido, Contínuo (discretizado) e Dinâmico exige o Tipo 3 (Baseado em objetivos).** O agente discretiza a telemetria em verificações conhecidas e usa busca para atingir o objetivo (concluir as verificações essenciais) no menor tempo, evitando respostas atrasadas.
4. **O objetivo binário dispensa o Tipo 4 (Baseado em utilidade).** Como o teste de objetivo é binário (satisfaz ou não satisfaz) e limiares fixos já equilibram as métricas $F$ e $FP$, o Tipo 3 é o mais simples que resolve.

---

## 4. Medida de desempenho

<!--
Perguntas que guiam o preenchimento:
  - A fórmula do campo Performance, agora em definição operacional: como se
    calcula, passo a passo, sem ambiguidade?
  - Métrica primária e duas secundárias. As secundárias pegam o que a
    primária deixa passar (custo, latência, reabertura).
  - O conjunto de casos: de onde vêm, quantos são, de que período.
  - O limiar de sucesso e o valor de hoje.
-->

**Quando se preenche:** a fórmula começa no Laboratório 01; a definição
operacional completa — primária, secundárias, conjunto e limiar — é item da
Atividade Orientada.

[métrica primária e duas secundárias, cada uma com: como se
calcula, sobre qual conjunto, qual o limiar de sucesso e o
valor de hoje]

---

## 5. Restrições

<!--
Perguntas que guiam o preenchimento:
  - Latência aceitável: a partir de quantos segundos a resposta perde valor?
  - Custo aceitável: quanto pode custar cada resolução?
  - O que o agente jamais pode fazer: a ação irreversível que ele não executa
    sozinho. Esta linha vira política em D12.
  - A troca que você aceita: quanto de qualidade por quanto de custo?
    Um exemplo numérico vale mais que a fórmula.
-->

**Quando se preenche:** na Atividade Orientada.

[latência aceitável, custo aceitável, o que o agente jamais
pode fazer sozinho, e a troca qualidade × custo que você
aceita — com um exemplo numérico]

---

## 6. Catálogo de ações

<!--
Perguntas que guiam o preenchimento:
  - Para cada ação: nome, entrada, saída, é reversível?, qual o risco se
    errar? As quatro colunas são obrigatórias — "baixo" não é descrição de
    risco.
  - Ações de leitura E de escrita: as que alteram o mundo são as que exigem
    cuidado, e são justamente as que mais ficam de fora.
  - Este catálogo é, literalmente, a lista de ferramentas que você vai
    implementar em D10.
-->

**Quando se preenche:** na Atividade Orientada — o pacote `D2-07` traz o
modelo da tabela e dois exemplos preenchidos.

[tabela: nome · entrada · saída · é reversível? · risco se
errar — ações de leitura e de escrita]

---

## 7. Formulação por busca

<!--
Perguntas que guiam o preenchimento:
  - Qual fatia do problema é um espaço de estados? (Nem toda fatia é — e
    reconhecer a que não é vale tanto quanto formular a que é.)
  - Os cinco componentes: estado inicial, ações, modelo de transição, teste
    de objetivo, custo de caminho. Comece pelo teste de objetivo.
  - O estado descreve a SITUAÇÃO, não a história de como se chegou nela.
-->

**Quando se preenche:** no Laboratório 03, sábado à tarde (encontro 2).

### Fatia do problema que usa busca

- **O que usa busca:** A determinação da ordem ideal de verificações da telemetria da máquina para chegar a um diagnóstico no menor tempo.

- **O que não usa busca:** A leitura dos dados de entrada da Ordem de Serviço e a redação da justificativa em linguagem natural pelos atuadores.

### Os cinco componentes da busca

- **Estado Inicial:** Nenhuma verificação realizada e nenhum resultado observado.

- **Ações:** Selecionar e realizar a próxima verificação pendente.

- **Modelo de Transição:** Registrar a verificação como feita e, se o resultado for anômalo, adicionar o resultado positivo ao estado.

- **Teste de Objetivo:** Chegar a uma conclusão com confiança suficiente (concluir todas as verificações essenciais do caso).

- **Custo de Caminho:** O tempo consumido pela verificação (a soma dos tempos das verificações executadas na sequência).

---

**Comando:**
`python verificar-formulacao.py diagnostico.py` ou `python verificar-formulacao.py diagnostico.py:AMS`

**Resultado:**

```
verificar-formulacao — teste de sanidade da formulação de busca

— diagnostico.py
  1. estado é hashable ✅
  2. transição é função ✅
  3. ações estáveis na ordem ✅
  4. custo é positivo ou zero ✅
  5. objetivo é alcançável ✅
  6. estado não guarda o caminho ✅
  resumo: 6 ✅ · 0 ⚠️ · 0 ❌

Seis verificações verdes — a formulação pode ir para o agent-spec.md e para o lab-04.
```
