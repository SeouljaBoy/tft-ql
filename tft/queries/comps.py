import tft.ql.expr as ql
import tft.client.meta as meta


def query_comps():
    return ql.query(meta.get_comp_details()).map(ql.idx('results').sub({
        'early': ql.idx('early_options').explode('level').map(ql.sub({
            'units': ql.idx('unit_list').split('&'),
            'avg_place': ql.idx('avg'),
            'games': ql.idx('count'),
            'level': ql.idx('level'),
        })),
        'late': ql.idx('options').explode('level').map(ql.sub({
            'units': ql.idx('units_list').split('&'),
            'avg_place': ql.idx('avg'),
            'games': ql.idx('count'),
            'level': ql.idx('level'),
        }))
    }).values().flatten()).explode('cluster').sort_by(ql.idx('games'), True)

def query_comp_details():
    return ql.query(meta.get_comp_details()).map(
        ql.idx('results').select([
            'placements',
            'unit_stats',
            'builds',
            'overall',
            'augments',
            'levels',
            'rerolls'
        ]))