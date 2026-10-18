"""Subproblema 1 do catálogo: a ordem das verificações num diagnóstico.

FORMULAÇÃO
Esta formulação vem do plano da D2, seção 9 (catálogo de subproblemas).
- Estado: o conjunto das verificações já feitas e os resultados delas.
- Ação: fazer a próxima verificação.
- Custo: o tempo da verificação.
- Objetivo: chegar a uma conclusão com confiança suficiente.

CASO DETERMINÍSTICO
O caso concreto é determinístico. Cada verificação tem um resultado fixo.
O resultado é um destes dois:
- confirma a hipótese principal;
- descarta uma hipótese alternativa.

Por isso o estado guarda dois grupos: as verificações feitas e as
verificações com resultado positivo.
As positivas derivam das feitas. Elas ficam no estado por dois motivos:
1. Elas seguem a formulação.
2. Elas mostram que o resultado é uma observação.
   O agente não escolhe o resultado.

CONFIANÇA SUFICIENTE
No caso, "confiança suficiente" tem este significado:
o laudo exige as verificações ESSENCIAIS.
As verificações essenciais distinguem as hipóteses.
As outras verificações são de rotina.
Uma verificação de rotina gasta tempo e não muda a conclusão.

DADOS
Os dados do caso são inventados. Eles ficam nas constantes do módulo.
Para usar o seu domínio (lab-03), troque as constantes.
Não mude a classe.
"""

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

    # Nome da verificação. Cada verificação tem um nome diferente.
    # O programa usa o nome para identificar a verificação.
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

# O caso "pedidos travados na fila do agente": três hipóteses concorrentes
# (limite de cota da API, credencial vencida, fila do provedor instável).
CASO_PEQUENO: tuple[Verificacao, ...] = (
    Verificacao("chamar a rota de saúde do provedor", 2.0, False, True),
    Verificacao("conferir o painel de cota da chave", 3.0, True, True),
    Verificacao("renovar a credencial em ambiente isolado", 8.0, False, True),
    Verificacao("olhar o log do último pedido bem-sucedido", 5.0, False, False),
    Verificacao("reproduzir o erro com carga mínima", 12.0, False, False),
    Verificacao("comparar a latência fora e dentro da rede", 10.0, True, False),
)

CASO_MAIOR: tuple[Verificacao, ...] = (
    Verificacao("chamar a rota de saúde do provedor", 2.0, False, True),
    Verificacao("conferir o painel de cota da chave", 3.0, True, True),
    Verificacao("renovar a credencial em ambiente isolado", 8.0, False, True),
    Verificacao("abrir o painel de erros 5xx do gateway", 4.0, False, True),
    Verificacao("conferir o limite de requisições por minuto", 3.0, False, True),
    Verificacao("olhar o log do último pedido bem-sucedido", 5.0, False, False),
    Verificacao("reproduzir o erro com carga mínima", 12.0, False, False),
    Verificacao("comparar a latência fora e dentro da rede", 10.0, True, False),
    Verificacao("pedir rastro a um cliente que funciona", 15.0, False, False),
    Verificacao("conferir o versionamento do certificado TLS", 9.0, False, False),
    Verificacao("medir o relógio do servidor contra o NTP", 6.0, False, False),
    Verificacao("inspecionar a fila de mensagens mortas", 11.0, True, False),
)


class Diagnostico:
    """O problema de busca: em que ordem fazer as verificações do caso.

    Esta classe tem os componentes da formulação.
    O motor de busca usa estes membros:
    estado_inicial, acoes, transicao, objetivo e custo.

    ESTADO
    O estado é um par de duas tuplas:
    - a primeira tem as verificações feitas;
    - a segunda tem as verificações com resultado positivo.
    Cada tupla fica ordenada pelo nome.
    Por isso dois caminhos com as mesmas verificações dão o mesmo estado.
    Estados iguais têm o mesmo hash.
    A ordem em que o agente fez as verificações não importa.
    """

    def __init__(self, verificacoes: tuple[Verificacao, ...]):
        # Todas as verificações do caso.
        self.verificacoes = verificacoes
        # Dicionário para achar uma verificação pelo nome.
        # A chave é o nome. O valor é a verificação.
        # O sublinhado no início indica uso interno da classe.
        self._por_nome = {v.nome: v for v in verificacoes}
        # Estado inicial: nenhuma verificação feita.
        # Também não há resultado positivo.
        self.estado_inicial: tuple[tuple[str, ...], tuple[str, ...]] = ((), ())

    def acoes(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> list[str]:
        # Devolve os nomes das verificações que ainda não foram feitas.
        # Cada nome é uma ação possível neste estado.
        # O "_" ignora as positivas. Esta função não precisa delas.
        feitas, _ = estado
        return [v.nome for v in self.verificacoes if v.nome not in feitas]

    def transicao(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]], acao: str,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        # Devolve o estado que resulta de fazer a ação.
        # Esta função não muda o estado recebido. Ela cria um estado novo.
        # O mesmo estado e a mesma ação sempre dão o mesmo resultado.
        feitas, positivas = estado
        verificacao = self._por_nome[acao]
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
        essenciais = {v.nome for v in self.verificacoes if v.essencial}
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
        return self._por_nome[acao].tempo

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
            v.tempo for v in self.verificacoes if v.essencial and v.nome not in feitas
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
                     if v.essencial and v.nome not in feitas)
        ja_feito = sum(self._por_nome[nome].tempo for nome in feitas)
        return 3.0 * faltam - 2.0 * ja_feito


PEQUENA = Diagnostico(CASO_PEQUENO)
MAIOR = Diagnostico(CASO_MAIOR)
