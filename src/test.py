import jieba
import jieba.analyse
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfpage import PDFPage,PDFTextExtractionNotAllowed
import logging
import os

wordsByMyself=['社会责任','义务','上市','公司'] #自定义词语,全局变量
fileNum=16#存储总共待处理的文件数量

#重命名所有文件夹下的文件，适应处理需要
def rename():
    path='dealPdf'
    filelist=os.listdir(path)
    for i,files in enumerate(filelist):
        Olddir=os.path.join(path,files)
        if os.path.isdir(Olddir):
            continue
        Newdir=os.path.join(path,str(i+1)+'.pdf')
        os.rename(Olddir,Newdir)

#将pdf文件转化成txt文件
def pdf_to_txt(dealPdf,index):
    # 不显示warning
    logging.propagate = False
    logging.getLogger().setLevel(logging.ERROR)
    pdf_filename = dealPdf
    device = PDFPageAggregator(PDFResourceManager(), laparams=LAParams())
    interpreter = PDFPageInterpreter(PDFResourceManager(), device)
    parser = PDFParser(open(pdf_filename, 'rb'))
    doc = PDFDocument(parser)


    txt_filename='dealTxt\\'+str(index)+'.txt'

    # 检测文档是否提供txt转换，不提供就忽略
    if not doc.is_extractable:
        raise PDFTextExtractionNotAllowed
    else:
        with open(txt_filename, 'w', encoding="utf-8") as fw:
            #print("num page:{}".format(len(list(doc.get_pages()))))
            for i,page in enumerate(PDFPage.create_pages(doc)):
                interpreter.process_page(page)
                # 接受该页面的LTPage对象
                layout = device.get_result()
                # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
                # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
                # 想要获取文本就获得对象的text属性，
                for x in layout:
                    if isinstance(x, LTTextBoxHorizontal):
                        results = x.get_text()
                        fw.write(results)

#对txt文件的换行符进行删除
def delete_huanhangfu(dealTxt,index):
    outPutString=''
    outPutTxt='outPutTxt\\'+str(index)+'.txt'
    with open(dealTxt,'r',encoding="utf-8") as f:
        lines=f.readlines()
        for i in range(len(lines)):
            if lines[i].endswith('\n'):
                lines[i]=lines[i][:-1] #将字符串末尾的\n去掉
        for j in range(len(lines)):
            outPutString+=lines[j]
    with open(outPutTxt,'w',encoding="utf-8") as fw:
        fw.write(outPutString)

#添加自定义词语
def word_by_myself():
    for i in range(len(wordsByMyself)):
        jieba.add_word(wordsByMyself[i])

#分词并进行词频统计
def cut_and_count(outPutTxt):
    with open(outPutTxt,encoding='utf-8') as f:
        #step1：读取文档并调用jieba分词
        text=f.read()
        words=jieba.lcut(text)
        #step2:读取停用词表，去停用词
        stopwords = {}.fromkeys([ line.rstrip() for line in open('stopwords.txt',encoding='utf-8') ])
        finalwords = []
        for word in words:
            if word not in stopwords:
                if (word != "。" and word != "，") :
                    finalwords.append(word)


                    #step3：统计特定关键词的出现次数
        counts={}
        for word in finalwords:
            if len(word) == 1:#单个词不计算在内
                continue
            else:
                counts[word]=counts.get(word,0)+1#遍历所有词语，每出现一次其对应值加1
        for i in range(len(wordsByMyself)):
            if wordsByMyself[i] in counts:
                print(wordsByMyself[i]+':'+str(counts[wordsByMyself[i]]))
            else:
                print(wordsByMyself[i]+':0')

#主函数
if __name__ == "__main__":
    #rename()
    for i in range(1,fileNum+1):
        pdf_to_txt('dealPdf\\'+str(i)+'.pdf',i)#将pdf文件转化成txt文件，传入文件路径
        delete_huanhangfu('dealTxt\\'+str(i)+'.txt',i)#对txt文件的换行符进行删除，防止词语因换行被拆分
        word_by_myself()#添加自定义词语
        print(f'----------result {i}----------')
        cut_and_count('outPutTxt\\'+str(i)+'.txt')#分词并进行词频统计，传入文件路径
