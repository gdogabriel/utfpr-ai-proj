Formulação: diagnostico.py:AMS

| Busca                               | Custo | Ações | Nós expandidos | Nós gerados | Prof. máx. | Segundos |
| ----------------------------------- | ----: | ----: | -------------: | ----------: | ---------: | -------: |
| largura                             |  26.0 |     6 |            299 |         402 |          6 |   0.0006 |
| custo_uniforme                      |  26.0 |     6 |            368 |         431 |          8 |   0.0008 |
| profundidade_limitada(limite=32)    |  26.0 |     6 |              7 |           6 |          6 |      0.0 |
| aprofundamento_iterativo(limite=32) |  26.0 |     6 |            219 |         524 |          6 |   0.0009 |
| gulosa[admissivel]                  |  26.0 |     6 |              7 |          27 |          6 |   0.0001 |
| a_estrela[admissivel]               |  26.0 |     6 |             78 |         144 |          6 |   0.0003 |
| gulosa[inadmissivel]                |  30.0 |     7 |              8 |          29 |          7 |   0.0001 |
| a_estrela[inadmissivel]             |  26.0 |     6 |              7 |          27 |          6 |   0.0001 |

Como ler (slide 36):
  - A estrela expandindo MAIS que o custo uniforme do lab-04? Heurística fraca. - *Não aconteceu.*
  - A estrela com custo PIOR que o custo uniforme? A heurística superestima. - *Não aconteceu.*
  - Antes de qualquer outra verificação: h vale zero em todo estado objetivo? - *Sim.*
  - O item que vale nota: o parágrafo da dominância, comparando as duas colunas de expandidos — a evidência são os números, a explicação é sua.

---

## Parágrafo da dominância

Entre duas heurísticas admissíveis, domina a que estima mais alto em todo estado; a heurística que domina expande menos nós, nunca mais (slide 31). A busca de custo uniforme equivale ao A* com estimativa zero em todos os estados. Já a heurística admissível estima o custo somando o tempo das verificações essenciais que ainda faltam. Como o tempo de cada verificação é positivo, a heurística estima mais alto que zero em qualquer estado antes do objetivo — logo, ela domina a estimativa zero do custo uniforme.

A evidência na tabela confirma a regra: o A* com a heurística admissível **preservou o ótimo (`26.0 ms`)** e expandiu apenas **78 nós**, contra **368 nós** do custo uniforme.

---

## diagnostico.py

```python
from __future__ import annotations

from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Verificacao:
    """Um passo do diagnóstico.

    O diagnóstico faz verificações para achar a causa de um problema.
    Cada verificação tem um tempo e um resultado.
    O resultado é fixo neste caso: ele não muda entre execuções.

    Esta classe só guarda dados. Ela não executa a verificação.
    Depois de criada, a verificação não muda.
    """

    id: str
    nome: str
    tempo: float
    positivo: bool
    essencial: bool
    dependencias: tuple[str, ...] = ()

# O caso concreto do Assistente de Manutenção Segura (AMS)
CASO_AMS: tuple[Verificacao, ...] = (
    Verificacao(
        id="sanity-check",
        nome="Validar integridade e limites físicos dos sensores (Sanity Check)",
        tempo=0.5,
        positivo=False,
        essencial=True,
    ),
    Verificacao(
        id="hdf",
        nome="Validar dissipação de calor e diferença de temperatura (HDF)",
        tempo=2.5,
        positivo=True,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="pwf",
        nome="Validar limite de potência mecânica e torque (PWF)",
        tempo=3.0,
        positivo=True,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="twf",
        nome="Validar limite de desgaste da ferramenta (TWF)",
        tempo=1.5,
        positivo=False,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="osf",
        nome="Validar sobretensão por esforço combinado no fuso (OSF)",
        tempo=3.5,
        positivo=False,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="ml-failure-probability",
        nome="Inferir probabilidade de falha via Rede Neural (AI4I 2020)",
        tempo=15.0,
        positivo=True,
        essencial=True,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="sensor-noise",
        nome="Verificar oscilações aleatórias de sinal e ruído nos sensores (RNF)",
        tempo=4.0,
        positivo=False,
        essencial=False,
        dependencias=("sanity-check",),
    ),
    Verificacao(
        id="product-type-tolerance",
        nome="Validar classe de tolerância do produto (Type L/M/H na OS)",
        tempo=1.0,
        positivo=False,
        essencial=False,
    ),
)

class Diagnostico:
    """O problema de busca: em que ordem fazer as verificações do caso."""

    def __init__(self, verificacoes: tuple[Verificacao, ...]):
        verificacoes_por_id = {v.id: v for v in verificacoes}
        essenciais = {v.id for v in verificacoes if v.essencial}
        fila = list(essenciais)
        while fila:
            id_filha = fila.pop()
            for id_parente in verificacoes_por_id[id_filha].dependencias:
                if id_parente not in essenciais:
                    essenciais.add(id_parente)
                    fila.append(id_parente)

        self.verificacoes = tuple(
            replace(v, essencial=v.id in essenciais) for v in verificacoes
        )
        self._por_id = {v.id: v for v in self.verificacoes}
        self.estado_inicial: tuple[tuple[str, ...], tuple[str, ...]] = ((), ())

    def acoes(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> list[str]:
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
        feitas, positivas = estado
        verificacao = self._por_id[acao]
        novas_feitas = tuple(sorted((*feitas, acao)))
        if verificacao.positivo:
            return novas_feitas, tuple(sorted((*positivas, acao)))
        return novas_feitas, positivas

    def objetivo(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
        feitas, _ = estado
        essenciais = {v.id for v in self.verificacoes if v.essencial}
        return essenciais.issubset(feitas)

    def custo(
        self,
        estado: tuple[tuple[str, ...], tuple[str, ...]],
        acao: str,
        estado_seguinte: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
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

AMS = Diagnostico(CASO_AMS)
```

