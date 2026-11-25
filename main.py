import pandas as pd
import gurobipy as gp
from gurobipy import GRB

# Entrada de dados

dados = pd.read_csv('itens_100.csv')

itens = dict(zip(dados['item'], dados['peso']))
caixas = list(range(1, 101))

import gurobipy as gp
from gurobipy import GRB

# Cria modelo

modelo = gp.Model("Empacotamento")

# Variáveis de Decisão

x = modelo.addVars([(i, j) for i in itens for j in caixas], vtype=GRB.BINARY, name="x")
y = modelo.addVars(caixas, vtype=GRB.BINARY, name="y")

# Função objetivo

modelo.setObjective(gp.quicksum(y[j] for j in caixas), GRB.MINIMIZE)

# Restrições

# Todo item deve estar em uma única caixa

for i in itens:
  modelo.addConstr(gp.quicksum(x[i, j] for j in caixas) == 1, name="item_na_caixa")

# A soma dos pesos dos itens em uma caixa não pode ultrapassar sua capacidade (10kg)

for j in caixas:
  modelo.addConstr(gp.quicksum(x[i, j] * itens[i] for i in itens) <= 10 * y[j], name="capacidade_max_caixa")

# Cada caixa pode possuir no máximo 3 itens

for j in caixas:
  modelo.addConstr(gp.quicksum(x[i, j] for i in itens) <= 3, name="max_item_caixa")

# Pelo menos 60% da capacidade da caixa é utilizada

for j in caixas:
  modelo.addConstr(gp.quicksum(x[i, j] * itens[i] for i in itens) >= 6 * y[j], name="capacidade_min_caixa")

modelo.optimize()

if modelo.status == GRB.OPTIMAL:
    print(f"\nTotal de caixas utilizadas: {int(modelo.objVal)}")
    relatorio = []
    for j in caixas:
        if y[j].X > 0.5:
            itens_alocados = [i for i in itens if x[i, j].X > 0.5]
            peso_total = sum(itens[i] for i in itens_alocados)
            ocupacao = (peso_total / 10.0) * 100
            print(f"Caixa {j}: Itens {itens_alocados} | Peso: {peso_total:.2f} kg ({ocupacao:.1f}%)")
            relatorio.append({
                "Caixa": j,
                "Itens": str(itens_alocados),
                "Qtd_Itens": len(itens_alocados),
                "Peso_Total_kg": round(peso_total, 2),
                "Ocupacao_%": round(ocupacao, 1)
            })
    pd.DataFrame(relatorio).to_csv("relatorio_logistica.csv", index=False)
elif modelo.status == GRB.INFEASIBLE:
    print("Modelo inviável: verifique se a restrição de 60% é atendível para todos os itens.")

