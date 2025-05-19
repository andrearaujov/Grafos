import sys
import os
import math
import heapq
from collections import defaultdict

class Graph:
    def __init__(self):
        self.num_vertices = 0
        self.edges = []
        self.edge_id_map = {}
        self.arcs = []
        self.arc_id_map = {}
        self.depot = None
        self.capacity = 0
        self.VR = []
        self.ER = []
        self.AR = []
        self.v_demand = {}
        self.v_cost = {}
        self.e_demand = {}
        self.e_cost = {}
        self.a_demand = {}
        self.a_cost = {}
        self.shortest = defaultdict(lambda: defaultdict(lambda: math.inf))
        self.adj = defaultdict(list)
        
        self.served_V = set()
        self.served_E = set()
        self.served_A = set()

    def load_instance(self, filename):
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        it = iter(lines)
        
        first_line = next(it).split()
        self.num_vertices, m, p = map(int, first_line[:3])
        
        second_line = next(it).split()
        self.depot = int(second_line[0])
        self.capacity = int(second_line[1])
        
        for _ in range(m):
            parts = next(it).split()
            eid = int(parts[1])
            u = int(parts[2])
            v = int(parts[3])
            w = float(parts[4])
            self.edges.append((u, v, w))
            self.edge_id_map[eid] = len(self.edges) - 1
            self.adj[u].append((v, w))
            self.adj[v].append((u, w))
            
        for _ in range(p):
            parts = next(it).split()
            aid = int(parts[1])
            u = int(parts[2])
            v = int(parts[3])
            w = float(parts[4])
            self.arcs.append((u, v, w))
            self.arc_id_map[aid] = len(self.arcs) - 1
            self.adj[u].append((v, w))
            
        line = next(it).split()
        k = int(line[1])
        for _ in range(k):
            parts = next(it).split()
            v = int(parts[0])
            self.VR.append(v)
            self.v_demand[v] = float(parts[1])
            self.v_cost[v] = float(parts[2])
            
        line = next(it).split()
        k = int(line[1])
        for _ in range(k):
            parts = next(it).split()
            eid = int(parts[0])
            eidx = self.edge_id_map[eid]
            self.ER.append(eidx)
            self.e_demand[eidx] = float(parts[1])
            self.e_cost[eidx] = float(parts[2])
            
        line = next(it).split()
        k = int(line[1])
        for _ in range(k):
            parts = next(it).split()
            aid = int(parts[0])
            aidx = self.arc_id_map[aid]
            self.AR.append(aidx)
            self.a_demand[aidx] = float(parts[1])
            self.a_cost[aidx] = float(parts[2])

    def compute_shortest_paths(self):
        for start in range(1, self.num_vertices + 1):
            self.shortest[start][start] = 0.0
            heap = [(0.0, start)]
            visited = set()
            
            while heap:
                dist_u, u = heapq.heappop(heap)
                if u in visited:
                    continue
                visited.add(u)
                
                for (v, weight) in self.adj[u]:
                    if dist_u + weight < self.shortest[start][v]:
                        self.shortest[start][v] = dist_u + weight
                        heapq.heappush(heap, (self.shortest[start][v], v))

    def initial_solution(self):
        routes = []
        tasks = []
        
        for v in self.VR:
            tasks.append(('V', v))
        for eidx in self.ER:
            tasks.append(('E', eidx))
        for aidx in self.AR:
            tasks.append(('A', aidx))
            
        while tasks:
            route_tasks = []
            route_cost = 0.0
            route_demand = 0.0
            current = self.depot
            remaining_cap = self.capacity
            
            while True:
                best_task = None
                best_cost = math.inf
                best_travel = 0.0
                best_finish = None
                best_demand = 0.0
                
                for i, task in enumerate(tasks):
                    ttype, tid = task
                    
                    if (ttype == 'V' and tid in self.served_V) or \
                       (ttype == 'E' and tid in self.served_E) or \
                       (ttype == 'A' and tid in self.served_A):
                        continue
                    
                    if ttype == 'V':
                        demand = self.v_demand[tid]
                        if demand > remaining_cap:
                            continue
                        travel = self.shortest[current][tid]
                        finish = tid
                        cost = travel + self.v_cost[tid]
                        
                    elif ttype == 'E':
                        demand = self.e_demand[tid]
                        if demand > remaining_cap:
                            continue
                        u, v, _ = self.edges[tid]
                        dist_u = self.shortest[current][u]
                        dist_v = self.shortest[current][v]
                        travel = min(dist_u, dist_v)
                        finish = u if dist_u < dist_v else v
                        cost = travel + self.e_cost[tid]
                        
                    else:  # Arco
                        demand = self.a_demand[tid]
                        if demand > remaining_cap:
                            continue
                        u, v, _ = self.arcs[tid]
                        travel = self.shortest[current][u]
                        finish = v
                        cost = travel + self.a_cost[tid]
                    
                    if cost < best_cost:
                        best_task = task
                        best_cost = cost
                        best_travel = travel
                        best_finish = finish
                        best_demand = demand
                
                if best_task is None:
                    break
                
                ttype, tid = best_task
                route_cost += best_cost
                route_demand += best_demand
                remaining_cap -= best_demand
                
                if ttype == 'V':
                    self.served_V.add(tid)
                    route_tasks.append(('V', tid))
                elif ttype == 'E':
                    self.served_E.add(tid)
                    route_tasks.append(('E', tid))
                else:
                    self.served_A.add(tid)
                    route_tasks.append(('A', tid))
                
                tasks.remove(best_task)
                current = best_finish
                
                if remaining_cap <= 0:
                    break
            
            # Return to depot
            return_cost = self.shortest[current][self.depot]
            route_cost += return_cost
            
            routes.append({
                'tasks': route_tasks,
                'cost': route_cost,
                'demand': route_demand
            })
        
        return routes

    def write_solution(self, instance_filename, routes):
        base = os.path.basename(instance_filename)
        instance_name = base.split('.')[0]
        sol_name = f"sol-{instance_name}.dat"
        
        total_cost = sum(r['cost'] for r in routes)
        total_demand = sum(r['demand'] for r in routes)
        
        with open(sol_name, 'w') as f:
            f.write(f"NUMERO_ROTAS: {len(routes)}\n")
            f.write(f"CUSTO_TOTAL: {total_cost:.2f}\n")
            f.write(f"DEMANDA_TOTAL: {total_demand:.2f}\n\n")
            
            for i, route in enumerate(routes, 1):
                f.write(f"ROTA_{i}:\n")
                f.write(f"CUSTO: {route['cost']:.2f}\n")
                f.write(f"DEMANDA: {route['demand']:.2f}\n")
                f.write("SERVICOS:\n")
                
                for task in route['tasks']:
                    if task[0] == 'V':
                        f.write(f"VERTICE {task[1]}\n")
                    elif task[0] == 'E':
                        u, v, _ = self.edges[task[1]]
                        f.write(f"ARESTA {u} {v}\n")
                    else:
                        u, v, _ = self.arcs[task[1]]
                        f.write(f"ARCO {u} {v}\n")
                f.write("\n")

def main():
    if len(sys.argv) != 2:
        print("Uso: python solucao.py <arquivo.dat>")
        return
    
    try:
        g = Graph()
        g.load_instance(sys.argv[1])
        g.compute_shortest_paths()
        routes = g.initial_solution()
        g.write_solution(sys.argv[1], routes)
        print(f"Solução gerada em sol-{os.path.basename(sys.argv[1])}")
    except Exception as e:
        print(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()