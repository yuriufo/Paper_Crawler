import os
import re
import time
import json

from configparser import ConfigParser
from collections import defaultdict

import arxiv

cwd = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.abspath(os.path.join(cwd, '..', 'config.ini'))

config = ConfigParser()
config.read(config_path)

sort_by_dict = {'relevance': arxiv.SortCriterion.Relevance,
                'lastUpdatedDate': arxiv.SortCriterion.LastUpdatedDate,
                'submittedDate': arxiv.SortCriterion.SubmittedDate}

sort_order_dict = {'descending': arxiv.SortOrder.Descending,
                    'ascending': arxiv.SortOrder.Ascending}


def load_set(subject):
    arxiv_db_path = os.path.abspath(os.path.join(cwd, '..', 'arXiv_db', subject))
    arxiv_db_set = os.path.join(arxiv_db_path, 'db.txt')
    if not os.path.exists(arxiv_db_path):
        # 第一次运行
        os.makedirs(arxiv_db_path)
        return set(), arxiv_db_path
    elif not os.path.exists(arxiv_db_set):
        return set(), arxiv_db_path
    else:
        # 读取已存在的
        with open(arxiv_db_set, "r") as f:
            tmp = json.loads(f.read())
        return set(tmp), arxiv_db_path


def load_markdown(markdown_fp):
    with open(markdown_fp, "r", encoding='utf-8') as f:
        raw_markdown = f.read()

    prog = re.compile('<summary>(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - (.*)<\/summary>\n\n- \*(.+)\*\n\n- `(.+)`.* \[pdf\]\((.+)\)\n\n> (.+)\n\n<\/details>')
    matches = prog.findall(raw_markdown)

    results = []

    for result in matches:
        ori = {}
        ori['title'] = result[1]
        ori['authors'] = result[2].split(', ')
        ori['updated_sorted'] = time.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        ori['updated'] = result[0]
        ori['summary'] = result[5]
        ori['pdf_url'] = result[4]
        ori['short_id'] = result[3]
        results.append(ori)
    return results


def crawler(query,
            sort_by,
            sort_order,
            page_size,
            subjectcategory,
            max_results=float('inf')):
    # 参数处理
    query = json.loads(query)
    subjectcategory = json.loads(subjectcategory)
    max_results = int(max_results) if isinstance(max_results, str) else max_results

    # client配置,每5秒一个API请求,出错重试5次
    client = arxiv.Client(
        page_size=int(page_size),
        delay_seconds=5,
        num_retries=5
    )

    for subject, key_words in query.items():
        query_results = defaultdict(list)
        db_set, arxiv_db_path = load_set(subject)

        # 每个关键字一个查询请求
        for key_word in key_words:
            search = arxiv.Search(
                query=key_word,
                max_results=max_results,
                sort_by=sort_by_dict[sort_by],
                sort_order=sort_order_dict[sort_order]
            )

            try:
                for result in client.get(search):
                    # 是否在指定的类别内
                    for cate in result.categories:
                        if cate in subjectcategory:
                            break
                    else:
                        continue

                    # 数据库中是否已存在
                    short_id = result.get_short_id()
                    if short_id in db_set:
                        continue
                    db_set.add(short_id)

                    year = result.updated.tm_year
                    ori = dict()
                    ori['title'] = result.title
                    ori['authors'] = [author.name for author in result.authors]
                    ori['updated_sorted'] = result.updated
                    # ori['published'] = time.strftime('%Y-%m-%d %H:%M:%S', result.published)
                    ori['updated'] = time.strftime('%Y-%m-%d %H:%M:%S', result.updated)
                    ori['summary'] = result.summary.replace('\n', ' ')
                    # ori['comment'] = result.comment
                    # ori['primary_category'] = result.primary_category
                    # ori['categories'] = result.categories
                    ori['pdf_url'] = result.get_pdf_url()
                    ori['short_id'] = result.get_short_id()
                    query_results[year].append(ori)
            except arxiv.UnexpectedEmptyPageError:
                print(f"{subject}--{key_word}: arxiv.UnexpectedEmptyPageError")
            except arxiv.HTTPError:
                print(f"{subject}--{key_word}: arxiv.HTTPError")
            except Exception as error:
                print(f"{subject}--{key_word}: {error}")

        # 解析存储结果
        for year, results in query_results.items():
            markdown_fp = os.path.join(arxiv_db_path, f'{year}.md')
            if os.path.exists(markdown_fp):
                old_results = load_markdown(markdown_fp)
                query_set = set([item['short_id'] for item in old_results])
                for item in results:
                    if item['short_id'] not in query_set:
                        old_results.append(item)
                results = old_results
            results = sorted(results, key=lambda item: item['updated_sorted'])

            markdown = []
            markdown.append(f"# {year}\n")

            toc = []
            content = defaultdict(list)
            for result in results:
                ym = result['updated'].rsplit('-', 1)[0]
                if ym not in toc:
                    toc.append(ym)
                paper = f"<details>\n\n<summary>{result['updated']} - {result['title']}</summary>\n\n" \
                        f"- *{', '.join(result['authors'])}*\n\n" \
                        f"- `{result['short_id']}` - [abs](http://arxiv.org/abs/{result['short_id']}) - [pdf]({result['pdf_url']})\n\n" \
                        f"> {result['summary']}\n\n" \
                        f"</details>\n\n"
                content[ym].append(paper)

            markdown.append("## TOC\n")
            toc = sorted(toc)
            markdown.append("\n".join([f"- [{t}](#{t})" for t in toc])+'\n')

            for ym, papers in content.items():
                markdown.append(f"## {ym}\n")
                markdown.append("".join(papers))

            with open(markdown_fp, "w", encoding='utf-8') as f:
                f.write("\n".join(markdown))

        if len(query_results) > 0:
            with open(os.path.join(arxiv_db_path, 'db.txt'), "w") as f:
                db_str = json.dumps(list(db_set))
                f.write(db_str)


if __name__ == '__main__':
    crawler(**dict(config.items("arXiv")))
