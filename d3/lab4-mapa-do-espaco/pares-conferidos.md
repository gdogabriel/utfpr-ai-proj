# O mapa do meu domínio — conferência (Laboratório 04)

Conjunto: manutencao · 384 dimensões antes da redução
Escolha registrada (slide 55): normalizado · semente da vizinhança: 20260901
Mapas: mapa-do-espaco.png (componentes principais à esquerda, vizinhança à direita) · pontos: mapa-pontos.csv

## Passo 4 — os três pares que você escolheu no mapa (slide 52)

| par | cosseno original | a vizinhança visual |
|---|---|---|
| (14, 164) | +0.3736 | NÃO confirma |
| (35, 36) | +0.9780 | confirma |
| (1, 62) | +0.1490 | NÃO confirma |

## As quatro perguntas do slide 53

1. Os dois métodos produzem os mesmos agrupamentos?
R: Não.

2. Há grupo que só aparece em um deles?
R: Sim.

3. Os vizinhos visuais confirmam no cosseno original?
R: Nem sempre. O mapa em duas dimensões pode indicar proximidade, mas há perda de informação.

4. O que aconteceria com um vetor novo, fora do conjunto?
R: Na análise de componentes principais (`PCA`), o vetor novo é projetado diretamente porque o método gera uma transformação fixa (no teste `--novo 105`, o ponto cai em `(-0.195, 0.242)`). Nos métodos baseados em vizinhança, não existe transformação fixa, então o mapa inteiro precisa ser refeito para incluir o vetor novo.

## O caso em que o mapa enganou (critério do slide 52)

Par e o que a figura sugeria, e o que o cosseno original disse:

R: O par (14, 164) apareceu muito próximo na projeção bidimensional do PCA. O ponto 14 trata de desbalanceamento de rotor e o ponto 164 relata medição de tensão em correia. No espaço original de 384 dimensões, a similaridade de cosseno é de apenas +0.3736 (< 0.50), comprovando que a proximidade visual 2D é ilusória.
