Formulação: diagnostico.py:AMS

| Busca | Custo | Ações | Nós expandidos | Nós gerados | Prof. máx. | Segundos |
|---|---:|---:|---:|---:|---:|---:|
| largura | 26.0 | 6 | 299 | 402 | 6 | 0.0006 |
| custo_uniforme | 26.0 | 6 | 368 | 431 | 8 | 0.0008 |
| profundidade_limitada(limite=32) | 26.0 | 6 | 7 | 6 | 6 | 0.0 |
| aprofundamento_iterativo(limite=32) | 26.0 | 6 | 219 | 524 | 6 | 0.0009 |

Custo e segundos arredondados. Forma: `comum.busca.comparar()` em 0.0023 s.

Lembre a ressalva de contagem (slide 20): a profundidade limitada é recursiva e não tem fronteira — nela, `nos_expandidos` conta entradas na recursão, sem repetidos. Parte da vantagem aparente dela é diferença de contagem. Registre isso na análise.

Próximo passo: cole a tabela na entrega e responda — alguma busca achou caminho mais barato que a largura? Em diagnostico.py, por quê?

Resposta:
> Não. As 4 buscas encontraram o mesmo custo (`26.0 ms`) com `6` ações.
>
> **Por quê em `diagnostico.py`:**
> 1. **Soma fixa das essenciais:** O objetivo exige fazer todas as 6 verificações essenciais do `CASO_AMS`. A soma do tempo dessas 6 verificações é sempre `26.0 ms`, não importa a ordem. Como a **busca em largura** escolhe o caminho com menos ações (`6`), ela faz apenas as 6 essenciais e ignora as 2 de rotina. Por isso, ela já acha o menor custo possível (`26.0 ms`).
> 2. **Custo uniforme expandiu mais nós (`368` contra `299` da largura):** A verificação essencial `ml-failure-probability` é cara (`15.0 ms`), enquanto as 2 de rotina são baratas (`1.0 ms` e `4.0 ms`). O custo uniforme testa primeiro os caminhos mais baratos, incluindo as verificações de rotina, antes de testar a verificação de `15.0 ms` que completa o objetivo.
> 3. **Ressalva da profundidade limitada (`7` nós expandidos):** O número é muito baixo por dois motivos:
>    - **Acerto de primeira:** No `CASO_AMS`, as 6 essenciais estão declaradas no início da lista. A busca desceu em linha reta pelo primeiro ramo e achou a solução sem precisar voltar atrás.
>    - **Diferença de contagem (slide 20):** A profundidade limitada é recursiva e não mantém uma fila de espera (fronteira) com nós aguardando. Na largura, `nos_expandidos` conta nós retirados da fila; na profundidade, conta apenas entradas na chamada de função. Os `7` nós são literalmente as 7 chamadas do mergulho em linha reta: 1 raiz + 6 ações.

-------------
diagostico.py
```python
from __future__ import annotations

from dataclasses import dataclass

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
