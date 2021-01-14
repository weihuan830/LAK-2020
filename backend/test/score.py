import database
import readdata
import json
problemarray = ["20x746187641c59c168", "22x9b87945d0701947f", "42xee63922e8a2e1ec7", "49xdc32850876d23639", "51x079fb52f20782c91"]
problemid = problemarray[3]
def _getUserSequenceByProblem():
    result = database.userSequenceByProblemByEventTime(problemid)
    data = []
    print("search end")
    for userdata in result:
        count = 0
        for item in userdata["data"]:
            if item['type'] == "mousedown" or item["type"] == "mouseup":
                count += 1
        data.append({"userid":userdata["_id"], "score":readdata.getScoreByID(userdata["_id"],problemid),"spant":count})
    data = sorted(data, key=lambda x: x["spant"])
    with open("./result/userproblemsequence", "w+") as f:
        f.write(str({"data":data}))
    return str({"data":data})

def _labelUserWithProblemType():
    users = {}
    with open("../datafile/records_dt.csv", "r") as f:
        tmp = f.readlines()
        for item in tmp:
            arr = item.split(",")
            if not arr[0] in users:
                users[arr[0]] = {}
            if arr[1] in readdata.question:
                pid = readdata.question[arr[1]][0]
                ptypes = readdata.question[pid]
                if len(ptypes) > 1:
                    for tp in ptypes[1:len(ptypes)]:
                        if tp in users[arr[0]]:
                            users[arr[0]][tp]["sequence"].append([pid, arr[2], arr[3].replace("\n","")])
                            users[arr[0]][tp]["count"] += 1
                        else:
                            users[arr[0]][tp] = {"count":1, "sequence": [[pid, arr[2], arr[3].replace("\n","")]]}
    ptypes= ["numeric","spatial", "measures","data-handling","geometric", "algebraic"]
    ''' problemType-user-count sorted  count>100'''
    # for item in ptypes:
    #     tmparr = []
    #     for u in users:
    #         if item in users[u]:
    #             tmparr.append([u, users[u][item]["count"]])
    #     tdata = sorted( (item for item in tmparr if item[1] > 100), key=lambda x: x[1], reverse=True)
    #     with open("./result/seq_user_"+ item +".txt","w+") as f:
    #         f.write(str(tdata))
    '''problemType-user-sequence(pid, score, date) sorted count>100'''
    # for item in ptypes:
    #     tmparr = []
    #     for u in users:
    #         if item in users[u]:
    #             tmparr.append([u, users[u][item]["count"], users[u][item]["sequence"]])
    #     tdata = sorted( (item for item in tmparr if item[1] > 100), key=lambda x: x[1], reverse=True)
    #     for uindex in range(len(tdata)):
    #         index = 1
    #         while True:
    #             if index >= len(tdata[uindex][2]):
    #                 break
    #             if tdata[uindex][2][index][0] == tdata[uindex][2][index-1][0]:
    #                 if int(tdata[uindex][2][index][1]) > int(tdata[uindex][2][index-1][1]):
    #                     del tdata[uindex][2][index-1]
    #                 else:
    #                     del tdata[uindex][2][index]
    #             else:
    #                 index+=1
    #     with open("./result/seq_user_"+ item +".json","w+") as f:
    #         f.write(str(tdata).replace("'","\""))
    '''Full seq without type '''
    # userseq = {}
    # with open("../datafile/records_dt.csv", "r") as f:
    #     tmp = f.readlines()
    #     for item in tmp:
    #         arr = item.split(",")
    #         if not arr[0] in userseq:
    #             userseq[arr[0]] = []
    #         if arr[1] in readdata.question:
    #             pid = readdata.question[arr[1]][0]
    #             userseq[arr[0]].append([pid, arr[2], arr[3].replace("\n","")])
    #         else:
    #             userseq[arr[0]] = [[pid, arr[2], arr[3].replace("\n","")]]
    # for us in userseq:
    #     index = 0
    #     while True:
    #         if index >= len(userseq[us]):
    #             break
    #         if userseq[us][index][0] == userseq[us][index-1][0]:
    #             if int(userseq[us][index][1]) > int(userseq[us][index-1][1]):
    #                 del userseq[us][index-1]
    #             else:
    #                 del userseq[us][index]
    #         else:
    #             index += 1
    # tmp = {}
    # for item in userseq:
    #     if len(userseq[item]) > 100:
    #         tmp[item] = userseq[item]
    # with open("full.json", "w+") as f:
    #     f.write(json.dumps(userseq))
    '''problem solving sequence difficulty level std-var'''
    userseq = {}
    with open("../datafile/records_dt.csv", "r") as f:
        tmp = f.readlines()
        for item in tmp:
            arr = item.split(",")
            if not arr[0] in userseq:
                userseq[arr[0]] = []
            if arr[1] in readdata.question:
                pid = readdata.question[arr[1]][0]
                userseq[arr[0]].append([pid, arr[2], arr[3].replace("\n","")])
            else:
                userseq[arr[0]] = [[pid, arr[2], arr[3].replace("\n","")]]
    for us in userseq:
        index = 0
        while True:
            if index >= len(userseq[us]):
                break
            if userseq[us][index][0] == userseq[us][index-1][0]:
                if int(userseq[us][index][1]) > int(userseq[us][index-1][1]):
                    del userseq[us][index-1]
                else:
                    del userseq[us][index]
            else:
                index += 1
    tmp = {}
    for item in userseq:
        if len(userseq[item]) > 50:
            for d in userseq[item]:
                if d[0] in tmp:
                    tmp[d[0]]["seq"].append(d[1])
                    tmp[d[0]]["user"].append(item)
                elif d[0] in readdata.question:
                    tmp[d[0]] = {
                        "level": readdata.localquestion["questionData"][str(readdata.question[d[0]][0])]["difficulty"],
                        "seq":[d[1]],
                        "user":[item]
                    }
    lt = {}
    for item in tmp:
        if len(tmp[item]["seq"]) > 100:
            lt[item] = tmp[item]
    with open("./result/pseqdiff.json", "w+") as f:
        f.write(json.dumps(lt))
_labelUserWithProblemType()
