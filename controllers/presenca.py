# coding=utf-8
import calendar
import locale
from datetime import datetime
from sie.SIEBolsistas import SIEBolsistas


# @auth.requires(lambda: proj.isCoordenador())
def index():
    locale.setlocale(locale.LC_ALL, 'pt_BR')
    meses = {mes: calendar.month_name[mes] for mes in range(1, 13)}
    mes_atual = date.today().month

    try:
        bolsistas = api.performGETRequest('V_BOLSISTAS_ATIVOS_DADOS', {'ID_PROJETO': request.vars.ID_PROJETO}).content

        presencas = {b['ID_BOLSISTA']: [] for b in bolsistas}
        presencas_meses = db(db.presencas.id_bolsista.belongs([b['ID_BOLSISTA'] for b in bolsistas])).select()
        for p in presencas_meses:
            presencas[p.id_bolsista].append(p.mes)

        def _presenca_btn(mes, bolsista):
            if mes not in presencas[bolsista['ID_BOLSISTA']]:
                if mes <= mes_atual:
                    uid = "%i%i" % (mes, bolsista['ID_BOLSISTA'])
                    return TD(A(T("Dar presença"),
                                target=uid,
                                _class="btn",
                                callback=URL('presenca', 'ajaxAdicionarPresenca', vars={'ID_BOLSISTA': bolsista['ID_BOLSISTA'],
                                                                                        'mes': mes,
                                                                                        'ano': datetime.today().year})),
                              _id=uid
                    )
                else:
                    return T("Presença bloqueada")
            else:
                return T("Presente")

        rows = [TR(TD(mes_nome), *[_presenca_btn(mes_num, b) for b in bolsistas]) for mes_num, mes_nome in meses.iteritems()]

        table = TABLE(
            THEAD(TH([TD(bolsista['BOLSISTA']) for bolsista in bolsistas])),
            *rows
        )

        return dict(
            meses=meses,
            table=table
        )
    except ValueError:
        session.flash = "Impossível atribuir presença. Não existe nenhum bolsista cadastrado."
        redirect(URL('default', 'index'))


def ajaxAdicionarPresenca():
    bolsista = SIEBolsistas().getBolsista(request.vars.ID_BOLSISTA)

    if request.vars.mes > date.today().month:
        return T("Presença bloqueada. Você não pode prever o futuro!")

    if proj.isCoordenador(bolsista['ID_PROJETO']):
        try:
            db.presencas.insert(
                id_bolsista=request.vars.ID_BOLSISTA,
                dt_presenca=datetime.today(),
                ano=request.vars.ano,
                mes=request.vars.mes,
                user_id=auth.user_id
            )
            return T("Presença adicionada")
        except Exception as e:
            return T("Um erro ocorreu ao inserir a presença.")

    return T("Você não possui permissão para acessar este recurso")