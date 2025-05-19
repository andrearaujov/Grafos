import sys
import os
import math
from pathlib import Path


# insere a pasta etapa1 no path de módulos
parent = os.path.dirname(__file__)                        # .../Grafos/etapa2
etapa1 = os.path.abspath(os.path.join(parent, '..', 'etapa1', 'src'))
sys.path.insert(0, etapa1)

from grafo import Grafo


class Etapa2(Grafo):
    def __init__(self):
        super().__init__()
    
    def compute_shortest(self):
        # usa floyd_warshall da classe Grafo
        self.dist, self.pred = self.floyd_warshall()

    def initial_solution(self):
        """
        Constrói solução inicial usando heurística gulosa a partir do depósito.
        Cada serviço (vértice, aresta ou arco) é atendido exatamente uma vez.
        """
        routes = []
        # montar lista de tarefas pendentes
        tasks = []
        for v in self.vertices_requeridos:
            tasks.append(('V', v))
        for e in self.arestas_requeridas:
            tasks.append(('E', e[:2]))  # (u,v)
        for a in self.arcos_requeridos:
            tasks.append(('A', (a[0],a[1])))

        while tasks:
            route = []
            load = 0.0
            cost = 0.0
            curr = int(self.info.get('v0', 1))  # depósito, chave v0 no header
            cap = float(self.info.get('CAPACIDADE', self.info.get('Q', 0)))
            remaining = cap

            while True:
                best = None
                best_val = math.inf
                for t in tasks:
                    typ, datum = t
                    if typ == 'V':
                        demand = self.get_vertex_demand(datum)
                        if demand > remaining: continue
                        travel = self.dist[curr-1][datum-1]
                        serv = self.get_vertex_cost(datum)
                        val = travel + serv
                        finish = datum
                    elif typ == 'E':
                        u, v = datum
                        idx = self.find_edge_index(u, v)
                        demand = self.get_edge_demand(idx)
                        if demand > remaining: continue
                        travel, finish = self._best_entry(curr, u, v)
                        serv = self.get_edge_cost(idx)
                        val = travel + serv
                    else:
                        u, v = datum
                        idx = self.find_arc_index(u, v)
                        demand = self.get_arc_demand(idx)
                        if demand > remaining: continue
                        travel = self.dist[curr-1][u-1]
                        finish = v
                        serv = self.get_arc_cost(idx)
                        val = travel + serv
                    if val < best_val:
                        best_val = val
                        best = (t, finish, demand, val)
                if not best:
                    break
                task, finish, dem, val = best
                route.append(task)
                cost += val
                load += dem
                remaining -= dem
                curr = finish
                tasks.remove(task)
                if remaining <= 0:
                    break

            # voltar ao depósito
            depot = int(self.info.get('v0',1))
            if curr != depot:
                cost += self.dist[curr-1][depot-1]
            routes.append((route, load, cost))
        return routes

    # Métodos auxiliares para demandas e custos
    def get_vertex_demand(self, v):
        for x in self.vertices_requeridos:
            if (x == v): return float(self.info.get(f"demand_node_{v}", 0))
        return 0
    def get_vertex_cost(self, v):
        return float(self.info.get(f"service_cost_node_{v}", 0))
    def get_edge_demand(self, idx):
        return self.arestas_requeridas[idx][3]
    def get_edge_cost(self, idx):
        return self.arestas_requeridas[idx][4]
    def get_arc_demand(self, idx):
        return self.arcos_requeridos[idx][3]
    def get_arc_cost(self, idx):
        return self.arcos_requeridos[idx][4]
    def find_edge_index(self, u, v):
        for i,(a,b,_,_,_) in enumerate(self.arestas_requeridas):
            if (a==u and b==v) or (a==v and b==u):
                return i
        raise ValueError(f"Edge {u}-{v} not found")
    def find_arc_index(self, u, v):
        for i,(a,b,_,_,_) in enumerate(self.arcos_requeridos):
            if a==u and b==v:
                return i
        raise ValueError(f"Arc {u}->{v} not found")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python etapa2.py instancia.dat")
        sys.exit(1)
    inst = sys.argv[1]
    e2 = Etapa2()
    e2.ler_dat(inst)
    e2.compute_shortest()
    sol = e2.initial_solution()
    # escreve sol-<inst>
    nome = os.path.basename(inst)
    with open(f"sol-{nome}", 'w') as f:
        for i,(route, load, cost) in enumerate(sol,1):
            f.write(f"Rota {i}: carga {load:.2f}, custo {cost:.2f}\n")
            for task in route:
                if task[0]=='V': f.write(f"  Vertice {task[1]}\n")
                if task[0]=='E': f.write(f"  Aresta {task[1][0]}-{task[1][1]}\n")
                if task[0]=='A': f.write(f"  Arco {task[1][0]}->{task[1][1]}\n")
            f.write("\n")
