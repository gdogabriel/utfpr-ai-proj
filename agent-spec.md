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
**Autor(a):** Gabriel Duarte · **Última revisão:** 05/11/2026

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
- **Escalar Ordem de Serviço:** Encaminhar a OS para revisão da supervisão/engenharia quando a verificação de integridade dos sensores (`sanity-check`) detectar leituras inválidas ou corrompidas.

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

- **Primária — Taxa de captura de falhas (`Recall`, $F = A / T$):**
  - **Como se calcula:** divide-se o número de casos com falha real em que o agente recomendou intervenção ($A$, isto é, `(risco == "alto" OU requer_bloqueio == true) E Machine failure == 1`) pelo total de casos com falha real ($T$, `Machine failure == 1`).
  - **Conjunto de casos:** 30 casos rotulados do domínio (`d2/lab6/casos-ams.csv`, extraídos do `ai4i2020.csv` com 15 falhas reais e 15 máquinas saudáveis, incluindo casos fáceis, difíceis de fronteira e 3 atípicos) e base completa (`data/raw/ai4i2020.csv`, 10.000 casos).
  - **Limiar de sucesso e valor de hoje:** meta acima de **85%** no conjunto de 30 casos (e $\ge 97{,}35\%$ na base completa). **Valor de hoje (linha de base em `src/ams/baseline.py`):** **80,00%** (`12/15` falhas capturadas nos 30 casos; `97,35%` ou `330/339` no reativo simples sobre a base completa).
- **Secundária 1 — Taxa de falsos positivos ($FP = B / S$):**
  - **Como se calcula:** divide-se o número de máquinas saudáveis em que o agente recomendou intervenção indevida ($B$, `(risco == "alto" OU requer_bloqueio == true) E Machine failure == 0`) pelo total de máquinas saudáveis ($S$, `Machine failure == 0`). Impede que a métrica primária seja inflada bloqueando todas as máquinas da planta.
  - **Limiar de sucesso e valor de hoje:** meta $\le 15\%$ no conjunto de 30 casos (e $\le 7{,}02\%$ na base completa). **Valor de hoje (`baseline.py`):** **26,67%** (`4/15` nos 30 casos, concentrados na fronteira de desgaste $\ge 190\text{ min}$; `7,02%` na base completa).
- **Secundária 2 — Latência de emissão do parecer:**
  - **Como se calcula:** tempo decorrido (em segundos) entre o recebimento da Ordem de Serviço e a entrega do parecer validado ao técnico. Impede que um parecer lento chegue quando a telemetria da máquina já mudou.
  - **Limiar de sucesso e valor de hoje:** meta abaixo de **5 segundos** por OS (teto máximo tolerado pela operação: `30 s`). **Valor de hoje:** `< 0,01 s` na linha de base por regras (`26,0 ms` na busca de verificações).

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

A fatia do problema que é busca: **em que ordem executar as verificações de telemetria do caso** — o subproblema 1 do catálogo da disciplina, adaptado com os dados e dependências do Assistente de Manutenção Segura (AMS). Os cinco componentes:

| Componente | Neste domínio |
| :--- | :--- |
| **Estado inicial** | Nenhuma verificação concluída e nenhuma anomalia detectada: `((), ())` |
| **Ações** | Executar uma verificação pendente cujas dependências já estão concluídas |
| **Transição** | Incluir o `id` da verificação nas concluídas (`feitas`) e, se houver anomalia (`positivo=True`), incluir também nas `positivas` |
| **Teste de objetivo** | Concluir todas as verificações essenciais do caso (incluindo suas dependências) |
| **Custo** | Soma do tempo de execução de cada verificação realizada, em milissegundos (`ms`) |

**O estado:** é o par de tuplas `(feitas, positivas)` ordenado por `id` — descreve apenas a situação atual, e nunca a ordem em que as verificações ocorreram: dois caminhos que executam as mesmas verificações chegam exatamente ao mesmo estado.

**O que não é busca neste domínio:** ler os dados de entrada da Ordem de Serviço, executar o cálculo interno de cada verificação, decidir o nível de risco e o bloqueio (`requer_bloqueio`), indicar a norma aplicável (`NR-10`, `NR-12`, `NR-35`) e redigir a justificativa técnica. A busca atua exclusivamente na etapa em que a ordem das verificações altera o custo total (tempo) do diagnóstico.

---

### Definição da Verificação e Caso AMS

```python
@dataclass(frozen=True)
class Verificacao:
    """Um passo do diagnóstico.

    O diagnóstico faz verificações para achar a causa de um problema.
    Cada verificação tem um tempo e um resultado.
    O resultado é fixo neste caso: ele não muda entre execuções.

    Esta classe só guarda dados. Ela não executa a verificação.
    Depois de criada, a verificação não muda.
    """

    # Identificador estável e único da verificação.
    id: str

    # Nome legível da verificação.
    nome: str

    # Tempo para fazer a verificação, em milissegundos.
    # Este valor é o custo da ação.
    tempo: float

    # O resultado da verificação neste caso. O resultado é fixo.
    # True: o resultado confirma a hipótese principal.
    # False: o resultado descarta uma hipótese alternativa.
    # O programa só registra este valor no estado.
    positivo: bool

    # True: o objetivo exige esta verificação.
    # O diagnóstico só termina quando todas as essenciais estão feitas.
    # False: a verificação é de rotina. Ela gasta tempo
    # e não muda a conclusão.
    essencial: bool

    # IDs das verificações que precisam ser feitas antes desta.
    dependencias: tuple[str, ...] = ()


# O caso concreto do Assistente de Manutenção Segura (AMS)
# Mapeia as regras de telemetria do dataset AI4I 2020 para esta Ordem de Serviço
CASO_AMS: tuple[Verificacao, ...] = (
    # --- VERIFICAÇÕES ESSENCIAIS ---
    # Necessárias para fechar o laudo de risco com confiança suficiente.
    # 1. Sanity Check (Barato)
    Verificacao(
        id="sanity-check",
        nome="Validar integridade e limites físicos dos sensores (Sanity Check)",
        tempo=0.5, # milissegundos (uma checagem de intervalo min/max é extremamente rápida)
        positivo=False, # False = leituras válidas; True = detectou dado absurdo/corrompido
        essencial=True # É obrigatória: sem dados válidos, o laudo fica comprometido
    ),
    # 2. Regras Lógicas de Telemetria (Custo Médio)
    Verificacao(
        id="hdf",
        nome="Validar dissipação de calor e diferença de temperatura (HDF)",
        tempo=2.5,  # milissegundos
        positivo=True,  # Anomalia confirmada nesta OS (temp. do ar vs. processo)
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="pwf",
        nome="Validar limite de potência mecânica e torque (PWF)",
        tempo=3.0,  # milissegundos
        positivo=True,  # Anomalia confirmada nesta OS (relação torque x rotação)
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="twf",
        nome="Validar limite de desgaste da ferramenta (TWF)",
        tempo=1.5,  # milissegundos
        positivo=False,  # Leitura normal (tempo de desgaste dentro do limite)
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="osf",
        nome="Validar sobretensão por esforço combinado no fuso (OSF)",
        tempo=3.5,  # milissegundos
        positivo=False,  # Leitura normal para esta OS
        essencial=True,
        dependencias=("sanity-check",),
    ),
    # 3. Inferência de Machine Learning / Rede Neural (Custo Maior)
    Verificacao(
        id="ml-failure-probability",
        nome="Inferir probabilidade de falha via Rede Neural (AI4I 2020)",
        tempo=15.0,
        positivo=True,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    # --- VERIFICAÇÕES DE ROTINA ---
    # Não essenciais: consomem tempo computacional sem alterar a conclusão do laudo.
    Verificacao(
        id="sensor-noise",
        nome="Verificar oscilações aleatórias de sinal e ruído nos sensores (RNF)",
        tempo=4.0,  # milissegundos
        positivo=False,
        essencial=False,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="product-type-tolerance",
        nome="Validar classe de tolerância do produto (Type L/M/H na OS)",
        tempo=1.0, # milissegundos
        positivo=False,
        essencial=False,
    ),
)
```

### Classe Diagnóstico

```python
class Diagnostico:
    """O problema de busca: em que ordem fazer as verificações do caso.

    Esta classe tem os componentes da formulação.
    O motor de busca usa estes membros:
    estado_inicial, acoes, transicao, objetivo e custo.

    ESTADO
    O estado é um par de duas tuplas:
    - a primeira tem os IDs das verificações feitas;
    - a segunda tem os IDs das verificações com resultado positivo.
    Cada tupla fica ordenada pelo ID.
    Por isso dois caminhos com as mesmas verificações dão o mesmo estado.
    Estados iguais têm o mesmo hash.
    A ordem em que o agente fez as verificações não importa.
    """

    def __init__(self, verificacoes: tuple[Verificacao, ...]):
        # Uma verificação essencial também exige todas as suas predecessoras.
        verificacoes_por_id = {v.id: v for v in verificacoes}
        essenciais = {v.id for v in verificacoes if v.essencial}
        fila = list(essenciais)
        while fila:
            id_filha = fila.pop()
            for id_parente in verificacoes_por_id[id_filha].dependencias:
                if id_parente not in essenciais:
                    essenciais.add(id_parente)
                    fila.append(id_parente)

        # Todas as verificações do caso, com essencialidade propagada.
        self.verificacoes = tuple(
            replace(v, essencial=v.id in essenciais) for v in verificacoes
        )
        # Dicionário para achar uma verificação pelo ID.
        # A chave é o ID. O valor é a verificação.
        # O sublinhado no início indica uso interno da classe.
        self._por_id = {v.id: v for v in self.verificacoes}
        # Estado inicial: nenhuma verificação feita.
        # Também não há resultado positivo.
        self.estado_inicial: tuple[tuple[str, ...], tuple[str, ...]] = ((), ())

    def acoes(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> list[str]:
        # Devolve os IDs das verificações disponíveis.
        # A verificação não pode estar concluída.
        # Todas as dependências da verificação devem estar concluídas.
        # O "_" ignora os resultados positivos. Esta função não usa esses resultados.
        feitas, _ = estado
        feitas_ids = set(feitas)
        return [
            v.id for v in self.verificacoes
            if v.id not in feitas_ids
            and all(dependencia in feitas_ids for dependencia in v.dependencias)
        ]

    def transicao(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]], acao: str,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        # Devolve o estado que resulta de fazer a ação.
        # Esta função não muda o estado recebido. Ela cria um estado novo.
        # O mesmo estado e a mesma ação sempre dão o mesmo resultado.
        feitas, positivas = estado
        verificacao = self._por_id[acao]
        # A ação sempre entra em "feitas".
        novas_feitas = tuple(sorted((*feitas, acao)))
        # A ação só entra em "positivas" se o resultado for positivo.
        if verificacao.positivo:
            return novas_feitas, tuple(sorted((*positivas, acao)))
        return novas_feitas, positivas

    def objetivo(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
        # Devolve True se o estado é um objetivo.
        # O estado é um objetivo quando todas as verificações essenciais
        # estão em "feitas". As verificações de rotina não importam.
        feitas, _ = estado
        essenciais = {v.id for v in self.verificacoes if v.essencial}
        return essenciais.issubset(feitas)

    def custo(
        self,
        estado: tuple[tuple[str, ...], tuple[str, ...]],
        acao: str,
        estado_seguinte: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        # Devolve o custo de UM passo: o tempo da verificação.
        # O custo do caminho é a soma dos custos dos passos.
        # Aqui o custo só depende da ação.
        # Por isso a função não usa "estado" nem "estado_seguinte".
        # Eles existem porque o motor de busca chama a função com os três.
        return self._por_id[acao].tempo

    def heuristica_admissivel(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        """Estima o custo que falta até o objetivo.

        Valor: a soma dos tempos das essenciais que ainda faltam.

        Esta heurística é admissível: ela nunca passa do custo real.
        Cada essencial que falta precisa ser feita e custa o seu tempo.
        O objetivo não é atingido sem elas.
        A função ignora as não essenciais, porque elas nunca são obrigatórias.
        """
        feitas, _ = estado
        return sum(
            v.tempo for v in self.verificacoes if v.essencial and v.id not in feitas
        )

    def heuristica_inadmissivel(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        """Estima o custo que falta, mas de forma errada.

        Esta função existe para o lab-05 medir o efeito do erro.

        Valor: 3 × (tempo das essenciais que faltam)
               − 2 × (tempo de tudo que já foi feito).

        Esta heurística NÃO é admissível.
        Ela parece correta à primeira vista:
        o que falta é o problema, e cada verificação feita é progresso.
        Uma contagem de progresso escrita de primeira costuma ficar assim.

        Os erros:
        - Ela abate o que foi feito duas vezes.
        - Ela superestima o que falta quando a essencial pendente é barata.
        - Ela fica negativa quando já se gastou tempo demais.
        - Ela faz o A* preferir caminhos que acumulam verificações.
        - O caminho devolvido custa mais que o ótimo. O lab-05 mede isso.
        """
        feitas, _ = estado
        faltam = sum(v.tempo for v in self.verificacoes
                     if v.essencial and v.id not in feitas)
        ja_feito = sum(self._por_id[id_verificacao].tempo for id_verificacao in feitas)
        return 3.0 * faltam - 2.0 * ja_feito


# Instância do problema de busca com as verificações do AMS
AMS = Diagnostico(CASO_AMS)
```

### Verificação da Formulação

**Comando:**
`python verificar-formulacao.py diagnostico.py:AMS`

**Resultado:**
```
verificar-formulacao — teste de sanidade da formulação de busca

— diagnostico.py:AMS
  1. estado é hashable ✅
  2. transição é função ✅
  3. ações estáveis na ordem ✅
  4. custo é positivo ou zero ✅
  5. objetivo é alcançável ✅
  6. estado não guarda o caminho ✅
  resumo: 6 ✅ · 0 ⚠️ · 0 ❌

Seis verificações verdes — a formulação pode ir para o agent-spec.md e para o lab-04.
```
