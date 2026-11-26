# Anotações — Laboratório 02, a descida à mão

> O critério do slide 11: as quatro perguntas respondidas por escrito, com o
> número que sustenta cada resposta. Preencha a tabela rodando o esqueleto
> com as três taxas do slide 12 e copiando a última linha de cada execução.

## A última linha de cada taxa

| Taxa | Última linha da saída (perda, w, b) |
|---|---|
| 0,001 | passo  200 perda 22462.1 w 215.016 b -17.7381 |
| 0,1 | passo  200 perda 0.752176 w 300.008 b 4.91185 |
| 1,5 | passo  200 perda inf w -3.12216e+190 b 4.826e+189 |

## As quatro perguntas do slide 11

**1. A perda está caindo a cada passo, ou oscilando?**

| Taxa | Comportamento da perda |
|---|---|
| 0,001 | Cai continuamente sem oscilar |
| 0,1 | Cai rápido sem oscilar | estabiliza
| 1,5 | Sobe exponencialmente sem oscilar | diverge

**2. Ela estabiliza, ou continua descendo até o fim?**

| Taxa | Estabilização da perda |
|---|---|
| 0,001 | Continua descendo até o fim |
| 0,1 | Estabiliza no passo 53 |
| 1,5 | Não estabiliza, explode para infinito |

A taxa 0,1 atinge o mínimo e estabiliza em 0,752176 a partir do passo 53. Em contraste, a taxa 0,001 desce devagar demais e segue em queda no passo 200 sem convergir.

**3. Os pesos encontrados batem com os que geraram os dados?**

| Taxa | Pesos no passo 200 ($w, b$) | Proximidade do alvo ($w=300, b=5$) |
|---|---|---|
| 0,001 | $w=215,016$; $b=-17,7381$ | Longe dos valores reais |
| 0,1 | $w=300,008$; $b=4,91185$ | Batem com alta precisão |
| 1,5 | $w \approx -3,12 \cdot 10^{190}$; $b \approx 4,83 \cdot 10^{189}$ | Totalmente divergentes |

Apenas a taxa 0,1 recupera com precisão os parâmetros originais geradores dos dados ($w=300,008$ e $b=4,91185$). A taxa 0,001 não teve passos suficientes para alcançar o alvo, enquanto a taxa 1,5 divergiu sem controle.

**4. Se algo divergiu, qual foi o primeiro passo estranho?**

| Taxa | Houve divergência? | Primeiro passo estranho |
|---|---|---|
| 0,001 | Não | Nenhum (perda sempre decrescente) |
| 0,1 | Não | Nenhum (perda sempre decrescente) |
| 1,5 | Sim | Passo 2 (perda subiu para $2,14 \cdot 10^7$) |

A divergência da taxa 1,5 ocorreu logo no passo 2, onde a perda subiu de $284.802$ para $21.435.800$ em vez de diminuir. A explosão exponencial seguiu a cada iteração até ultrapassar o limite de ponto flutuante no passo 161 (`inf`).
