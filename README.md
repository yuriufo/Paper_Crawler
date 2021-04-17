<h1 align="center">Paper_Crawler</h1>
<p align="center">
    <img src="https://img.shields.io/badge/python-3.8-blue"/>
    <img src="https://img.shields.io/github/stars/yuriufo/Paper_Crawler.svg"/>  
    <img src="https://img.shields.io/github/forks/yuriufo/Paper_Crawler.svg"/> 
    <img src="https://img.shields.io/github/issues/yuriufo/Paper_Crawler.svg"/> 
    <img src="https://img.shields.io/github/license/yuriufo/Paper_Crawler.svg"/> 
</p>
<p align="center">
    <img src="https://img.shields.io/github/repo-size/yuriufo/Paper_Crawler.svg"/>
    <img src="https://img.shields.io/github/commit-activity/m/yuriufo/Paper_Crawler.svg"/>
    <img src="https://img.shields.io/github/last-commit/yuriufo/Paper_Crawler.svg"/>
</p>



> 从各大学术搜索平台上爬论文信息
> 
> 使用GitHub Actions定时爬取

## Usage

### 1. fork或clone到自己仓库中

### 2. 修改配置

修改`config.ini`中配置，其中：
  - `page_size`: 每次API请求论文数
  - `query`: 键为**主题类别**，值为**关键字(列表)**
  - `sort_by`: 排序方式
  - `sort_order`: 升序或降序
  - `subjectcategory`: 主题(默认已选择部分与安全相关的主题)

### 3. 爬取数据

每次`push`或每天在国际标准时间22点（北京时间早上6点）运行。

数据存储在`./*_db`下。

## Currently Supports 

- [x] arXiv

## Reference

- https://github.com/lukasschwab/arxiv.py
