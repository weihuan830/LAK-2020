import json
from pathlib import Path
import os,sys,re
import database
from readdata import readDataObj
import statistics
from scipy.stats import skew
import math
from scipy.stats import iqr
from datetime import datetime

class dataProcessor:
    keys = []
    def _avgTimeMouseDensity(self, sequence):
        count = 0
        for item in sequence:
            if item[3] != "mousemove":
                count += 1
        t = (sequence[len(sequence)-1][4] - sequence[0][4])
        if t == 0:
            return 0
        return count

    def _highDensityDetect(self, userseq, minwindow, threshold):
        step = minwindow
        avg = (self._avgTimeMouseDensity(userseq) / len(userseq)) * ( threshold/10 )
        flag = True
        startindex = 0
        endindex = 0
        lastden = 0
        for i in range(0, len(userseq)-(step+1) ):
            tmpden = self._avgTimeMouseDensity(userseq[i:i+step])/float(step)
            if flag:
                if tmpden >= avg:
                    startindex = i
                    flag = False
                    lastden = tmpden
            else:
                if lastden < avg:
                    return startindex,endindex
                else:
                    lastden = tmpden
                    endindex = i+step
        if startindex != 0:
            return startindex, len(userseq)-1
        return -1,-1

    def _gapDetecter(self, userseq, timestep):
        gapindex = []
        for i in range(0, len(userseq)):
            if userseq[i][2] > timestep:
                gapindex.append(i)
        gapindex.append(len(userseq))
        return gapindex

    def _gapSpliter(self, userseq, timestep):
        sequenceIndex = []
        gapindex = self._gapDetecter(userseq, timestep)
        for i in range(0,len(gapindex)):
            if i == 0:
                sequenceIndex.append([0, gapindex[i]])
            else:
                sequenceIndex.append([gapindex[i-1], gapindex[i]])
        return sequenceIndex

    def _mousemoveSpliter(self, userseq, indexlist):
        mousemove = []
        flag = True
        for index in indexlist:
            seq = userseq[index[0]:index[1]]
            lasindex = index[0]
            for i in range(len(seq)):
                if seq[i][3] != "mousemove":
                    if flag == False:
                        continue
                    mousemove.append([lasindex, i + index[0]])
                    flag = False
                else:
                    if flag == False:
                        lasindex = i + index[0]
                    flag = True
            if lasindex < index[1]:
                mousemove.append([lasindex, index[1]])
        return mousemove

    def _matchSeqScore(self, pid, sequencelist):
        userid = sequencelist[0]['userid']
        if userid in readDataObj.aprilScore:
            if pid in readDataObj.aprilScore[userid]:
                timeIndex = []
                for index in range(len(sequencelist)):
                    # print(sequencelist[index])
                    timeIndex.append([sequencelist[index]["sequence"][-1][5], index])
                userdt = readDataObj.aprilScore[userid][pid]
                for item in userdt:
                    timeIndex.append([item[2], -1, item[1]])
                tmp = sorted(timeIndex, key=lambda x: x[0])
                indexScore = []
                for index in range(len(tmp)):
                    if tmp[index][1] == -1:
                        indexScore.append([tmp[index-1][1], tmp[index][2]])
                return indexScore
        return None

    def _splitBytime(self, pid, userid, sequence):
        # split sequences by score time
        scoresubmitgap = []
        seqinfo = []
        if userid in readDataObj.aprilScore:
            if pid in readDataObj.aprilScore[userid]:
                for scoretime in readDataObj.aprilScore[userid][pid]:
                    if scoretime[2] < sequence[0][5]:
                        continue
                    for index in range(len(sequence)):
                        if scoretime[2] < sequence[index][5]:
                            scoresubmitgap.append(index)
                            seqinfo.append(scoretime)
                            break
                        if index == len(sequence) - 1:
                            seqinfo.append(scoretime)
                            scoresubmitgap.append(len(sequence))
        return scoresubmitgap,seqinfo

    def _minsequence(self, problemid, lid, tmp, finalSeq):
        tmpdata,seqinfo = self._splitBytime(problemid, lid, tmp)
        if len(tmpdata) != 0:
            last = 0
            for index in range(len(tmpdata)):
                finalSeq.append([ [ lid ] + seqinfo[index] ] + tmp[last:tmpdata[index]])
                last = tmpdata[index]

    def extractDragSeg(self, sequence):
        arr = []
        downindex = -1
        for index in range(len(sequence)):
            if sequence[index][3] == "mousedown":
                downindex = index
            elif downindex != -1 and sequence[index][3] == "mouseup":
                arr.append((downindex, index))
                downindex = -1
        return arr

    def DragSegMSS(self, indexlist, sequence):
        directDistance = []
        segDistance = []
        segTime = []
        K = []
        timeBetween = [indexlist[0][0]]
        for i in range(1, len(indexlist)-1):
            timeBetween.append(indexlist[i][0] - indexlist[i-1][1])
        for item in indexlist:
            segTime.append(sequence[item[1]][4] - sequence[item[0]][4] + 0.1)
            tmpSegDistance = 0.0001
            for i in range(item[0], item[1]):
                tmpSegDistance += math.sqrt((sequence[i][0] - sequence[i+1][0])**2 + (sequence[i][1] - sequence[i+1][1])**2)
            segDistance.append(tmpSegDistance)
            dirD = math.sqrt((sequence[item[0]][0] - sequence[item[1]][0])**2 + (sequence[item[0]][1] - sequence[item[1]][1])**2)
            directDistance.append(dirD)
            K.append(dirD/tmpSegDistance)
        speed1 = []
        speed2 = []
        for index in range(len(directDistance)):
            speed1.append(segDistance[index]/segTime[index])
            speed2.append(directDistance[index]/segTime[index])
        return [self.caMSS(directDistance), self.caMSS(segDistance), self.caMSS(K), self.caMSS(segTime), self.caMSS(timeBetween)]
    
    def DistanceK(self, sequence):
        item = [0, len(sequence)-2]
        curveSegDistance = 0
        directDistance = 0
        for i in range(item[0], item[1]):
            curveSegDistance += math.sqrt((sequence[i][0] - sequence[i+1][0])**2 + (sequence[i][1] - sequence[i+1][1])**2)
        directDistance = math.sqrt((sequence[item[0]][0] - sequence[item[1]][0])**2 + (sequence[item[0]][1] - sequence[item[1]][1])**2)
        K = directDistance/curveSegDistance
        return K, curveSegDistance, directDistance

    def caMSS(self, datalist):
        Mean = statistics.mean(datalist)
        if len(datalist) == 1:
            datalist = datalist + datalist
        Std = statistics.variance(datalist)
        Skw = skew(datalist)
        return [ Mean, Std, Skw, statistics.median(datalist), iqr(datalist) ]

    def clickStats(self, sequence):
        timeBetween = []
        for index in range(len(sequence)):
            if sequence[index][3] == "mousedown":
                timeBetween.append(sequence[index][4])
            elif sequence[index][3] == "mouseup":
                timeBetween.append(sequence[index][4])
        for i in range(0, len(timeBetween)):
            timeBetween[i]
        timeList = []
        i = 0
        while i < len(timeBetween)-2:
            timeList.append(timeBetween[i+1] - timeBetween[i])
            i += 2
        return self.caMSS(timeList), len(timeList)

    def AllDistance(self, sequence):
        item = [0, len(sequence)-2]
        AllDistance = 0
        for i in range(0, len(sequence)-1):
            AllDistance += math.sqrt((sequence[i][0] - sequence[i+1][0])**2 + (sequence[i][1] - sequence[i+1][1])**2)
        return AllDistance

    def MoveMentsMSS(self, sequence):
        secSpan = 1000
        maxv = max([item[4] for item in sequence])
        countList = [0] * int(maxv/secSpan+1)
        for item in sequence:
            countList[int(item[4]/secSpan)] += 1
        return self.caMSS(countList)

    def MoveMentsTakenMSS(self, sequence):
        values = []
        for index in range(1, len(sequence)):
            values.append(sequence[index][4] - sequence[index-1][4])
        return self.caMSS(values)

    def _readValidAreas(self, problemid, sequences):
        with open("./allproblemcache/"+ problemid +"/tmp") as f:
            tmp = f.readline()
        data = json.loads(tmp)
        start_drag = 0
        end_drag = 0
        for index in range(len(sequences)):
            if sequences[index][3] == 'mousedown':
                start_drag = index + 1
            elif sequences[index][3] == 'mouseup':
                end_drag = index + 1
                return start_drag, end_drag
        return -1,-1
    
    def _ifValidEvent(self, point, dataset):
        x = int(int(point[0])/dataset["scale"])
        y = int(int(point[1])/dataset["scale"])
        s = [str(x-1) + "_" + str(y-1), str(x-1) + "_" + str(y), str(x-1) + "_" + str(y+1), str(x) + "_" + str(y-1), str(x) + "_" + str(y), str(x) + "_" + str(y+1), str(x+1) + "_" + str(y-1), str(x+1) + "_" + str(y), str(x+1) + "_" + str(y+1)]
        for item in s:
            if item in dataset["data"]:
                return True
        return False

    def overlapByindex(self, index, problemid, sequence):
        with open("./allproblemcache/"+ problemid +"/tmp") as f:
            tmp = f.readline()
        data = json.loads(tmp)
        count = 0
        for item in range(0, index):
            if self._validArea(sequence[item], data):
                count += 1
        return count/index

    def step4overlapRate(self, problemid, sequence):
        with open("./allproblemcache/"+ problemid +"/tmp") as f:
            tmp = f.readline()
        data = json.loads(tmp)
        count = [0, 0, 0, 0]
        indexes = [0.1, 0.1, 0.1]
        for index in range(0, len(sequence)):
            if sequence[index][4] < 10000:
                indexes[0] += 1
                if self._ifValidEvent(sequence[index], data):
                    count[0] += 1
            elif sequence[index][4] < 20000:
                indexes[1] += 1
                if self._ifValidEvent(sequence[index], data):
                    count[1] += 1
            elif sequence[index][4] < 30000: 
                indexes[2] += 1
                if self._ifValidEvent(sequence[index], data):
                    count[2] += 1
            else:
                if self._ifValidEvent(sequence[index], data):
                    count[3] += 1
        return [ count[0]/indexes[0], (count[1] + count[0])/indexes[1], (count[0] + count[1] + count[2])/indexes[2], sum(count)/len(sequence) ]

    def _validArea(self, point, dataset):
        x = int(float(point[0])/dataset["scale"])
        y = int(float(point[1])/dataset["scale"])
        s = [str(x) + "_" + str(y)]
        for item in s:
            if item in dataset["data"]:
                return True
        return False

    def _write2File(self, data):
        l = []
        for item in data:
            l.append(list(item.values()))
        return l
        
    def userSequenceByProblem(self, problemid, threshold):
        print(problemid)
        my_file = Path("./dbcache/"+ problemid)
        result = []
        if my_file.is_file():
            with open("./dbcache/"+ problemid,"r") as f:
                result = json.loads(f.readline().replace("\n",""))
        else:
            return []
            print("No cached sequence data for " + problemid + ", querying from DB")
            result = database.userSequenceByProblemByEventTime(problemid)
            r = json.dumps(result)
            with open("./dbcache/"+ problemid,"w+") as f:
                f.write(r)
        finalSeq = []

        for item in result:
            if len(item["_id"].strip()) < 3:
                continue
            lid = re.split(r"[0]{3,}",item["_id"])[1]
            tmp = [ ]
            lasttime = float(item["data"][0]["time2"])
            lasttype = "mousemove"
            tid = lid+"_"+problemid
            if tid in readDataObj.recentScore:
                for t in item["data"]:
                    time2 = float(t["time2"])
                    if lasttime - time2 > 2000:
                        tmp = []
                    if t['time'] <= readDataObj.recentScore[tid][4]:
                        if t["type"] == "mousemove":
                            if lasttype == "mousedown":
                                tmp.append([ int(t["x"]), int(t["y"]), 0, "mousedrag", time2, t["time"]])
                            else:
                                tmp.append([ int(t["x"]), int(t["y"]), 0, "mousemove", time2, t["time"]])
                        elif t["type"] == "mouseup":
                                tmp.append([ int(t["x"]), int(t["y"]) , 0 , "mouseup", time2, t["time"]])
                                lasttype = "mousemove"
                        else:
                                tmp.append([ int(t["x"]), int(t["y"]) , 0 , "mousedown", time2, t["time"]])
                                lasttype = "mousedown"
                    else:
                        break
                    lasttime = time2
                        # self._minsequence(problemid, lid, tmp, finalSeq)
                finalSeq.append([ [lid, problemid, readDataObj.recentScore[tid][3], readDataObj.recentScore[tid][4] ] ] + tmp)
        data = []
        userlist = {}
        minwindow = 10

        for item in finalSeq:
            try:
                if len(item) > 20 and len(item[0]) > 1:
                    start_index,end_index = self._highDensityDetect(item[1:len(item)], minwindow, threshold)
                    if start_index <= 0 or end_index <= start_index:
                        continue
                    clicks,clkcount = self.clickStats(item[1:len(item)])
                    allDistance = self.AllDistance(item[1:len(item)])
                    
                    firstDragIndex, firstDragIndexEnd = self._readValidAreas(problemid, item[1:len(item)])
                    firstDrag_overlap = self.overlapByindex(firstDragIndex, problemid, item[1:len(item)])

                    dragSegIndex = self.extractDragSeg(item[1:len(item)])

                    FirstDragK = self.DistanceK(item[start_index:end_index+1])
                    drg = self.DragSegMSS(dragSegIndex, item[1:len(item)])
                    mv = self.MoveMentsMSS(item[1:len(item)])
                    mtt = self.MoveMentsTakenMSS(item[1:len(item)])
                    t = {
                        "ClickCounts": clkcount,
                        "ClicksPerSecond": clkcount/(item[len(item)-1][4] - item[1][4]),
                        "AvgtimeBtwClicks":clicks[0],
                        "AvgtimeMedian":clicks[3],
                        "AvgtimeStd":clicks[1],
                        "OverallDistance":allDistance,
                        
                            # first attempt
                            "waitTimeLength": item[start_index][4],
                            "waitTimePercent": item[start_index][4]/item[len(item)-1][4],
                            "waitTimeEventCount": start_index,
                            "waitTimeEventPercent": start_index/(len(item)-1),
                            "changePointEndEventCount": end_index, #########
                            "changePointTimeLength": item[end_index][4] - item[start_index][4], #########

                            # first click
                            "FirstDragPointTimeLength": item[firstDragIndex][4],
                            "FirstDragPointTimePercent": item[firstDragIndex][4]/item[len(item)-1][4],
                            "FirstDragPointEventCount": firstDragIndex,
                            "FirstDragPointEventPercent": firstDragIndex/(len(item)-1),
                            "FirstDragPointEndEventCount": firstDragIndexEnd, #########
                            "FirstDragTimeLength": item[firstDragIndexEnd][4] - item[firstDragIndex][4], #########
                            "FirstDragK": FirstDragK[0],
                            "FirstDragCurvature": FirstDragK[1],
                            "FirstDragDistance": FirstDragK[2],

                            "MedianDelta": drg[0][3], # straight-line distance traveled by themouse, between starting and end points, in counts;
                            "IQRDelta": drg[0][4],
                            "MeanDelta": drg[0][0],
                            "MedianD": drg[1][3], # total distance traveled by the mouseDrag;
                            "IQRD": drg[1][4],
                            "MeanD":drg[1][0],
                            "MedianT": mtt[3], # time taken to make a mouse movement in milliseconds;
                            "MeanT":mtt[0],
                            "IQRT": mtt[4],
                            "MedianK": drg[2][3], # mouse move-ment curvature, ranging from 0 to 1 (05looped, 15straight line);
                            "IQRK": drg[2][4],
                            "MeanK":drg[2][0],
                            "MedianIdle": drg[3][3], # time spent drag
                            "IQRIdle": drg[3][4],
                            "MeanIdle":drg[3][0],
                            "MedianL": drg[4][3], # time between drag
                            "IQRL": drg[4][4],
                            "MeanL":drg[4][0],
                            "MedianMovSec": mv[3],
                            "IQRMovSec": mv[4],
                            "MeanMovSec": mv[0],
                            "DragTimesCount": len(dragSegIndex),
                            "Totaltime": item[len(item)-1][4],
                            "TotalEventCount": len(item),
                            "score": int(item[0][2]),
                            "userid": item[0][0],
                            "problemid": problemid,
                            "date": str(datetime.fromtimestamp(int(item[0][3])))
                        }
                    data.append(t)
                    self.keys = list(t.keys())
            except:
                pass
        return self._write2File(data)

obj = dataProcessor()
ln = []

problems = os.listdir("allproblemcache")
solvedproblems = os.listdir("dbcache")
# for index in range(1100, len(problems)):
    # name = problems[index]

# v6_2 --- 91pb
# problems = ["3235x164c38f47660fe4e","3255xe8e88106b52395ca","3261x0c3c8d8a702b4bf0","3263x5377031ec1cfca6e","3265xdf2443849c08b8b4","3268xd8e228543fc52dd4","3300xa3737a4c89e4538e","3301x6aa270a5bf488ce8","3305x8805d572d4b2376d","3306x0c010ee944551c49","3307x1e4d9504c6f3512b","3350x5b5f1804f2cdad46","3359x7e1fcd6b5c174111","3369xa0b3f6f02f993e2e","3395x77fb9d95117be7d5","3541x594e58e3c07d7058","3604x43c402cd9efef8db","3605xbaca8aba24da500f","3608xd1c67ec2443b84ed","742xfe25658ddf3a7d34","2278xce3ae33f4268139d","2511x4c5d2065c326341f","2512x86e1d97952122cdc","2633x25eb47069b20e671","2636x2b9b45a262421f98","2637x52344b3c5c1515bd","2641x5b1d90f5d1caf093","2795xa5311e169451dcfa","2891xb2ba51bb0ec03ec8","2892x087fead617f76210","2924xfdf3b514c895a459","2937x735fd0dbd5acd2e2","2950x2742a2e850a9105d","3009xe9c71ac13121be1b","3012x53a9d7588d80ec34","3013xe7514618865a7669","3041x6fef3221cbcc5351","3057x71d5aecff7b71a7c","3172x781eae8c91cfff7d","3230x86ee36e71f81dd17","3232x57857a5924551a9c","3233xdd875c213d859caa","3234x54e2d1dee8210380","285x6eeef7326cbfb695","286xcd13ff515c507173","289xa752f6b4e48543e7","319x24764c5cc505303d","349x4aecce399718177f","362x8998029a8b586c6b","368xf906318b3b294499","370x03f60f03f00c3637","402xedecc233d6c00723","407xd249885044ba59fd","416x02cddacf8b76a66a","419x942b91dfd3afae17","486xf879455b68c3b6a0","491x7d0ae84dbae21f03","500x6634d130ec0c0b2a","528xa5473b71467bd990","547x3ff489c8af4013fc","553xccfb9018cb2b3eec","609x967a043f548ea820","613x759989fe586f46dd","633x1ab692c8ec6e65ad","639xd650387f6b816d9e","642x0c347e49cbdf8c29","646x180daed387427e18","2xbee2fdb4aec4e218","9x0bfe6a9e0082aa03","25x09b4b0ef20df9f68","31xc05d1c38b9d38ef1","33xa418919f3d8d497f","45xa3c07a492c5ef86a","46xc88699e39afc7b26","66x1bf324e1092671be","68xd38f0e67d5a609e4","69xb489aa790b565172","70xf28c26b89b726a9a","100xf32107109e4e182b","107x045caf5a7632eb3c","110x5cfffff1990fcf9b","130xbdfbf7a10b6a4ca3","132xb0e07a8168ff8bf6","164x862ed21e89633147","198x3be61ba1ee022265","200xf4ca90e4d35734d2","201xd66fa64e9b00f44f","218xf04372630df32ce3","230xaeae4e68ed0843e5","252x5e74ff51a4f3ad00","254x297ff4608968c6da"]

# v6_3 --- 61pb
# problems = ["3235x164c38f47660fe4e","3300xa3737a4c89e4538e","3301x6aa270a5bf488ce8","3307x1e4d9504c6f3512b","3350x5b5f1804f2cdad46","3359x7e1fcd6b5c174111","3369xa0b3f6f02f993e2e","3395x77fb9d95117be7d5","3541x594e58e3c07d7058","3604x43c402cd9efef8db","3605xbaca8aba24da500f","742xfe25658ddf3a7d34","2278xce3ae33f4268139d","2511x4c5d2065c326341f","2512x86e1d97952122cdc","2633x25eb47069b20e671","2637x52344b3c5c1515bd","2641x5b1d90f5d1caf093","2795xa5311e169451dcfa","2891xb2ba51bb0ec03ec8","2892x087fead617f76210","2924xfdf3b514c895a459","2950x2742a2e850a9105d","3009xe9c71ac13121be1b","3012x53a9d7588d80ec34","3013xe7514618865a7669","3041x6fef3221cbcc5351","3057x71d5aecff7b71a7c","3230x86ee36e71f81dd17","3233xdd875c213d859caa","285x6eeef7326cbfb695","286xcd13ff515c507173","289xa752f6b4e48543e7","349x4aecce399718177f","362x8998029a8b586c6b","370x03f60f03f00c3637","402xedecc233d6c00723","419x942b91dfd3afae17","486xf879455b68c3b6a0","491x7d0ae84dbae21f03","609x967a043f548ea820","613x759989fe586f46dd","639xd650387f6b816d9e","642x0c347e49cbdf8c29","2xbee2fdb4aec4e218","9x0bfe6a9e0082aa03","25x09b4b0ef20df9f68","31xc05d1c38b9d38ef1","45xa3c07a492c5ef86a","66x1bf324e1092671be","68xd38f0e67d5a609e4","69xb489aa790b565172","70xf28c26b89b726a9a","100xf32107109e4e182b","107x045caf5a7632eb3c","130xbdfbf7a10b6a4ca3","132xb0e07a8168ff8bf6","198x3be61ba1ee022265","200xf4ca90e4d35734d2","201xd66fa64e9b00f44f","230xaeae4e68ed0843e5"]

# v6_5 ----
# addset = ["2288x7f5a6f65dd75801d","2429xf6543cba0f4573ee","2432xc4d999b1cf9f614e","727x4779a725ffd9f106","2708x48a08e1afdce6fe0","3252xc49863e66a8fc931","479x816c87d52cc45854","3080x378fd1d37ccdae2f","2820x14e92c6138516135","3089xa145f8962284f7db","2289x958b720e7416b65c","2599xff2fa160637f2a1d","3138x575e3ee8860246d6", "2364x304de66b8955e57d","2430xa792ee1e54362209","2358x9edd4b83d9972f5c","3574x9833e866ff7e7ce4","2344x8773a6898a1f33cf","3249x0f82a23881d8b6bf","2865x9f51081866142895","3027xd367103233aaa153","2350x67dbe3cf12d34feb","3086xe4b65dc961ab6b06","3373x4c78a6c277496b43", "2710x5e08b2670ec59556","3114x68cac673c6473b40","2362x98de6203fa24b54b", "2597x6322306025942b84","3246x43e33d8a377bc980", "3279xbcdeff56ebca9751","3085x99164c9a39d3ccf2"]
#  ["2288x7f5a6f65dd75801d","479x816c87d52cc45854","2289x958b720e7416b65c","2599xff2fa160637f2a1d","2364x304de66b8955e57d","2358x9edd4b83d9972f5c","3574x9833e866ff7e7ce4","2344x8773a6898a1f33cf","3027xd367103233aaa153","3373x4c78a6c277496b43","2710x5e08b2670ec59556","2597x6322306025942b84"]
#problems = problems + addset

# Geometric v6_4 --- 52pb + 12
# problems = ["67x5b4fba667df52fa1","128x811b2570178bf7f4","203x3bc460c3ede7581a","492xa8d62ce400033970","2215xb218e7d30d44d7f7","2216xec49885fc36eed79","2724xf65ee49b8a20e811","2726x6a315b534378f1f2","2750xf06a70e229b22315","2758x663ddb984a6654cf","2837x6f95d44ac77071c5","2918x070f68e2b1b77c99","2967x7f0f4189294f20b5","3125xdc7240e6bbac240a","3258x7b1d5d7a3c8e48df","3278xec934e87e95ecac7","2694x8168e598b648d4fc","3289xe34cfad14af148a7","3291x4e69934e9a450f44","3294x108cbb41acddc434","3296x9ea02cdc40fbae79","3316x089f20bc40de1ab0","3321xe28bad6743371306","3333xbe2b90abda67f262","3334x01b7616674b81f2e","3366x6277e8d643ed747d","3368x405cd92ea40f8df2","3372x490097c76cac33d3","3375x5fabd7dc8e8ed390","3377xd74a547591fa16bf","3382x115ab67c4579dd45","3386xeb28732acec3e57c","3389x84868dbcb468861b","3411xa6f1914ee7f02bb5","3416xde9cb574518258fa","3419xc58d1beb281ebaa0","3420xe4d92775e9c6dfdc","3422x80e2ea3f82461b78","3425x43f83a5974e705b3","3438xbc2876d6d1651409","3440x0ec7411cd057fb15","3442xa09c6c5358ec17f4","3443xccc6d51438b60e48","3456xce74d9e75d050919","3457x778a3a7bfd756ed4","3458xa141820dce2b539e","3461x61ad3af75f3f80b0","3507xd88c61d84be2f77b","3520xbea53103c41e925f","3533xd2edee7b4beb8249","3591xf6c43d2e83f5c56b","3589x3211f371c00b0418", "3311x73cb964adc8be7c7","3113x55a393ac7444abb3","3331xde2f4ef708d49596","3384xb975398ba31383ea","463xcfe7b496cc84ebb6","3367x5acd49b8eee72c8e","3295x6d53f37c9e7f55fc","406xe0ee871f1fe41772","282x976393d02d97f2ca","2234xfdffacb0b8925af4"]


# V7 problems of all measures
# problems = ["2xbee2fdb4aec4e218","9x0bfe6a9e0082aa03","25x09b4b0ef20df9f68","31xc05d1c38b9d38ef1","33xa418919f3d8d497f","36x31612b2e056b384a","45xa3c07a492c5ef86a","66x1bf324e1092671be","68xd38f0e67d5a609e4","69xb489aa790b565172","70xf28c26b89b726a9a","100xf32107109e4e182b","107x045caf5a7632eb3c","110x5cfffff1990fcf9b","130xbdfbf7a10b6a4ca3","132xb0e07a8168ff8bf6","198x3be61ba1ee022265","200xf4ca90e4d35734d2","201xd66fa64e9b00f44f","218xf04372630df32ce3","230xaeae4e68ed0843e5","252x5e74ff51a4f3ad00","286xcd13ff515c507173","289xa752f6b4e48543e7","294x507732a7a046eb0b","319x24764c5cc505303d","327xefab6249f2bf8385","362x8998029a8b586c6b","402xedecc233d6c00723","407xd249885044ba59fd","419x942b91dfd3afae17","481x9d4d5fe4b5fb4934","484xce36ad1c400ef1b1","486xf879455b68c3b6a0","491x7d0ae84dbae21f03","500x6634d130ec0c0b2a","547x3ff489c8af4013fc","602x19934a5d8944f5d6","609x967a043f548ea820","613x759989fe586f46dd","639xd650387f6b816d9e","642x0c347e49cbdf8c29","665xf8a900f3242ff98a","700xf368e229c7b1b84c","742xfe25658ddf3a7d34","2358x9edd4b83d9972f5c","2362x98de6203fa24b54b","2364x304de66b8955e57d","2511x4c5d2065c326341f","2512x86e1d97952122cdc","2597x6322306025942b84","2599xff2fa160637f2a1d","2708x48a08e1afdce6fe0","2742xa55c68aba6742310","2747x741fb92d58e2b4ca","2795xa5311e169451dcfa","2811x30e15186c6aedb18","2820x14e92c6138516135","2822xdb8adc6441e12097","2824x16b8c299ebb9f18e","2891xb2ba51bb0ec03ec8","2892x087fead617f76210","2924xfdf3b514c895a459","2950x2742a2e850a9105d","3009xe9c71ac13121be1b","3012x53a9d7588d80ec34","3013xe7514618865a7669","3027xd367103233aaa153","3041x6fef3221cbcc5351","3057x71d5aecff7b71a7c","3078x7eb7235bbe360ddf","3080x378fd1d37ccdae2f","3085x99164c9a39d3ccf2","3086xe4b65dc961ab6b06","3089xa145f8962284f7db","3114x68cac673c6473b40","3120xd44a0ac91791828a","3138x575e3ee8860246d6","3249x0f82a23881d8b6bf","3252xc49863e66a8fc931","3338x123a09ea588bfdbe","3342x5dc9727cff361b4a","3343x62802fab4b8448c7","3418x4466db098f67d1c4","3574x9833e866ff7e7ce4","3604x43c402cd9efef8db","3605xbaca8aba24da500f"]

# sel = ["2543x06db65090a7aeec6","32x58445f5725394f16","138x3cab8aec78171ccf","395x5018ceb3ebf28126","512xef3038d41b53cf16","602x19934a5d8944f5d6","2381x4c795226a02f2243","2384x665649b12ba6c3f3","2519x58c4546d4354f13e","2520x414affc38058b81e","2549x1213864fa32095df","2585x0bf3bed05ba68718","2720x4b18d6563ea10750","2766x235d39a2d7545331","2769xeaa34617e65d7a81","2779x564ce39c1d0418be","2791x509d4f12e7c4adc6","2898x2fa4741a56cef1f4","3028x09e42f929d6eb7e7","3101x0817bcfbed6094a5","3103x416b26bcb2407676","3138x575e3ee8860246d6","3151x476e403c55866f40","3201xf0842471009e9640","3204x3571f38e3997484b","3217xef1a390ed3baf3e8","3230x86ee36e71f81dd17","3235x164c38f47660fe4e","3240x5f7a4a53b86c33c9","3254x4ee1c47b34202949","3273xc7d1d93a33246ee3","3345x563ac713a3b6df9f","3418x4466db098f67d1c4","3446x4e7389423350e44c","3486xa0678ad22a4ca086","36x31612b2e056b384a","383x9e2e0564e39820ac","2194xc3de2d1f4ce489ed","2765x5b57a0abafd12365","2906x6d5a6cdff8f5ea1a","2995xd939bf23ba4f9fa9","3271xe5860febe9337117","2601xbc259c50418f46d5"]
# problems = list(set(problems + sel))
# for name in problems:

grid = [10]

for threshold in grid:
    ln = []
    for index in range(0, len(problems)):
        name = problems[index]
        my_file = Path("./allproblemcache/"+ name +"/tmp")
        if my_file.is_file():
            ln += obj.userSequenceByProblem(name, threshold)

    with open("userEventSeqData.csv", "w+") as f:
        s = ",".join(obj.keys)
        f.write(s + "\n")
        for i in ln:
            f.write(",".join(str(v) for v in i) + "\n")