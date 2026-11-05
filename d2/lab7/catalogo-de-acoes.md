# Catálogo de ações — Assistente de Manutenção Segura (AMS)

<!--
Baseado em COMO-PREENCHER.pdf, catalogo-de-acoes-modelo.md e dois-catalogos-comentados.pdf.
Este catálogo é a lista de ferramentas a implementar em D10: cada linha vira uma função com contrato.
-->

| Ação | Entrada | Saída | É reversível? | Risco se errar |
|---|---|---|---|---|
| Ler a ordem de serviço e a telemetria | Identificador da OS + `Product ID` | Descrição da intervenção, `Type` (`L`/`M`/`H`) e leituras dos 5 sensores físicos | Sim — só lê dados da OS e dos sensores | Leitura defasada ou sensor descalibrado distorce o diagnóstico a jusante; custo de reavaliação |
| Executar verificação de diagnóstico | Nome da verificação (`sanity-check`, `hdf`, `pwf`, `twf`, `osf`, histórico da família ou inferência de falha) + leituras da máquina | Resultado (`positivo`/`negativo`) + tempo gasto em milissegundos | Sim — só computa sobre as leituras em memória | Falso negativo oculta modo de falha ativo (`HDF`, `PWF`, `TWF` ou `OSF`); falso positivo infla o nível de risco |
| Consultar normas de segurança e manuais | Descrição da intervenção planejada + `Type` da máquina | Normas aplicáveis (`NR-10`, `NR-12`, `NR-35` ou `NENHUMA`) e trechos de procedimento | Sim — só consulta a base documental | Omitir norma exigida (ex.: esquecer `NR-10` em painel elétrico ou `NR-12` em eixo rotativo) deixa o parecer sem a proteção obrigatória |
| Montar rascunho do parecer de risco | Resultados das verificações + normas aplicáveis | Objeto `AvaliacaoRisco` em memória (`nivel_risco`, `confianca`, `justificativa`, `normas_aplicaveis`, `requer_bloqueio`) | Sim — é rascunho interno antes da validação de esquema, não foi emitido ao técnico | Rascunho fora do esquema ou incoerente exige nova tentativa e consome cota/tempo de deliberação |
| Emitir parecer de risco e normas na OS | Parecer `AvaliacaoRisco` validado + identificador da OS | Relatório oficial gravado na OS e exibido na tela do técnico de manutenção | Não — uma vez entregue na tela e gravado na OS, o técnico age em campo com base nele | **Escrita e comunicação, risco alto:** emitir risco `baixo` (`requer_bloqueio = false`) em máquina prestes a quebrar leva à quebra em produção ou acidente; emitir `requer_bloqueio = true` em máquina saudável (falso positivo) gera parada preventiva indevida e perda de capacidade |
| Escalar ordem de serviço para supervisão | Identificador da OS + falha no `sanity-check` (leituras inválidas) ou baixa confiança + verificações já feitas | Alerta de revisão humana aberto na fila da supervisão/engenharia | Sim — o alerta pode ser reclassificado ou devolvido após revisão dos sensores | Fadiga de escalonamento se a régua for frouxa; escalar sem anexar as verificações já feitas duplica o trabalho de análise |

---

## Governança e limites de autonomia

**Quem executa cada ação** (o agente sozinho? com confirmação humana? só humano?):
- **O agente executa sozinho:** todas as 6 ações do catálogo (`Ler a ordem de serviço e a telemetria`, `Executar verificação de diagnóstico`, `Consultar normas de segurança e manuais`, `Montar rascunho do parecer de risco`, `Emitir parecer de risco e normas na OS` quando os dados são válidos e `Escalar ordem de serviço para supervisão` quando o `sanity-check` reprova as leituras). O agente entrega o relatório de forma autônoma, sem depender de aprovação prévia do técnico.
- **Só humano (fora do escopo do agente):** decidir e executar o bloqueio físico e etiquetagem (LOTO) na máquina, interromper ou religar o equipamento na planta e realizar a intervenção de manutenção em campo.

**O que o agente JAMAIS executa sozinho:**
- **Emitir parecer de risco quando o `sanity-check` reprovar a integridade dos sensores (leituras fisicamente impossíveis ou corrompidas) ou atuar diretamente sobre a máquina na planta (desligar, travar ou religar equipamento).** Com sensores inválidos, emitir o relatório induziria o técnico ao erro de forma irreversível; nesses casos, o agente é proibido de emitir o parecer e deve escalar a OS.
