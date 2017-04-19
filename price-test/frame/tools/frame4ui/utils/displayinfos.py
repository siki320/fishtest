#/***************************************************************************
# *
# * Copyright (c) 2010 XX, Inc. All Rights Reserved
# *
# **************************************************************************/
#/**
# * @author yangming03
# * @date 2012/11/26
# * @version $Revision: 1.0
# *
# **/
import os
from core.logprint import Logger

class DTSInfos:
    def __init__(self):
        self.infos = []
        self.col_len = []
        self.start_index = ''
        self.Line_flag = False   #show more Line flag
	self.window_min = 100
    def drawline(self, lineMAX=100, charLine='='):
        hLine = charLine * lineMAX
        Logger.output("%s"%hLine)

    def formatText(self, rowElements, frameWidth):
        output = ""
        max_frame_width = sum(self.columnWidths)
	#len(lines) > 1
        if (self.Line_flag):
            contentLengths = map(lambda contentElem: len(contentElem), rowElements)
            max_contentLengths = max(contentLengths)
            max_columnWidths = max(self.columnWidths)
            if max_contentLengths > max_columnWidths:
                outputList = ["" for i in range(max_contentLengths/max_columnWidths+1)]
            else:
                outputList = ["" for i in range(max_columnWidths/max_contentLengths+1)]
            for index in range(len(rowElements)):
                dspLine = 1
                actualColWidth = self.columnWidths[index]-len(self.start_index)
                tempStrList = []
                if (len(rowElements[index]) >= self.columnWidths[index]):
                    dspLine = (len(rowElements[index])/ actualColWidth)
                    if (len(rowElements[index]) % (actualColWidth) > 0):
                        dspLine += 1
                if (dspLine == 1):
                        tempStrList.append(rowElements[index]) # content of the row
                        if (actualColWidth - len(rowElements[index]))> 0 :
                            tempStrList.append(' '* (actualColWidth - len(rowElements[index]))) 
                        tempStrList.append(' ' * ((frameWidth - max_frame_width)/len(rowElements))) 
                        if (index != len(rowElements) -1):
                                tempStrList.append(self.start_index)

                        outputList[0] += ''.join(tempStrList) 
                        for j in range(1,len(outputList)):
                            outputList[j] += ' '* actualColWidth + ' '* ((frameWidth - max_frame_width)/len(rowElements))
                            if (index != len(rowElements) -1):
                                outputList[j] += self.start_index
                # write lines
                else:
                    for i in range(dspLine):
                        outputList[i] += rowElements[index][actualColWidth*(i):actualColWidth*(i+1)]+ \
                              ' '* (actualColWidth - len(rowElements[index][actualColWidth*(i):actualColWidth*(i+1)]))+ \
                              ' '* ((frameWidth - max_frame_width)/len(rowElements))
                        #add a start_index element
                        if (index != len(rowElements) -1):
                            outputList[i] += self.start_index
            output = "\n".join(outputList)
        # only one line
        else:
            for index in range(0,len(rowElements)):
                actualColWidth = self.columnWidths[index]-len(self.start_index)
                output += rowElements[index] + ' '* (actualColWidth - len(rowElements[index]))+ ' '* ((frameWidth - max_frame_width)/len(rowElements))
                if (index != len(rowElements) -1):
                    output += self.start_index
        return output

    def display(self):
        frameWidth = self.window_min
        try:
            frameWidth = int(os.popen('tput cols').read())
        except:
            Logger.output("Cannot get the terminal information setting size to default(=100)")
        frameWidth -= 5
        #print frameWidth
        if (frameWidth < self.window_min):
            frameWidth = self.window_min

        totalColWidth = sum(self.columnWidths)
        NoOfCols = len(self.infos[0])
        if totalColWidth + (NoOfCols )  > frameWidth:
            self.Line_flag = True
            longCols = [self.columnWidths[j] for j in range(NoOfCols) if (self.columnWidths[j]> frameWidth/NoOfCols)]
            rest = frameWidth - (totalColWidth - sum(longCols))
            for j in range(0,NoOfCols):
                if self.columnWidths[j] in longCols:
                    self.columnWidths[j] = (self.columnWidths[j] *rest)/sum(longCols)
	#self.drawline(frameWidth,'=')
	table_file = open ('.table_file', "w")
	temp_Line = "\n"+"="*frameWidth+"\n"
	table_file.write(temp_Line)
	print "*"*(frameWidth/2-6)+"|Case Infos|"+"*"*(frameWidth/2-6)
        self.drawline(frameWidth)
        try:
            for i in range(len(self.infos)):
                rowContent = self.infos[i]
                Logger.output("%s"%((self.formatText(rowContent,frameWidth))).rstrip())#
		table_file.write(((self.formatText(rowContent,frameWidth))).rstrip())
		table_file.write("\n")
                if not (i == len(self.infos)-1):
                    self.drawline(frameWidth,"-")
		    temp_Line = "="*frameWidth+"\n"
        	    table_file.write(temp_Line)
        except IndexError:
            Logger.output("format error: please make it wider.(Current width: %d)"%frameWidth)

        self.drawline(frameWidth)
	temp_Line = "="*frameWidth+"\n"
        table_file.write(temp_Line)

    def add(self, contentList):
        strContentList = [str(x) for x in contentList]
        if not self.infos:
            self.columnWidths = map(lambda headerElem: len(headerElem)+1, contentList)
        else:
            contentLengths = map(lambda contentElem: len(contentElem)+1, strContentList)
            self.columnWidths = [max(x,y) for (x,y) in zip(self.columnWidths,contentLengths)]
        self.infos.append(strContentList)

    def showInfos(self, contentRows):
        if 0 < len(contentRows):
            frameStart = 0
            header = []
            footer = []
            readHeader = True
            hasTable = False
            for row in contentRows:
                if readHeader:
                    if isinstance(row, type([])):
                        dispRow = []
                        for cell in row:
                            dispRow.append(cell)
                        self.add(dispRow)
                        hasTable=True
                        readHeader = False
                    else:
                        header.append("%s"%row)
                else:
                    if isinstance(row, type([])):
                        dispRow = []
                        for cell in row:
                            dispRow.append(cell)
                        self.add(dispRow)
                        hasTable=True
                    else:
                        footer.append("%s"%row)

            if [] != header:
                for row in header:
                    Logger.output("%s"%row)

            if hasTable:
                self.display()

            if [] != footer:
                for row in footer:
                    Logger.output("%s"%row)

        else:
            Logger.output("Error: No content to show in frame.")


def main():
    pass


if __name__ == '__main__':
    main()
