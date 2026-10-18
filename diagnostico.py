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
    """Uma verificação que o diagnóstico pode fazer."""

    nome: str
    tempo: float      # custo de executá-la (minutos)
    positivo: bool    # o resultado NESTE caso (o caso é fixo)
    essencial: bool   # precisa entrar no laudo para a confiança suficiente


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

    O estado é o par (verificações feitas, verificações com resultado
    positivo), cada um como tupla ordenada — por isso estados iguais são
    o mesmo hash, não importa a ordem em que as verificações foram feitas.
    """

    def __init__(self, verificacoes: tuple[Verificacao, ...]):
        self.verificacoes = verificacoes
        self._por_nome = {v.nome: v for v in verificacoes}
        self.estado_inicial: tuple[tuple[str, ...], tuple[str, ...]] = ((), ())

    def acoes(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> list[str]:
        feitas, _ = estado
        return [v.nome for v in self.verificacoes if v.nome not in feitas]

    def transicao(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]], acao: str,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        feitas, positivas = estado
        verificacao = self._por_nome[acao]
        novas_feitas = tuple(sorted((*feitas, acao)))
        if verificacao.positivo:
            return novas_feitas, tuple(sorted((*positivas, acao)))
        return novas_feitas, positivas

    def objetivo(self, estado: tuple[tuple[str, ...], tuple[str, ...]]) -> bool:
        feitas, _ = estado
        essenciais = {v.nome for v in self.verificacoes if v.essencial}
        return essenciais.issubset(feitas)

    def custo(
        self,
        estado: tuple[tuple[str, ...], tuple[str, ...]],
        acao: str,
        estado_seguinte: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        return self._por_nome[acao].tempo

    def heuristica_admissivel(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        """Soma dos tempos das essenciais que ainda faltam.

        Admissível: cada essencial que falta ainda precisará ser feita e
        custa exatamente o seu tempo — o laudo não fecha sem elas. Ignora
        as não essenciais, que nunca são obrigatórias.
        """
        feitas, _ = estado
        return sum(
            v.tempo for v in self.verificacoes if v.essencial and v.nome not in feitas
        )

    def heuristica_inadmissivel(
        self, estado: tuple[tuple[str, ...], tuple[str, ...]],
    ) -> float:
        """O progresso que desconta: o que falta vale 3×, o que foi feito abate 2×.

        NÃO é admissível, e é tentadora por isso: "quanto falta ainda é o
        problema, e cada coisa que já chequei me adiantou" é a contagem de
        progresso que se escreve de primeira — ela trata verificação cara e
        barata como o mesmo passo e abate o feito duas vezes. Superestima o
        trecho que falta quando a essencial pendente é barata, vira negativa
        quando já se gastou tempo de mais, e faz o A* preferir caminhos que
        acumulam verificações — o caminho devolvido sai mais caro que o
        ótimo (o lab-05 mede isso).
        """
        feitas, _ = estado
        faltam = sum(v.tempo for v in self.verificacoes
                     if v.essencial and v.nome not in feitas)
        ja_feito = sum(self._por_nome[nome].tempo for nome in feitas)
        return 3.0 * faltam - 2.0 * ja_feito


PEQUENA = Diagnostico(CASO_PEQUENO)
MAIOR = Diagnostico(CASO_MAIOR)
