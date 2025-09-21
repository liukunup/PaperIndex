#!/usr/bin/python
# -*- coding: UTF-8 -*-
# author : Liu Kun
# date   : 2021-09-01 00:00:01

import os
import cmd
import json
import requests
from bs4 import BeautifulSoup


def request_paper_list(url, debug=False):
    """
    根据链接爬取论文信息
    :param url:   目标链接
    :param debug: 调试信息打印开关[默认关闭]
    :return: 论文信息列表
    """
    # 请求页面
    base_url = f"https://openaccess.thecvf.com"
    response = requests.get(url)
    # 使用BeautifulSoup加载页面
    soup = BeautifulSoup(response.content, features="lxml")
    # 按标签查找
    dl = soup.find("dl")
    dt_list = dl.find_all("dt")
    dd_list = dl.find_all("dd")
    # 去除Back
    if "back" in dd_list[0].text.strip().lower():
        dd_list.pop(0)
    # 按奇偶处理dd标签
    dd_odd_list = dd_list[::2]
    dd_even_list = dd_list[1::2]
    # 用于存放论文信息
    papers = list()
    # 逐行处理
    for item in zip(dt_list, dd_odd_list, dd_even_list):
        # Line 1
        line_1 = item[0]
        tag_a_1 = line_1.find("a")
        # Line 2
        line_2 = item[1]
        # Line 3
        line_3 = item[2]
        tag_a_2 = line_3.find("a")
        tag_div = line_3.find("div")
        paper_json = {
            "web_url": base_url + tag_a_1["href"],
            "title": tag_a_1.text.strip(),
            "author": line_2.text.strip().replace("\n", "").replace("\r", ""),
            "pdf_url": base_url + tag_a_2["href"],
            "infos": tag_div.text.strip().replace("\n", "").replace("\r", "").replace("[bibtex]", ""),
        }
        # 修复链接中缺少/链接符的问题
        if not str(tag_a_1["href"]).startswith("/"):
            paper_json["web_url"] = base_url + "/" + tag_a_1["href"]
        if not str(tag_a_2["href"]).startswith("/"):
            paper_json["pdf_url"] = base_url + "/" + tag_a_2["href"]
        if debug:
            print("-" * 100)
            print(json.dumps(paper_json, sort_keys=True, indent=4, separators=(',', ': ')))
        papers.append(paper_json)
    print("共爬取到论文信息%d条" % len(papers))
    return papers


def request_eccv_paper_list(url="https://www.ecva.net/papers.php", year=None, debug=False):
    """
    ECCV
    :param url:   目标链接
    :param year:  年份标识
    :param debug: 调试信息打印开关[默认关闭]
    :return: 论文信息列表
    """
    # 参数检查
    if year is None or not isinstance(year, str) or len(year) <= 0:
        return list()
    # 获取标识 ECCV2018 -> 2018
    flag = year.upper().replace("ECCV", "")
    # 请求页面
    base_url = f"https://www.ecva.net"
    response = requests.get(url)
    # 使用BeautifulSoup加载页面
    soup = BeautifulSoup(response.content, features="lxml")
    # 按标签查找
    div_list = soup.find_all("div", attrs={"class": "accordion-content"})
    # 用于存放论文信息
    papers = list()
    for div in div_list:
        dt_list = div.find_all("dt")
        dd_list = div.find_all("dd")
        # 按奇偶处理dd标签
        dd_odd_list = dd_list[::2]
        dd_even_list = dd_list[1::2]
        # 逐行处理
        for item in zip(dt_list, dd_odd_list, dd_even_list):
            # Line 1
            line_1 = item[0]
            tag_a_1 = line_1.find("a")
            # Line 2
            line_2 = item[1]
            # Line 3
            line_3 = item[2]
            tag_a_2 = line_3.find("a")
            paper_json = {
                "web_url": base_url + tag_a_1["href"],
                "title": tag_a_1.text.strip(),
                "author": line_2.text.strip().replace("\n", "").replace("\r", ""),
                "pdf_url": base_url + tag_a_2["href"],
            }
            # 修复链接中缺少/链接符的问题
            if not str(tag_a_1["href"]).startswith("/"):
                paper_json["web_url"] = base_url + "/" + tag_a_1["href"]
            if not str(tag_a_2["href"]).startswith("/"):
                paper_json["pdf_url"] = base_url + "/" + tag_a_2["href"]
            if debug:
                print("-" * 100)
                print(json.dumps(paper_json, sort_keys=True, indent=4, separators=(',', ': ')))
            if paper_json["web_url"].find(flag) != -1:
                papers.append(paper_json)
    print("共爬取到论文信息%d条" % len(papers))
    return papers


def request_nips_paper_list(url="https://papers.nips.cc/paper_files/paper/2024", year="NeurIPS2024", debug=False):
    """
    NeurIPS
    :param url:   目标链接
    :param year:  年份标识
    :param debug: 调试信息打印开关[默认关闭]
    :return: 论文信息列表
    """
    # 参数检查
    if year is None or not isinstance(year, str) or len(year) <= 0:
        return list()
    # 获取标识 NeurIPS2024 -> 2024
    flag = year.upper().replace("NEURIPS", "")
    # 请求页面
    response = requests.get(url)
    # 使用BeautifulSoup加载页面
    soup = BeautifulSoup(response.content, features="lxml")
    # 按标签查找
    li_list = soup.select("li.conference, li.datasets_and_benchmarks_track, li.none")
    print("共找到论文链接%d条" % len(li_list))
    # 用于存放论文信息
    base_url = "https://papers.nips.cc"
    papers = list()
    for li in li_list:
        li_a_tag = li.find("a")
        li_i_tag = li.find("i")
        link1 = li_a_tag["href"]
        link2 = None
        if link1 and link1.startswith("/paper_files/paper/"):
            link2 = link1.replace("hash", "file").replace("Abstract", "Paper").replace(".html", ".pdf")
        paper_json = {
            "web_url": f"{base_url}{link1}",
            "title": li_a_tag.text.strip(),
            "author": li_i_tag.text.strip(),
            "pdf_url": f"{base_url}{link2}",
        }
        if debug:
            print("-" * 100)
            print(json.dumps(paper_json, sort_keys=True, indent=4, separators=(',', ': ')))
        if paper_json["web_url"].find(flag) != -1:
            papers.append(paper_json)
    print("共爬取到论文信息%d条" % len(papers))
    return papers


def request_icml_paper_list(url="https://icml.cc/static/virtual/data/icml-2025-orals-posters.json",
                            year="ICML2025", debug=False):
    """
    ICML
    :param url:   目标链接
    :param year:  年份标识
    :param debug: 调试信息打印开关[默认关闭]
    :return: 论文信息列表
    """
    # 参数检查
    if year is None or not isinstance(year, str) or len(year) <= 0:
        return list()
    # 获取标识 ICML2025 -> 2025
    flag = year.upper().replace("ICML", "")
    # 请求页面
    response = requests.get(url)
    # 解析JSON
    # {"count": 3459, "next": null, "previous": null, "results": []}
    json_obj = json.loads(response.content)
    count = json_obj.get("count", 0)
    results = json_obj.get("results", list())
    print("找到论文记录%d条(count:%d)" % (len(results), count))
    # 用于存放论文信息
    base_url = "https://icml.cc"
    papers = list()
    for item in results:
        authors = item.get("authors", list())
        author_str = ""
        if isinstance(authors, list):
            author_str = ", ".join([author.get("fullname", "") for author in authors])
        paper_url = item.get("paper_url", "")
        paper_pdf_url = item.get("paper_pdf_url", "")
        virtualsite_url = item.get("virtualsite_url", "")
        pdf_url = item.get("pdf_url", "")
        paper_json = {
            "web_url": paper_url or f"{base_url}{virtualsite_url}",
            "title": item.get("name", ""),
            "author": author_str,
            "pdf_url": pdf_url or paper_pdf_url or paper_url.replace("forum", "pdf"),
            "raw": item,
        }
        if debug:
            print("-" * 100)
            print(json.dumps(paper_json, sort_keys=True, indent=4, separators=(',', ': ')))
        papers.append(paper_json)
    print("共爬取到论文信息%d条" % len(papers))
    return papers


def export_jsonl(papers, filename):
    """
    导出为jsonl格式
    每行一条json数据
    :param papers: 论文信息列表
    :param filename: 导出文件名
    :return: 无
    """
    with open(filename, "a+") as jsonl:
        for p in papers:
            jsonl.write(json.dumps(p) + "\n")
    pass


def export_url(papers, filename):
    """
    导出为url格式
    每行一条url数据
    :param papers: 论文信息列表
    :param filename: 导出文件名
    :return: 无
    """
    with open(filename, "a+") as txt:
        for p in papers:
            txt.write(p["pdf_url"] + "\n")
    pass


def downloader(url, folder):
    """
    下载论文到指定目录
    :param url: 论文链接
    :param folder: 存储目录
    :return: 本地文件名
    """
    filename = url.split("/")[-1]
    file = os.path.join(folder, filename)
    if os.path.exists(file):
        print(f"skip {file} @ {url}")
        return file
    print(f"download {file} from {url}")
    response = requests.get(url)
    with open(file, "wb") as output:
        output.write(response.content)
    return file


class CLI(cmd.Cmd):

    intro = "输入 help 或者 ? 查看帮助。\n"
    prompt = "thecvf>"
    __menu_list = None

    def preloop(self):
        with open("menu.json", "r") as f:
            self.__menu_list = json.load(f)

    def do_crawler(self, arg):
        """
        爬取论文信息
        :param arg: 即将爬取的目录+年份(如CVPR2021)
        :return: 无
        """
        if arg is not None and len(arg) > 0:
            for target in self.__menu_list:
                # 打印待爬取信息
                sub_path = target["path"]
                if sub_path != arg:
                    continue
                print(target)
                # 如文件夹不存在则创建
                if not os.path.exists(sub_path):
                    os.makedirs(sub_path)
                logfile = target["logfile"]
                target_url_list = target["links"]
                for target_url in target_url_list:
                    # 爬取论文链接
                    if sub_path.startswith("ECCV"):
                        paper_list = request_eccv_paper_list(target_url, year=sub_path)
                    elif sub_path.startswith("NeurIPS"):
                        paper_list = request_nips_paper_list(target_url, year=sub_path)
                    elif sub_path.startswith("ICML"):
                        paper_list = request_icml_paper_list(target_url, year=sub_path)
                    else:
                        paper_list = request_paper_list(target_url)
                    # 记录论文信息到日志文件
                    fn = os.path.join(sub_path, logfile)
                    export_jsonl(paper_list, fn)
                    export_url(paper_list, fn.replace("jsonl", "txt"))
        else:
            for target in self.__menu_list:
                # 打印待爬取信息
                print(target)
                sub_path = target["path"]
                # 如文件夹不存在则创建
                if not os.path.exists(sub_path):
                    os.makedirs(sub_path)
                logfile = target["logfile"]
                target_url_list = target["links"]
                for target_url in target_url_list:
                    # 爬取论文链接
                    if sub_path.startswith("ECCV"):
                        paper_list = request_eccv_paper_list(target_url, year=sub_path)
                    else:
                        paper_list = request_paper_list(target_url)
                    # 记录论文信息到日志文件
                    fn = os.path.join(sub_path, logfile)
                    export_jsonl(paper_list, fn)
                    export_url(paper_list, fn.replace("jsonl", "txt"))

    def do_download(self, arg):
        """
        下载论文
        输入期望下载的目录名称，例如 CVPR2021
        注意: 未输入任何名称时，将全部下载
        :param arg: 即将下载的目录名称
        :return: 无
        """
        if arg is not None and len(arg) > 0:
            for paper in self.__menu_list:
                paper_path = paper["path"]
                if paper_path != arg:
                    continue
                paper_jsonl = paper["logfile"]
                print(f"download {paper_path}")
                with open(f"{paper_path}/{paper_jsonl}", "r") as f:
                    rows = f.readlines()
                    for r in rows:
                        obj = json.loads(r)
                        downloader(obj["pdf_url"], paper_path)
        else:
            for paper in self.__menu_list:
                paper_path = paper["path"]
                paper_jsonl = paper["logfile"]
                print(f"download {paper_path}")
                with open(f"{paper_path}/{paper_jsonl}", "r") as f:
                    rows = f.readlines()
                    for r in rows:
                        obj = json.loads(r)
                        downloader(obj["pdf_url"], paper_path)
        pass

    def do_clean(self, arg):
        """
        清理目录
        输入期望清理的目录名称，例如 CVPR2021
        注意: 未输入任何名称时，将全部清理
        :param arg: 即将清理的目录名称
        :return: 无
        """
        if arg is not None and len(arg) > 0:
            for paper in self.__menu_list:
                path = paper["path"]
                if path != arg:
                    continue
                os.system(f"rm -rf {path}")
                print(f"remove {path}")
        else:
            for paper in self.__menu_list:
                path = paper["path"]
                os.system(f"rm -rf {path}")
                print(f"remove {path}")
        pass

    def do_exit(self, _):
        """
        退出命令行
        :param _: 无需输入参数
        :return: 无
        """
        exit(0)


if __name__ == '__main__':
    CLI().cmdloop()
    pass
