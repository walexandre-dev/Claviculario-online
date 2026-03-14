import math
from datetime import datetime
from fpdf import FPDF


class RelatorioPDF(FPDF):
    BRAND_COLOR   = (15,  23,  42)
    ACCENT_COLOR  = (59, 130, 246)
    SUCCESS_COLOR = (16, 185, 129)
    DANGER_COLOR  = (239, 68,  68)
    WARNING_COLOR = (245, 158, 11)
    HEADER_TEXT   = (255, 255, 255)
    BODY_TEXT     = (30,  41,  59)
    MUTED_TEXT    = (100, 116, 139)
    ROW_ALT       = (248, 250, 252)
    ROW_WHITE     = (255, 255, 255)
    BORDER_COLOR  = (226, 232, 240)

    def __init__(self, periodo_texto='Histórico Completo', stats=None):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.periodo_texto = periodo_texto
        self.stats = stats or {}
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=18)

    def rounded_rect(self, x, y, w, h, r, style=''):
        k  = self.k
        hp = self.h
        op = {'F': 'f', 'FD': 'B', 'DF': 'B'}.get(style, 'S')
        arc = 4 / 3 * (math.sqrt(2) - 1)
        self._out(f'{(x+r)*k:.2f} {(hp-y)*k:.2f} m')
        xc, yc = x+w-r, y+r
        self._out(f'{xc*k:.2f} {(hp-y)*k:.2f} l')
        self._out(f'{(xc+r*arc)*k:.2f} {(hp-y)*k:.2f} {(x+w)*k:.2f} {(hp-yc+r*arc)*k:.2f} {(x+w)*k:.2f} {(hp-yc)*k:.2f} c')
        yc = y+h-r
        self._out(f'{(x+w)*k:.2f} {(hp-yc)*k:.2f} l')
        self._out(f'{(x+w)*k:.2f} {(hp-yc-r*arc)*k:.2f} {(xc+r*arc)*k:.2f} {(hp-(y+h))*k:.2f} {xc*k:.2f} {(hp-(y+h))*k:.2f} c')
        xc = x+r
        self._out(f'{xc*k:.2f} {(hp-(y+h))*k:.2f} l')
        self._out(f'{(xc-r*arc)*k:.2f} {(hp-(y+h))*k:.2f} {x*k:.2f} {(hp-yc-r*arc)*k:.2f} {x*k:.2f} {(hp-yc)*k:.2f} c')
        yc = y+r
        self._out(f'{x*k:.2f} {(hp-yc)*k:.2f} l')
        self._out(f'{x*k:.2f} {(hp-yc+r*arc)*k:.2f} {(xc-r*arc)*k:.2f} {(hp-y)*k:.2f} {xc*k:.2f} {(hp-y)*k:.2f} c')
        self._out(op)

    def header(self):
        self.set_fill_color(*self.BRAND_COLOR)
        self.rect(0, 0, 297, 28, 'F')
        self.set_fill_color(*self.ACCENT_COLOR)
        self.rect(0, 28, 297, 5, 'F')
        self.set_fill_color(*self.ACCENT_COLOR)
        self.rounded_rect(12, 5, 18, 18, 3, style='F')
        self.set_text_color(*self.HEADER_TEXT)
        self.set_font('Arial', 'B', 14)
        self.set_xy(14, 10)
        self.cell(14, 8, 'K', 0, 0, 'C')
        self.set_font('Arial', 'B', 16)
        self.set_xy(34, 6)
        self.cell(150, 8, 'SISTEMA CLAVICULARIO DIGITAL', 0, 2, 'L')
        self.set_font('Arial', '', 9)
        self.set_text_color(148, 163, 184)
        self.set_x(34)
        self.cell(150, 6, 'Relatorio de Movimentacoes de Chaves', 0, 0, 'L')
        self.set_font('Arial', 'B', 8)
        self.set_xy(180, 6)
        self.cell(100, 5, 'PERIODO', 0, 2, 'R')
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*self.HEADER_TEXT)
        self.set_x(180)
        self.cell(100, 6, self.periodo_texto, 0, 2, 'R')
        self.set_font('Arial', '', 8)
        self.set_text_color(148, 163, 184)
        self.set_x(180)
        self.cell(100, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'R')
        self.ln(12)

    def footer(self):
        self.set_y(-14)
        self.set_draw_color(*self.BORDER_COLOR)
        self.line(15, self.get_y(), 282, self.get_y())
        self.ln(1)
        self.set_font('Arial', 'I', 7.5)
        self.set_text_color(*self.MUTED_TEXT)
        self.cell(130, 5, 'CONFIDENCIAL - Uso restrito aos responsaveis autorizados', 0, 0, 'L')
        self.set_font('Arial', 'B', 8)
        self.cell(0, 5, f'Pagina {self.page_no()}', 0, 0, 'R')

    def stats_row(self):
        if not self.stats:
            return
        y = self.get_y()
        cw, ch, gap, sx = 55, 16, 5, 15
        data = [
            ('TOTAL DE REGISTROS', str(self.stats.get('total', 0)),      self.ACCENT_COLOR),
            ('CONCLUIDOS',         str(self.stats.get('concluidos', 0)), self.SUCCESS_COLOR),
            ('EM ABERTO',          str(self.stats.get('em_aberto', 0)),  self.DANGER_COLOR),
            ('CHAVES DISTINTAS',   str(self.stats.get('chaves', 0)),     self.WARNING_COLOR),
        ]
        for i, (label, value, color) in enumerate(data):
            x = sx + i * (cw + gap)
            self.set_fill_color(248, 250, 252)
            self.rounded_rect(x, y, cw, ch, 2, style='F')
            self.set_fill_color(*color)
            self.rounded_rect(x, y, 3, ch, 1, style='F')
            self.set_font('Arial', 'B', 15)
            self.set_text_color(*self.BODY_TEXT)
            self.set_xy(x+7, y+1)
            self.cell(cw-10, 8, value, 0, 2, 'L')
            self.set_font('Arial', '', 6.5)
            self.set_text_color(*self.MUTED_TEXT)
            self.set_x(x+7)
            self.cell(cw-10, 4, label, 0, 0, 'L')
        self.ln(ch + 8)

    def table_header(self, col_widths, col_labels):
        self.set_fill_color(*self.BRAND_COLOR)
        self.set_text_color(*self.HEADER_TEXT)
        self.set_font('Arial', 'B', 8)
        self.set_draw_color(*self.BRAND_COLOR)
        for label, w in zip(col_labels, col_widths):
            self.cell(w, 9, label, 1, 0, 'C', fill=True)
        self.ln()

    def table_row(self, data, col_widths, row_index, aligns=None):
        if aligns is None:
            aligns = ['L'] * len(data)
        r, g, b = self.ROW_WHITE if row_index % 2 == 0 else self.ROW_ALT
        self.set_draw_color(*self.BORDER_COLOR)
        for i, (cell_val, w, align) in enumerate(zip(data, col_widths, aligns)):
            is_status = (i == len(data) - 1)
            if is_status and 'EM ABERTO' in str(cell_val).upper():
                self.set_fill_color(254, 243, 199)
                self.set_text_color(146, 64, 14)
            elif is_status and 'CONCLUIDO' in str(cell_val).upper():
                self.set_fill_color(209, 250, 229)
                self.set_text_color(6, 95, 70)
            else:
                self.set_fill_color(r, g, b)
                self.set_text_color(*self.BODY_TEXT)
            self.set_font('Arial', 'B' if is_status else '', 8.5)
            self.cell(w, 8, str(cell_val), 1, 0, align, fill=True)
        self.ln()
        self.set_text_color(*self.BODY_TEXT)
        self.set_fill_color(*self.ROW_WHITE)

    def section_title_box(self, title):
        self.set_fill_color(*self.ACCENT_COLOR)
        self.set_text_color(*self.HEADER_TEXT)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 8, f'  {title}', 0, 1, 'L', fill=True)
        self.ln(3)


def _safe(text):
    if not text:
        return '—'
    return str(text).encode('latin-1', 'replace').decode('latin-1')


def gerar_relatorio_pdf(movimentacoes, periodo_texto='Histórico Completo'):
    total      = len(movimentacoes)
    concluidos = sum(1 for m in movimentacoes if m.data_devolucao)
    em_aberto  = total - concluidos
    chaves_set = len({m.chave_id for m in movimentacoes})

    stats = {
        'total': total, 'concluidos': concluidos,
        'em_aberto': em_aberto, 'chaves': chaves_set,
    }

    pdf = RelatorioPDF(periodo_texto=periodo_texto, stats=stats)
    pdf.add_page()
    pdf.section_title_box('RESUMO DO PERIODO')
    pdf.stats_row()
    pdf.section_title_box('DETALHAMENTO DAS MOVIMENTACOES')

    col_widths = [45, 45, 30, 20, 30, 20, 27, 50]
    col_labels = ['CHAVE / LOCAL', 'USUARIO', 'DATA RET.', 'HORA',
                  'DATA DEV.', 'HORA', 'DURACAO', 'STATUS']
    aligns = ['L', 'L', 'C', 'C', 'C', 'C', 'C', 'C']

    pdf.table_header(col_widths, col_labels)

    if not movimentacoes:
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 10, 'Nenhuma movimentacao encontrada para o periodo selecionado.', 0, 1, 'C')
    else:
        for idx, mov in enumerate(movimentacoes):
            chave_nome = _safe(mov.chave.nome if mov.chave else 'Chave Excluida')
            usuario    = _safe(mov.usuario_nome or 'Desconhecido')
            data_ret   = mov.data_retirada.strftime('%d/%m/%Y') if mov.data_retirada else '—'
            hora_ret   = mov.data_retirada.strftime('%H:%M')    if mov.data_retirada else '—'
            if mov.data_devolucao:
                data_dev = mov.data_devolucao.strftime('%d/%m/%Y')
                hora_dev = mov.data_devolucao.strftime('%H:%M')
                tot_min  = int((mov.data_devolucao - mov.data_retirada).total_seconds() // 60)
                if tot_min < 60:
                    dur = f'{tot_min}min'
                elif tot_min < 1440:
                    dur = f'{tot_min // 60}h {tot_min % 60}min'
                else:
                    dur = f'{tot_min // 1440}d {(tot_min % 1440) // 60}h'
                status = 'CONCLUIDO'
            else:
                data_dev = hora_dev = '—'
                dur, status = 'Em aberto', 'EM ABERTO'

            pdf.table_row(
                [chave_nome, usuario, data_ret, hora_ret,
                 data_dev, hora_dev, dur, status],
                col_widths, idx, aligns
            )

        # Linha de totais
        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 8.5)
        pdf.set_draw_color(15, 23, 42)
        pdf.cell(col_widths[0]+col_widths[1], 8, f'  TOTAL: {total} registros', 1, 0, 'L', fill=True)
        pdf.cell(sum(col_widths[2:7]), 8, '', 1, 0, 'C', fill=True)
        pdf.set_text_color(209, 250, 229)
        pdf.cell(col_widths[7], 8, f'{concluidos} OK / {em_aberto} ABERTO', 1, 1, 'C', fill=True)

    pdf_bytes = bytes(pdf.output())
    filename  = f'relatorio_claviculario_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    return pdf_bytes, filename
