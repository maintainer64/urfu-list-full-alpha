from typing import List, Dict, Optional

from dash import Dash, html, dash_table, Input, Output, callback, dcc
from pydantic import BaseModel

from urfu_list_priority import loader_csv
from config import IS_DEBUG, log
from query_zip import query_json_decode, query_json_encode

app = Dash(__name__, url_base_pathname="/urfu/")


class QueryParamsString(BaseModel):
    page_current: Optional[int] = 1
    page_size: Optional[int] = 500
    sort_by: Optional[List[Dict[str, str]]] = []
    filter: Optional[str] = ""
    state: Optional[List[str]] = []

    def encode(self) -> str:
        return query_json_encode(self.model_dump(mode='python'))

    @classmethod
    def decode(cls, q: str) -> 'QueryParamsString':
        return cls.model_validate(obj=query_json_decode(q))


def query_decode(search):
    search = (search or "")
    if search.startswith("?q="):
        search = search[3:]
    q = QueryParamsString.decode(q=search)
    return q


def reload_app(loader):
    app.layout = html.Div(
        id="div-id",
        children=[
            dcc.Location(id="url", refresh="callback-nav"),
            html.P(
                id="datetime-paragraph",
                children=f"Последняя дата обновления {loader.LAST_UPDATED_DATE} / кол-во: {loader.ALL_COUNT}"
            ),
            dcc.Dropdown(
                id="filter_dropdown",
                options=loader.STATES_LIST,
                placeholder="-Выбрать направления-",
                multi=True,
            ),
            dash_table.DataTable(
                id='table-sorting-filtering',
                columns=[
                    {'name': i, 'id': i, 'deletable': True} for i in loader.df.columns
                ],
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_table={
                    'overflowX': 'auto',
                },
                style_cell={'textAlign': 'left', 'fontSize': '14px', },
                page_current=0,
                page_size=loader.PAGE_SIZE,
                page_action='custom',
                filter_action='custom',
                filter_query='',
                sort_action='custom',
                sort_mode='multi',
                sort_by=loader.SORTED_AUTO
            ),
        ])


reload_app(loader=loader_csv)
loader_csv.add_reload_callback(fn=reload_app)

operators = [
    ['contains '],
]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


@callback(
    Output('table-sorting-filtering', 'data'),
    Input("url", "search"),
)
def update_table(search):
    q = query_decode(search)
    filtering_expressions = q.filter.split(' && ')
    dff = loader_csv.df[loader_csv.df[loader_csv.STATES_NAME].isin(q.state)] if q.state else loader_csv.df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator == 'contains':
            log(col_name, operator, filter_value)
            dff = dff.loc[dff[col_name].astype(str).str.contains(filter_value)]

    if len(q.sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in q.sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in q.sort_by
            ],
            inplace=False
        )

    page = q.page_current
    size = q.page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')


@callback(
    Output("url", "href"),
    Input('table-sorting-filtering', "page_current"),
    Input('table-sorting-filtering', "page_size"),
    Input('table-sorting-filtering', 'sort_by'),
    Input('table-sorting-filtering', 'filter_query'),
    Input("filter_dropdown", "value"),
    prevent_initial_call=True,
)
def callback_url(page_current, page_size, sort_by, filter, state):
    q = QueryParamsString(
        page_current=page_current,
        page_size=page_size,
        sort_by=sort_by,
        filter=filter,
        state=state,
    )
    return f"?q={q.encode()}"


if __name__ == '__main__':
    from apscheduler.schedulers.background import BackgroundScheduler
    from urfu_list_priority import job

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(job, 'interval', max_instances=1, seconds=10 * 60 if IS_DEBUG else 10 * 60)
    scheduler.start()
    host = "127.0.0.1" if IS_DEBUG else "0.0.0.0"
    app.run(host=host, debug=IS_DEBUG)
