# -*- coding: utf-8 -*-
'''
@Author: CaptainHu
@Date: 2021年 09月 07日 星期二 11:24:18 CST
@Description: 用于显示远程服务器上数据的标注
'''

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import os

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from dash.dependencies import Output, Input, State

import utils

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
app.layout = html.Div(children=[
    dcc.Store(id='all_img_path_list'),
    dcc.Store(id='current_img_path'),

    html.H1(children='Show Me The Label!'),
    html.Div(id="w_start_layout",
             children=[
                 html.H6("请输入文件夹或者图片路径,按 Enter 确认"),
                 dcc.Input(id="w_dir_input",
                           type="text",
                           placeholder="请输入文件夹所在路径",
                           value="",
                           persistence_type="session",
                           debounce=True),
                 html.Div(id="w_show_input_dir")
             ]),
    html.Div(children=[
        html.Div(id="w_imgs_path_slider_layout", hidden=True),
        html.Div(id="w_btn_layout", hidden=True),
        html.Div(
            id="w_show_current_img_path_div",
            children="",
        ),
        html.Div(id="show_img_layout",children=dcc.Graph(id="show_img_graph"), hidden=False),
    ]),
    html.Div(id="test_w"),
])


@app.callback(
    output=[
        Output("all_img_path_list", "data"),
        Output("w_show_input_dir", "children")
    ],
    inputs=Input("w_dir_input", "value"),
    prevent_initial_call=True,
)
def update_w_show_input_div(w_dir_input: str):
    all_img_path = []
    if os.path.exists(w_dir_input):
        info = "您输入的路径是: {} \n".format(w_dir_input)
        if os.path.isdir(w_dir_input):
            all_img_path = utils.get_all_file_path(w_dir_input)
        else:
            all_img_path = [w_dir_input]

    else:
        info = "{} 路径不存在!!! \n".format(w_dir_input)

    return all_img_path, info


@app.callback(
    output=[
        Output("w_imgs_path_slider_layout", "children"),
        Output("w_imgs_path_slider_layout", "hidden"),
        Output("w_btn_layout", "children"),
        Output("w_btn_layout", "hidden")
    ],
    inputs=dict(all_img_path_list=Input("all_img_path_list", "data"), ),
    prevent_initial_call=True,
)
def generate_result_show_widget(all_img_path_list: list):
    hidden = True
    slider_layout = ""
    btn_layout = ""
    if all_img_path_list:
        imgs_path_slider_max = len(all_img_path_list)
        #显示滑块
        hidden = False
        slider_layout = dcc.Slider(id="imgs_path_slider",
                                   min=0,
                                   max=len(all_img_path_list)-1,
                                   step=1,
                                   value=0)
        btn_layout = [
            dcc.Dropdown(id="files_dropdown",
                         options=[{
                             'label':os.path.basename(path),
                             'value':idx
                         } for idx, path in enumerate(all_img_path_list)],
                         value=0,clearable=False),
            html.Button(children="上一张", id="w_reduce1_bt", accessKey='d'),
            html.Button(children="下一张", id="w_add1_bt", accessKey='a')
        ]

    return slider_layout, hidden, btn_layout, hidden


@app.callback(
    output=[Output("imgs_path_slider","value"),
        Output("files_dropdown","value"),
        Output("current_img_path","data")
    ],
    inputs=dict(
        btn_r=Input("w_reduce1_bt", "n_clicks"),
        btn_a=Input("w_add1_bt", "n_clicks"),
        slider_value=Input("imgs_path_slider","value"),
        files_dropdown_value=Input("files_dropdown","value"),
        all_img_path=State("all_img_path_list", "data")
    ),
    prevent_initial_call=True,
)
def connet_bt2slider(btn_r, btn_a,slider_value,files_dropdown_value,all_img_path):
    if "w_reduce1_bt" == utils.get_callback_id():
        slider_value -=1
    if "w_add1_bt" == utils.get_callback_id():
        slider_value +=1

    if "files_dropdown" == utils.get_callback_id():
        slider_value=files_dropdown_value
    slider_value=max(0,slider_value)
    slider_value=min(len(all_img_path)-1,slider_value)
    files_dropdown_value=slider_value

    return slider_value,files_dropdown_value,all_img_path[slider_value]

@app.callback(
    output=[Output("show_img_layout","hidden"),
            Output("show_img_graph","figure")],
    inputs=[Input("current_img_path","data"),],
    prevent_initial_call=True,

)
def show_img(current_img_path,):
    fig=utils.show_img(current_img_path)
    return False,fig



if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
