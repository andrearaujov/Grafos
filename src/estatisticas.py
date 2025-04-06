from grafo import Grafo

def carregar_grafo(caminho_arquivo):
    grafo = Grafo()
    grafo.ler_dat(caminho_arquivo)
    return grafo

def calcular_estatisticas(grafo):
    estatisticas = {
        "Quantidade de vértices": grafo.quantidade_vertices(),
        "Quantidade de arestas": grafo.quantidade_arestas(),
        "Quantidade de arcos": grafo.quantidade_arcos(),
        "Quantidade de vértices requeridos": len(grafo.vertices_requeridos),
        "Quantidade de arestas requeridas": len(grafo.arestas_requeridas),
        "Quantidade de arcos requeridos": len(grafo.arcos_requeridos),
        "Densidade do grafo": grafo.densidade(),
        "Componentes conectados": grafo.componentes_conectados(),
        "Grau mínimo": grafo.grau_minimo(),
        "Grau máximo": grafo.grau_maximo(),
        "Intermediação (betweenness)": grafo.intermediation(),
        "Caminho médio": grafo.caminho_medio(),
        "Diâmetro": grafo.diametro()
    }
    return estatisticas

