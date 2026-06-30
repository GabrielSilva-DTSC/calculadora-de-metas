#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║  CALCULADORA DE METAS — Interface Gráfica Moderna            ║
║  Visual inspirado em Regular Show (vibrante, cartoon-like)    ║
║  Framework: PySide6                                          ║
║                                                              ║
║  Dependências:                                               ║
║    pip install PySide6 pandas openpyxl                        ║
║                                                              ║
║  Execute: python app.py                                      ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sys, math
from collections import defaultdict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QScrollArea, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QAbstractItemView, QDoubleSpinBox
)
from PySide6.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QRectF, Property, Signal, QPointF
)
from PySide6.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QLinearGradient,
    QPainterPath, QIcon, QPixmap
)

# ═══════════════════════════════════════════════════════════════
#  LÓGICA DE NEGÓCIO — Importação do módulo existente
# ═══════════════════════════════════════════════════════════════
_LOGIC_FROM_MODULE = False
try:
    from vendedoresII import (
        Vendedor, VendedorComBonus, VendedorSuperstar, GerenciadorVendas
    )
    _LOGIC_FROM_MODULE = True
except ImportError:
    pass

if not _LOGIC_FROM_MODULE:
    import pandas as pd
    from abc import ABC, abstractmethod

    class IAvaliavel(ABC):
        @abstractmethod
        def calcular_progresso(self) -> float: pass
        @abstractmethod
        def relatorio(self) -> str: pass

    class Vendedor(IAvaliavel):
        def __init__(self, nome: str, setor: str, meta: float):
            self.__nome = nome; self.__setor = setor
            self.__meta = meta; self.__vendas = 0.0
        @property
        def nome(self): return self.__nome
        @nome.setter
        def nome(self, v):
            if not v.strip(): raise ValueError("Nome vazio.")
            self.__nome = v.strip()
        @property
        def setor(self): return self.__setor
        @setor.setter
        def setor(self, v): self.__setor = v.strip()
        @property
        def meta(self): return self.__meta
        @meta.setter
        def meta(self, v):
            if v <= 0: raise ValueError("Meta positiva.")
            self.__meta = v
        @property
        def vendas(self): return self.__vendas
        @vendas.setter
        def vendas(self, v):
            if v < 0: raise ValueError("Vendas negativas.")
            self.__vendas = v
        def calcular_progresso(self) -> float:
            return (self.__vendas / self.__meta) * 100 if self.__meta > 0 else 0
        def relatorio(self) -> str:
            s = "✔ Bateu!" if self.__vendas >= self.__meta else "✘ Não bateu."
            return f"{self.__nome} | {self.__setor} | R$ {self.__vendas:.2f} | {self.calcular_progresso():.1f}% | {s}"
        def __str__(self): return self.relatorio()
        def __repr__(self):
            return f"Vendedor({self.__nome!r}, {self.__setor!r}, {self.__vendas:.2f})"

    class VendedorComBonus(Vendedor):
        FAIXAS = [(200, 0.15), (150, 0.10), (100, 0.05), (0, 0.00)]
        def __init__(self, nome, setor, meta, salario_base=2000.0):
            super().__init__(nome, setor, meta)
            self.__salario_base = salario_base
        @property
        def salario_base(self): return self.__salario_base
        def calcular_bonus(self) -> float:
            p = self.calcular_progresso()
            for mn, pc in self.FAIXAS:
                if p >= mn: return self.__salario_base * pc
            return 0.0
        def relatorio(self) -> str:
            return f"{super().relatorio()} | Bônus: R$ {self.calcular_bonus():.2f}"

    class VendedorSuperstar(Vendedor):
        def calcular_progresso(self) -> float:
            return min(super().calcular_progresso(), 999.0)
        def relatorio(self) -> str:
            return f"★ SUPERSTAR ★ {super().relatorio()}"

    class GerenciadorVendas:
        META_PADRAO = 1567.70
        def __init__(self):
            self.__vendedores: list = []
        def __len__(self): return len(self.__vendedores)
        def carregar_dados(self, arq_vendas, arq_produtos, arq_vendedores):
            self.__vendedores = []
            df_v = pd.read_excel(arq_vendas, engine="openpyxl").rename(columns={"vendedores": "vendedor"})
            df_p = pd.read_excel(arq_produtos, engine="openpyxl")
            df_s = pd.read_excel(arq_vendedores, engine="openpyxl").rename(columns={"eletronicos": "setor"})
            df_d = pd.merge(df_v, df_p, on="produto")
            df_d["faturamento"] = df_d["quantidade"] * df_d["preco"]
            totais = df_d.groupby("vendedor")["faturamento"].sum().to_dict()
            for _, row in df_s.iterrows():
                n, s = row["vendedor"], row["setor"]
                t = totais.get(n, 0.0)
                if t >= self.META_PADRAO * 2:
                    v = VendedorSuperstar(n, s, self.META_PADRAO)
                elif s in ("eletronicos", "domesticos"):
                    v = VendedorComBonus(n, s, self.META_PADRAO, 2000.0)
                else:
                    v = Vendedor(n, s, self.META_PADRAO)
                v.vendas = t
                self.__vendedores.append(v)


def get_vendedores_list(ger) -> list:
    """Acessa a lista interna de vendedores do gerenciador."""
    return ger._GerenciadorVendas__vendedores


# ═══════════════════════════════════════════════════════════════
#  TEMA — Cores, fontes e constantes visuais
# ═══════════════════════════════════════════════════════════════
class T:
    """Constantes do tema visual (Regular Show — vibrante e cartoon)."""
    PRIMARY      = "#00B4D8"
    PRIMARY_DK   = "#0096B7"
    PRIMARY_LT   = "#90E0EF"
    SECONDARY    = "#FF6B35"
    SECONDARY_DK = "#E55A25"
    SECONDARY_LT = "#FFD6C2"
    ACCENT       = "#7CB518"
    ACCENT_DK    = "#5A8A10"
    ACCENT_LT    = "#D4E8A8"
    BG           = "#F0F4E8"
    BG_SIDEBAR   = "#1B2838"
    BG_SIDEBAR2  = "#243447"
    BG_CARD      = "#FFFFFF"
    TXT          = "#1B2838"
    TXT2         = "#5A6C7D"
    TXT_LT       = "#FFFFFF"
    TXT_MUTED    = "#8E9EAB"
    OK           = "#2D6A4F"
    OK_LT        = "#D8F3DC"
    WARN         = "#FFB703"
    WARN_LT      = "#FFF3CD"
    ERR          = "#E63946"
    ERR_LT       = "#FFE0E3"
    BORDER       = "#E2E8D0"
    PURPLE       = "#7C3AED"
    PURPLE_LT    = "#EDE9FE"
    PINK         = "#EC4899"
    PINK_LT      = "#FCE7F3"
    R            = 12
    R_LG         = 16
    R_SM         = 8

SETOR_CORES = {
    "roupas":      ("#00B4D8", "#D4F1F9"),
    "eletronicos": ("#FF6B35", "#FFD6C2"),
    "domesticos":  ("#7CB518", "#D4E8A8"),
    "cosmeticos":  ("#EC4899", "#FCE7F3"),
    "acessorios":  ("#7C3AED", "#EDE9FE"),
}

STYLESHEET = f"""
QWidget {{ font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 13px; color: {T.TXT}; }}
#sidebar {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {T.BG_SIDEBAR},stop:1 {T.BG_SIDEBAR2}); border:none; }}
#sidebarBtn {{ background:transparent; border:none; border-left:3px solid transparent; color:{T.TXT_MUTED}; padding:11px 18px; text-align:left; font-size:13px; border-radius:0; }}
#sidebarBtn:hover {{ background:rgba(255,255,255,0.06); color:{T.TXT_LT}; }}
#sidebarBtn:checked {{ background:rgba(0,180,216,0.13); border-left-color:{T.PRIMARY}; color:{T.PRIMARY}; font-weight:bold; }}
#metricCard {{ background:{T.BG_CARD}; border-radius:{T.R}px; border:1px solid {T.BORDER}; }}
#metricCard:hover {{ border-color:{T.PRIMARY_LT}; }}
QTableWidget {{ background:{T.BG_CARD}; border:1px solid {T.BORDER}; border-radius:{T.R}px; gridline-color:{T.BG}; selection-background-color:#D4F1F9; selection-color:{T.TXT}; outline:none; }}
QTableWidget::item {{ padding:7px 10px; border-bottom:1px solid {T.BG}; }}
QTableWidget::item:hover {{ background:#F8FAF4; }}
QHeaderView::section {{ background:{T.BG}; color:{T.TXT2}; font-weight:bold; padding:10px 10px; border:none; border-bottom:2px solid {T.BORDER}; font-size:11px; text-transform:uppercase; letter-spacing:0.5px; }}
QLineEdit, QDoubleSpinBox {{ background:{T.BG_CARD}; border:2px solid {T.BORDER}; border-radius:{T.R_SM}px; padding:8px 12px; color:{T.TXT}; font-size:13px; }}
QLineEdit:focus, QDoubleSpinBox:focus {{ border-color:{T.PRIMARY}; }}
QComboBox {{ background:{T.BG_CARD}; border:2px solid {T.BORDER}; border-radius:{T.R_SM}px; padding:8px 12px; color:{T.TXT}; min-width:140px; }}
QComboBox:focus {{ border-color:{T.PRIMARY}; }}
QComboBox::drop-down {{ border:none; width:30px; }}
QComboBox::down-arrow {{ image:none; border-left:5px solid transparent; border-right:5px solid transparent; border-top:6px solid {T.TXT2}; margin-right:10px; }}
QComboBox QAbstractItemView {{ background:{T.BG_CARD}; border:1px solid {T.BORDER}; selection-background-color:{T.PRIMARY_LT}; border-radius:{T.R_SM}px; padding:4px; }}
QScrollBar:vertical {{ background:transparent; width:7px; margin:0; }}
QScrollBar::handle:vertical {{ background:#C5D1BE; border-radius:4px; min-height:30px; }}
QScrollBar::handle:vertical:hover {{ background:#A0B498; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QPushButton {{ border-radius:{T.R_SM}px; padding:9px 18px; font-weight:bold; border:none; }}
#primaryBtn {{ background:{T.PRIMARY}; color:white; }}
#primaryBtn:hover {{ background:{T.PRIMARY_DK}; }}
#secondaryBtn {{ background:{T.BG}; color:{T.TXT}; border:1px solid {T.BORDER}; }}
#secondaryBtn:hover {{ background:{T.BORDER}; }}
#dangerBtn {{ background:{T.ERR}; color:white; }}
#dangerBtn:hover {{ background:#C5303C; }}
"""


# ═══════════════════════════════════════════════════════════════
#  UTILITÁRIOS
# ═══════════════════════════════════════════════════════════════
def fmt_moeda(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def sombra(cor="#00000015", desloc=0, raio=12):
    e = QGraphicsDropShadowEffect()
    e.setColor(QColor(cor))
    e.setOffset(desloc)
    e.setBlurRadius(raio)
    return e

def fade_in(widget, dur=350):
    eff = QGraphicsOpacityEffect(widget)
    eff.setOpacity(0)
    widget.setGraphicsEffect(eff)
    a = QPropertyAnimation(eff, b"opacity")
    a.setStartValue(0); a.setEndValue(1)
    a.setDuration(dur); a.setEasingCurve(QEasingCurve.OutCubic)
    a.start()
    QTimer.singleShot(dur + 50, lambda: widget.setGraphicsEffect(None))

def criar_icone(cor: str, desenho, tam=22) -> QIcon:
    pm = QPixmap(tam, tam); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen); p.setBrush(QColor(cor))
    desenho(p, tam); p.end()
    return QIcon(pm)

def icone_dashboard(p, s):
    m = 3; r = 2.5
    p.drawRoundedRect(m, m, s/2-m*1.5, s/2-m*1.5, r, r)
    p.drawRoundedRect(s/2+m*0.5, m, s/2-m*1.5, s/2-m*1.5, r, r)
    p.drawRoundedRect(m, s/2+m*0.5, s/2-m*1.5, s/2-m*1.5, r, r)
    p.drawRoundedRect(s/2+m*0.5, s/2+m*0.5, s/2-m*1.5, s/2-m*1.5, r, r)

def icone_vendedores(p, s):
    cx, cy = s/2, s*0.32; r = s*0.16
    p.drawEllipse(QPointF(cx, cy), r, r)
    p.drawRoundedRect(cx-r*1.3, cy+r*1.1, r*2.6, s*0.35, r*1.5, r*1.5)

def icone_produtos(p, s):
    m = s*0.18; b = s*0.12
    p.drawRoundedRect(m, s*0.25, s-2*m, s*0.55, 3, 3)
    p.drawRect(m+b, s*0.25-b, s-2*m-2*b, b*2)

def icone_relatorios(p, s):
    w = s*0.14; g = s*0.22
    bx = s*0.22
    p.drawRoundedRect(bx, s*0.55, w, s*0.25, 2, 2)
    p.drawRoundedRect(bx+g, s*0.35, w, s*0.45, 2, 2)
    p.drawRoundedRect(bx+g*2, s*0.2, w, s*0.6, 2, 2)

def icone_config(p, s):
    cx, cy = s/2, s/2; ro = s*0.32; ri = s*0.14; nw = 6
    path = QPainterPath()
    for i in range(nw):
        a1 = (360/nw)*i - 90; a2 = a1 + 360/nw*0.5
        path.moveTo(cx+ri*math.cos(math.radians(a1)), cy+ri*math.sin(math.radians(a1)))
        path.lineTo(cx+ro*math.cos(math.radians(a1)), cy+ro*math.sin(math.radians(a1)))
        path.arcTo(QRectF(cx-ro, cy-ro, ro*2, ro*2), -a1, -(a2-a1))
        path.lineTo(cx+ri*math.cos(math.radians(a2)), cy+ri*math.sin(math.radians(a2)))
        path.arcTo(QRectF(cx-ri, cy-ri, ri*2, ri*2), -a2, (a2-a1))
    p.drawPath(path)
    p.drawEllipse(QPointF(cx, cy), ri*0.65, ri*0.65)

# NOTE: QPixmap/QIcon não podem ser criados antes de existir uma QApplication.
# Por isso os dicionários de ícones são preenchidos por construir_icones(),
# chamada em main() logo após a criação do QApplication (e não no import do módulo).
ICONS = {}
ICONS_ATIVO = {}

def construir_icones():
    """Popula ICONS e ICONS_ATIVO. Deve ser chamada após criar a QApplication."""
    global ICONS, ICONS_ATIVO
    ICONS = {
        "dashboard":  criar_icone(T.TXT_MUTED, icone_dashboard),
        "vendedores": criar_icone(T.TXT_MUTED, icone_vendedores),
        "produtos":   criar_icone(T.TXT_MUTED, icone_produtos),
        "relatorios": criar_icone(T.TXT_MUTED, icone_relatorios),
        "config":     criar_icone(T.TXT_MUTED, icone_config),
    }
    ICONS_ATIVO = {
        "dashboard":  criar_icone(T.PRIMARY, icone_dashboard),
        "vendedores": criar_icone(T.PRIMARY, icone_vendedores),
        "produtos":   criar_icone(T.PRIMARY, icone_produtos),
        "relatorios": criar_icone(T.PRIMARY, icone_relatorios),
        "config":     criar_icone(T.PRIMARY, icone_config),
    }


# ═══════════════════════════════════════════════════════════════
#  WIDGETS PERSONALIZADOS
# ═══════════════════════════════════════════════════════════════
class CardWidget(QFrame):
    """Card base com sombra e bordas arredondadas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        self.setGraphicsEffect(sombra())
        self.setMinimumHeight(100)

class MetricCard(CardWidget):
    """Card de métrica para o dashboard."""
    def __init__(self, icone_txt: str, titulo: str, valor: str, cor: str, cor_fundo: str, parent=None):
        super().__init__(parent)
        self.cor = cor
        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        # Ícone
        ic = QFrame(); ic.setFixedSize(50, 50); ic.setStyleSheet(f"background:{cor_fundo}; border-radius:14px;")
        il = QLabel(icone_txt, ic); il.setAlignment(Qt.AlignCenter)
        il.setStyleSheet(f"font-size:22px; background:transparent;")
        il.setGeometry(0, 0, 50, 50)
        lay.addWidget(ic)
        # Texto
        txt = QVBoxLayout(); txt.setSpacing(2)
        t = QLabel(titulo); t.setObjectName("cardTitle")
        t.setStyleSheet(f"font-size:11px; color:{T.TXT2}; text-transform:uppercase; letter-spacing:0.5px; background:transparent;")
        v = QLabel(valor); v.setObjectName("cardValue")
        v.setStyleSheet(f"font-size:26px; font-weight:bold; color:{T.TXT}; background:transparent;")
        txt.addWidget(t); txt.addWidget(v)
        lay.addLayout(txt, 1)
        # Barra lateral colorida
        bar = QFrame(); bar.setFixedWidth(5); bar.setStyleSheet(f"background:{cor}; border-radius:3px;")
        lay.addWidget(bar)

class AnimatedProgressBar(QFrame):
    """Barra de progresso animada com cores dinâmicas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self.setFixedHeight(24)
    def get_p(self): return self._progress
    def set_p(self, v):
        self._progress = max(0, min(v, 999))
        self.update()
    progress = Property(float, get_p, set_p)
    def animar_para(self, alvo, dur=700):
        a = QPropertyAnimation(self, b"progress")
        a.setStartValue(self._progress); a.setEndValue(alvo)
        a.setDuration(dur); a.setEasingCurve(QEasingCurve.OutCubic); a.start()
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); r = h/2
        p.setPen(Qt.NoPen); p.setBrush(QColor(T.BORDER))
        p.drawRoundedRect(0, 0, w, h, r, r)
        if self._progress > 0:
            fw = max(h, min(w, w * min(self._progress, 100) / 100))
            if self._progress >= 100: c1, c2 = QColor(T.OK), QColor("#40916C")
            elif self._progress >= 50: c1, c2 = QColor(T.WARN), QColor("#FB8500")
            else: c1, c2 = QColor(T.ERR), QColor("#FF6B6B")
            g = QLinearGradient(0, 0, fw, 0); g.setColorAt(0, c1); g.setColorAt(1, c2)
            p.setBrush(QBrush(g)); p.drawRoundedRect(0, 0, int(fw), h, r, r)
        cor_txt = "#FFFFFF" if self._progress > 20 else T.TXT2
        p.setPen(QColor(cor_txt))
        p.setFont(QFont("Segoe UI", 9, QFont.Bold))
        p.drawText(QRect(0, 0, w, h), Qt.AlignCenter, f"{self._progress:.1f}%")
        p.end()

class ToastWidget(QFrame):
    """Notificação toast temporária."""
    def __init__(self, msg, tipo="info", parent=None):
        super().__init__(parent)
        cores = {"info": (T.PRIMARY, "#D4F1F9"), "ok": (T.OK, T.OK_LT),
                "warn": (T.WARN, T.WARN_LT), "err": (T.ERR, T.ERR_LT)}
        icones = {"info": "ℹ", "ok": "✓", "warn": "⚠", "err": "✕"}
        fg, bg = cores.get(tipo, cores["info"])
        self.setFixedHeight(52); self.setMaximumWidth(380)
        self.setStyleSheet(f"background:{bg}; border-radius:{T.R_SM}px; border-left:4px solid {fg};")
        lay = QHBoxLayout(self); lay.setContentsMargins(14, 0, 14, 0)
        ic = QLabel(icones.get(tipo, "ℹ"))
        ic.setStyleSheet(f"font-size:18px; font-weight:bold; color:{fg}; background:transparent;")
        tx = QLabel(msg)
        tx.setStyleSheet(f"font-size:13px; color:{T.TXT}; background:transparent;")
        lay.addWidget(ic); lay.addWidget(tx, 1)
        self._y_offset = 0
    def get_yo(self): return self._y_offset
    def set_yo(self, v): self._y_offset = v; self.move(self.x(), v)
    y_offset = Property(int, get_yo, set_yo)

class ToastManager(QWidget):
    """Gerenciador de toasts posicionado no canto superior direito."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._toasts = []; self._spacing = 60
        self.raise_()
    def mostrar(self, msg, tipo="info", dur=3000):
        t = ToastWidget(msg, tipo, self)
        t.show(); t.adjustSize()
        y = 12 + len(self._toasts) * self._spacing
        t.move(self.width() - t.width() - 12, y)
        a = QPropertyAnimation(t, b"y_offset")
        a.setStartValue(y - 60); a.setEndValue(y)
        a.setDuration(350); a.setEasingCurve(QEasingCurve.OutBack); a.start()
        self._toasts.append((t, a))
        QTimer.singleShot(dur, lambda: self._remover(t))
    def _remover(self, t):
        a = QPropertyAnimation(t, b"y_offset")
        a.setStartValue(t.y()); a.setEndValue(t.y() - 60)
        a.setDuration(250); a.setEasingCurve(QEasingCurve.InCubic)
        a.start()
        a.finished.connect(lambda: (t.deleteLater(), self._limpar()))
    def _limpar(self):
        self._toasts = [(t, a) for t, a in self._toasts if t.parent()]
    def resizeEvent(self, e):
        super().resizeEvent(e)
        for i, (t, _) in enumerate(self._toasts):
            t.move(self.width() - t.width() - 12, 12 + i * self._spacing)

class CustomDialog(QFrame):
    """Diálogo modal personalizado."""
    def __init__(self, titulo, mensagem, tipo="info", botoes=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(420, 220)
        cores_ic = {"info": T.PRIMARY, "ok": T.OK, "warn": T.WARN, "err": T.ERR}
        fundos = {"info": "#D4F1F9", "ok": T.OK_LT, "warn": T.WARN_LT, "err": T.ERR_LT}
        icones = {"info": "ℹ", "ok": "✓", "warn": "⚠", "err": "✕"}
        ci = cores_ic.get(tipo, T.PRIMARY); bg = fundos.get(tipo, "#D4F1F9")
        ic = icones.get(tipo, "ℹ")
        self.setStyleSheet(f"background:{T.BG_CARD}; border-radius:{T.R_LG}px;")
        self.setGraphicsEffect(sombra("#00000030", 0, 25))
        lay = QVBoxLayout(self); lay.setContentsMargins(28, 24, 28, 20); lay.setSpacing(12)
        top = QHBoxLayout()
        ico_f = QFrame(); ico_f.setFixedSize(46, 46)
        ico_f.setStyleSheet(f"background:{bg}; border-radius:14px;")
        ico_l = QLabel(ic, ico_f); ico_l.setAlignment(Qt.AlignCenter)
        ico_l.setStyleSheet(f"font-size:22px; font-weight:bold; color:{ci}; background:transparent;")
        ico_l.setGeometry(0, 0, 46, 46)
        top.addWidget(ico_f)
        tit = QLabel(titulo)
        tit.setStyleSheet(f"font-size:17px; font-weight:bold; color:{T.TXT}; background:transparent;")
        top.addWidget(tit, 1); lay.addLayout(top)
        msg = QLabel(mensagem)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"font-size:13px; color:{T.TXT2}; background:transparent; line-height:1.5;")
        lay.addWidget(msg)
        lay.addSpacing(6)
        btns = QHBoxLayout(); btns.addStretch()
        if botoes is None:
            botoes = [("Fechar", "sec", lambda: self.close())]
        for txt, estilo, fn in botoes:
            b = QPushButton(txt)
            oid = "primaryBtn" if estilo == "pri" else "dangerBtn" if estilo == "dan" else "secondaryBtn"
            b.setObjectName(oid); b.clicked.connect(fn); btns.addWidget(b)
        lay.addLayout(btns)
    def show_modal(self):
        self._overlay = QFrame(self.parent())
        self._overlay.setStyleSheet("background:rgba(27,40,56,0.25); border:none;")
        self._overlay.setGeometry(self.parent().rect())
        self._overlay.show(); self._overlay.raise_()
        self.raise_(); self.show()
        fade_in(self, 250)
        qr = self.parent().rect()
        self.move(qr.center().x() - self.width()//2, qr.center().y() - self.height()//2)
    def closeEvent(self, e):
        if hasattr(self, '_overlay') and self._overlay:
            self._overlay.deleteLater()
        super().closeEvent(e)

class LoadingOverlay(QFrame):
    """Overlay de carregamento com animação."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:rgba(240,244,232,0.92); border:none;")
        self._angle = 0
        self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(30)
        self._lbl = QLabel("Processando vendas...", self)
        self._lbl.setStyleSheet(f"font-size:14px; color:{T.TXT2}; background:transparent;")
        self._lbl.setAlignment(Qt.AlignCenter)
    def _tick(self):
        self._angle = (self._angle + 6) % 360; self.update()
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._lbl.setGeometry(0, self.height()//2 + 35, self.width(), 30)
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width()//2, self.height()//2 - 5; r = 22
        p.setPen(Qt.NoPen); p.setBrush(QColor(T.BORDER))
        p.drawEllipse(QPointF(cx, cy), r, r)
        for i in range(8):
            a = math.radians(self._angle + i * 45)
            alpha = int(255 * (1 - i / 8))
            cor = QColor(T.PRIMARY); cor.setAlpha(alpha)
            p.setPen(Qt.NoPen); p.setBrush(cor)
            px = cx + (r - 6) * math.cos(a); py = cy + (r - 6) * math.sin(a)
            p.drawEllipse(QPointF(px, py), 4, 4)
        p.end()
    def parar(self):
        self._timer.stop(); self.deleteLater()


# ═══════════════════════════════════════════════════════════════
#  GRÁFICOS CUSTOMIZADOS (QPainter)
# ═══════════════════════════════════════════════════════════════
class DonutChart(QWidget):
    """Gráfico de rosca para proporção de metas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._segs = []; self._ct = ""; self._cs = ""
        self.setMinimumSize(190, 190)
    def set_data(self, segs, ct="", cs=""):
        self._segs = segs; self._ct = ct; self._cs = cs; self.update()
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w/2, h/2
        radius = min(w, h)/2 - 18; thick = radius * 0.32
        total = sum(v for v, _, _ in self._segs)
        if total == 0:
            p.setPen(Qt.NoPen); p.setBrush(QColor(T.BORDER))
            p.drawEllipse(QPointF(cx, cy), radius, radius)
            p.setBrush(QColor(T.BG))
            p.drawEllipse(QPointF(cx, cy), radius - thick, radius - thick)
        else:
            sa = -90
            for val, cor, _ in self._segs:
                span = (val / total) * 360
                p.setPen(Qt.NoPen); p.setBrush(QColor(cor))
                rect = QRectF(cx - radius, cy - radius, radius*2, radius*2)
                p.drawPie(rect, int(sa * 16), int(span * 16))
                sa += span
            p.setBrush(QColor(T.BG_CARD))
            p.drawEllipse(QPointF(cx, cy), radius - thick, radius - thick)
        p.setPen(QColor(T.TXT))
        p.setFont(QFont("Segoe UI", 20, QFont.Bold))
        p.drawText(QRectF(cx-60, cy-18, 120, 36), Qt.AlignCenter, self._ct)
        p.setFont(QFont("Segoe UI", 10)); p.setPen(QColor(T.TXT2))
        p.drawText(QRectF(cx-60, cy+14, 120, 20), Qt.AlignCenter, self._cs)
        # Legenda
        ly = h - 8
        for val, cor, lbl in reversed(self._segs):
            p.setBrush(QColor(cor)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(cx - 70, ly - 8, 12, 12, 3, 3)
            p.setPen(QColor(T.TXT2)); p.setFont(QFont("Segoe UI", 9))
            p.drawText(cx - 54, ly + 3, f"{lbl} ({val})")
            ly -= 18
        p.end()

class BarChartWidget(QWidget):
    """Gráfico de barras verticais."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bars = []; self._title = ""
        self.setMinimumHeight(230)
    def set_data(self, bars, title=""):
        self._bars = bars; self._title = title; self.update()
    def paintEvent(self, e):
        if not self._bars: return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mr, mt, mb = 68, 15, 32, 44
        cw = w - ml - mr; ch = h - mt - mb
        p.setPen(QColor(T.TXT)); p.setFont(QFont("Segoe UI", 12, QFont.Bold))
        p.drawText(ml, 22, self._title)
        mx = max(v for _, v, _ in self._bars) or 1
        n = len(self._bars)
        bw = min(52, cw / n * 0.55); gap = cw / n
        for i in range(5):
            y = mt + ch - (ch * i / 4)
            p.setPen(QPen(QColor(T.BORDER), 1, Qt.DotLine))
            p.drawLine(ml, int(y), w - mr, int(y))
            p.setPen(QColor(T.TXT_MUTED)); p.setFont(QFont("Segoe UI", 8))
            vl = mx * i / 4
            p.drawText(QRect(0, int(y) - 8, ml - 6, 16), Qt.AlignRight | Qt.AlignVCenter, f"R${vl:,.0f}".replace(",", "."))
        for i, (lbl, val, cor) in enumerate(self._bars):
            x = ml + gap * i + (gap - bw) / 2
            bh = (val / mx) * ch; y = mt + ch - bh
            p.setPen(Qt.NoPen); p.setBrush(QColor(cor))
            path = QPainterPath(); r = min(bw/2, 6)
            path.moveTo(x, mt + ch)
            path.lineTo(x, y + r); path.quadTo(x, y, x + r, y)
            path.lineTo(x + bw - r, y); path.quadTo(x + bw, y, x + bw, y + r)
            path.lineTo(x + bw, mt + ch); path.closeSubpath()
            p.drawPath(path)
            p.setPen(QColor(T.TXT)); p.setFont(QFont("Segoe UI", 8, QFont.Bold))
            p.drawText(QRectF(x - 8, y - 17, bw + 16, 15), Qt.AlignCenter, fmt_moeda(val))
            p.setPen(QColor(T.TXT2)); p.setFont(QFont("Segoe UI", 9))
            p.drawText(QRectF(x - 8, mt + ch + 5, bw + 16, 28), Qt.AlignCenter | Qt.TextWordWrap, lbl.capitalize())
        p.end()


# ═══════════════════════════════════════════════════════════════
#  PÁGINAS
# ═══════════════════════════════════════════════════════════════
class DashboardPage(QScrollArea):
    def __init__(self, ger: GerenciadorVendas, toasts: ToastManager, parent=None):
        super().__init__(parent)
        self.ger = ger; self.toasts = toasts
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:transparent; border:none;")
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.main_lay = QVBoxLayout(container)
        self.main_lay.setContentsMargins(24, 20, 24, 24); self.main_lay.setSpacing(20)
        self.setWidget(container)
    def atualizar(self):
        vends = get_vendedores_list(self.ger)
        while self.main_lay.count():
            item = self.main_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub = item.layout().takeAt(0)
                    if sub.widget(): sub.widget().deleteLater()
        total_v = len(vends)
        bateram = sum(1 for v in vends if v.vendas >= v.meta)
        fat_total = sum(v.vendas for v in vends)
        bonus_total = sum(v.calcular_bonus() for v in vends if isinstance(v, VendedorComBonus))
        prog_medio = (sum(v.calcular_progresso() for v in vends) / total_v) if total_v else 0
        superstars = sum(1 for v in vends if isinstance(v, VendedorSuperstar))
        # Título
        tit = QLabel("Painel de Controle")
        tit.setStyleSheet(f"font-size:24px; font-weight:bold; color:{T.TXT}; background:transparent;")
        self.main_lay.addWidget(tit)
        sub = QLabel("Visão geral do desempenho dos vendedores")
        sub.setStyleSheet(f"font-size:13px; color:{T.TXT2}; background:transparent; margin-bottom:4px;")
        self.main_lay.addWidget(sub)
        # Cards de métricas
        grid = QGridLayout(); grid.setSpacing(14)
        cards = [
            ("👥", "Total de Vendedores", str(total_v), T.PRIMARY, T.PRIMARY_LT),
            ("✅", "Bateram a Meta", str(bateram), T.OK, T.OK_LT),
            ("💰", "Faturamento Total", fmt_moeda(fat_total), T.SECONDARY, T.SECONDARY_LT),
            ("🎁", "Bônus Distribuídos", fmt_moeda(bonus_total), T.WARN, T.WARN_LT),
            ("📈", "Progresso Médio", f"{prog_medio:.1f}%", T.ACCENT, T.ACCENT_LT),
            ("⭐", "Superstars", str(superstars), T.PINK, T.PINK_LT),
        ]
        for i, (ic, ti, vl, c, bg) in enumerate(cards):
            card = MetricCard(ic, ti, vl, c, bg)
            card.setCursor(Qt.PointingHandCursor)
            grid.addWidget(card, i // 3, i % 3)
        self.main_lay.addLayout(grid)
        # Gráficos
        charts_lay = QHBoxLayout(); charts_lay.setSpacing(16)
        # Bar chart — faturamento por setor
        setores_d: dict = defaultdict(float)
        for v in vends: setores_d[v.setor] += v.vendas
        bar_data = [(s, t, SETOR_CORES.get(s, (T.TXT_MUTED, T.BG))[0]) for s, t in sorted(setores_d.items(), key=lambda x: -x[1])]
        bc = CardWidget(); bc_lay = QVBoxLayout(bc); bc_lay.setContentsMargins(16, 14, 16, 10)
        bc_chart = BarChartWidget(); bc_chart.set_data(bar_data, "Faturamento por Setor")
        bc_lay.addWidget(bc_chart); charts_lay.addWidget(bc, 3)
        # Donut chart — meta
        dc = CardWidget(); dc_lay = QVBoxLayout(dc); dc_lay.setContentsMargins(16, 14, 16, 10)
        donut = DonutChart()
        pct = (bateram / total_v * 100) if total_v else 0
        donut.set_data([(bateram, T.OK, "Bateu"), (total_v - bateram, T.ERR, "Não bateu")],
                    f"{pct:.0f}%", "atingiram a meta")
        dc_lay.addWidget(donut, 1, Qt.AlignCenter)
        charts_lay.addWidget(dc, 2)
        self.main_lay.addLayout(charts_lay)
        # Top 5
        top5 = sorted(vends, key=lambda v: v.vendas, reverse=True)[:5]
        tc = CardWidget(); tc_lay = QVBoxLayout(tc); tc_lay.setContentsMargins(18, 14, 18, 10)
        ttl = QLabel("🏆  Top 5 Vendedores")
        ttl.setStyleSheet(f"font-size:14px; font-weight:bold; color:{T.TXT}; background:transparent; margin-bottom:8px;")
        tc_lay.addWidget(ttl)
        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        for i, v in enumerate(top5):
            row = QHBoxLayout(); row.setSpacing(12)
            ml = QLabel(medals[i])
            ml.setFixedWidth(28); ml.setAlignment(Qt.AlignCenter)
            ml.setStyleSheet(f"font-size:16px; background:transparent;")
            nl = QLabel(v.nome.title())
            nl.setStyleSheet(f"font-size:13px; font-weight:600; color:{T.TXT}; background:transparent;")
            sl = QLabel(v.setor.capitalize())
            sl.setStyleSheet(f"font-size:11px; color:{T.TXT_MUTED}; background:transparent; padding:2px 8px; border-radius:10px; background:{SETOR_CORES.get(v.setor, (T.TXT_MUTED, T.BG))[1]};")
            vl = QLabel(fmt_moeda(v.vendas))
            vl.setStyleSheet(f"font-size:13px; font-weight:bold; color:{T.TXT}; background:transparent;")
            row.addWidget(ml); row.addWidget(nl); row.addWidget(sl); row.addStretch(); row.addWidget(vl)
            tc_lay.addLayout(row)
        self.main_lay.addWidget(tc)
        self.main_lay.addStretch()
        fade_in(self.widget(), 300)


class VendedoresPage(QScrollArea):
    detalhe_signal = Signal(object)
    def __init__(self, ger: GerenciadorVendas, toasts: ToastManager, parent=None):
        super().__init__(parent)
        self.ger = ger; self.toasts = toasts
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:transparent; border:none;")
        self._vends_cache = []
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.lay = QVBoxLayout(container)
        self.lay.setContentsMargins(24, 20, 24, 24); self.lay.setSpacing(16)
        self.setWidget(container)
    def atualizar(self):
        self._vends_cache = get_vendedores_list(self.ger)
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    s = it.layout().takeAt(0)
                    if s.widget(): s.widget().deleteLater()
        # Título
        tit = QLabel("Vendedores")
        tit.setStyleSheet(f"font-size:24px; font-weight:bold; color:{T.TXT}; background:transparent;")
        self.lay.addWidget(tit)
        # Filtros
        filtros = QHBoxLayout(); filtros.setSpacing(12)
        self.busca = QLineEdit(); self.busca.setPlaceholderText("🔍  Buscar vendedor...")
        self.busca.setFixedWidth(280)
        self.busca.textChanged.connect(self._filtrar)
        filtros.addWidget(self.busca)
        self.filtro_setor = QComboBox(); self.filtro_setor.addItem("Todos os setores")
        setores = sorted(set(v.setor for v in self._vends_cache))
        for s in setores: self.filtro_setor.addItem(s.capitalize())
        self.filtro_setor.currentIndexChanged.connect(self._filtrar)
        filtros.addWidget(self.filtro_setor)
        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos os status", "Bateu a meta", "Não bateu a meta"])
        self.filtro_status.currentIndexChanged.connect(self._filtrar)
        filtros.addWidget(self.filtro_status)
        filtros.addStretch()
        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet(f"font-size:12px; color:{T.TXT_MUTED}; background:transparent;")
        filtros.addWidget(self.lbl_count)
        self.lay.addLayout(filtros)
        # Tabela
        self.tabela = QTableWidget(); self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(["Vendedor", "Setor", "Tipo", "Total Vendido", "Meta", "Progresso", "Status", "Bônus"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.tabela.setColumnWidth(5, 140)
        self.tabela.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.tabela.setColumnWidth(7, 110)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.cellDoubleClicked.connect(self._mostrar_detalhe)
        self.lay.addWidget(self.tabela)
        self._filtrar()
        fade_in(self.widget(), 300)
    def _filtrar(self):
        texto = self.busca.text().lower()
        setor_idx = self.filtro_setor.currentIndex()
        status_idx = self.filtro_status.currentIndex()
        setores = sorted(set(v.setor for v in self._vends_cache))
        filtro_setor = setores[setor_idx - 1] if setor_idx > 0 else None
        filtrados = []
        for v in self._vends_cache:
            if texto and texto not in v.nome.lower(): continue
            if filtro_setor and v.setor != filtro_setor: continue
            if status_idx == 1 and v.vendas < v.meta: continue
            if status_idx == 2 and v.vendas >= v.meta: continue
            filtrados.append(v)
        self.tabela.setRowCount(len(filtrados))
        self.lbl_count.setText(f"{len(filtrados)} vendedor(es) encontrado(s)")
        for i, v in enumerate(filtrados):
            self._preencher_linha(i, v)
    def _preencher_linha(self, row, v):
        def item(txt, align=Qt.AlignLeft, bold=False):
            it = QTableWidgetItem(txt)
            it.setTextAlignment(align)
            if bold: it.setFont(QFont("Segoe UI", 10, QFont.Bold))
            return it
        self.tabela.setItem(row, 0, item(v.nome.title()))
        self.tabela.setItem(row, 1, item(v.setor.capitalize()))
        tipo = "Superstar" if isinstance(v, VendedorSuperstar) else "Com Bônus" if isinstance(v, VendedorComBonus) else "Padrão"
        self.tabela.setItem(row, 2, item(tipo))
        self.tabela.setItem(row, 3, item(fmt_moeda(v.vendas), Qt.AlignRight, True))
        self.tabela.setItem(row, 4, item(fmt_moeda(v.meta), Qt.AlignRight))
        # Progresso
        pb = AnimatedProgressBar(); pb.animar_para(v.calcular_progresso(), 500)
        cel = QWidget(); cl = QHBoxLayout(cel); cl.setContentsMargins(6, 2, 6, 2)
        cl.addWidget(pb); self.tabela.setCellWidget(row, 5, cel)
        # Status
        bateu = v.vendas >= v.meta
        sl = QLabel("✓ Bateu" if bateu else "✕ Não bateu")
        sl.setAlignment(Qt.AlignCenter)
        sl.setStyleSheet(f"font-size:11px; font-weight:bold; color:{T.OK if bateu else T.ERR}; background:{T.OK_LT if bateu else T.ERR_LT}; padding:4px 10px; border-radius:12px; background:transparent;")
        sw = QWidget(); sl_lay = QHBoxLayout(sw); sl_lay.setContentsMargins(4, 0, 4, 0)
        sl_lay.addWidget(sl); self.tabela.setCellWidget(row, 6, sw)
        # Bônus
        if isinstance(v, VendedorComBonus):
            b = v.calcular_bonus()
            self.tabela.setItem(row, 7, item(fmt_moeda(b), Qt.AlignRight, b > 0))
        else:
            self.tabela.setItem(row, 7, item("—", Qt.AlignCenter))
        self.tabela.setRowHeight(row, 40)
    def _mostrar_detalhe(self, row, col):
        v = self._filtrar_lista()[row] if row < len(self._filtrar_lista()) else None
        if v: self.detalhe_signal.emit(v)
    def _filtrar_lista(self):
        texto = self.busca.text().lower()
        setor_idx = self.filtro_setor.currentIndex()
        status_idx = self.filtro_status.currentIndex()
        setores = sorted(set(v.setor for v in self._vends_cache))
        filtro_setor = setores[setor_idx - 1] if setor_idx > 0 else None
        res = []
        for v in self._vends_cache:
            if texto and texto not in v.nome.lower(): continue
            if filtro_setor and v.setor != filtro_setor: continue
            if status_idx == 1 and v.vendas < v.meta: continue
            if status_idx == 2 and v.vendas >= v.meta: continue
            res.append(v)
        return res


class ProdutosPage(QScrollArea):
    def __init__(self, ger: GerenciadorVendas, toasts: ToastManager, parent=None):
        super().__init__(parent)
        self.ger = ger; self.toasts = toasts; self._df_prod = None
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:transparent; border:none;")
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.lay = QVBoxLayout(container)
        self.lay.setContentsMargins(24, 20, 24, 24); self.lay.setSpacing(16)
        self.setWidget(container)
    def atualizar(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    s = it.layout().takeAt(0)
                    if s.widget(): s.widget().deleteLater()
        tit = QLabel("Produtos")
        tit.setStyleSheet(f"font-size:24px; font-weight:bold; color:{T.TXT}; background:transparent;")
        self.lay.addWidget(tit)
        sub = QLabel("Catálogo de produtos disponíveis para venda")
        sub.setStyleSheet(f"font-size:13px; color:{T.TXT2}; background:transparent;")
        self.lay.addWidget(sub)
        # Tentar carregar produtos do Excel
        try:
            import pandas as pd
            self._df_prod = pd.read_excel("produtos.xlsx", engine="openpyxl")
        except Exception:
            self._df_prod = None
            self.toasts.mostrar("Arquivo 'produtos.xlsx' não encontrado.", "warn")
        if self._df_prod is not None and len(self._df_prod) > 0:
            busca_lay = QHBoxLayout()
            self.busca_prod = QLineEdit(); self.busca_prod.setPlaceholderText("🔍  Buscar produto...")
            self.busca_prod.setFixedWidth(280); self.busca_prod.textChanged.connect(self._filtrar_prod)
            busca_lay.addWidget(self.busca_prod); busca_lay.addStretch()
            self.lay.addLayout(busca_lay)
            self.tabela_prod = QTableWidget(); self.tabela_prod.setColumnCount(3)
            self.tabela_prod.setHorizontalHeaderLabels(["#", "Produto", "Preço"])
            self.tabela_prod.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            self.tabela_prod.setColumnWidth(0, 50)
            self.tabela_prod.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            self.tabela_prod.setColumnWidth(2, 130)
            self.tabela_prod.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            self.tabela_prod.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tabela_prod.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.tabela_prod.verticalHeader().setVisible(False)
            self.tabela_prod.setShowGrid(False)
            self.lay.addWidget(self.tabela_prod)
            self._filtrar_prod()
        self.lay.addStretch()
        fade_in(self.widget(), 300)
    def _filtrar_prod(self):
        if self._df_prod is None: return
        texto = getattr(self, 'busca_prod', None)
        t = texto.text().lower() if texto else ""
        df = self._df_prod
        if t:
            df = df[df["produto"].str.lower().str.contains(t, na=False)]
        self.tabela_prod.setRowCount(len(df))
        for i, (_, row) in enumerate(df.iterrows()):
            ni = QTableWidgetItem(str(i + 1)); ni.setTextAlignment(Qt.AlignCenter)
            self.tabela_prod.setItem(i, 0, ni)
            self.tabela_prod.setItem(i, 1, QTableWidgetItem(row["produto"]))
            pi = QTableWidgetItem(fmt_moeda(row["preco"]))
            pi.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            pi.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.tabela_prod.setItem(i, 2, pi)
            self.tabela_prod.setRowHeight(i, 38)


class RelatoriosPage(QScrollArea):
    def __init__(self, ger: GerenciadorVendas, toasts: ToastManager, parent=None):
        super().__init__(parent)
        self.ger = ger; self.toasts = toasts
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:transparent; border:none;")
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.lay = QVBoxLayout(container)
        self.lay.setContentsMargins(24, 20, 24, 24); self.lay.setSpacing(16)
        self.setWidget(container)
    def atualizar(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    s = it.layout().takeAt(0)
                    if s.widget(): s.widget().deleteLater()
        vends = get_vendedores_list(self.ger)
        tit = QLabel("Relatórios")
        tit.setStyleSheet(f"font-size:24px; font-weight:bold; color:{T.TXT}; background:transparent;")
        self.lay.addWidget(tit)
        # Resumo por setor
        stl = QLabel("Resumo por Setor")
        stl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{T.TXT}; background:transparent; margin-top:4px;")
        self.lay.addWidget(stl)
        setores_d: dict = defaultdict(list)
        for v in vends: setores_d[v.setor].append(v)
        sg = QGridLayout(); sg.setSpacing(12)
        for i, (setor, lista) in enumerate(sorted(setores_d.items())):
            total = sum(v.vendas for v in lista)
            media = total / len(lista)
            bateram = sum(1 for v in lista if v.vendas >= v.meta)
            cor, cor_bg = SETOR_CORES.get(setor, (T.TXT_MUTED, T.BG))
            card = CardWidget()
            cl = QVBoxLayout(card); cl.setContentsMargins(16, 14, 16, 12)
            header = QHBoxLayout()
            dot = QFrame(); dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background:{cor}; border-radius:6px;")
            nl = QLabel(setor.capitalize())
            nl.setStyleSheet(f"font-size:14px; font-weight:bold; color:{T.TXT}; background:transparent;")
            header.addWidget(dot); header.addWidget(nl); header.addStretch()
            cl.addLayout(header)
            for lbl, val in [("Vendedores", str(len(lista))), ("Faturamento", fmt_moeda(total)),
                            ("Média", fmt_moeda(media)), ("Bateram", f"{bateram}/{len(lista)}")]:
                r = QHBoxLayout()
                rl = QLabel(lbl); rl.setStyleSheet(f"font-size:12px; color:{T.TXT2}; background:transparent;")
                rv = QLabel(val); rv.setStyleSheet(f"font-size:12px; font-weight:bold; color:{T.TXT}; background:transparent;")
                r.addWidget(rl); r.addStretch(); r.addWidget(rv)
                cl.addLayout(r)
            sg.addWidget(card, i // 3, i % 3)
        self.lay.addLayout(sg)
        # Ranking
        rl = QLabel("Ranking de Desempenho")
        rl.setStyleSheet(f"font-size:16px; font-weight:bold; color:{T.TXT}; background:transparent; margin-top:8px;")
        self.lay.addWidget(rl)
        rank_lay = QHBoxLayout(); rank_lay.setSpacing(16)
        # Top 5
        top5 = sorted(vends, key=lambda v: v.vendas, reverse=True)[:5]
        tc = CardWidget(); tcl = QVBoxLayout(tc); tcl.setContentsMargins(16, 14, 16, 10)
        tcl.addWidget(self._rank_titulo("🟢 Melhores Desempenhos", T.OK))
        for j, v in enumerate(top5):
            tcl.addLayout(self._rank_linha(j + 1, v, T.OK))
        rank_lay.addWidget(tc, 1)
        # Bottom 5
        bot5 = sorted(vends, key=lambda v: v.vendas)[:5]
        bc = CardWidget(); bcl = QVBoxLayout(bc); bcl.setContentsMargins(16, 14, 16, 10)
        bcl.addWidget(self._rank_titulo("🔴 Menores Desempenhos", T.ERR))
        for j, v in enumerate(bot5):
            bcl.addLayout(self._rank_linha(j + 1, v, T.ERR))
        rank_lay.addWidget(bc, 1)
        self.lay.addLayout(rank_lay)
        self.lay.addStretch()
        fade_in(self.widget(), 300)
    def _rank_titulo(self, txt, cor):
        l = QLabel(txt)
        l.setStyleSheet(f"font-size:13px; font-weight:bold; color:{cor}; background:transparent; margin-bottom:8px;")
        return l
    def _rank_linha(self, pos, v, cor):
        r = QHBoxLayout(); r.setSpacing(10)
        pl = QLabel(f"{pos}.")
        pl.setFixedWidth(22); pl.setAlignment(Qt.AlignRight)
        pl.setStyleSheet(f"font-size:13px; font-weight:bold; color:{T.TXT}; background:transparent;")
        nl = QLabel(v.nome.title())
        nl.setStyleSheet(f"font-size:13px; color:{T.TXT}; background:transparent;")
        vl = QLabel(fmt_moeda(v.vendas))
        vl.setStyleSheet(f"font-size:13px; font-weight:bold; color:{T.TXT}; background:transparent;")
        r.addWidget(pl); r.addWidget(nl); r.addStretch(); r.addWidget(vl)
        return r


class ConfiguracoesPage(QScrollArea):
    recalcular_signal = Signal()
    def __init__(self, ger: GerenciadorVendas, toasts: ToastManager, parent=None):
        super().__init__(parent)
        self.ger = ger; self.toasts = toasts
        self.setWidgetResizable(True); self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:transparent; border:none;")
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.lay = QVBoxLayout(container)
        self.lay.setContentsMargins(24, 20, 24, 24); self.lay.setSpacing(16)
        self.setWidget(container)
    def atualizar(self):
        while self.lay.count():
            it = self.lay.takeAt(0)
            if it.widget(): it.widget().deleteLater()
            elif it.layout():
                while it.layout().count():
                    s = it.layout().takeAt(0)
                    if s.widget(): s.widget().deleteLater()
        tit = QLabel("Configurações")
        tit.setStyleSheet(f"font-size:24px; font-weight:bold; color:{T.TXT}; background:transparent;")
        self.lay.addWidget(tit)
        sub = QLabel("Ajuste os parâmetros de cálculo e recarregue os dados")
        sub.setStyleSheet(f"font-size:13px; color:{T.TXT2}; background:transparent;")
        self.lay.addWidget(sub)
        # Card de meta
        mc = CardWidget(); mcl = QVBoxLayout(mc); mcl.setContentsMargins(20, 18, 20, 18); mcl.setSpacing(14)
        mcl.addWidget(self._secTitulo("🎯  Meta Individual em Reais"))
        meta_desc = QLabel("Defina o valor mínimo que cada vendedor deve atingir para cumprir a meta.")
        meta_desc.setWordWrap(True)
        meta_desc.setStyleSheet(f"font-size:12px; color:{T.TXT2}; background:transparent;")
        mcl.addWidget(meta_desc)
        meta_lay = QHBoxLayout()
        self.spin_meta = QDoubleSpinBox()
        self.spin_meta.setRange(1, 999999); self.spin_meta.setDecimals(2)
        self.spin_meta.setPrefix("R$ "); self.spin_meta.setValue(self.ger.META_PADRAO)
        self.spin_meta.setFixedWidth(200)
        meta_lay.addWidget(self.spin_meta); meta_lay.addStretch()
        mcl.addLayout(meta_lay)
        self.lay.addWidget(mc)
        # Card de salário
        sc = CardWidget(); scl = QVBoxLayout(sc); scl.setContentsMargins(20, 18, 20, 18); scl.setSpacing(14)
        scl.addWidget(self._secTitulo("💼  Salário Base para Bônus"))
        sal_desc = QLabel("Salário base utilizado no cálculo de bônus para vendedores dos setores Eletrônicos e Domésticos.")
        sal_desc.setWordWrap(True)
        sal_desc.setStyleSheet(f"font-size:12px; color:{T.TXT2}; background:transparent;")
        scl.addWidget(sal_desc)
        sal_lay = QHBoxLayout()
        self.spin_sal = QDoubleSpinBox()
        self.spin_sal.setRange(1, 999999); self.spin_sal.setDecimals(2)
        self.spin_sal.setPrefix("R$ "); self.spin_sal.setValue(2000.0)
        self.spin_sal.setFixedWidth(200)
        sal_lay.addWidget(self.spin_sal); sal_lay.addStretch()
        scl.addLayout(sal_lay)
        self.lay.addWidget(sc)
        # Botão recalcular
        btn_lay = QHBoxLayout(); btn_lay.addStretch()
        btn_rec = QPushButton("🔄  Recalcular Vendas")
        btn_rec.setObjectName("primaryBtn"); btn_rec.setCursor(Qt.PointingHandCursor)
        btn_rec.setMinimumWidth(220)
        btn_rec.clicked.connect(self._recalcular)
        btn_lay.addWidget(btn_rec); btn_lay.addStretch()
        self.lay.addLayout(btn_lay)
        # Info
        ic = CardWidget(); icl = QVBoxLayout(ic); icl.setContentsMargins(20, 18, 20, 18); icl.setSpacing(8)
        icl.addWidget(self._secTitulo("ℹ️  Sobre o Sistema"))
        info_txt = (
            "Calculadora de Metas v2.0\n\n"
            "Sistema desenvolvido para o gerenciamento e cálculo de metas de vendas.\n"
            "Utiliza conceitos de Programação Orientada a Objetos: herança, polimorfismo,\n"
            "encapsulamento e interfaces abstratas.\n\n"
            "Persona: Josefino Nonato — gerente que precisa organizar bônus de funcionários.\n"
            "Disciplina: Princípios da Programação II"
        )
        il = QLabel(info_txt); il.setWordWrap(True)
        il.setStyleSheet(f"font-size:12px; color:{T.TXT2}; background:transparent; line-height:1.6;")
        icl.addWidget(il)
        self.lay.addWidget(ic)
        self.lay.addStretch()
        fade_in(self.widget(), 300)
    def _secTitulo(self, txt):
        l = QLabel(txt)
        l.setStyleSheet(f"font-size:15px; font-weight:bold; color:{T.TXT}; background:transparent;")
        return l
    def _recalcular(self):
        nova_meta = self.spin_meta.value()
        novo_sal = self.spin_sal.value()
        self.ger.META_PADRAO = nova_meta
        # Reconstruir vendedores com novos parâmetros
        try:
            self.ger.carregar_dados("vendas.xlsx", "produtos.xlsx", "vendedores.xlsx")
            # Atualizar salário base dos VendedorComBonus
            for v in get_vendedores_list(self.ger):
                if isinstance(v, VendedorComBonus):
                    v._VendedorComBonus__salario_base = novo_sal
            self.toasts.mostrar("Dados recalculados com sucesso!", "ok")
            self.recalcular_signal.emit()
        except Exception as ex:
            self.toasts.mostrar(f"Erro ao recalcular: {str(ex)}", "err")


# ═══════════════════════════════════════════════════════════════
#  JANELA PRINCIPAL
# ═══════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Metas")
        self.setMinimumSize(1100, 680)
        self.resize(1360, 820)
        self.ger = GerenciadorVendas()
        self._loaded = False
        self._setup_ui()
        self._setup_sidebar()
        self._setup_pages()
        self._load_data()
    def _setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        self.root = QHBoxLayout(central)
        self.root.setContentsMargins(0, 0, 0, 0); self.root.setSpacing(0)
        self.setStyleSheet(STYLESHEET)
    def _setup_sidebar(self):
        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        sl = QVBoxLayout(self.sidebar); sl.setContentsMargins(0, 0, 0, 0); sl.setSpacing(0)
        # Logo
        logo_w = QWidget(); logo_l = QVBoxLayout(logo_w)
        logo_l.setContentsMargins(20, 24, 20, 8); logo_l.setSpacing(2)
        logo_txt = QLabel("📊 Calculadora")
        logo_txt.setStyleSheet(f"font-size:17px; font-weight:bold; color:{T.TXT_LT}; background:transparent;")
        logo_sub = QLabel("de Metas")
        logo_sub.setStyleSheet(f"font-size:13px; color:{T.TXT_MUTED}; background:transparent; padding-left:2px;")
        logo_l.addWidget(logo_txt); logo_l.addWidget(logo_sub)
        sl.addWidget(logo_w)
        # Separador
        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:rgba(255,255,255,0.08); border:none; margin:8px 16px;")
        sl.addWidget(sep)
        # Nav label
        nav_lbl = QLabel("  MENU")
        nav_lbl.setStyleSheet(f"font-size:10px; color:{T.TXT_MUTED}; letter-spacing:1.5px; background:transparent; padding:12px 0 6px 0;")
        sl.addWidget(nav_lbl)
        # Botões de navegação
        self.nav_btns = []
        paginas = [
            ("dashboard", "Painel de Controle"),
            ("vendedores", "Vendedores"),
            ("produtos", "Produtos"),
            ("relatorios", "Relatórios"),
            ("config", "Configurações"),
        ]
        self.btn_group = []
        for key, label in paginas:
            btn = QPushButton(f"  {label}")
            btn.setObjectName("sidebarBtn")
            btn.setIcon(ICONS[key]); btn.setIconSize(QSize(18, 18))
            btn.setCheckable(True); btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("nav_key", key)
            btn.clicked.connect(lambda checked, k=key: self._navegar(k))
            sl.addWidget(btn)
            self.nav_btns.append((key, btn))
            self.btn_group.append(btn)
        sl.addStretch()
        # Versão
        ver = QLabel("  v2.0  •  POO II")
        ver.setStyleSheet(f"font-size:10px; color:{T.TXT_MUTED}; background:transparent; padding:12px;")
        sl.addWidget(ver)
        self.root.addWidget(self.sidebar)
    def _setup_pages(self):
        self.content = QFrame()
        self.content.setStyleSheet(f"background:{T.BG}; border:none;")
        cl = QVBoxLayout(self.content); cl.setContentsMargins(0, 0, 0, 0); cl.setSpacing(0)
        self.stack = QStackedWidget(); self.stack.setStyleSheet("background:transparent; border:none;")
        self.toasts = ToastManager(self.content)
        self.dashboard = DashboardPage(self.ger, self.toasts)
        self.vendedores = VendedoresPage(self.ger, self.toasts)
        self.produtos = ProdutosPage(self.ger, self.toasts)
        self.relatorios = RelatoriosPage(self.ger, self.toasts)
        self.config = ConfiguracoesPage(self.ger, self.toasts)
        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.vendedores)
        self.stack.addWidget(self.produtos)
        self.stack.addWidget(self.relatorios)
        self.stack.addWidget(self.config)
        cl.addWidget(self.stack)
        self.root.addWidget(self.content, 1)
        # Conectar sinais
        self.vendedores.detalhe_signal.connect(self._mostrar_detalhe_vendedor)
        self.config.recalcular_signal.connect(self._atualizar_todas_paginas)
    def _navegar(self, key):
        idx = {"dashboard": 0, "vendedores": 1, "produtos": 2, "relatorios": 3, "config": 4}.get(key, 0)
        for k, btn in self.nav_btns:
            btn.setChecked(k == key)
            btn.setIcon(ICONS_ATIVO[k] if k == key else ICONS[k])
        self.stack.setCurrentIndex(idx)
        # Atualizar página ao navegar
        pag = self.stack.widget(idx)
        if hasattr(pag, 'atualizar') and self._loaded:
            pag.atualizar()
    def _load_data(self):
        self.loading = LoadingOverlay(self.content)
        self.loading.setGeometry(self.content.rect())
        self.loading.raise_(); self.loading.show()
        QTimer.singleShot(50, self._do_load)
    def _do_load(self):
        try:
            self.ger.carregar_dados("vendas.xlsx", "produtos.xlsx", "vendedores.xlsx")
            self._loaded = True
            self._navegar("dashboard")
            self.toasts.mostrar(f"{len(self.ger)} vendedores carregados com sucesso!", "ok")
        except FileNotFoundError as e:
            self.toasts.mostrar(f"Arquivo não encontrado: {e}", "err")
            self._mostrar_erro_critico(
                "Arquivos não encontrados",
                f"Não foi possível localizar os arquivos Excel necessários.\n\n"
                f"Certifique-se de que os seguintes arquivos estão na mesma pasta do aplicativo:\n"
                f"• vendas.xlsx\n• produtos.xlsx\n• vendedores.xlsx\n\n"
                f"Erro: {e}"
            )
        except Exception as e:
            self.toasts.mostrar(f"Erro ao carregar dados: {e}", "err")
            self._mostrar_erro_critico("Erro ao carregar", f"Ocorreu um erro inesperado:\n\n{e}")
        finally:
            if hasattr(self, 'loading') and self.loading:
                self.loading.parar()
                self.loading = None
    def _mostrar_erro_critico(self, titulo, msg):
        d = CustomDialog(titulo, msg, "err",
                        [("Entendi", "pri", lambda: None)], self.content)
        d.show_modal()
    def _atualizar_todas_paginas(self):
        for i in range(self.stack.count()):
            pag = self.stack.widget(i)
            if hasattr(pag, 'atualizar'):
                pag.atualizar()
    def _mostrar_detalhe_vendedor(self, v):
        tipo_nome = "Superstar ⭐" if isinstance(v, VendedorSuperstar) else \
                    "Com Bônus 🎁" if isinstance(v, VendedorComBonus) else "Padrão"
        bateu = v.vendas >= v.meta
        bonus_txt = ""
        if isinstance(v, VendedorComBonus):
            bonus_txt = f"\n🎁  Bônus: {fmt_moeda(v.calcular_bonus())}"
        msg = (
            f"👥  Nome: {v.nome.title()}\n"
            f"🏷️  Setor: {v.setor.capitalize()}\n"
            f"📋  Tipo: {tipo_nome}\n"
            f"🎯  Meta: {fmt_moeda(v.meta)}\n"
            f"💰  Total Vendido: {fmt_moeda(v.vendas)}\n"
            f"📈  Progresso: {v.calcular_progresso():.1f}%\n"
            f"{'✅  Status: Bateu a meta!' if bateu else '❌  Status: Não bateu a meta.'}"
            f"{bonus_txt}"
        )
        d = CustomDialog(v.nome.title(), msg, "ok" if bateu else "warn",
                        [("Fechar", "sec", lambda: None)], self.content)
        d.setFixedSize(440, 300)
        d.show_modal()
    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.toasts.resize(self.content.size())
        if hasattr(self, 'loading') and self.loading and self.loading.parent():
            self.loading.setGeometry(self.content.rect())


# ═══════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ═══════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    construir_icones()  # precisa de uma QApplication ativa para criar QPixmap/QIcon
    app.setStyle("Fusion")
    # Paleta global para o Fusion
    pal = app.palette()
    pal.setColor(pal.ColorRole.Window, QColor(T.BG))
    pal.setColor(pal.ColorRole.WindowText, QColor(T.TXT))
    pal.setColor(pal.ColorRole.Base, QColor(T.BG_CARD))
    pal.setColor(pal.ColorRole.AlternateBase, QColor(T.BG))
    pal.setColor(pal.ColorRole.Text, QColor(T.TXT))
    pal.setColor(pal.ColorRole.Button, QColor(T.BG_CARD))
    pal.setColor(pal.ColorRole.ButtonText, QColor(T.TXT))
    pal.setColor(pal.ColorRole.Highlight, QColor(T.PRIMARY))
    pal.setColor(pal.ColorRole.HighlightedText, QColor(T.TXT_LT))
    app.setPalette(pal)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()