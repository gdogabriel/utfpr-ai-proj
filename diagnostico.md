# Classe `Diagnostico`: como a busca usa a classe

Este documento mostra, com diagramas, como a classe `Diagnostico`
funciona. A classe define o problema de busca: em que ordem fazer as
verificações de um diagnóstico.

## Como usar este documento

Leia as seções na ordem. Cada seção responde a uma pergunta.

1. **Ciclo da busca.** Quais membros da classe a busca chama, e em que ordem?
2. **Caminho completo.** Como o estado e os números mudam a cada passo?
3. **Tuplas ordenadas.** Por que a ordem das verificações não muda o estado?

## Termos usados

| Termo | Significado |
|---|---|
| Estado | O par `(feitas, positivas)`. Cada parte é uma tupla ordenada. |
| Ação | Fazer uma verificação que ainda não foi feita. |
| `g` | Custo do caminho. Soma dos custos dos passos já dados. |
| `h` | Estimativa do custo que falta. Valor de `heuristica_admissivel`. |
| Essencial | Verificação que o objetivo exige. |
| Rotina | Verificação que gasta tempo e não muda a conclusão. |

## Limites deste documento

- O exemplo usa 4 verificações do `CASO_PEQUENO`. O tempo está em minutos.
- O documento não explica `heuristica_inadmissivel`.
- O documento não explica os algoritmos de busca. A classe só descreve o problema.

## Esquemas

1. O ciclo da busca e onde cada membro da classe entra

```text
estado_inicial = ((), ())          nada feito, nenhum resultado positivo
        │
        ▼
┌─────────────────────┐
│    ESTADO ATUAL     │◄────────────────────────────┐
│ (feitas, positivas) │                             │
└─────────────────────┘                             │
        │                                           │
        ▼                                           │
objetivo(estado)?  ── sim ──►  FIM                  │
        │ não                                       │
        ▼                                           │
acoes(estado)                                       │
= verificações que ainda não foram feitas           │
        │ a busca escolhe uma                       │
        ▼                                           │
transicao(estado, acao)  ──►  estado seguinte  ─────┘
custo(estado, acao, seguinte)
= tempo da verificação (custo de UM passo)
````

2. Um caminho completo, com o estado em cada passo

Exemplo com 4 verificações (tempos em minutos):
rota de saúde (2, essencial), painel de cota (3, essencial, positiva), log (5, rotina), latência (10, rotina, positiva).

```text
passo  ação feita              feitas            positivas   g    h
─────  ──────────────────────  ────────────────  ──────────  ───  ───
  0    (nenhuma)               ()                ()          0    5
  1    painel de cota  (3)     (painel)          (painel)    3    2
  2    rota de saúde   (2)     (painel, rota)    (painel)    5    0
                                                 objetivo(estado) = sim

g = custo do caminho = soma dos custos dos passos
h = heuristica_admissivel = tempo das essenciais que faltam
Nas tuplas reais ficam os nomes completos, não os abreviados.
```

3. Por que as tuplas são ordenadas

```text
caminho 1:  rota de saúde ──► painel de cota ──┐
                                               ├──►  mesmo estado
caminho 2:  painel de cota ──► rota de saúde ──┘     (painel, rota)
                                                     (painel)

A ordem em que o agente fez as verificações não entra no estado.
Os dois caminhos têm o mesmo custo e chegam à mesma situação,
então o conjunto de explorados reconhece a repetição.
```