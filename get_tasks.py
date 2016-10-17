#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# (C) Copyright 2015 Jaidev Deshpande
# All right reserved.
#

"""

"""

from todoist import TodoistAPI
import os
import pandas as pd
import tempfile
from tqdm import tqdm

RECURRING_PREFIXES = "every weekly yearly monthly".split()


def get_raw_items():
    api = TodoistAPI(os.environ['TODOIST_SECRET'], cache=tempfile.mkdtemp())
    syncresp = api.sync()
    print "Synced!"
    history = get_history(api)
    items = syncresp['items']  # this is the current items var
    return items, history, api


def is_recurring(item):
    date_string = item.get('date_string', "")
    if date_string:
        for prefix in RECURRING_PREFIXES:
            if date_string.startswith(prefix):
                return True
    return False


def get_history(api):
    offset = 0
    batch_tasks = api.completed.get_all(limit=50, offset=offset)['items']
    task_accumulator = batch_tasks
    while len(batch_tasks) == 50:
        offset += 1
        batch_tasks = api.completed.get_all(limit=50,
                offset=(50 * offset))['items']
        task_accumulator.extend(batch_tasks)
    return task_accumulator


def write_csv(fname="tasks.tsv"):
    items, history, api = get_raw_items()

    for task in tqdm(history):
        payload = api.items.get(task['id'])
        if payload is None:
            task['is_deleted'] = 1
            payload = task
        else:
            payload = payload['item']
            payload['is_deleted'] = 0
        payload['is_recurring'] = is_recurring(payload)
        items.append(payload)  # this the the completed items var

    df = pd.DataFrame.from_records(items)
    df['is_deleted'] = df['is_deleted'].astype(bool)
    df.to_csv(fname, sep="\t", encoding='utf-8', index=False)

if __name__ == '__main__':
    write_csv()
