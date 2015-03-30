from tables import TableTransparenciaBolsistas, TableAPIResult


@cache.action(time_expire=600, cache_model=cache.ram)
def bolsistas():
    ativos = api.performGETRequest(
        'V_BOLSISTAS_ATIVOS_DADOS',
        {
            'LMIN': 0,
            'LMAX': 9999,
            'ORDERBY': 'NOME_DISCIPLINA'
        },
        ('NUM_PROCESSO', 'COORDENADOR', 'NOME_DISCIPLINA', 'BOLSISTA', 'VL_BOLSA', 'ID_PROJETO')
    ).content

    table = TableTransparenciaBolsistas(ativos)
    return dict(ativos=ativos, table=table)


# @cache.action(time_expire=600, cache_model=cache.ram)
def bolsas_unidades():
    unidades = api.performGETRequest(
        'V_BOLSISTAS_DEPARTAMENTOS',
        {
            'LMIN': 0,
            'LMAX': 9999,
            'ORDERBY': 'NOME_UNIDADE'
        },
        ('NOME_UNIDADE', 'TOTAL')
    )

    table = TableAPIResult(unidades)
    total = sum([k['TOTAL'] for k in unidades.content])

    return dict(unidades=unidades, table=table, total=total)


@auth.requires(lambda: edicao.requires_edicao())
# @cache.action(time_expire=3000, session=True, cache_model=cache.ram)
def projetos_aprovados():
    try:
        projetos = api.performGETRequest(
            'V_PROJETOS_DADOS',
            {
                "ID_CLASSIFICACAO": 40161,
                "DT_INICIAL": session.edicao.dt_inicial_projeto,
                "SITUACAO_ITEM": 2,
                "LMIN": 0,
                "LMAX": 9999
            },
            ('NOME_DISCIPLINA', 'COD_DISCIPLINA', 'NOME_UNIDADE', 'COORDENADOR', 'NUM_PROCESSO', 'ID_PROJETO')
        )

        table = TableAPIResult(projetos)
    except ValueError:
        pass

    return dict(table=table.printTable())