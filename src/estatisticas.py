# src/estatisticas.py

import sys
from grafo import Grafo

def carregar_grafo(caminho_arquivo):
    grafo = Grafo()
    grafo.ler_dat(caminho_arquivo)
    return grafo

def calcular_estatisticas(grafo):
    # Ajuste dos nomes dos métodos para os definidos em Grafo
    qtd_v = grafo.qtd_vertices()
    qtd_e = grafo.qtd_arestas()
    qtd_a = grafo.qtd_arcos()
    qtd_vr = grafo.qtd_vertices_requeridos()
    qtd_er = grafo.qtd_arestas_requeridas()
    qtd_ar = grafo.qtd_arcos_requeridos()
    dens = grafo.densidade()
    comp = grafo.componentes_conectados()
    grau_min, grau_max = grafo.grau_min_max()
    betw = grafo.betweenness()
    cam_m = grafo.caminho_medio()
    diam = grafo.diametro()

    estatisticas = {
        "Quantidade de vértices": qtd_v,
        "Quantidade de arestas": qtd_e,
        "Quantidade de arcos": qtd_a,
        "Quantidade de vértices requeridos": qtd_vr,
        "Quantidade de arestas requeridas": qtd_er,
        "Quantidade de arcos requeridos": qtd_ar,
        "Densidade do grafo": dens,
        "Componentes conectados": comp,
        "Grau mínimo": grau_min,
        "Grau máximo": grau_max,
        "Intermediação (betweenness)": betw,
        "Caminho médio": cam_m,
        "Diâmetro": diam
    }
    return estatisticas

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python estatisticas.py <arquivo.dat>")
        sys.exit(1)
    arquivo = sys.argv[1]
    g = carregar_grafo(arquivo)
    stats = calcular_estatisticas(g)
    for chave, valor in stats.items():
        print(f"{chave}: {valor}")
