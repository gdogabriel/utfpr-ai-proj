# Análise — Assistente de Manutenção Segura (AMS)

## O que torna o problema difícil

Três propriedades do ambiente industrial explicam os limites observados nos experimentos:

- **Observabilidade parcial:** os 5 sensores instantâneos não mostram toda degradação mecânica. Por isso, a linha de base (`src/ams/baseline.py`) perdeu 3 falhas reais em `d2/lab6/casos-ams.csv`: `UDI-1438` e `UDI-4045` falharam com leituras normais (`RNF=1`), e `UDI-4685` sofreu falha térmica (`HDF=1`) logo abaixo do corte fixo.
- **Determinismo estocástico e espaço contínuo:** o desgaste da ferramenta não causa quebra em um minuto exato. Como a linha de base aplica um corte fixo de desgaste, o agente gerou 4 falsos positivos na fronteira (`UDI-72`, `UDI-73`, `UDI-74` e `UDI-157`), bloqueando máquinas saudáveis.
- **Custos assimétricos de verificação:** na formulação por busca (`diagnostico.py:AMS`), as checagens de rotina custam de `1.0 ms` a `4.0 ms`, enquanto o modelo `ml-failure-probability` custa `15.0 ms`. Sem heurística, a busca `custo_uniforme` expande `368` nós em combinações baratas antes de testar o modelo. Já a busca `a_estrela[admissivel]` foca nas verificações obrigatórias faltantes e atinge o mesmo custo ótimo (`26.0 ms`) expandindo apenas `78` nós.

## Que tipo de agente o problema realmente exige

Um **agente reativo simples** não resolve o problema. Se o agente olha apenas a leitura atual com corte fixo em `200 min`, ele perde falhas em lotes já degradados, como o caso `UDI-1997` (`TWF=1` com `198 min`).

O uso de **estado interno** (`EstadoDaFrota` com janela de 5 casos por tipo `L`, `M` e `H`) captura o caso `UDI-1997` e eleva o Recall de `11/15` (`73.33%`) para `12/15` (`80.00%`). Porém, esse mesmo estado interno gera 2 falsos positivos na fronteira (`UDI-72` e `UDI-73`).

Por isso, o problema exige um **agente baseado em objetivos com estado interno e verificador determinístico**. O agente deve ordenar as consultas (sensores, histórico, modelo preditivo e normas `NR-10`, `NR-12` e `NR-35`) dentro do limite de `30 s` e `R$ 0,01` por ordem de serviço. Essa escolha exige memória de curto prazo da frota, validação do esquema `AvaliacaoRisco` e rota de escalonamento quando `sanity-check` falha. Em contrapartida, o projeto dispensa atuação física direta na máquina (LOTO), que cabe apenas ao técnico humano.

## O que isto muda no projeto

Para superar a linha de base na D10, o agente com modelo deve adicionar 3 capacidades:

1. Combinar as variáveis contínuas para detectar casos limítrofes como `UDI-4685` sem aumentar os falsos positivos em `200 min`.
2. Consultar os trechos aplicáveis das normas `NR-10`, `NR-12` e `NR-35` para cada modo de falha.
3. Validar a saída com um verificador determinístico externo que exige `AvaliacaoRisco` e aciona o escalonamento humano quando `sanity-check` falha.

A linha de base já atinge `80.00%` de Recall nos 30 casos (`97.35%` nas `10000` linhas de `data/raw/ai4i2020.csv`) com custo zero e latência abaixo de `1 ms`. Portanto, as regras físicas funcionam como filtro inicial rápido e definem a meta mínima de segurança para o agente da D10.
