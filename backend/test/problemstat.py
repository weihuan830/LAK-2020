import math
import os
import json
from readdata import readDataObj
roi_config = {
    "blursize": 3,
    "filterval": 0.022,
    "rectsize": 4,
    "basefilterval": 0.082,
    "cellRadius": 4,
    "lowerThresh": 82,
    "upperThresh": 41,
    "cellCoef": 3
}
validSetCenterSize = []
validSetCenter = []

def _setImportantArea(problemid, result):
    with open("./allproblemcache/"+problemid+"/"+"tmp", "w+") as f:
        json.dump(result, f)

def render (problemid, data):
    gaussData = gaussFilter(roi_config["blursize"], data)
    rectarr = rawToBox(roi_config["rectsize"], gaussData)
    filterSet = detectObject(selectValid(roi_config["filterval"], rectarr))
    baseFilterSet = {}
    baseFilterSet = selectValid(roi_config["basefilterval"], rectarr)
    for key in baseFilterSet:
        baseFilterSet[key] = minCenterDistance(key)
    countObjectSize(baseFilterSet)
    _setImportantArea(problemid, { "data": baseFilterSet, "scale": roi_config["rectsize"], "config": roi_config })

def countObjectSize (baseFilterSet):
    localmax = 0
    for key in baseFilterSet:
        if baseFilterSet[key] > localmax:
            localmax = baseFilterSet[key]
    validSetCenterSize = [0] * (localmax+1)
    for key in baseFilterSet:
        validSetCenterSize[baseFilterSet[key]] += 1

def minCenterDistance (key):
    x = int(key.split('_')[0])
    y = int(key.split('_')[1])
    localmin = 100000000
    index = 0
    for i in range(0, len(validSetCenter)):
        tmp = (x - validSetCenter[i][0])**2 + (y - validSetCenter[i][1])**2
        if tmp < localmin:
            localmin = tmp
            index = i
    return index

def detectObject (filterSet):
    dealed = {}
    index = 0
    def recuDetect (sideset, currentSector, localindex):
        for i in range(0, len(sideset)):
            if not sideset[i] in filterSet and not currentSector[sideset[i]]:
                dealed[sideset[i]] = localindex
                currentSector[sideset[i]] = 1
                x = int(sideset[i].split('_')[0])
                y = int(sideset[i].split('_')[1])
                points = [str(x - 1) + '_' + str(y - 1), str(x) + '_' + str(y - 1), str(x + 1) + '_' + str(y - 1), str(x - 1) + '_' + str(y), str(x + 1) + '_' + str(y), str(x - 1) + '_' + str(y + 1), str(x) + '_' + str(y + 1), str(x + 1) + '_' + str(y + 1)]
                recuDetect(points, currentSector, localindex)

    for key in filterSet:
        if  not key in dealed:
            currentSector = {}
            sumx = 0
            sumy = 0
            recuDetect([key], currentSector, index)
            curlen = len(currentSector.keys())
            if curlen > 5:
                for key in currentSector:
                    sumx += int(key.split('_')[0])
                    sumy += int(key.split('_')[1])
                validSetCenter.append([sumx / float(curlen), sumy / float(curlen)])
                index += 1
    return dealed

def rawToBox (rectsize, data):
    rectData = []
    wi = int(len(data) / rectsize)
    hi = int(len(data[0]) / rectsize)
    for i in range(0, wi): # (let i = 0; i < wi; i++) {
        tmp = []
        for t in range(0, hi): #(let t = 0; t < hi; t++) {
            sm = 0
            basex = i * rectsize
            basey = t * rectsize
            for x in range(0, rectsize):
                for y in range(0, rectsize):
                    try:
                        sm += data[x + basex][y + basey]
                    except:
                        pass
            tmp.append(sm)
        rectData.append(tmp)
    return normalize(rectData)

def normalize (arr):
    maxvalue = 0
    for i in range(0, len(arr)):
        for t in range(0, len(arr[0])):
            if arr[i][t] > maxvalue:
                maxvalue = arr[i][t]
    for i in range(0, len(arr)):
        for t in range(0, len(arr[i])):
            arr[i][t] = arr[i][t] / float(maxvalue)
    return arr

def selectValid (threshold, arr):
    localset = {}
    for i in range(0, len(arr)):
        for t in range(0, len(arr[i])):
            if arr[i][t] >= threshold:
                localset[str(i) + '_' + str(t)] = 1
    return localset

def gaussFilter (blursize, arr):
    newarr = []
    blursqr = float(blursize * blursize)
    for i in range(0, len(arr)):
        tmp = []
        for t in range(0, len(arr[i])):
            avg = arr[i][t]
            for x in range(i - blursize, i + blursize):
                for y in range(t - blursize, t + blursize):
                    if x >= 0 and y >= 0 and x < len(arr) and y < len(arr[i]):
                        avg += arr[x][y]
            tmp.append(avg / blursqr)
        newarr.append(tmp)
    return newarr


def readDir():
    pid = os.listdir("./allproblemcache")
    recProblemSet = readDataObj.recentProblems
    print("total", len(recProblemSet.keys()))
    for idindex in range(68, len(pid)):
        problemid = pid[idindex]
        if problemid in recProblemSet:
            try:
                with open("./allproblemcache/" + problemid+"/problemsequence", "r") as f:
                    tmpdata = json.loads(f.readline().replace("'","\""))
                    render(problemid, tmpdata["data"])
                    print(problemid)
            except:
                print(problemid, "failed")
readDir()