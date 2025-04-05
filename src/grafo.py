# src/grafo.py

class Grafo:
    def __init__(self):
        self.info = {}                 
        self.vertices = set()         
        self.arestas = []             
        self.arcos = []                
        
        self.vertices_requeridos = set()     
        self.arestas_requeridas = []         
        self.arcos_requeridos = []     
        
    def floyd_warshall(self):
        vertices = sorted(self.vertices)
        dist = {u: {v: float('inf') for v in vertices} for u in vertices}
        pred = {u: {v: None for v in vertices} for u in vertices}
        
        for u in vertices:
            dist[u][u] = 0
        
        # Processa arestas (não requeridas) como conexões bidirecionais
        for u, v, t_cost in self.arestas:
            if t_cost < dist[u][v]:
                dist[u][v] = t_cost
                pred[u][v] = u
            if t_cost < dist[v][u]:
                dist[v][u] = t_cost
                pred[v][u] = v
        
        # Processa arestas requeridas (bidirecionais)
        for u, v, t_cost, demand, s_cost in self.arestas_requeridas:
            if t_cost < dist[u][v]:
                dist[u][v] = t_cost
                pred[u][v] = u
            if t_cost < dist[v][u]:
                dist[v][u] = t_cost
                pred[v][u] = v

        # Processa arcos (não requeridos) – direcionados
        for u, v, t_cost in self.arcos:
            if t_cost < dist[u][v]:
                dist[u][v] = t_cost
                pred[u][v] = u

        # Processa arcos requeridos (direcionados)
        for u, v, t_cost, demand, s_cost in self.arcos_requeridos:
            if t_cost < dist[u][v]:
                dist[u][v] = t_cost
                pred[u][v] = u
        
        for k in vertices:
            for i in vertices:
                for j in vertices:
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]
                        
        return dist, pred
              
    def ler_dat(self, nome_arquivo):
        with open(nome_arquivo, 'r') as f:
            linhas = f.readlines()
            
        current_section = "header"  

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue  
            
            if linha.startswith("ReN."):
                current_section = "ReN"
                continue
            elif linha.startswith("ReE."):
                current_section = "ReE"
                continue
            elif linha.startswith("EDGE"):
                current_section = "EDGE"
                continue
            elif linha.startswith("ReA."):
                current_section = "ReA"
                continue
            elif linha.startswith("ARC"):
                current_section = "ARC"
                continue

            if current_section == "header":
                if ":" in linha:
                    partes = linha.split(":", 1)
                    chave = partes[0].strip()
                    valor = partes[1].strip()
                    self.info[chave] = valor
                continue

            elif current_section == "ReN":
                tokens = linha.split()
                if len(tokens) >= 3:
                    node_str = tokens[0]
                    if node_str.startswith("N"):
                        try:
                            node = int(node_str[1:])
                        except ValueError:
                            continue
                    else:
                        try:
                            node = int(node_str)
                        except ValueError:
                            continue
                    demand = float(tokens[1])
                    s_cost = float(tokens[2])
                    self.vertices_requeridos.add(node)
                    self.vertices.add(node)
                continue

            elif current_section == "ReE":
                tokens = linha.split()
                if len(tokens) >= 6:
                    try:
                        from_node = int(tokens[1])
                        to_node = int(tokens[2])
                        t_cost = float(tokens[3])
                        demand = float(tokens[4])
                        s_cost = float(tokens[5])
                    except ValueError:
                        continue
                    self.arestas_requeridas.append((from_node, to_node, t_cost, demand, s_cost))
                    self.vertices.add(from_node)
                    self.vertices.add(to_node)
                continue

            elif current_section == "EDGE":
                tokens = linha.split()
                if tokens[0] == "EDGE":
                    continue
                if len(tokens) >= 4:
                    try:
                        from_node = int(tokens[1])
                        to_node = int(tokens[2])
                        t_cost = float(tokens[3])
                    except ValueError:
                        continue
                    self.arestas.append((from_node, to_node, t_cost))
                    self.vertices.add(from_node)
                    self.vertices.add(to_node)
                continue

            elif current_section == "ReA":
                tokens = linha.split()
                if len(tokens) >= 6:
                    try:
                        from_node = int(tokens[1])
                        to_node = int(tokens[2])
                        t_cost = float(tokens[3])
                        demand = float(tokens[4])
                        s_cost = float(tokens[5])
                    except ValueError:
                        continue
                    self.arcos_requeridos.append((from_node, to_node, t_cost, demand, s_cost))
                    self.vertices.add(from_node)
                    self.vertices.add(to_node)
                continue

            elif current_section == "ARC":
                tokens = linha.split()
                if tokens[0].isdigit() and len(tokens) >= 3:
                    try:
                        from_node = int(tokens[0])
                        to_node = int(tokens[1])
                        t_cost = float(tokens[2])
                    except ValueError:
                        continue
                    self.arcos.append((from_node, to_node, t_cost))
                    self.vertices.add(from_node)
                    self.vertices.add(to_node)
                continue

    # Estatísticas 1 a 6: contagens básicas
    def quantidade_vertices(self):
        return len(self.vertices)

    def quantidade_arestas(self):
        return len(self.arestas)

    def quantidade_arcos(self):
        return len(self.arcos)

    def quantidade_vertices_requeridos(self):
        return len(self.vertices_requeridos)

    def quantidade_arestas_requeridas(self):
        return len(self.arestas_requeridas)

    def quantidade_arcos_requeridos(self):
        return len(self.arcos_requeridos)

    def densidade(self):
        n = len(self.vertices)
        if n < 2:
            return 0
        total_conexoes = (len(self.arestas) + len(self.arestas_requeridas) +
                          len(self.arcos) + len(self.arcos_requeridos))
        max_conexoes = n * (n - 1) / 2
        return total_conexoes / max_conexoes

    def componentes_conectados(self):
        grafo_adj = {u: set() for u in self.vertices}
        for edge in self.arestas + self.arestas_requeridas:
            u, v, *_ = edge  
            grafo_adj[u].add(v)
            grafo_adj[v].add(u)
        for arco in self.arcos + self.arcos_requeridos:
            u, v, *_ = arco  
            grafo_adj[u].add(v)
            grafo_adj[v].add(u)
            
        visitados = set()
        componentes = []
        
        for u in self.vertices:
            if u not in visitados:
                comp = set()
                stack = [u]
                while stack:
                    atual = stack.pop()
                    if atual not in visitados:
                        visitados.add(atual)
                        comp.add(atual)
                        stack.extend(grafo_adj[atual] - visitados)
                componentes.append(comp)
        return componentes

    def graus(self):
        graus = {u: 0 for u in self.vertices}
        for edge in self.arestas + self.arestas_requeridas:
            u, v, *_ = edge  
            graus[u] += 1
            graus[v] += 1
        for arco in self.arcos + self.arcos_requeridos:
            u, v, *_ = arco  
            graus[u] += 1
            graus[v] += 1
        return graus

    def grau_minimo(self):
        g = self.graus()
        return min(g.values()) if g else 0

    def grau_maximo(self):
        g = self.graus()
        return max(g.values()) if g else 0

    def intermediation(self):
        dist, pred = self.floyd_warshall()
        betweenness = {u: 0 for u in self.vertices}
        vertices = sorted(self.vertices)
        for s in vertices:
            for t in vertices:
                if s != t and dist[s][t] < float('inf'):
                    caminho = []
                    atual = t
                    while atual != s:
                        caminho.append(atual)
                        atual = pred[s][atual]
                        if atual is None:
                            break
                    caminho.append(s)
                    caminho.reverse()
                    for v in caminho[1:-1]:
                        betweenness[v] += 1
        return betweenness

    def caminho_medio(self):
        dist, _ = self.floyd_warshall()
        soma = 0
        cont = 0
        for u in self.vertices:
            for v in self.vertices:
                if u != v and dist[u][v] < float('inf'):
                    soma += dist[u][v]
                    cont += 1
        return soma / cont if cont > 0 else float('inf')

    def diametro(self):
        dist, _ = self.floyd_warshall()
        diam = 0
        for u in self.vertices:
            for v in self.vertices:
                if u != v and dist[u][v] < float('inf'):
                    diam = max(diam, dist[u][v])
        return diam

    def __str__(self):
        cabecalho = "Informações do Cabeçalho:\n" + "\n".join(f"{k}: {v}" for k, v in self.info.items())
        vertices_str = f"Vértices (total: {len(self.vertices)}): {sorted(self.vertices)}"
        req_n = f"Vértices Requeridos: {sorted(self.vertices_requeridos)}"
        req_e = f"Arestas Requeridas: {self.arestas_requeridas}"
        req_a = f"Arcos Requeridos: {self.arcos_requeridos}"
        arestas_str = f"Arestas (não requeridas): {self.arestas}"
        arcos_str = f"Arcos (não requeridos): {self.arcos}"

        stats = [
            f"Quantidade de vértices: {self.quantidade_vertices()}",
            f"Quantidade de arestas: {self.quantidade_arestas()}",
            f"Quantidade de arcos: {self.quantidade_arcos()}",
            f"Quantidade de vértices requeridos: {self.quantidade_vertices_requeridos()}",
            f"Quantidade de arestas requeridas: {self.quantidade_arestas_requeridas()}",
            f"Quantidade de arcos requeridos: {self.quantidade_arcos_requeridos()}",
            f"Densidade do grafo: {self.densidade():.4f}",
            f"Componentes conectados: {self.componentes_conectados()}",
            f"Grau mínimo: {self.grau_minimo()}",
            f"Grau máximo: {self.grau_maximo()}",
            f"Intermediação (betweenness): {self.intermediation()}",
            f"Caminho médio: {self.caminho_medio():.4f}",
            f"Diâmetro: {self.diametro()}"
        ]

        return "\n\n".join([cabecalho, vertices_str, req_n, req_e, req_a, arestas_str, arcos_str] + stats)

if __name__ == "__main__":
    grafo = Grafo()
    grafo.ler_dat('../instances/BHW1.dat')  
    print(grafo)
    dist, pred = grafo.floyd_warshall()
    print("\nMatriz de Distâncias:")
    for u in sorted(dist):
        print(f"{u}: {dist[u]}")
