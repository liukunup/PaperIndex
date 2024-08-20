#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author : Liu Kun
# date   : 2024-08-19 22:54:05

import os
import json
import hashlib
import datetime
import dashscope
import pandas as pd
from typing import Text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import PaperIndex, Certificate
from http import HTTPStatus


def call_llm_dash_scope(pdf_url):
    """
    调用DashScope去解析PDF并提取信息
    :param pdf_url: PDF链接
    :return: 解析结果
    """
    # 需要使用到PDF解析插件
    plugins = {'pdf_extracter': {}}
    # 调用指令
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': [
                    {'text': '任务1:从首页中抽取作者(author)、机构(organization)、邮箱(email),输出是一个以作者为维度的对象列表;'
                             '任务2:翻译Abstract部分,输出包含原文(en)、译文(zh)。'
                             '输出格式:JSON'},
                    {'file': pdf_url}]
                }]
    # 灵积! 启动～
    response = dashscope.Generation.call(
        dashscope.Generation.Models.qwen_plus,
        messages=messages,
        result_format='message',
        plugins=plugins,
    )
    if response.status_code == HTTPStatus.OK:
        return messages, response
    else:
        print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
            response.request_id, response.status_code,
            response.code, response.message
        ))
    return messages, None


class Task:

    # 至少预留3w的余量
    RESERVED_TOKEN_NUM = 30000

    def __init__(self, username: Text = None, password: Text = None, host: Text = None, port: int = 3306,
                 schema: Text = None):
        # 获取数据库的参数
        self.username = username if username else os.getenv('DB_USERNAME', 'root')
        self.password = password if password else os.getenv('DB_PASSWORD', 'changeit')
        self.host = host if host else os.getenv('DB_HOST', 'localhost')
        self.schema = schema if schema else os.getenv('DB_SCHEMA', 'staging')
        # 创建引擎
        self.engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{schema}')
        # 加载开放平台的API调用凭证
        self.certificate_id = -1
        self.load_certificate()

    def load_certificate(self):
        Session = sessionmaker(bind=self.engine)
        with (Session() as session):
            certificate_list = session.query(Certificate).filter(Certificate.unused_token_num > self.RESERVED_TOKEN_NUM).all()
            for cert in certificate_list:
                for k, v in cert.data.items():
                    print('-' * 100)
                    print(f'加载凭证: id={cert.id} platform={cert.platform} model={cert.model} '
                          f'unused_token={cert.unused_token_num} owner={cert.owner}')
                    self.certificate_id = cert.id
                    os.environ[k] = v
                    return
        raise Exception('加载鉴权凭证失败! 请确保你在数据库中已经配置了可用的凭证(比如,API-KEY)')

    def consume_token(self, num):
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            obj = session.query(Certificate).filter(Certificate.id == self.certificate_id).one_or_none()
            if obj:  # 扣减
                obj.unused_token_num -= num
                obj.updated_at = datetime.datetime.now()
                session.commit()
                if obj.unused_token_num < self.RESERVED_TOKEN_NUM:  # 替换凭证
                    tmp_id = self.certificate_id
                    self.load_certificate()  # 重新加载凭证
                    # 加载完应该会更新才对
                    if self.certificate_id == tmp_id:
                        raise Exception('无法自动加载到可用的凭证,请检查!')

    def upsert_paper(self, data):
        # 入参检查
        if not data:
            return

        def md5_hash(s):
            """ 计算md5哈希值 """
            hash_object = hashlib.md5()
            hash_object.update(s.encode('utf-8'))
            md5_digest = hash_object.hexdigest()
            return md5_digest

        # 插入或更新
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            obj = session.query(PaperIndex).filter(PaperIndex.pdf_url == data['pdf_url']).one_or_none()
            if obj:
                obj.source = data['source']
                obj.title = data['title']
                obj.web_url = data['web_url']
                obj.authors = data['author']
                obj.reference = None if 'infos' not in data else data['infos']
                obj.md5_hash = md5_hash(f"{data['pdf_url']}{data['title']}{data['author']}")
                obj.updated_at = datetime.datetime.now()
            else:
                paper = PaperIndex(
                    source=data['source'],
                    title=data['title'],
                    web_url=data['web_url'],
                    pdf_url=data['pdf_url'],
                    authors=data['author'],
                    reference=None if 'infos' not in data else data['infos'],
                    md5_hash=md5_hash(f"{data['pdf_url']}{data['title']}{data['author']}"),
                )
                session.add(paper)
            session.commit()

    def update_call_history(self, data, req, resp):
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            obj = session.query(PaperIndex).filter(PaperIndex.id == data.id).one_or_none()
            if obj:
                obj.dash_scope_req = req
                obj.dash_scope_resp = resp
                obj.updated_at = datetime.datetime.now()
                session.commit()

    def update_result(self, data, result):
        Session = sessionmaker(bind=self.engine)
        with Session() as session:
            obj = session.query(PaperIndex).filter(PaperIndex.id == data.id).one_or_none()
            if obj:
                obj.dash_scope_result = result
                obj.is_extracted = 1 if result else 0
                obj.updated_at = datetime.datetime.now()
                session.commit()

    def upload_paper_to_db(self):
        # 定位目标路径
        target_path = os.path.join(os.path.dirname(os.getcwd()), 'thecvf')

        def helper(path):
            """ 筛选jsonl文件 """
            if not os.path.isdir(path):
                return []
            target = []
            for f in os.listdir(path):
                fn = os.path.join(path, f)
                if os.path.isfile(fn) and fn.endswith('.jsonl'):
                    target.append(fn)
                elif os.path.isdir(fn):
                    target.extend(helper(fn))
                else:
                    pass
            return target

        # 遍历指定目录
        jsonl_files = helper(target_path)
        for jsonl in jsonl_files:
            print('-' * 100)
            print(f'upload {jsonl} ...')
            source = os.path.basename(jsonl).replace('.jsonl', '')
            with open(jsonl, 'r') as file:
                for i, line in enumerate(file.readlines()):
                    obj = json.loads(line)
                    obj.update({'source': source})
                    print(f"{i}: {obj['title']}")
                    self.upsert_paper(obj)

    def load_papers(self, max_num: int = -1):
        Session = sessionmaker(bind=self.engine)
        with (Session() as session):
            if max_num < 0:
                return session.query(PaperIndex).filter(
                    PaperIndex.is_extracted == 0).order_by(PaperIndex.id.asc()).all()
            else:
                return session.query(PaperIndex).filter(
                    PaperIndex.is_extracted == 0).order_by(PaperIndex.id.asc()).limit(max_num).all()

    def extract(self, max_num: int = -1):
        papers = self.load_papers(max_num=max_num)
        for paper in papers:
            print(f'extract pdf {paper.id} {paper.title}')
            req, resp = call_llm_dash_scope(paper.pdf_url)
            if resp:
                self.consume_token(num=resp.usage.total_tokens)
                self.update_call_history(paper, req, json.loads(resp.__str__()))
                try:
                    s = resp.output.choices[0].message.content
                    if isinstance(s, str):
                        obj = json.loads(s)
                        self.update_result(paper, obj)
                except Exception as e:
                    pass
            else:
                self.update_call_history(paper, req, None)

    def export_excel(self, max_num: int = -1, excel_filename: Text = 'output.xlsx'):
        output = {
            'id': [],
            'title': [],
            'pdf': [],
            'authors-1': [],
            'authors-2': [],
            'en': [],
            'zh': [],
        }
        papers = self.load_papers(max_num=max_num)
        for paper in papers:
            output['id'].append(paper.id)
            output['title'].append(paper.title)
            output['pdf'].append(paper.pdf_url)
            output['authors-1'].append(paper.authors)
            tmp = ''
            for item in paper.dash_scope_result['authors']:
                try:
                    name = ''
                    if 'author' in item:
                        name = item['author']
                    if 'name' in item:
                        name = item['name']
                    tmp += f"{name} / {item['email']} / {item['organization']}\n"
                except Exception as e:
                    print(item)
            output['authors-2'].append(tmp)
            output['en'].append(paper.dash_scope_result['abstract']['en'])
            output['zh'].append(paper.dash_scope_result['abstract']['zh'])
        df = pd.DataFrame(output)
        df.to_excel(excel_filename)


if __name__ == '__main__':
    inst = Task(username='root', password='changeit', host='localhost', port=3306, schema='staging')
    inst.extract(max_num=5)
    # inst.export_excel()
