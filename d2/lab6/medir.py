"""medir.py — a medição da linha de base sobre os casos rotulados.

Roda o agente (a função `decidir` e o estado do `esqueleto.py`) sobre o
conjunto de casos, caso a caso, na ordem cronológica, e imprime as três
informações que o slide 28 cobra que o aluno traga:

  1. A MÉTRICA — qual é (a primária do `agent-spec.md`);
  2. O VALOR — quanto deu;
  3. O CONJUNTO — sobre quais casos, quantos são e como se distribuem.

E acrescenta a leitura mais valiosa (slide 30): ONDE o agente erra — a
lista dos casos com decisão diferente do rótulo, que é a matéria-prima da
análise escrita da entrega final.

Uso:  python medir.py            (usa o CAMINHO_DOS_CASOS do esqueleto)
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import esqueleto


def _intervencao(decisao: tuple[str, bool]) -> bool:
    """Critério de intervenção do PEAS (`agent-spec.md`):
    `(risco == "alto" OU bloqueio == Sim)`.
    """
    risco, requer_bloqueio = decisao
    return risco == "alto" or requer_bloqueio is True


def medir(caminho: str | Path, decidir=None, classe_estado=None) -> dict:
    """Roda o agente sobre os casos e devolve o resultado da medição.

    Mantém a medição global do esqueleto (`acertos` / `total`) e calcula
    as métricas do PEAS definidas no `agent-spec.md`:
      - Métrica primária: Taxa de captura de falhas (F = A / T)
      - Métrica secundária: Taxa de falsos positivos (FP = B / S)
    """
    decidir = decidir or esqueleto.decidir
    classe_estado = classe_estado or esqueleto.EstadoDaFrota
    casos = esqueleto.carregar_casos(caminho)
    estado = classe_estado()
    acertos = 0
    erros: list[dict] = []

    total_falhas_reais = 0      # T (Machine failure == 1)
    falhas_capturadas = 0       # A ((risco == "alto" OU bloqueio == True) E Machine failure == 1)
    total_saudaveis = 0         # S (Machine failure == 0)
    falsos_positivos = 0        # B ((risco == "alto" OU bloqueio == True) E Machine failure == 0)

    for registro in casos:
        decisao = decidir(registro, estado)
        correta = registro["acao_correta"]
        falha_real = int(registro.get("Machine failure", registro.get("falhou_depois", 0))) == 1
        interveio = _intervencao(decisao)

        if falha_real:
            total_falhas_reais += 1
            if interveio:
                falhas_capturadas += 1
        else:
            total_saudaveis += 1
            if interveio:
                falsos_positivos += 1

        # Um caso é considerado acerto quando a recomendação de intervenção
        # coincide com a ocorrência real de falha (Machine failure).
        acertou_caso = (falha_real and interveio) or (not falha_real and not interveio)
        if acertou_caso:
            acertos += 1
        else:
            erros.append({
                "id_caso": registro["id_caso"],
                "decidiu": decisao,
                "correta": correta,
            })
        estado.registrar_desfecho(registro)

    total = len(casos)
    rotulos = Counter(registro["acao_correta"] for registro in casos)
    recall = falhas_capturadas / total_falhas_reais if total_falhas_reais else 0.0
    taxa_fp = falsos_positivos / total_saudaveis if total_saudaveis else 0.0

    return {
        "caminho": str(caminho),
        "total": total,
        "acertos": acertos,
        "valor": acertos / total if total else 0.0,
        "falhas_capturadas": falhas_capturadas,
        "total_falhas_reais": total_falhas_reais,
        "recall": recall,
        "falsos_positivos": falsos_positivos,
        "total_saudaveis": total_saudaveis,
        "taxa_fp": taxa_fp,
        "distribuicao": dict(rotulos),
        "erros": erros,
    }


def imprimir(resultado: dict, nome_da_metrica: str) -> None:
    """As três informações do slide 28, as métricas do PEAS e a lista de onde erra (slide 30)."""
    print(f"Métrica primária (PEAS): {nome_da_metrica}")
    print(f"Valor (F = A / T): {resultado['falhas_capturadas']}/{resultado['total_falhas_reais']} = "
          f"{round(resultado['recall'], 4)} ({resultado['recall']:.2%})")
    print(f"Métrica secundária (FP = B / S): {resultado['falsos_positivos']}/{resultado['total_saudaveis']} = "
          f"{round(resultado['taxa_fp'], 4)} ({resultado['taxa_fp']:.2%})")
    print(f"Acerto global (modelo original): {resultado['acertos']}/{resultado['total']} = "
          f"{round(resultado['valor'], 4)} ({resultado['valor']:.2%})")
    print(f"Conjunto: {resultado['caminho']} — {resultado['total']} casos "
          f"rotulados {resultado['distribuicao']}")
    if resultado["erros"]:
        print("Onde erra (o rótulo que o agente não deu):")
        for erro in resultado["erros"]:
            print(f"  caso {erro['id_caso']}: decidiu "
                  f"{erro['decidiu']}, correto era {erro['correta']}")
    else:
        print("Onde erra: em nenhum dos casos — cuidado com um conjunto só "
              "de casos fáceis (slide 24: número bonito e inútil).")


def medir_e_imprimir(caminho: str | Path, decidir, classe_estado) -> None:
    resultado = medir(caminho, decidir, classe_estado)
    imprimir(resultado, "Taxa de captura de falhas / Recall "
                        "(F = A / T: (risco == 'alto' OU bloqueio == True) sobre o total de falhas reais)")


if __name__ == "__main__":
    medir_e_imprimir(esqueleto.CAMINHO_DOS_CASOS,
                     esqueleto.decidir, esqueleto.EstadoDaFrota)
