# Trabalho Prático de Grafos 

Este repositório contém a implementação de um algoritmo para resolver o problema NEARP (Node, Edge, and Arc Routing Problem) em grafos, desenvolvido como trabalho prático da disciplina de Teoria dos Grafos.

## Descrição do Problema

O NEARP é uma generalização de problemas de roteamento em grafos, onde serviços devem ser executados em vértices, arestas e arcos de um grafo. O objetivo é encontrar um conjunto de rotas de custo mínimo, respeitando as seguintes restrições:
- Cada rota começa e termina em um vértice depósito
- Cada serviço deve ser executado exatamente uma vez
- A demanda total de cada rota não pode exceder a capacidade do veículo

## Estrutura do Projeto

```
.
├── etapa1/
│   └── src/
│       ├── grafo.py         # Implementação da classe Grafo e funções de pré-processamento
│       └── estatisticas.py  # Cálculo de estatísticas dos grafos
├── etapa2/
│   ├── dados/
│   │   └── MCGRP/           # Instâncias de teste
│   └── solucao_etapa2.py    # Algoritmo construtivo para solução inicial
├── etapa3/
│   └── solucao_etapa3.py    # Método de melhoria (busca local)
└── G3Result/                # Resultados gerados pelos algoritmos
```

## Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão: sys, os, time, glob, random, copy, math

## Etapas do Trabalho

### Etapa 1: Pré-processamento dos Dados

Nesta etapa, implementamos:
- Estruturas de dados para representação de grafos
- Leitura de arquivos de instância
- Cálculo de estatísticas dos grafos:
  - Quantidade de vértices, arestas e arcos
  - Densidade do grafo
  - Componentes conectados
  - Grau mínimo e máximo dos vértices
  - Intermediação (betweenness)
  - Caminho médio e diâmetro
- Algoritmo de Floyd-Warshall para cálculo de caminhos mais curtos

#### Como executar:
```bash
python estatisticas.py <arquivo.dat>
```

### Etapa 2: Solução Inicial

Nesta etapa, implementamos um algoritmo construtivo que:
- Inicia com uma solução vazia
- Constrói rotas respeitando as restrições de capacidade
- Garante que cada serviço seja executado exatamente uma vez
- Utiliza uma estratégia gulosa para seleção do próximo serviço

#### Como executar:
```bash
# Para processar um único arquivo
python solucao_etapa2.py <arquivo.dat>

# Para processar todos os arquivos em uma pasta
python solucao_etapa2.py <pasta_dados>
```

### Etapa 3: Método de Melhoria

Nesta etapa, implementamos um método de busca local para aprimorar a solução inicial:

**Busca Local**:
- **2-opt**: reordenação de serviços dentro de uma rota
- **Realocação intra-rota**: movimentação de serviços dentro da mesma rota
- **Troca entre rotas**: intercâmbio de serviços entre diferentes rotas
- **Realocação entre rotas**: movimentação de serviços de uma rota para outra

A busca local é aplicada iterativamente até que não seja mais possível encontrar melhorias ou até atingir um número máximo de iterações.

#### Como executar:
```bash
# Para processar todos os arquivos em uma pasta
python solucao_etapa3.py <pasta_dados>
```

## Formato de Saída

O formato de saída segue o padrão especificado no enunciado:
```
<custo_total>
<numero_rotas>
<tempo_execucao>
<tempo_execucao>
0 1 <id_rota> <demanda_total> <custo_total> <total_visitas> (D 0,1,1) (S <id_servico>,<de>,<para>) ... (D 0,1,1)
...
```

## Comparação dos Métodos

Para comparar os resultados dos diferentes métodos:

1. Execute o algoritmo construtivo (etapa 2):
```bash
python solucao_etapa2.py <pasta_dados>
# Salve os resultados em uma pasta separada
mv G3Result G3Result_Construtivo
```

2. Execute a busca local (etapa 3):
```bash
python solucao_etapa3.py <pasta_dados>
# Os resultados serão salvos na pasta G3Result
```

## Análise dos Resultados

A busca local consegue melhorar significativamente a qualidade das soluções iniciais para muitas instâncias, reduzindo o custo total das rotas. No entanto, para algumas instâncias específicas, a melhoria pode ser limitada ou inexistente.

Algumas instâncias (como CBMix1.dat e DI-NEARP-n240-Q2k.dat) podem não ter solução viável com os algoritmos implementados, o que é um comportamento esperado devido às características estruturais dessas instâncias.

## Autores

- André Araújo Mendonça

## Referências

- Laporte, G. (2000). The Vehicle Routing Problem: An overview of exact and approximate algorithms. European Journal of Operational Research, 59(3), 345-358.
- Prins, C., & Bouchenoua, S. (2005). A Memetic Algorithm Solving the VRP, the CARP and General Routing Problems with Nodes, Edges and Arcs. In Recent Advances in Memetic Algorithms (pp. 65-85).
