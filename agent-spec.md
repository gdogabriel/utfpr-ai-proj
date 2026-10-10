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
**Autor(a):** Gabriel Duarte · **Última revisão:** 10/10/2026

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

**Performance:**

Considerando que:

- Máquina com falha custa para a empresa, pode impactar na qualidade do produto, perder insumos ou parar a produção.
- Manutenções preventivas de máquinas também param a produção, é um custo de oportunidade.
- Máquinas em manutenção requerem técnicos, e há um limite na capacidade da equipe.

Plano de métricas:

- Métrica principal: taxa de falhas nas máquinas numa janela de tempo.
  - Objetivo: minimizar (manter abaixo da baseline) ou zerar (sucesso total) a taxa de falhas nas máquinas.
  - Fórmula: `número de falhas / total de medições` em uma janela de tempo.
  - Contexto: o agente orientará técnicos informando se as máquinas podem falhar em breve (calculando o risco, justificativa, bloqueio, normas, confiança), auxiliando assim na priorização de máquinas e o procedimento para fazer manutenção.

- Métrica secundária: número de bloqueios numa janela de tempo.
  - Objetivo: minimizar o número de manutenções
  - Fórmula: `número de bloqueios / total de medições`
  - Contexto: ter máquinas paradas diminuem a produção. Isso reduz o lucro da empresa. Com a métrica primária, o agente poderia recomendar o bloqueio em todas as ordens de serviço. Esta métrica é um contra peso de performance do agente.

**Environment:**

- planta industrial com as máquinas.
- sistema de monitoramento das máquinas.
- base de dados de sensores.
- normas regulamentares de intervenção NR-10, NR-12, NR-35.
- técnico que recebe o relatório gerado pelo agente.

**Actuators:**

- validar leitura dos sensores: aceitar ou rejeitar valores impossíveis
- calcular o nível risco de falha da máquina (baixo / médio / alto)
- desenvolver justificativa textual em português, para o técnico entender o porquê do nível de risco
- estimar confiança (percentual)
- decidir se a intervenção exige bloqueio e etiquetagem
  - `requer_bloqueio` = `true` | `false`
- identificar normas regulamentares aplicáveis de intervenção, ou marcar `NENHUMA`:
  - NR-10 se houver instalação
    elétrica;
  - NR-12 para máquinas e equipamentos;
  - NR-35 para trabalho em altura.

**Sensors:**

- ler ordem de serviço
  - ler descrição da intervenção
  - ler identificador e tipo da máquina
  - ler temperaturas de ar e processo
  - ler rotação e torque do fuso
  - ler minutos de desgaste da ferramenta
  - ler se há falha na máquina (`Machine failure`)
  - ler qual é o modo de falha

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

| Dimensão                  | Minha classificação | Justificativa (uma frase)                                                                                                                                                                                                                                                                                           |
| ------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Observabilidade           | parcial             | Lê apenas valores dos sensores na ordem de serviço. Não acessa um histórico de decisões recentes, isto é, não tem como aprender com decisões recentes.                                                                                                                                                              |
| Número de agentes         | único               | Idealizei ter eventos que acionam agentes, com um controlador distribuindo tarefas, onde uma nova OS aciona um agente, sem risco de dois agentes pegarem a mesma OS.                                                                                                                                                |
| Determinismo              | estocástico         | Estocástico, por conta de considerar usar LLM gerar justificativas, identificar normas e outras saídas.                                                                                                                                                                                                             |
| Episódico ou sequencial   | episódico           | Pensei em ter regras criadas offline (um contexto fixo), em que cada OS recebida pelo agente é avaliada em sua totalidade, as variáveis são os valores dos sensores e metadados da máquina, e gera uma saída de risco, justificativa e outros, sem que o agente acesse uma base de dados de suas decisões recentes. |
| Estático ou dinâmico      | dinâmico            | Uma máquina sem falhas pode falhar enquanto ordens de serviço esperam serem processadas, então é preciso um prazo para tratar para que o valor registrado dos sensores não estejam defasados da realidade.                                                                                                          |
| Discreto ou contínuo      | contínuo            | Há sensores discretos (ex: falha, tipo de falha) mas também contínuos (temperatura, rotação, torque) e tais valores precisam ser discretizados.                                                                                                                                                                     |
| Conhecido ou desconhecido | conhecido           | Considerando a base histórica de 10 mil linhas, e normas dadas, pode-se elaborar regras e definições que serão o contexto com regras fixas para tomada de decisões racionais, por isso é o conhecido.                                                                                                               |

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

[o tipo mais simples que resolve, justificado pela dimensão
do ambiente que o obriga]

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

[os cinco componentes do seu subproblema: estado inicial,
ações, transição, teste de objetivo, custo]
