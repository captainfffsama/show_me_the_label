# -*- coding: utf-8 -*-
'''
@Author: CaptainHu
@Date: 2021年 09月 07日 星期二 16:47:48 CST
@Description: 用于放一些工具函数
'''

import os
from functools import lru_cache
import xml.etree.ElementTree as ET

import dash
from PIL import Image

import plotly.graph_objects as go


@lru_cache(None)
def get_all_file_path(file_dir: str, filter_: tuple = ('.jpg', )) -> list:
    #遍历文件夹下所有的file
    return [os.path.join(maindir,filename) for maindir,_,file_name_list in os.walk(file_dir) \
            for filename in file_name_list \
            if os.path.splitext(filename)[1] in filter_ ]


def get_callback_id(no_attr=True):
    if no_attr:
        return dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    else:
        return dash.callback_context.triggered[0]['prop_id']


def parse_rec(filename) -> list:
    r"""
        分析xml文件
    """
    tree = ET.parse(filename)
    objects = []
    for obj in tree.findall('object'):
        obj_struct = {}
        obj_struct['name'] = obj.find('name').text
        obj_struct['pose'] = obj.find('pose').text
        obj_struct['truncated'] = int(obj.find('truncated').text)
        obj_struct['difficult'] = int(obj.find('difficult').text)
        bbox = obj.find('bndbox')
        obj_struct['bbox'] = [
            int(bbox.find('xmin').text),
            int(bbox.find('ymin').text),
            int(bbox.find('xmax').text),
            int(bbox.find('ymax').text)
        ]
        objects.append(obj_struct)

    return objects


def pil_to_fig(im, showlegend=False, title=None):
    img_width, img_height = im.size
    fig = go.Figure()
    # This trace is added to help the autoresize logic work.
    fig.add_trace(
        go.Scatter(x=[img_width * 0.05, img_width * 0.95],
                   y=[img_height * 0.95, img_height * 0.05],
                   showlegend=False,
                   mode="markers",
                   marker_opacity=0,
                   hoverinfo="none",
                   legendgroup='Image'))

    fig.add_layout_image(
        dict(
            source=im,
            opacity=1,
            layer="below",
            x=0,
            y=0,
            xref="x",
            yref="y",
            sizex=img_width,
            sizey=img_height,
        ))

    # Adapt axes to the right width and height, lock aspect ratio
    fig.update_xaxes(showgrid=False,
                     visible=False,
                     constrain="domain",
                     range=[0, img_width])

    fig.update_yaxes(showgrid=False,
                     visible=False,
                     scaleanchor="x",
                     scaleratio=1,
                     range=[img_height, 0])

    fig.update_layout(title=title,
                      showlegend=showlegend,
                      width=1920,
                      height=1080)

    return fig


def add_bbox(fig,
             x0,
             y0,
             x1,
             y1,
             showlegend=True,
             name=None,
             color=None,
             opacity=0.5,
             group=None,
             text=None,font_size=10,):
    fig.add_shape(type="rect",
                  x0=x0,
                  y0=y0,
                  x1=x1,
                  y1=y1,
                  line=dict(color=color))
    text_size=max(font_size,min((x1-x0),(y1-y0))//10)
    fig.add_annotation(x=x0,
                       y=y1,
                       text=text,
                       font=dict(color="yellow",size=text_size),
                       xanchor="left",
                       yanchor="bottom",
                       align="left",
                       showarrow=False)


@lru_cache(None)
def show_img(img_path):
    img = Image.open(img_path)

    fig = pil_to_fig(img)

    xml_path = os.path.splitext(img_path)[0] + ".xml"
    font_size=max(1,min(img.size)//30)

    if os.path.exists(xml_path):
        ann_obj = parse_rec(xml_path)
        for obj in ann_obj:
            x0, y0, x1, y1 = obj["bbox"]
            label = obj["name"]
            add_bbox(
                fig,
                x0,
                y0,
                x1,
                y1,
                opacity=0.7,
                group=label,
                name=label,
                color="green",
                showlegend=True,
                text=label,
                font_size=font_size,
            )

    return fig
