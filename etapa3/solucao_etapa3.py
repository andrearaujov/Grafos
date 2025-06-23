import math
import os
import sys
import time
import glob
import random
import copy
sys.path.append(os.path.abspath('../etapa1/src'))

from grafo import Grafo

class SolucaoMelhorada:
    def __init__(self, grafo, capacidade_veiculo):
        self.grafo = grafo
        self.capacidade_veiculo = capacidade_veiculo
        self.deposito = int(self.grafo.info.get('Depot Node', 1))
        self.servicos_nao_atendidos = self._inicializar_servicos()
        self.dist_matrix, self.pred_matrix = self.grafo.floyd_warshall()
        self.verts = sorted(self.grafo.vertices)
        self.index = {v: i for i, v in enumerate(self.verts)}
        self.rotas = []
        self.custo_total = 0
        self.tempo_inicio = 0
        self.tempo_fim = 0
        
    def _inicializar_servicos(self):
        """Inicializa a lista de serviços não atendidos com seus IDs e informações."""
        servicos = []
        
        # Adicionar vértices requeridos (ID começa em 1)
        id_servico = 1
        for v in sorted(self.grafo.vertices_requeridos):
            servicos.append({
                'id': id_servico,
                'tipo': 'vertice',
                'de': v,
                'para': v,
                'demanda': 1,
                'custo_servico': 1
            })
            id_servico += 1
        
        # Adicionar arestas requeridas
        for u, v, t_cost, demand, s_cost in self.grafo.arestas_requeridas:
            servicos.append({
                'id': id_servico,
                'tipo': 'aresta',
                'de': u,
                'para': v,
                'demanda': demand,
                'custo_servico': s_cost
            })
            id_servico += 1
        
        # Adicionar arcos requeridos
        for u, v, t_cost, demand, s_cost in self.grafo.arcos_requeridos:
            servicos.append({
                'id': id_servico,
                'tipo': 'arco',
                'de': u,
                'para': v,
                'demanda': demand,
                'custo_servico': s_cost
            })
            id_servico += 1
            
        return servicos
    
    def _calcular_caminho(self, origem, destino):
        """Calcula o caminho mais curto entre dois vértices usando a matriz de predecessores."""
        if origem == destino:
            return [origem], 0
            
        i, j = self.index[origem], self.index[destino]
        if self.pred_matrix[i][j] is None:
            return None, float('inf')  # Não há caminho
            
        caminho = [destino]
        custo = self.dist_matrix[i][j]
        atual = destino
        
        while atual != origem:
            pred = self.pred_matrix[self.index[origem]][self.index[atual]]
            caminho.append(pred)
            atual = pred
            
        caminho.reverse()
        return caminho, custo
    
    def _selecionar_proximo_servico(self, posicao_atual, capacidade_restante):
        """Seleciona o próximo serviço a ser atendido com base na proximidade e capacidade."""
        melhor_servico = None
        menor_distancia = float('inf')
        
        for servico in self.servicos_nao_atendidos:
            # Verificar se o serviço cabe na capacidade restante
            if servico['demanda'] > capacidade_restante:
                continue
                
            # Calcular distância até o serviço
            caminho, distancia = self._calcular_caminho(posicao_atual, servico['de'])
            if caminho is None:
                continue  # Não há caminho para este serviço
                
            if distancia < menor_distancia:
                menor_distancia = distancia
                melhor_servico = servico
                
        return melhor_servico, menor_distancia
    
    def construir_solucao_inicial(self):
        """Constrói uma solução inicial para o problema usando algoritmo construtivo guloso."""
        # Ordenar serviços por proximidade ao depósito para melhorar a solução inicial
        servicos_ordenados = []
        for servico in self.servicos_nao_atendidos:
            caminho, distancia = self._calcular_caminho(self.deposito, servico['de'])
            if caminho is not None:  # Garantir que há um caminho válido
                servicos_ordenados.append((servico, distancia))
        
        # Ordenar por distância e extrair apenas os serviços
        servicos_ordenados.sort(key=lambda x: x[1])
        self.servicos_nao_atendidos = [s[0] for s in servicos_ordenados]
        
        while self.servicos_nao_atendidos:
            # Iniciar nova rota
            rota = {
                'id': len(self.rotas) + 1,
                'demanda_total': 0,
                'custo_total': 0,
                'visitas': [],
                'servicos': []
            }
            
            capacidade_restante = self.capacidade_veiculo
            posicao_atual = self.deposito
            
            # Adicionar visita inicial ao depósito
            rota['visitas'].append((self.deposito, self.deposito))
            
            while True:
                # Selecionar próximo serviço
                servico, distancia = self._selecionar_proximo_servico(posicao_atual, capacidade_restante)
                
                if servico is None:
                    # Não há mais serviços que caibam nesta rota
                    break
                    
                # Adicionar serviço à rota
                rota['servicos'].append(servico)
                rota['demanda_total'] += servico['demanda']
                
                # Adicionar custo de deslocamento até o serviço
                rota['custo_total'] += distancia
                
                # Adicionar custo do serviço
                rota['custo_total'] += servico['custo_servico']
                
                # Atualizar capacidade restante
                capacidade_restante -= servico['demanda']
                
                # Atualizar posição atual
                posicao_atual = servico['para']
                
                # Adicionar visita ao serviço
                rota['visitas'].append((servico['de'], servico['para']))
                
                # Remover serviço da lista de não atendidos
                self.servicos_nao_atendidos.remove(servico)
                
                if not self.servicos_nao_atendidos:
                    break
            
            # Adicionar retorno ao depósito
            caminho_retorno, distancia_retorno = self._calcular_caminho(posicao_atual, self.deposito)
            if caminho_retorno:
                rota['custo_total'] += distancia_retorno
                rota['visitas'].append((self.deposito, self.deposito))
            
            # Adicionar rota à solução
            self.rotas.append(rota)
            self.custo_total += rota['custo_total']
    
    def _calcular_custo_rota(self, rota):
        """Calcula o custo total de uma rota."""
        custo = 0
        posicao_atual = self.deposito
        
        # Para cada serviço na rota
        for servico in rota['servicos']:
            # Custo de deslocamento até o serviço
            _, distancia = self._calcular_caminho(posicao_atual, servico['de'])
            custo += distancia
            
            # Custo do serviço
            custo += servico['custo_servico']
            
            # Atualizar posição atual
            posicao_atual = servico['para']
        
        # Adicionar retorno ao depósito
        _, distancia_retorno = self._calcular_caminho(posicao_atual, self.deposito)
        custo += distancia_retorno
        
        return custo
    
    def _reconstruir_visitas_rota(self, rota):
        """Reconstrói as visitas de uma rota com base nos serviços."""
        visitas = [(self.deposito, self.deposito)]  # Visita inicial ao depósito
        
        for servico in rota['servicos']:
            visitas.append((servico['de'], servico['para']))
        
        visitas.append((self.deposito, self.deposito))  # Visita final ao depósito
        
        return visitas
    
    def _aplicar_2opt_intra_rota(self, rota):
        """Aplica o algoritmo 2-opt para melhorar uma rota."""
        if len(rota['servicos']) < 2:
            return rota, False
        
        melhor_rota = copy.deepcopy(rota)
        melhoria_encontrada = False
        
        for i in range(len(rota['servicos']) - 1):
            for j in range(i + 1, len(rota['servicos'])):
                # Criar uma nova rota com os serviços invertidos entre i e j
                nova_rota = copy.deepcopy(rota)
                nova_rota['servicos'][i:j+1] = reversed(nova_rota['servicos'][i:j+1])
                
                # Recalcular o custo da nova rota
                nova_rota['custo_total'] = self._calcular_custo_rota(nova_rota)
                
                # Se a nova rota for melhor, atualizar a melhor rota
                if nova_rota['custo_total'] < melhor_rota['custo_total']:
                    melhor_rota = nova_rota
                    melhoria_encontrada = True
        
        # Se houve melhoria, reconstruir as visitas da rota
        if melhoria_encontrada:
            melhor_rota['visitas'] = self._reconstruir_visitas_rota(melhor_rota)
        
        return melhor_rota, melhoria_encontrada
    
    def _aplicar_realocacao_intra_rota(self, rota):
        """Aplica o operador de realocação para melhorar uma rota."""
        if len(rota['servicos']) < 2:
            return rota, False
        
        melhor_rota = copy.deepcopy(rota)
        melhoria_encontrada = False
        
        for i in range(len(rota['servicos'])):
            servico_removido = rota['servicos'][i]
            
            for j in range(len(rota['servicos']) + 1):
                if j == i or j == i + 1:
                    continue  # Mesma posição ou posição adjacente
                
                # Criar uma nova rota com o serviço realocado
                nova_rota = copy.deepcopy(rota)
                nova_rota['servicos'].pop(i)
                
                if j > i:
                    j -= 1  # Ajustar índice após remoção
                
                nova_rota['servicos'].insert(j, servico_removido)
                
                # Recalcular o custo da nova rota
                nova_rota['custo_total'] = self._calcular_custo_rota(nova_rota)
                
                # Se a nova rota for melhor, atualizar a melhor rota
                if nova_rota['custo_total'] < melhor_rota['custo_total']:
                    melhor_rota = nova_rota
                    melhoria_encontrada = True
        
        # Se houve melhoria, reconstruir as visitas da rota
        if melhoria_encontrada:
            melhor_rota['visitas'] = self._reconstruir_visitas_rota(melhor_rota)
        
        return melhor_rota, melhoria_encontrada
    
    def _verificar_capacidade_rota(self, rota):
        """Verifica se a rota respeita a restrição de capacidade."""
        demanda_total = sum(servico['demanda'] for servico in rota['servicos'])
        return demanda_total <= self.capacidade_veiculo
    
    def _aplicar_troca_entre_rotas(self, rota1, rota2):
        """Aplica o operador de troca entre duas rotas."""
        if not rota1['servicos'] or not rota2['servicos']:
            return rota1, rota2, False
        
        melhor_rota1 = copy.deepcopy(rota1)
        melhor_rota2 = copy.deepcopy(rota2)
        custo_atual = rota1['custo_total'] + rota2['custo_total']
        melhoria_encontrada = False
        
        for i in range(len(rota1['servicos'])):
            for j in range(len(rota2['servicos'])):
                # Criar novas rotas com os serviços trocados
                nova_rota1 = copy.deepcopy(rota1)
                nova_rota2 = copy.deepcopy(rota2)
                
                servico1 = nova_rota1['servicos'][i]
                servico2 = nova_rota2['servicos'][j]
                
                nova_rota1['servicos'][i] = servico2
                nova_rota2['servicos'][j] = servico1
                
                # Verificar se as novas rotas respeitam a restrição de capacidade
                if not self._verificar_capacidade_rota(nova_rota1) or not self._verificar_capacidade_rota(nova_rota2):
                    continue
                
                # Recalcular os custos das novas rotas
                nova_rota1['custo_total'] = self._calcular_custo_rota(nova_rota1)
                nova_rota2['custo_total'] = self._calcular_custo_rota(nova_rota2)
                
                novo_custo = nova_rota1['custo_total'] + nova_rota2['custo_total']
                
                # Se as novas rotas forem melhores, atualizar as melhores rotas
                if novo_custo < custo_atual:
                    melhor_rota1 = nova_rota1
                    melhor_rota2 = nova_rota2
                    custo_atual = novo_custo
                    melhoria_encontrada = True
        
        # Se houve melhoria, reconstruir as visitas das rotas
        if melhoria_encontrada:
            melhor_rota1['visitas'] = self._reconstruir_visitas_rota(melhor_rota1)
            melhor_rota2['visitas'] = self._reconstruir_visitas_rota(melhor_rota2)
            
            # Recalcular demanda total
            melhor_rota1['demanda_total'] = sum(servico['demanda'] for servico in melhor_rota1['servicos'])
            melhor_rota2['demanda_total'] = sum(servico['demanda'] for servico in melhor_rota2['servicos'])
        
        return melhor_rota1, melhor_rota2, melhoria_encontrada
    
    def _aplicar_realocacao_entre_rotas(self, rota1, rota2):
        """Aplica o operador de realocação entre duas rotas."""
        if not rota1['servicos']:
            return rota1, rota2, False
        
        melhor_rota1 = copy.deepcopy(rota1)
        melhor_rota2 = copy.deepcopy(rota2)
        custo_atual = rota1['custo_total'] + rota2['custo_total']
        melhoria_encontrada = False
        
        for i in range(len(rota1['servicos'])):
            servico = rota1['servicos'][i]
            
            # Verificar se o serviço cabe na rota2
            nova_demanda_rota2 = rota2['demanda_total'] + servico['demanda']
            if nova_demanda_rota2 > self.capacidade_veiculo:
                continue
            
            for j in range(len(rota2['servicos']) + 1):
                # Criar novas rotas com o serviço realocado
                nova_rota1 = copy.deepcopy(rota1)
                nova_rota2 = copy.deepcopy(rota2)
                
                # Remover o serviço da rota1
                servico_removido = nova_rota1['servicos'].pop(i)
                
                # Inserir o serviço na rota2
                nova_rota2['servicos'].insert(j, servico_removido)
                
                # Recalcular os custos das novas rotas
                nova_rota1['custo_total'] = self._calcular_custo_rota(nova_rota1)
                nova_rota2['custo_total'] = self._calcular_custo_rota(nova_rota2)
                
                novo_custo = nova_rota1['custo_total'] + nova_rota2['custo_total']
                
                # Se as novas rotas forem melhores, atualizar as melhores rotas
                if novo_custo < custo_atual:
                    melhor_rota1 = nova_rota1
                    melhor_rota2 = nova_rota2
                    custo_atual = novo_custo
                    melhoria_encontrada = True
        
        # Se houve melhoria, reconstruir as visitas das rotas
        if melhoria_encontrada:
            melhor_rota1['visitas'] = self._reconstruir_visitas_rota(melhor_rota1)
            melhor_rota2['visitas'] = self._reconstruir_visitas_rota(melhor_rota2)
            
            # Recalcular demanda total
            melhor_rota1['demanda_total'] = sum(servico['demanda'] for servico in melhor_rota1['servicos'])
            melhor_rota2['demanda_total'] = sum(servico['demanda'] for servico in melhor_rota2['servicos'])
        
        return melhor_rota1, melhor_rota2, melhoria_encontrada
    
    def _aplicar_busca_local_intra_rota(self):
        """Aplica busca local dentro de cada rota."""
        melhoria_global = False
        
        for i in range(len(self.rotas)):
            # Aplicar 2-opt
            self.rotas[i], melhoria_2opt = self._aplicar_2opt_intra_rota(self.rotas[i])
            
            # Aplicar realocação
            self.rotas[i], melhoria_realocacao = self._aplicar_realocacao_intra_rota(self.rotas[i])
            
            if melhoria_2opt or melhoria_realocacao:
                melhoria_global = True
        
        return melhoria_global
    
    def _aplicar_busca_local_entre_rotas(self):
        """Aplica busca local entre pares de rotas."""
        melhoria_global = False
        
        for i in range(len(self.rotas)):
            for j in range(i + 1, len(self.rotas)):
                # Aplicar troca entre rotas
                self.rotas[i], self.rotas[j], melhoria_troca = self._aplicar_troca_entre_rotas(self.rotas[i], self.rotas[j])
                
                # Aplicar realocação entre rotas
                self.rotas[i], self.rotas[j], melhoria_realocacao = self._aplicar_realocacao_entre_rotas(self.rotas[i], self.rotas[j])
                
                # Tentar também na direção oposta
                self.rotas[j], self.rotas[i], melhoria_realocacao_oposta = self._aplicar_realocacao_entre_rotas(self.rotas[j], self.rotas[i])
                
                if melhoria_troca or melhoria_realocacao or melhoria_realocacao_oposta:
                    melhoria_global = True
        
        return melhoria_global
    
    def _recalcular_custo_total(self):
        """Recalcula o custo total da solução."""
        self.custo_total = sum(rota['custo_total'] for rota in self.rotas)
    
    def aplicar_busca_local(self, max_iteracoes=100):
        """Aplica busca local para melhorar a solução."""
        iteracao = 0
        melhoria = True
        
        while melhoria and iteracao < max_iteracoes:
            melhoria_intra = self._aplicar_busca_local_intra_rota()
            melhoria_entre = self._aplicar_busca_local_entre_rotas()
            
            melhoria = melhoria_intra or melhoria_entre
            
            if melhoria:
                self._recalcular_custo_total()
            
            iteracao += 1
    
    def aplicar_simulated_annealing(self, temperatura_inicial=100, taxa_resfriamento=0.95, iteracoes_por_temperatura=100, temperatura_minima=0.1):
        """Aplica o algoritmo Simulated Annealing para melhorar a solução."""
        melhor_solucao = copy.deepcopy(self.rotas)
        melhor_custo = self.custo_total
        
        temperatura = temperatura_inicial
        
        while temperatura > temperatura_minima:
            for _ in range(iteracoes_por_temperatura):
                # Escolher um movimento aleatório
                tipo_movimento = random.choice(['2opt', 'realocacao_intra', 'troca_entre', 'realocacao_entre'])
                
                if tipo_movimento == '2opt':
                    # Escolher uma rota aleatória
                    if not self.rotas:
                        continue
                    
                    i = random.randint(0, len(self.rotas) - 1)
                    
                    # Aplicar 2-opt
                    nova_rota, _ = self._aplicar_2opt_intra_rota(self.rotas[i])
                    
                    # Calcular diferença de custo
                    delta_custo = nova_rota['custo_total'] - self.rotas[i]['custo_total']
                    
                    # Decidir se aceita o movimento
                    if delta_custo < 0 or random.random() < math.exp(-delta_custo / temperatura):
                        self.rotas[i] = nova_rota
                        self._recalcular_custo_total()
                
                elif tipo_movimento == 'realocacao_intra':
                    # Escolher uma rota aleatória
                    if not self.rotas:
                        continue
                    
                    i = random.randint(0, len(self.rotas) - 1)
                    
                    # Aplicar realocação
                    nova_rota, _ = self._aplicar_realocacao_intra_rota(self.rotas[i])
                    
                    # Calcular diferença de custo
                    delta_custo = nova_rota['custo_total'] - self.rotas[i]['custo_total']
                    
                    # Decidir se aceita o movimento
                    if delta_custo < 0 or random.random() < math.exp(-delta_custo / temperatura):
                        self.rotas[i] = nova_rota
                        self._recalcular_custo_total()
                
                elif tipo_movimento == 'troca_entre':
                    # Escolher duas rotas aleatórias
                    if len(self.rotas) < 2:
                        continue
                    
                    i = random.randint(0, len(self.rotas) - 1)
                    j = random.randint(0, len(self.rotas) - 1)
                    
                    while j == i:
                        j = random.randint(0, len(self.rotas) - 1)
                    
                    # Aplicar troca entre rotas
                    nova_rota1, nova_rota2, _ = self._aplicar_troca_entre_rotas(self.rotas[i], self.rotas[j])
                    
                    # Calcular diferença de custo
                    custo_atual = self.rotas[i]['custo_total'] + self.rotas[j]['custo_total']
                    novo_custo = nova_rota1['custo_total'] + nova_rota2['custo_total']
                    delta_custo = novo_custo - custo_atual
                    
                    # Decidir se aceita o movimento
                    if delta_custo < 0 or random.random() < math.exp(-delta_custo / temperatura):
                        self.rotas[i] = nova_rota1
                        self.rotas[j] = nova_rota2
                        self._recalcular_custo_total()
                
                elif tipo_movimento == 'realocacao_entre':
                    # Escolher duas rotas aleatórias
                    if len(self.rotas) < 2:
                        continue
                    
                    i = random.randint(0, len(self.rotas) - 1)
                    j = random.randint(0, len(self.rotas) - 1)
                    
                    while j == i:
                        j = random.randint(0, len(self.rotas) - 1)
                    
                    # Aplicar realocação entre rotas
                    nova_rota1, nova_rota2, _ = self._aplicar_realocacao_entre_rotas(self.rotas[i], self.rotas[j])
                    
                    # Calcular diferença de custo
                    custo_atual = self.rotas[i]['custo_total'] + self.rotas[j]['custo_total']
                    novo_custo = nova_rota1['custo_total'] + nova_rota2['custo_total']
                    delta_custo = novo_custo - custo_atual
                    
                    # Decidir se aceita o movimento
                    if delta_custo < 0 or random.random() < math.exp(-delta_custo / temperatura):
                        self.rotas[i] = nova_rota1
                        self.rotas[j] = nova_rota2
                        self._recalcular_custo_total()
                
                # Atualizar melhor solução
                if self.custo_total < melhor_custo:
                    melhor_solucao = copy.deepcopy(self.rotas)
                    melhor_custo = self.custo_total
            
            # Resfriar
            temperatura *= taxa_resfriamento
        
        # Restaurar melhor solução
        self.rotas = melhor_solucao
        self.custo_total = melhor_custo
    
    def resolver(self, metodo='busca_local'):
        """Resolve o problema usando o método especificado."""
        self.tempo_inicio = time.perf_counter_ns()
        
        # Construir solução inicial
        self.construir_solucao_inicial()
        
        # Aplicar método de melhoria
        if metodo == 'busca_local':
            self.aplicar_busca_local()
        elif metodo == 'simulated_annealing':
            try:
                import math
                self.aplicar_simulated_annealing()
            except ImportError:
                print("Módulo math não disponível. Usando busca local.")
                self.aplicar_busca_local()
        
        self.tempo_fim = time.perf_counter_ns()
        return self.rotas
    
    def formatar_saida(self):
        """Formata a saída conforme o padrão especificado."""
        # Calcular tempo em clocks/ciclos (valor inteiro)
        tempo_execucao = self.tempo_fim - self.tempo_inicio
        
        saida = []
        saida.append(f"{self.custo_total:.2f}")
        saida.append(f"{len(self.rotas)}")
        saida.append(f"{tempo_execucao}")
        saida.append(f"{tempo_execucao}")
        
        for rota in self.rotas:
            # Formato: índice_depósito dia_roteirização id_rota demanda_total custo_total total_visitas
            total_visitas = len(rota['visitas'])
            linha = f"0 1 {rota['id']} {rota['demanda_total']} {rota['custo_total']:.2f} {total_visitas}"
            
            # Adicionar visitas
            visitas_formatadas = []
            
            # Primeira visita ao depósito
            visitas_formatadas.append("(D 0,1,1)")
            
            # Visitas aos serviços
            for i, servico in enumerate(rota['servicos']):
                de, para = servico['de'], servico['para']
                visitas_formatadas.append(f"(S {servico['id']},{de},{para})")
            
            # Última visita ao depósito
            visitas_formatadas.append("(D 0,1,1)")
            
            linha += " " + " ".join(visitas_formatadas)
            saida.append(linha)
            
        return "\n".join(saida)

def processar_arquivo(arquivo_dat, pasta_saida, metodo='busca_local'):
    """Processa um arquivo .dat e salva o resultado na pasta de saída."""
    try:
        # Extrair o nome base do arquivo
        nome_base = os.path.basename(arquivo_dat)
        
        # Carregar grafo
        g = Grafo()
        g.ler_dat(arquivo_dat)
        
        # Obter capacidade do veículo do arquivo
        capacidade = 5  # Valor padrão
        with open(arquivo_dat, 'r') as f:
            for linha in f:
                if linha.startswith("Capacity:"):
                    capacidade = int(linha.split(":")[1].strip())
                    break
        
        # Construir solução
        solucao = SolucaoMelhorada(g, capacidade)
        solucao.resolver(metodo)
        
        # Formatar saída
        resultado = solucao.formatar_saida()
        
        # Criar arquivo de saída
        arquivo_saida = os.path.join(pasta_saida, f"sol-{nome_base}")
        with open(arquivo_saida, 'w') as f:
            f.write(resultado)
        
        print(f"Processado: {nome_base} -> {arquivo_saida}")
        return True
    except Exception as e:
        print(f"Erro ao processar {arquivo_dat}: {str(e)}")
        return False

def main():
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso: python solucao_etapa3.py <pasta_dados> [metodo]")
        print("Métodos disponíveis: busca_local, simulated_annealing")
        sys.exit(1)
    
    pasta_dados = sys.argv[1]
    
    # Método de melhoria (padrão: busca_local)
    metodo = 'busca_local'
    if len(sys.argv) > 2:
        metodo = sys.argv[2]
    
    # Verificar se a pasta existe
    if not os.path.isdir(pasta_dados):
        print(f"Erro: A pasta {pasta_dados} não existe.")
        sys.exit(1)
    
    # Criar pasta de saída G3Result se não existir
    pasta_saida = "G3Result_SimulatedAnnealing"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        print(f"Pasta {pasta_saida} criada.")
    
    # Encontrar todos os arquivos .dat na pasta
    arquivos_dat = glob.glob(os.path.join(pasta_dados, "*.dat"))
    
    if not arquivos_dat:
        print(f"Nenhum arquivo .dat encontrado em {pasta_dados}")
        sys.exit(1)
    
    print(f"Encontrados {len(arquivos_dat)} arquivos .dat para processar.")
    print(f"Método de melhoria: {metodo}")
    
    # Processar cada arquivo
    sucessos = 0
    falhas = 0
    
    for arquivo in arquivos_dat:
        if processar_arquivo(arquivo, pasta_saida, metodo):
            sucessos += 1
        else:
            falhas += 1
    
    print(f"\nProcessamento concluído: {sucessos} arquivos processados com sucesso, {falhas} falhas.")

if __name__ == "__main__":
    main()
