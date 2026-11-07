# Pares que surpreenderam — Laboratório 01

> O slide 19 do D3-E1 pede DOIS casos anotados: um par PRÓXIMO sem razão
> aparente e um par DISTANTE que deveria estar junto. Eles voltam na D7,
> quando a turma montar o próprio índice de recuperação — escreva aqui e
> guarde este arquivo no seu repositório.

## Um par PRÓXIMO sem razão aparente

- Índices do par: (35, 36)
- As duas frases:
  - primeira: Afrouxe os parafusos do mancal em ordem cruzada antes de remover a tampa.
  - segunda: Aperte os parafusos do mancal em ordem cruzada antes de remover a tampa.
- Cosseno medido: 0.9780
- Por que essa proximidade surpreendeu:

R: O par tem o cosseno mais próximo de 1 em todo o conjunto. Esse valor indica a maior similaridade da base. Porém, as frases contêm verbos antagônicos ("Afrouxe" e "Aperte"). Esses verbos invertem a ação operacional. Todas as outras palavras são idênticas. O resultado mostra que a similaridade de cosseno identifica assuntos parecidos, mas não garante o mesmo sentido.

## Um par DISTANTE que deveria estar junto

- Índices do par: (59, 115)
- As duas frases:
  - primeira: A tensão entre fases do quadro N2 ficou desequilibrada em cinco por cento.
  - segunda: O quadro geral de baixa tensão recebeu termografia completa em setembro.
- Cosseno medido: 0.1453
- Por que essa distância surpreendeu:

R: Ambas as frases tratam do mesmo tema: quadros elétricos e tensão de energia da fábrica. As duas frases usam termos comuns de eletricidade ("tensão" e "quadro"). Mesmo assim, o cosseno medido foi de apenas 0.1453. Esse valor baixo indica quase nenhuma relação entre os vetores.

## O que a comparação com NORMALIZAR = True mudou

- Alguma ordem mudou? De qual par:

R: Não, a ordem não mudou. A fórmula do cosseno já divide os vetores pelas normas. Por isso, a normalização prévia não altera a direção nem os valores do cosseno. A mudança ocorreu na distância euclidiana. Com `NORMALIZAR = False`, as distâncias não possuem um limite fixo e dependem do tamanho das frases. Com `NORMALIZAR = True`, as distâncias ficam restritas ao intervalo entre 0 e 2.
