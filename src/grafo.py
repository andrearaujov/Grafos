# src/grafo.py

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
            if not linha:
                continue

            # Detecção de seções
            if linha.startswith("ReN."):
                current_section = "ReN"
                continue
            elif linha.startswith("ReE."):
                current_section = "ReE"
                continue
            elif linha.startswith(("EDGE", "NrE")):
                current_section = "EDGE"
                continue
            elif linha.startswith("ReA."):
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
                if len(tokens) < 3 or not (tokens[0].startswith("N") or tokens[0].isdigit()):
                    continue
                try:
                    node = int(tokens[0][1:] if tokens[0].startswith("N") else tokens[0])
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
        for u, v, *_ in self.arestas + self.arestas_requeridas:
            graus[u] = graus.get(u, 0) + 1
            graus[v] = graus.get(v, 0) + 1
        for u, v, *_ in self.arcos + self.arcos_requeridos:
            graus[u] = graus.get(u, 0) + 1
        graus_values = graus.values()
        return (min(graus_values), max(graus_values)) if graus_values else (0, 0)
    
    # Métodos adicionais para componentes conectados, betweenness, caminho médio e diâmetro
    # (Implementação mais complexa, requer algoritmos como BFS/DFS ou Floyd-Warshall)