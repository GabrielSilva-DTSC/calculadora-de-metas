### ABOUT ME
- **CONTACT**:  everton.gabriel@academico.ufpb.br
- **Developer:** [Gabriel Silva](https://github.com/GabrielSilva-DTSC)
- **Subject:** Principles of Programming II
- **Professor:** Dr. Adriana

# 📊 Goal Calculator

Desktop system for calculating and managing sales goals, with a modern and intuitive graphical interface. Developed as a project for the **Principles of Programming II** course, demonstrating Object-Oriented Programming concepts applied to a real-world problem.

> **Persona:** Josefino Nonato — a manager who uses Excel spreadsheets to organize employee information but finds it difficult to calculate bonuses clearly and efficiently.

---

## ✨ Features

- **Control Panel** — Overview with 6 key metrics, revenue chart by sector, and donut chart for goals
- **Salesperson Management** — Full table with animated progress bars, filters by name/sector/status, and one-click details
- **Product Catalog** — Product listing with prices and integrated search
- **Reports** — Summary by sector, ranking of top and bottom performers
- **Settings** — Dynamic adjustment of goals and base salary, with real-time recalculation
- **Automatic Bonus** — Tiered calculation (5%, 10%, 15%) based on the percentage of the goal achieved
- **Smart Classification** — Salespeople who achieve 200%+ of their goal are marked as *Superstar*

---

## 🎨 Interface

Vibrant and cartoon-like visuals, featuring:
- Colorful palette inspired by Regular Show (cyan, orange, green, pink)
- Rounded corners and soft shadows
- Custom vector graphics (bar and donut charts)
- Progress, entrance, and notification animations
- Modal dialogs without native operating system styling
- Responsive layout that adapts to window size

---

## 🛠️ Technologies

| Layer | Technology |
|--------|-----------|
| Graphical Interface | **PySide6** (Qt 6) |
| Data Manipulation | **pandas** |
| Excel Reading | **openpyxl** |
| Language | **Python 3.10+** |

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- Git

### Steps

```bash
# Clone the repository
git clone https://github.com/GabrielSilva-DTSC/calculadora-de-metas.git
cd calculadora-de-metas

# (Optional) Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install PySide6 pandas openpyxl
```

---

## 🚀 Execution

Make sure the data files are in the same folder as `app.py`:

```
calculadora-de-metas/
├── app.py              ← Graphical interface (entry point)
├── vendedoresII.py     ← Business logic (OOP)
├── vendas.xlsx         ← Sales data
├── produtos.xlsx       ← Product catalog
├── vendedores.xlsx     ← Salesperson and sector registration
└── README.md
```

```bash
python app.py
```

> It is also possible to run only the business logic in the terminal:
> ```bash
> python vendedoresII.py
> ```

---

## 🏗️ Architecture

The project follows the principle of **separation between UI and business logic**:

```
┌─────────────────────────────────────────────┐
│                  app.py                      │
│  (Presentation Layer — PySide6)             │
│  • Pages, widgets, charts, animations       │
│  • Does not contain business rules          │
└──────────────────┬──────────────────────────┘
                   │ import
                   ▼
┌─────────────────────────────────────────────┐
│             vendedoresII.py                  │
│  (Business Layer — pure OOP)                │
│  • IAvaliavel (abstract interface)          │
│  • Vendedor (base class)                    │
│  • VendedorComBonus (inheritance + polymorphism)│
│  • VendedorSuperstar (inheritance + polymorphism)│
│  • GerenciadorVendas (orchestrator)         │
└──────────────────┬──────────────────────────┘
                   │ reading
                   ▼
┌─────────────────────────────────────────────┐
│           *.xlsx (Data)                     │
│  vendas.xlsx · produtos.xlsx · vendedores   │
└─────────────────────────────────────────────┘
```

---

## 📚 Demonstrated OOP Concepts

| Concept | Where it is |
|----------|-----------|
| **Abstract Class** | `IAvaliavel` — defines contract with `calcular_progresso()` and `relatorio()` |
| **Encapsulation** | Private attributes (`__nome`, `__setor`, `__vendas`, `__meta`) with `@property` and `@setter` |
| **Inheritance** | `VendedorComBonus` and `VendedorSuperstar` extend `Vendedor` |
| **Polymorphism** | Each subclass implements `calcular_progresso()` and `relatorio()` differently |
| **Dunder Methods** | `__init__`, `__str__`, `__repr__`, `__len__` |
| **Validation** | Setters with `raise ValueError` for invalid data |
| **Composition** | `GerenciadorVendas` manages a list of `Vendedor` objects |

---

## 📐 Data Structure

### vendedores.xlsx
| salesperson | sector |
|----------|-------|
| ana silva | clothes |
| bruno oliveira | domestic |
| eduardo pereira | electronics |
| ... | ... |

### produtos.xlsx
| product | price |
|---------|-------|
| cotton polo shirt | 129.90 |
| smartphone | 1899.00 |
| ... | ... |

### vendas.xlsx
| salespeople | product | quantity |
|------------|---------|------------|
| ana silva | cotton polo shirt | 10 |
| bruno oliveira | premium jeans | 15 |
| ... | ... | ... |

---

## 📋 Business Rules

- **Default goal:** R$ 1,567.70 per salesperson
- **Automatic classification:**
  - Sales ≥ 200% of goal → `VendedorSuperstar`
  - Electronics or domestic sector → `VendedorComBonus`
  - Others → `Vendedor` (default)
- **Bonus tiers** (on top of the base salary of R$ 2,000.00):
  - Above 200% → 15% (R$ 300.00)
  - Above 150% → 10% (R$ 200.00)
  - Above 100% → 5% (R$ 100.00)
  - Below 100% → no bonus

---

## 🤖 AI Tools Used

The development of the graphical interface and bug fixing were assisted by artificial intelligence:

- **GLM (Zhipu AI)** — Full production of the modern graphical interface with PySide6, including custom widgets, vector graphics, navigation system, animations, modal dialogs, and the entire thematic visual design
- **Claude Code (Anthropic)** — Bug fixing, import adjustments, and refinements in the integration between the UI layer and the existing business logic

> AI tools were used as assistants in the development process. The project architecture, business logic (`vendedoresII.py`), and data are authored by the developer.

---

## 📄 License

This project was developed for academic purposes.
```
---
---
### SOBRE MIM
- **CONTATO**:  everton.gabriel@academico.ufpb.br
- **Desenvolvedor:** [Gabriel Silva](https://github.com/GabrielSilva-DTSC)
- **Disciplina:** Princípios da Programação II
- **Professora:** Dr. Adriana

# 📊 Calculadora de Metas

Sistema desktop para cálculo e gerenciamento de metas de vendas, com interface gráfica moderna e intuitiva. Desenvolvido como projeto da disciplina **Princípios da Programação II**, demonstrando conceitos de Programação Orientada a Objetos aplicados a um problema real.

> **Persona:** Josefino Nonato — gerente que utiliza planilhas Excel para organizar informações de funcionários, mas encontra dificuldades para calcular bônus de forma clara e eficiente.

---

## ✨ Funcionalidades

- **Painel de Controle** — Visão geral com 6 métricas-chave, gráfico de faturamento por setor e gráfico de rosca de metas
- **Gestão de Vendedores** — Tabela completa com barras de progresso animadas, filtros por nome/setor/status e detalhes em um clique
- **Catálogo de Produtos** — Listagem dos produtos com preços e busca integrada
- **Relatórios** — Resumo por setor, ranking dos melhores e menores desempenhos
- **Configurações** — Ajuste dinâmico de meta e salário base, com recálculo em tempo real
- **Bônus Automático** — Cálculo escalonado (5%, 10%, 15%) baseado no percentual de meta atingido
- **Classificação Inteligente** — Vendedores que atingem 200%+ da meta são marcados como *Superstar*

---

## 🎨 Interface

Visual vibrante e cartoon-like, com:
- Paleta colorida inspirada em Regular Show (ciano, laranja, verde, rosa)
- Cantos arredondados e sombras suaves
- Gráficos vetoriais customizados (barras e rosca)
- Animações de progresso, entrada e notificações
- Diálogos modais sem estilo nativo do sistema operacional
- Layout responsivo que se adapta ao tamanho da janela

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Interface Gráfica | **PySide6** (Qt 6) |
| Manipulação de Dados | **pandas** |
| Leitura de Excel | **openpyxl** |
| Linguagem | **Python 3.10+** |

---

## 📦 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Git

### Passos

```bash
# Clone o repositório
git clone https://github.com/GabrielSilva-DTSC/calculadora-de-metas.git
cd calculadora-de-metas

# (Opcional) Crie e ative um ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instale as dependências
pip install PySide6 pandas openpyxl
```

---

## 🚀 Execução

Certifique-se de que os arquivos de dados estão na mesma pasta do `app.py`:

```
calculadora-de-metas/
├── app.py              ← Interface gráfica (ponto de entrada)
├── vendedoresII.py     ← Lógica de negócio (POO)
├── vendas.xlsx         ← Dados de vendas
├── produtos.xlsx       ← Catálogo de produtos
├── vendedores.xlsx     ← Cadastro de vendedores e setores
└── README.md
```

```bash
python app.py
```

> Também é possível executar apenas a lógica de negócio no terminal:
> ```bash
> python vendedoresII.py
> ```

---

## 🏗️ Arquitetura

O projeto segue o princípio de **separação entre UI e lógica de negócio**:

```
┌─────────────────────────────────────────────┐
│                  app.py                      │
│  (Camada de Apresentação — PySide6)         │
│  • Páginas, widgets, gráficos, animações    │
│  • Não contém regras de negócio             │
└──────────────────┬──────────────────────────┘
                   │ import
                   ▼
┌─────────────────────────────────────────────┐
│             vendedoresII.py                  │
│  (Camada de Negócio — POO pura)             │
│  • IAvaliavel (interface abstrata)          │
│  • Vendedor (classe base)                   │
│  • VendedorComBonus (herança + polimorfismo)│
│  • VendedorSuperstar (herança + polimorfismo│
│  • GerenciadorVendas (orchestrador)         │
└──────────────────┬──────────────────────────┘
                   │ leitura
                   ▼
┌─────────────────────────────────────────────┐
│           *.xlsx (Dados)                     │
│  vendas.xlsx · produtos.xlsx · vendedores   │
└─────────────────────────────────────────────┘
```

---

## 📚 Conceitos de POO Demonstrados

| Conceito | Onde está |
|----------|-----------|
| **Classe Abstrata** | `IAvaliavel` — define contrato com `calcular_progresso()` e `relatorio()` |
| **Encapsulamento** | Atributos privados (`__nome`, `__setor`, `__vendas`, `__meta`) com `@property` e `@setter` |
| **Herança** | `VendedorComBonus` e `VendedorSuperstar` estendem `Vendedor` |
| **Polimorfismo** | Cada subclasse implementa `calcular_progresso()` e `relatorio()` de forma diferente |
| **Dunder Methods** | `__init__`, `__str__`, `__repr__`, `__len__` |
| **Validação** | Setters com `raise ValueError` para dados inválidos |
| **Composição** | `GerenciadorVendas` gerencia uma lista de objetos `Vendedor` |

---

## 📐 Estrutura dos Dados

### vendedores.xlsx
| vendedor | setor |
|----------|-------|
| ana silva | roupas |
| bruno oliveira | domesticos |
| eduardo pereira | eletronicos |
| ... | ... |

### produtos.xlsx
| produto | preco |
|---------|-------|
| camisa polo algodão | 129.90 |
| smartphone | 1899.00 |
| ... | ... |

### vendas.xlsx
| vendedores | produto | quantidade |
|------------|---------|------------|
| ana silva | camisa polo algodão | 10 |
| bruno oliveira | calça jeans premium | 15 |
| ... | ... | ... |

---

## 📋 Regras de Negócio

- **Meta padrão:** R$ 1.567,70 por vendedor
- **Classificação automática:**
  - Vendas ≥ 200% da meta → `VendedorSuperstar`
  - Setor eletrônicos ou domésticos → `VendedorComBonus`
  - Demais → `Vendedor` (padrão)
- **Faixas de bônus** (sobre o salário base de R$ 2.000,00):
  - Acima de 200% → 15% (R$ 300,00)
  - Acima de 150% → 10% (R$ 200,00)
  - Acima de 100% → 5% (R$ 100,00)
  - Abaixo de 100% → sem bônus

---

Aqui está a seção atualizada para adicionar ao final do README, antes da licença:

```markdown
---

## 🤖 Ferramentas de IA Utilizadas

O desenvolvimento da interface gráfica e a correção de bugs contaram com o auxílio de inteligência artificial:

- **GLM (Zhipu AI)** — Produção completa da interface gráfica moderna com PySide6, incluindo widgets customizados, gráficos vetoriais, sistema de navegação, animações, diálogos modais e todo o design visual temático
- **Claude Code (Anthropic)** — Correção de bugs, ajustes de importação e refinamentos na integração entre a camada de UI e a lógica de negócio existente

> As ferramentas de IA foram utilizadas como assistentes no processo de desenvolvimento. A arquitetura do projeto, a lógica de negócio (`vendedoresII.py`) e os dados são de autoria do desenvolvedor.

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos.
```

Substitua a seção final do seu README por isso. Fica claro, honesto e registra exatamente o papel de cada ferramenta sem atribuir a elas a autoria do projeto como um todo.
```
