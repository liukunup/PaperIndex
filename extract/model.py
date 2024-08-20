# -*- coding: UTF-8 -*-
# author : Liu Kun
# date   : 2024-08-19 22:52:01

from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import BIGINT, TINYINT

Base = declarative_base()


class PaperIndex(Base):
    __tablename__ = 't_paper_index'

    id = Column(BIGINT, autoincrement=True, primary_key=True, comment='记录ID')
    source = Column(String(256), default=False, comment='来源')
    title = Column(String(256), nullable=False, comment='标题')
    web_url = Column(String(256), nullable=False, comment='页面链接')
    pdf_url = Column(String(256), nullable=False, comment='PDF链接')
    authors = Column(String(1024), nullable=False, comment='作者列表')
    reference = Column(String(1024), nullable=False, comment='参考文献')
    md5_hash = Column(String(32), unique=True, nullable=False, comment='MD5(pdf_url+title+authors)')
    dash_scope_req = Column(JSON, default=None, comment='信息抽取的请求参数')
    dash_scope_resp = Column(JSON, default=None, comment='信息抽取的响应结果')
    dash_scope_result = Column(JSON, default=None, comment='被抽取信息')
    is_extracted = Column(TINYINT, default=0, comment='是否已抽取')
    is_locked = Column(TINYINT, default=0, comment='是否被锁定(人工修正过,不希望再次被更新)')
    is_deleted = Column(TINYINT, default=0, comment='是否已删除')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='记录创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP',
                        comment='记录更新时间')


class Certificate(Base):
    __tablename__ = 't_certificate'

    id = Column(Integer, autoincrement=True, primary_key=True, comment='记录ID')
    platform = Column(String(256), nullable=False, comment='平台')
    model = Column(String(256), nullable=False, comment='模型')
    data = Column(JSON, nullable=False, comment='请求鉴权凭证')
    unused_token_num = Column(BIGINT, default=0, comment='Token剩余量')
    owner = Column(String(256), comment='所有者')
    created_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', comment='记录创建时间')
    updated_at = Column(TIMESTAMP, server_default='CURRENT_TIMESTAMP', onupdate='CURRENT_TIMESTAMP',
                        comment='记录更新时间')
