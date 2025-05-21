import os
import sys
import time
import glob
sys.path.append(os.path.abspath('../etapa1/src'))

from grafo import Grafo

class SolucaoConstrutiva:
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
    
    def construir_solucao(self):
        """Constrói uma solução inicial para o problema."""
        self.tempo_inicio = time.perf_counter_ns()
        
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

def processar_arquivo(arquivo_dat, pasta_saida):
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
        solucao = SolucaoConstrutiva(g, capacidade)
        solucao.construir_solucao()
        
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
    if len(sys.argv) != 2:
        print("Uso: python processar_todos.py <pasta_dados>")
        sys.exit(1)
    
    pasta_dados = sys.argv[1]
    
    # Verificar se a pasta existe
    if not os.path.isdir(pasta_dados):
        print(f"Erro: A pasta {pasta_dados} não existe.")
        sys.exit(1)
    
    # Criar pasta de saída G3Result se não existir
    pasta_saida = "G3Result"
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
        print(f"Pasta {pasta_saida} criada.")
    
    # Encontrar todos os arquivos .dat na pasta
    arquivos_dat = glob.glob(os.path.join(pasta_dados, "*.dat"))
    
    if not arquivos_dat:
        print(f"Nenhum arquivo .dat encontrado em {pasta_dados}")
        sys.exit(1)
    
    print(f"Encontrados {len(arquivos_dat)} arquivos .dat para processar.")
    
    # Processar cada arquivo
    sucessos = 0
    falhas = 0
    
    for arquivo in arquivos_dat:
        if processar_arquivo(arquivo, pasta_saida):
            sucessos += 1
        else:
            falhas += 1
    
    print(f"\nProcessamento concluído: {sucessos} arquivos processados com sucesso, {falhas} falhas.")

if __name__ == "__main__":
    main()
