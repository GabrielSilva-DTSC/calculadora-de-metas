from abc import ABC, abstractmethod
import pandas as pd


# ══════════════════════════════════════════════════════════════
# 1. INTERFACE  →  abc + @abstractmethod
# ══════════════════════════════════════════════════════════════
class IAvaliavel(ABC):
    """Contrato: qualquer entidade avaliável deve saber calcular
    seu progresso e gerar um relatório."""

    @abstractmethod
    def calcular_progresso(self) -> float:
        pass

    @abstractmethod
    def relatorio(self) -> str:
        pass


# ══════════════════════════════════════════════════════════════
# 2. CLASSE BASE  →  Encapsulamento + Dunder + @property
# ══════════════════════════════════════════════════════════════
class Vendedor(IAvaliavel):
    """
    Representa um vendedor genérico.
    Demonstra: __init__, __str__, __repr__, @property, @setter,
    atributos privados (__nome, __setor, __vendas).
    """

    # [Requisito 4 – Dunder] construtor obrigatório
    def __init__(self, nome: str, setor: str, meta: float):
        # [Requisito 1 – Encapsulamento] atributos privados
        self.__nome   = nome
        self.__setor  = setor
        self.__meta   = meta
        self.__vendas = 0.0

    # ── [Requisito 2 e 3 – Getters/Setters com @property] ──
    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, valor: str):
        if not valor.strip():
            raise ValueError("Nome não pode ser vazio.")
        self.__nome = valor.strip()

    @property
    def setor(self):
        return self.__setor

    @setor.setter
    def setor(self, valor: str):
        self.__setor = valor.strip()

    @property
    def meta(self):
        return self.__meta

    @meta.setter
    def meta(self, valor: float):
        if valor <= 0:
            raise ValueError("Meta deve ser positiva.")
        self.__meta = valor

    @property
    def vendas(self):
        return self.__vendas

    @vendas.setter
    def vendas(self, valor: float):
        if valor < 0:
            raise ValueError("Vendas não podem ser negativas.")
        self.__vendas = valor

    # [Requisito 6 – Polimorfismo] implementação base
    def calcular_progresso(self) -> float:
        return (self.__vendas / self.__meta) * 100

    def relatorio(self) -> str:
        status = "✔ Bateu a meta!" if self.__vendas >= self.__meta else "✘ Não bateu."
        return (
            f"Vendedor: {self.__nome:<20} | Setor: {self.__setor:<12} | "
            f"Total Vendido: R$ {self.__vendas:>8.2f} | "
            f"Progresso: {self.calcular_progresso():>6.1f}% | {status}"
        )

    # [Requisito 4 – Dunder] __str__ e __repr__
    def __str__(self):
        return self.relatorio()

    def __repr__(self):
        return (
            f"Vendedor(nome={self.__nome!r}, setor={self.__setor!r}, "
            f"vendas={self.__vendas:.2f}, meta={self.__meta:.2f})"
        )


# ══════════════════════════════════════════════════════════════
# 3. CLASSES FILHAS  →  Herança + Polimorfismo
# ══════════════════════════════════════════════════════════════
class VendedorComBonus(Vendedor):
    """
    Vendedor que recebe bônus escalonado por desempenho.
    [Requisito 5 – Herança] estende Vendedor.
    [Requisito 6 – Polimorfismo] sobrescreve calcular_progresso e relatorio.
    """

    FAIXAS_BONUS = [
        (200, 0.15),   # acima de 200% → 15%
        (150, 0.10),   # acima de 150% → 10%
        (100, 0.05),   # acima de 100% →  5%
        (0,   0.00),   # abaixo de 100% → sem bônus
    ]

    def __init__(self, nome: str, setor: str, meta: float, salario_base: float):
        super().__init__(nome, setor, meta)
        self.__salario_base = salario_base

    @property
    def salario_base(self):
        return self.__salario_base

    def calcular_bonus(self) -> float:
        progresso = self.calcular_progresso()
        for minimo, percentual in self.FAIXAS_BONUS:
            if progresso >= minimo:
                return self.__salario_base * percentual
        return 0.0

    # Polimorfismo: inclui bônus no relatório
    def relatorio(self) -> str:
        base = super().relatorio()
        bonus = self.calcular_bonus()
        return f"{base} | Bônus: R$ {bonus:.2f}"


class VendedorSuperstar(Vendedor):
    """
    Vendedor de alto desempenho com ranking especial.
    [Requisito 5 – Herança] estende Vendedor.
    [Requisito 6 – Polimorfismo] sobrescreve calcular_progresso com teto 999%.
    """

    def calcular_progresso(self) -> float:
        # Teto visual de 999% para não distorcer relatórios
        return min(super().calcular_progresso(), 999.0)

    def relatorio(self) -> str:
        base = super().relatorio()
        return f" * SUPERSTAR * {base}"


# ══════════════════════════════════════════════════════════════
# 4. GERENCIADOR  →  Encapsulamento + Dunder extra
# ══════════════════════════════════════════════════════════════
class GerenciadorVendas:
    """Carrega os dados dos Excel e gerencia os objetos Vendedor."""

    META_PADRAO = 1567.70

    def __init__(self):
        self.__vendedores: list[Vendedor] = []   # Encapsulamento

    def __len__(self):
        return len(self.__vendedores)

    def __repr__(self):
        return f"GerenciadorVendas({len(self)} vendedores carregados)"

    def carregar_dados(self, arq_vendas: str, arq_produtos: str, arq_vendedores: str):
        self.__vendedores = []
        df_vendas    = pd.read_excel(arq_vendas,     engine="openpyxl").rename(columns={"vendedores": "vendedor"})
        df_produtos  = pd.read_excel(arq_produtos,   engine="openpyxl")
        df_vendedores = pd.read_excel(arq_vendedores, engine="openpyxl").rename(columns={"eletronicos": "setor"})

        # Cruzamento e cálculo de faturamento
        df_detalhe = pd.merge(df_vendas, df_produtos, on="produto")
        df_detalhe["faturamento"] = df_detalhe["quantidade"] * df_detalhe["preco"]
        total_por_vendedor = df_detalhe.groupby("vendedor")["faturamento"].sum().to_dict()

        # Cria os objetos usando as classes filhas para os maiores vendedores
        for _, linha in df_vendedores.iterrows():
            nome  = linha["vendedor"]
            setor = linha["setor"]
            total = total_por_vendedor.get(nome, 0.0)

            if total >= self.META_PADRAO * 2:
                v = VendedorSuperstar(nome, setor, self.META_PADRAO)
            elif setor in ("eletronicos", "domesticos"):
                v = VendedorComBonus(nome, setor, self.META_PADRAO, salario_base=2000.0)
            else:
                v = Vendedor(nome, setor, self.META_PADRAO)

            v.vendas = total   # usa o @setter com validação
            self.__vendedores.append(v)

    def exibir_relatorio(self):
        print(f"\n{'─'*100}")
        print(f" RELATÓRIO DE VENDAS  |  Meta: R$ {self.META_PADRAO:.2f}  |  {len(self)} vendedores")
        print(f"{'─'*100}")
        for v in self.__vendedores:
            print(v)      # chama __str__ → relatorio() (polimorfismo em ação)
        print(f"{'─'*100}\n")

    def resumo_por_setor(self):
        setores: dict[str, list[float]] = {}
        for v in self.__vendedores:
            setores.setdefault(v.setor, []).append(v.vendas)

        print(" RESUMO POR SETOR")
        print(f"{'─'*50}")
        for setor, valores in sorted(setores.items()):
            total = sum(valores)
            media = total / len(valores)
            print(f"  {setor:<14} | Total: R$ {total:>9.2f} | Média: R$ {media:>7.2f}")
        print(f"{'─'*50}\n")


# ══════════════════════════════════════════════════════════════
# 5. EXECUÇÃO
# ══════════════════════════════════════════════════════════════


if __name__ == "__main__":

    gerenciador = GerenciadorVendas()

    # Carregar a partir dos arquivos do repositório original
    gerenciador.carregar_dados(
        arq_vendas="vendas.xlsx",
        arq_produtos="produtos.xlsx",
        arq_vendedores="vendedores.xlsx"
    )

    # Relatório completo (polimorfismo: cada tipo de vendedor imprime diferente)
    gerenciador.exibir_relatorio()

    # Resumo por setor
    gerenciador.resumo_por_setor()

    # ── Demonstração explícita dos conceitos ──────────────────

    print("=== DEMONSTRAÇÃO DOS CONCEITOS DE POO ===\n")

    # Dunder __repr__ e __len__
    print("[Dunder __repr__]", repr(gerenciador))
    print(f"[Dunder __len__]  Total de vendedores: {len(gerenciador)}\n")

    # @property getter e setter com validação
    teste = VendedorComBonus("Teste Silva", "roupas", 1567.70, 2000.0)
    print(f"[Getter @property] nome = {teste.nome!r}")
    teste.nome = "Gabriel Silva"       # setter OK
    print(f"[Setter válido]    nome atualizado para {teste.nome!r}")
    try:
        teste.vendas = -50             # setter com erro
    except ValueError as e:
        print(f"[Setter inválido]  {e}")

    # Polimorfismo: calcular_progresso() difere por classe
    print("\n[Polimorfismo – calcular_progresso()]")
    v1 = Vendedor("Padrão",    "roupas",      1567.70)
    v2 = VendedorComBonus("Com Bônus", "eletronicos", 1567.70, 2000.0)
    v3 = VendedorSuperstar("Superstar", "eletronicos", 1567.70)
    for v in (v1, v2, v3):
        v.vendas = 3500.0
        print(f"  {v.__class__.__name__:<20}: {v.calcular_progresso():.1f}%")

    print("\n[__str__ de VendedorComBonus]")
    print(v2)

    print("\n[__repr__ de VendedorSuperstar]")
    print(repr(v3))