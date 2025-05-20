import sys
import os

class Grafo:
    def __init__(self):
        self.info = {}
        self.vertices = set()
        self.arestas = []       # (from, to, t_cost)
        self.arcos = []         # (from, to, t_cost)
        self.vertices_requeridos = set()
        self.arestas_requeridas = []  # (from, to, t_cost, demand, s_cost)
        self.arcos_requeridos = []    # (from, to, t_cost, demand, s_cost)
        
    def ler_dat(self, nome_arquivo):
        with open(nome_arquivo, 'r') as f:
            linhas = f.readlines()

        current_section = "header"
        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith('#'):
                continue

            # Detecção de seções
            if linha.startswith("ReN"):
                current_section = "ReN"
                continue
            elif linha.startswith("ReE"):
                current_section = "ReE"
                continue
            elif linha.startswith(("EDGE", "NrE")):
                current_section = "EDGE"
                continue
            elif linha.startswith("ReA"):
                current_section = "ReA"
                continue
            elif linha.startswith(("ARC", "NrA")):
                current_section = "ARC"
                continue

            # Processamento por seção
            if current_section == "header":
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    self.info[chave.strip()] = valor.strip()
            
            elif current_section == "ReN":
                tokens = linha.split()
                if len(tokens) < 3:
                    continue
                try:
                    # Verificar se o primeiro token começa com 'N' ou é um número
                    if tokens[0].startswith("N"):
                        node = int(tokens[0][1:])
                    else:
                        # Tentar converter diretamente para inteiro
                        node = int(tokens[0])
                    
                    # Garantir que temos pelo menos demanda e custo
                    if len(tokens) >= 3:
                        demand = float(tokens[1])
                        s_cost = float(tokens[2])
                        self.vertices_requeridos.add(node)
                        self.vertices.add(node)
                except (ValueError, IndexError):
                    continue
                
            elif current_section == "ReE":
                tokens = linha.split()
                has_e = tokens[0].startswith("E")
                min_tokens = 6 if has_e else 5
                if len(tokens) < min_tokens:
                    continue
                try:
                    idx = 1 if has_e else 0
                    from_node = int(tokens[idx])
                    to_node = int(tokens[idx+1])
                    t_cost = float(tokens[idx+2])
                    demand = float(tokens[idx+3])
                    s_cost = float(tokens[idx+4])
                    self.arestas_requeridas.append((from_node, to_node, t_cost, demand, s_cost))
                    self.vertices.update([from_node, to_node])
                except (ValueError, IndexError):
                    continue
                
            elif current_section == "EDGE":
                tokens = linha.split()
                if tokens[0] in ("EDGE", "NrE") or tokens[0].startswith("NrE"):
                    continue
                try:
                    if tokens[0].startswith("NrE"):
                        from_node = int(tokens[1])
                        to_node = int(tokens[2])
                        t_cost = float(tokens[3])
                    else:
                        from_node = int(tokens[0])
                        to_node = int(tokens[1])
                        t_cost = float(tokens[2])
                    self.arestas.append((from_node, to_node, t_cost))
                    self.vertices.update([from_node, to_node])
                except (ValueError, IndexError):
                    continue
            
            elif current_section == "ReA":
                tokens = linha.split()
                has_a = tokens[0].startswith("A")
                min_tokens = 6 if has_a else 5
                if len(tokens) < min_tokens:
                    continue
                try:
                    idx = 1 if has_a else 0
                    from_node = int(tokens[idx])
                    to_node = int(tokens[idx+1])
                    t_cost = float(tokens[idx+2])
                    demand = float(tokens[idx+3])
                    s_cost = float(tokens[idx+4])
                    self.arcos_requeridos.append((from_node, to_node, t_cost, demand, s_cost))
                    self.vertices.update([from_node, to_node])
                except (ValueError, IndexError):
                    continue
            
            elif current_section == "ARC":
                tokens = linha.split()
                if tokens[0] in ("ARC", "NrA") or tokens[0].startswith("NrA"):
                    continue
                try:
                    if tokens[0].startswith("NrA"):
                        from_node = int(tokens[1])
                        to_node = int(tokens[2])
                        t_cost = float(tokens[3])
                    else:
                        from_node = int(tokens[0])
                        to_node = int(tokens[1])
                        t_cost = float(tokens[2])
                    self.arcos.append((from_node, to_node, t_cost))
                    self.vertices.update([from_node, to_node])
                except (ValueError, IndexError):
                    continue
        
        # Garantir que o depósito esteja incluído nos vértices
        if 'Depot Node' in self.info:
            deposito = int(self.info['Depot Node'])
            self.vertices.add(deposito)

    # Métodos para estatísticas
    def qtd_vertices(self):
        return len(self.vertices)
    
    def qtd_arestas(self):
        return len(self.arestas) + len(self.arestas_requeridas)
    
    def qtd_arcos(self):
        return len(self.arcos) + len(self.arcos_requeridos)
    
    def qtd_vertices_requeridos(self):
        return len(self.vertices_requeridos)
    
    def qtd_arestas_requeridas(self):
        return len(self.arestas_requeridas)
    
    def qtd_arcos_requeridos(self):
        return len(self.arcos_requeridos)
    
    def densidade(self):
        v = self.qtd_vertices()
        if v < 2:
            return 0.0
        total_edges = self.qtd_arestas() + self.qtd_arcos()
        max_edges = v * (v - 1)  # Considerando direcionado
        return total_edges / max_edges
    
    def grau_min_max(self):
        graus = {}
        # Graus para vértices (arestas não direcionadas)
        for (u, v, *_) in self.arestas + self.arestas_requeridas:
            graus[u] = graus.get(u, 0) + 1
            graus[v] = graus.get(v, 0) + 1
        # Graus para arcos (somente entrada não conta aqui, apenas saída incrementa)
        for (u, v, *_) in self.arcos + self.arcos_requeridos:
            graus[u] = graus.get(u, 0) + 1
        if graus:
            return (min(graus.values()), max(graus.values()))
        else:
            return (0, 0)

    # Métodos adicionais para componentes conectados, betweenness, caminho médio, diâmetro e Floyd-Warshall
    def componentes_conectados(self):
        # Considera arcos/arestas como não direcionados para cálculo de componentes
        adj = {v: [] for v in self.vertices}
        # Arestas (não direcionadas)
        for (u, v, _) in self.arestas:
            adj[u].append(v)
            adj[v].append(u)
        for (u, v, _, _, _) in self.arestas_requeridas:
            adj[u].append(v)
            adj[v].append(u)
        # Arcos (tratados como não direcionados para conectividade)
        for (u, v, _) in self.arcos:
            adj[u].append(v)
            adj[v].append(u)
        for (u, v, _, _, _) in self.arcos_requeridos:
            adj[u].append(v)
            adj[v].append(u)
        visited = set()
        count = 0
        for v in self.vertices:
            if v not in visited:
                count += 1
                stack = [v]
                while stack:
                    curr = stack.pop()
                    if curr not in visited:
                        visited.add(curr)
                        for w in adj.get(curr, []):
                            if w not in visited:
                                stack.append(w)
        return count

    def floyd_warshall(self):
        import math
        verts = sorted(self.vertices)
        index = {v: i for i, v in enumerate(verts)}
        n = len(verts)
        # Inicialização de distâncias
        dist = [[math.inf] * n for _ in range(n)]
        next_node = [[None] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0.0
            next_node[i][i] = verts[i]
        # Arestas (não direcionadas)
        for (u, v, t) in self.arestas:
            i, j = index[u], index[v]
            if t < dist[i][j]:
                dist[i][j] = t
                dist[j][i] = t
                next_node[i][j] = v
                next_node[j][i] = u
        for (u, v, t, _, _) in self.arestas_requeridas:
            i, j = index[u], index[v]
            if t < dist[i][j]:
                dist[i][j] = t
                dist[j][i] = t
                next_node[i][j] = v
                next_node[j][i] = u
        # Arcos (direcionados)
        for (u, v, t) in self.arcos:
            i, j = index[u], index[v]
            if t < dist[i][j]:
                dist[i][j] = t
                next_node[i][j] = v
        for (u, v, t, _, _) in self.arcos_requeridos:
            i, j = index[u], index[v]
            if t < dist[i][j]:
                dist[i][j] = t
                next_node[i][j] = v
        # Floyd-Warshall principal
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
        # Montar matriz de predecessores
        pred = [[None] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j or next_node[i][j] is None:
                    pred[i][j] = None
                else:
                    cur = i
                    target = verts[j]
                    # Se o próximo de i para j já é j, então predecessor é i
                    if next_node[cur][j] == target:
                        pred[i][j] = verts[cur]
                    else:
                        # Avança até encontrar penúltimo nó antes de j
                        while next_node[cur][j] != target:
                            cur = index[next_node[cur][j]]
                        pred[i][j] = verts[cur]
        return dist, pred

    def caminho_medio(self):
        # Calcula média das menores distâncias entre todos os pares de vértices
        dist, _ = self.floyd_warshall()
        n = len(dist)
        total = 0.0
        count = 0
        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] != float('inf'):
                    total += dist[i][j]
                    count += 1
        return (total / count) if count > 0 else 0.0

    def diametro(self):
        # Maior das menores distâncias entre pares de vértices
        dist, _ = self.floyd_warshall()
        max_dist = 0.0
        n = len(dist)
        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] != float('inf'):
                    if dist[i][j] > max_dist:
                        max_dist = dist[i][j]
        return max_dist

    def betweenness(self):
        # Calcula a intermediação de todos os vértices pelos caminhos mais curtos
        dist, pred = self.floyd_warshall()
        verts = sorted(self.vertices)
        index = {v: i for i, v in enumerate(verts)}
        n = len(verts)
        bet = {v: 0 for v in verts}
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                # Se não há caminho (predecessor nulo), pula
                if pred[i][j] is None:
                    continue
                # Reconstrói o caminho de i até j usando pred
                cur = j
                path_idx = []
                while cur != i:
                    path_idx.append(cur)
                    cur = index[pred[i][cur]]
                # path_idx = [j, ..., i]
                # Conta os vértices intermediários (exclui j e i)
                if len(path_idx) > 2:
                    for node_idx in path_idx[1:-1]:
                        bet[verts[node_idx]] += 1
        return bet

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python grafo.py <arquivo.dat>")
        sys.exit(1)
    arquivo = sys.argv[1]
    g = Grafo()
    g.ler_dat(arquivo)
    print("Vertices:", g.qtd_vertices())
    print("Arestas:", g.qtd_arestas())
    print("Arcos:", g.qtd_arcos())
    print("Vertices requeridos:", g.qtd_vertices_requeridos())
    print("Arestas requeridas:", g.qtd_arestas_requeridas())
    print("Arcos requeridos:", g.qtd_arcos_requeridos())
    print("Densidade:", g.densidade())
    grau_min, grau_max = g.grau_min_max()
    print("Grau min:", grau_min, "Grau max:", grau_max)
    print("Componentes conectados:", g.componentes_conectados())
    print("Caminho médio:", g.caminho_medio())
    print("Diâmetro:", g.diametro())
    bt = g.betweenness()
    for v in sorted(bt):
        print(f"Betweenness({v}):", bt[v])
