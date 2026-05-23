import pandas as pd

# Parâmetros iniciais
META_EM_REAIS = 1567.70

# Criando classe vendedor:
class Vendedor():
    def __init__(self, nome, setor):
        self.nome = nome
        self.setor = setor
        self.vendas = 0  # Inicializado em 0

    # Método de vendas
    def vendeu(self, vendas):
        self.vendas = vendas

    # Método para avaliar cumprimento de metas
    def meta_alcancada(self, meta):
        if self.vendas >= meta:
            return 1  # Retorna 1 se bateu a meta
        else:
            return 0  # Retorna 0 se não bateu

# Lendo os dados do Excel
try:
    df_vendas_realizadas = pd.read_excel('vendas.xlsx')
    df_produtos = pd.read_excel('produtos.xlsx')
    df_vendedores = pd.read_excel('vendedores.xlsx').rename(columns={"eletronicos": "setor"})
except FileNotFoundError as e:
    print(f"Erro ao carregar arquivos: {e}")
    print("Verifique se 'vendas.xlsx', 'produtos.xlsx' e 'vendedores.xlsx' estão na mesma pasta.")
    exit()

print("--- PROCESSANDO AS VENDAS ---")

# Cruzando os dados das tabelas
# Unificamos o nome para "vendedor" antes do merge.
df_vendas_realizadas = df_vendas_realizadas.rename(columns={"vendedores": "vendedor"})
df_detalhe_vendas = pd.merge(df_vendas_realizadas, df_produtos, on="produto")

# Calculando o faturamento de cada linha (Quantidade * Preço)
df_detalhe_vendas["faturamento"] = df_detalhe_vendas["quantidade"] * df_detalhe_vendas["preco"]

# Agrupando por Vendedor para saber o total que cada um vendeu
total_por_vendedor = df_detalhe_vendas.groupby("vendedor")["faturamento"].sum().to_dict()

# Usei i.a para criar essa parte 
for index, linha in df_vendedores.iterrows():
    nome = linha["vendedor"]
    setor = linha["setor"]

    # Cria o objeto Vendedor usando a classe
    vendedor_obj = Vendedor(nome, setor)

    # Busca o total vendido por ele (se não vendeu nada, assume 0)
    valor_vendas = total_por_vendedor.get(nome, 0)

    # Usa o método da classe para atualizar as vendas
    vendedor_obj.vendeu(valor_vendas)

    # Avalia a meta
    resultado_meta = vendedor_obj.meta_alcancada(META_EM_REAIS)

    status_meta = "Bateu a meta!" if resultado_meta == 1 else "Não bateu."

    print(
        f"Vendedor: {vendedor_obj.nome:<20} | Setor: {vendedor_obj.setor:<12} | "
        f"Total Vendido: R$ {vendedor_obj.vendas:>8.2f} | Status: {status_meta}"
    )
