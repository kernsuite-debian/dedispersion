#!/usr/bin/env python
# Copyright 2014 Alessio Sclocco <a.sclocco@vu.nl>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import manage

def statistics(queue, table, scenario, flags):
    confs = list()
    dms_range = manage.get_dm_range(queue, table, scenario)
    for dm in dms_range:
        if flags[0]:
            queue.execute("SELECT MIN(GFLOPs),AVG(GFLOPs),MAX(GFLOPs),STDDEV_POP(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 1)")
        elif flags[1]:
            queue.execute("SELECT MIN(GFLOPs),AVG(GFLOPs),MAX(GFLOPs),STDDEV_POP(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 0)")
        else:
            queue.execute("SELECT MIN(GFLOPs),AVG(GFLOPs),MAX(GFLOPs),STDDEV_POP(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND "  + scenario + ")")
        line = queue.fetchall()
        confs.append([dm[0], line[0][0], line[0][2], line[0][1], line[0][3], (line[0][2] - line[0][1]) / line[0][3]])
    return confs

def histogram(queue, table, scenario, flags):
    hists = list()
    dms_range = manage.get_dm_range(queue, table, scenario)
    for dm in dms_range:
        if flags[0]:
            queue.execute("SELECT MAX(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 1)")
        elif flags[1]:
            queue.execute("SELECT MAX(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 0)")
        else:
            queue.execute("SELECT MAX(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ")")
        maximum = int(queue.fetchall()[0][0])
        hist = [0 for i in range(0, maximum + 1)]
        if flags[0]:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 1)")
        elif flags[1]:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + "  AND local = 0)")
        else:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ")")
        flops = queue.fetchall()
        for flop in flops:
            hist[int(flop[0])] = hist[int(flop[0])] + 1
        hists.append(hist)
    return hists

def optimization_space(queue, table, scenario, flags):
    confs = list()
    dms_range = manage.get_dm_range(queue, table, scenario)
    for dm in dms_range:
        if flags[0]:
            queue.execute("SELECT local,nrThreadsD0,nrThreadsD1,nrItemsD0,nrItemsD1,GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 1)")
        elif flags[1]:
            queue.execute("SELECT local,nrThreadsD0,nrThreadsD1,nrItemsD0,nrItemsD1,GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND local = 0)")
        else:
            queue.execute("SELECT local,nrThreadsD0,nrThreadsD1,nrItemsD0,nrItemsD1,GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ")")
        best = queue.fetchall()
        confs.append([best[0][0], best[0][1], best[0][2], best[0][3], best[0][4], best[0][5]])
    return confs

def percentiles(queue, table, scenario, flags):
    results = list()
    condition = str()
    if flags[0] == 1:
        condition = "local = 1"
    elif flags[0] == 2:
        condition = "local = 0"
    if flags[1] == 1:
        if flags[0] != 0:
            condition += " AND splitBatches = 1"
        else:
            condition = "splitBatches = 1"
    elif flags[1] == 2:
        if flags[0] != 0:
            condition += " AND splitBatches = 0"
        else:
            condition = "splitBatches = 0"
    dms_range = manage.get_dm_range(queue, table, scenario)
    for dm in dms_range:
        internalResults = list()
        internalResults.append(dm[0])
        if flags[0] == 0 and flags[1] == 0:
            queue.execute("SELECT COUNT(id),MIN(GFLOPs),MAX(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ")")
        else:
            queue.execute("SELECT COUNT(id),MIN(GFLOPs),MAX(GFLOPs) FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND " + condition + ")")
        items = queue.fetchall()
        nrItems = items[0][0]
        internalResults.append(int(items[0][1]))
        internalResults.append(int(items[0][2]))
        if flags[0] == 0 and flags[1] == 0:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ") ORDER BY GFLOPs LIMIT " + str(int(nrItems / 4))  + ",1")
        else:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND " + condition + ") ORDER BY GFLOPs LIMIT " + str(int(nrItems / 4))  + ",1")
        items = queue.fetchall()
        internalResults.append(int(items[0][0]))
        if flags[0] == 0 and flags[1] == 0:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ") ORDER BY GFLOPs LIMIT " + str((int(nrItems / 4)) * 2)  + ",1")
        else:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND " + condition + ") ORDER BY GFLOPs LIMIT " + str((int(nrItems / 4)) * 2)  + ",1")
        items = queue.fetchall()
        internalResults.append(int(items[0][0]))
        if flags[0] == 0 and flags[1] == 0:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + ") ORDER BY GFLOPs LIMIT " + str((int(nrItems / 4)) * 3)  + ",1")
        else:
            queue.execute("SELECT GFLOPs FROM " + table + " WHERE (DMs = " + str(dm[0]) + " AND " + scenario + " AND " + condition + ") ORDER BY GFLOPs LIMIT " + str((int(nrItems / 4)) * 3)  + ",1")
        items = queue.fetchall()
        internalResults.append(int(items[0][0]))
        results.append(internalResults)
    return results

