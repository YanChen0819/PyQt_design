#!/usr/bin/env python
# coding: utf-8

# In[2]:


from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


import pandas as pd
import sqlite3
from sqlite3 import Error
import sys
import os
import re 
import importlib
import pickle
import pyqtgraph as pg
import numpy as np
from PIL.ImageQt import ImageQt
from PIL import Image

# 確認是否已安裝套件
try:
    importlib.import_module("nltk")
    importlib.import_module("wordcloud")

except ModuleNotFoundError:
    # 未安裝，使用pip安裝
    import subprocess
    subprocess.check_call(['pip', 'install', 'nltk'])
    subprocess.check_call(['pip', 'install', 'wordcloud'])


# 使用套件
import nltk
import wordcloud
from wordcloud import ImageColorGenerator
 
    
#------------確認 nltk 兩個定義檔有無下載----------------------------------
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download("wordnet")
    nltk.download('omw-1.4')

    

class TableModel(QtCore.QAbstractTableModel):
 
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data
 
    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()] #pandas's iloc method
            return str(value)
 
        if role == Qt.ItemDataRole.TextAlignmentRole:          
            return Qt.AlignmentFlag.AlignVCenter + Qt.AlignmentFlag.AlignHCenter
         
        if role == Qt.ItemDataRole.BackgroundRole and (index.row()%2 == 0):
            return QtGui.QColor('#d8ffdb')
 
    def rowCount(self, index):
        return self._data.shape[0]
 
    def columnCount(self, index):
        return self._data.shape[1]
 
    # Add Row and Column header
    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole: # more roles
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
 
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

class AnotherWindow(QtWidgets.QMainWindow):
    # create a customized signal 
    submitted = QtCore.pyqtSignal(str) # "submitted" is like a component name 
 
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('sql_4.ui', self)
#         self.setGeometry(800, 200, 400, 600)
        self.setWindowTitle('Sub Window for Papers Detail')
        submitted = QtCore.pyqtSignal(str) 
        self.mainwindow = MainWindow()
        database = r"./database_sample/test.sqlite"
        img_dir = r"./database_sample/NIP2015_Images/"
        # create a database connect
        self.conn = create_connection(database)
        
#         # Signal
        self.PTBN_quary.clicked.connect(self.on_submit)
     


    def on_submit(self):
        # emit a signal and pass data along
#         self.submitted.emit(self.lineEdit_sub_mu.text()) 
        self.close()            
    # Slots
    def backtomain(self):
        self.mainwindow = MainWindow()
        self.mainwindow.show()
            
    def show_authors(self, paperid):
        sql = "select name from authors A, paperauthors B where B.paperid=" + \
            str(paperid)+" and A.id=B.authorid"
        with self.conn:
            self.rows = SQLExecute(self, sql)
            names = ""
            for row in self.rows:
                names = names + row[0] + "; "
            self.textBrowser_authors.setText(names)

    def show_title(self, paperid):
        sql = "select title from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            title = SQLExecute(self, sql)
            self.LB_title.setText(title[0][0])             
            
            
    def show_abstract(self, paperid):
        sql = "select abstract from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            abstract = SQLExecute(self, sql)
            self.textBrowser_abstract.setText(abstract[0][0])   
            
            
    def show_paper(self, paperid):
        sql = "select papertext from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            papertext = SQLExecute(self, sql)
            self.textBrowser_paper.setText(papertext[0][0])
            
            
    def show_img(self, paperid):
        img_dir = r"./database_sample/NIP2015_Images/"
        sql = "select imgfile from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            img = SQLExecute(self, sql)
            pixmap_img = QPixmap(img_dir+img[0][0])
            self.LB_img.setPixmap(pixmap_img)
            
    def show_type(self, paperid):
        sql = "select eventtype from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            type = SQLExecute(self, sql)
            self.textBrowser_type.setText(type[0][0])
            
            
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('sql_3.ui', self)
        self.table = self.tableView

        database = r"./database_sample/test.sqlite"
        self.mask = np.array(Image.open("./icon/heart_2.png"))
        # create a database connect
        self.conn = create_connection(database)
        self.setWindowTitle('Paper Query System')

        # Signals
        #------------exit-----------------------
        self.actionEXIT.triggered.connect(self.appEXIT)
        
        #------------query-----------------------
        
        self.lineEdit_key.returnPressed.connect(self.query)
        self.lineEdit_key.returnPressed.connect(self.bye_)
        self.p_But_by_title.clicked.connect(self.query)
        self.p_But_by_title.clicked.connect(self.clean)
        self.CBX_type_fill()
        self.CBX_type.currentIndexChanged.connect(self.query)
#         self.lineEdit_key.returnPressed.connect(self.CBX_type_fill)
#         self.p_But_by_title.clicked.connect(self.CBX_type_fill)




        #------------table view-----------------------
        
        self.table.doubleClicked.connect(self.rowSelected)
        self.table.doubleClicked.connect(self.call_subWin)

        self.actionSave_Data.triggered.connect(self.saveData)
        
        #-----------換頁-----------------------
        
        self.ptbn_next.clicked.connect(self.nextpages)
        self.PTBN_first.clicked.connect(self.firstpages)
        self.PTBN_last.clicked.connect(self.lastpages)
        self.PTBN_previous.clicked.connect(self.prepages)

        self.currIndex = 0

        #------------- 將名稱匯入 combo box-----------------------------
        self.CMBX_page.currentIndexChanged.connect(self.PageNow)

        self.PTBN_exit.clicked.connect(self.dialogBox)
        
        
        self.RTBN_all.toggled.connect(self.search_color)
        self.RTBN_title.toggled.connect(self.search_color)
        self.RTBN_authors.toggled.connect(self.search_color)

        
        img_path_all="./icon/all_CKBX_g.png"
        img_path_title="./icon/title_CKBX.png"
        img_path_author="./icon/authors_CKBX.png"
        img_path_abstract="./icon/abstract_CKBX.png"
                        
        pixmap_all = QPixmap(img_path_all)
#         pixmap = pixmap.scaled(self.LB_M12.size(), Qt.KeepAspectRatio)
        self.LB_all.setPixmap(pixmap_all)
    
        pixmap_title = QPixmap(img_path_title)
        self.LB_title.setPixmap(pixmap_title)
        
        pixmap_author = QPixmap(img_path_author)
        self.LB_authors.setPixmap(pixmap_author)
        
        pixmap_abstract = QPixmap(img_path_abstract)
        self.LB_abstract.setPixmap(pixmap_abstract)


    def clean(self):
        self.lineEdit_key.clear()
        
    def query(self):
        
            
        sql = "select a.id,name,title,abstract,eventtype"

        if self.CBX_type.currentText()=="ALL":
            self.type_name = ""    

        else:
            self.type_name = self.CBX_type.currentText().lower()

        if self.RTBN_all.isChecked():
            
            self.search_key = self.lineEdit_key.text()
            
                
            
            # papertext包含 abstract，全搜索選一個就好
            sql += " FROM papers A, paperauthors B, authors C WHERE (A.title LIKE '%" + self.search_key +\
            "%' OR C.name LIKE '%" + self.search_key + "%' or A.Papertext LIKE '%" + self.search_key+\
            "%' )and A.eventtype LIKE '%" + self.type_name+"%' AND A.id = B.paperid AND B.authorid = C.id"   
            
        if self.RTBN_title.isChecked():
          
            self.title_key = self.lineEdit_key.text()
            

        
            sql = sql + " from papers A,paperauthors B ,authors C where (A.title like '%"+\
            self.title_key+"%' and A.eventtype LIKE '%" + self.type_name+"%') and A.id = B.paperid and B.authorid = C.id"           

        if self.RTBN_authors.isChecked():
            
            self.name_key = self.lineEdit_key.text()
            


            sql = sql + " from papers A,paperauthors B ,authors C where( C.name like '%"+self.name_key + \
                "%' and A.eventtype LIKE '%" + self.type_name+"%')and A.id = B.paperid and B.authorid = C.id"
        
#         sql = sql + " from papers A,paperauthors B ,authors C where C.name like '%"+self.name_key + \
#                 "%' and A.title like '%"+self.title_key+"%'and A.id = B.paperid and B.authorid = C.id"  

        if self.RTBN_abstract.isChecked():
            
            self.search_key = self.lineEdit_key.text()
            

            
            # papertext包含 abstract，全搜索選一個就好
            sql += " FROM papers A, paperauthors B, authors C WHERE (A.abstract LIKE '%" + self.search_key+\
            "%' and A.eventtype LIKE '%" + self.type_name+"%' ) AND A.id = B.paperid AND B.authorid = C.id"   
            


          
        
        
        with self.conn:
            self.rows = SQLExecute(self, sql)
            self.pg = int(len(self.rows) / 10)+1

            self.CMBX_page.clear()
            self.CMBX_page.addItems([str(i) for i in range(1, self.pg+1)])
            self.CMBX_page.setCurrentIndex(0)
            self.LB_sample.setText(str(len(self.rows)))
            if len(self.rows) > 0:
                ToTableView(self, self.rows[0:10])
#                 self.show_page.setText(str(1)+' / '+str(self.pg))
                self.pagenum = 1
    

    def CBX_type_fill(self):
        self.CBX_type.clear()
        self.CBX_type.addItems(["ALL"])
        sql = "select distinct eventtype from papers A, paperauthors B"
        with self.conn:
            result = SQLExecute(self, sql)
            types = [row[0] for row in result]
        self.CBX_type.addItems(types)
            
    def search_color(self):
        
        sql = "select a.id,name,title,abstract"
        
        img_path_all="./icon/all_CKBX.png"
        img_path_all_g="./icon/all_CKBX_g.png"
        img_path_title="./icon/title_CKBX.png"
        img_path_title_g="./icon/title_CKBX_g.png"
        img_path_author="./icon/authors_CKBX.png"
        img_path_author_g="./icon/authors_CKBX_g.png"
        img_path_abstract="./icon/abstract_CKBX.png"
        img_path_abstract_g="./icon/abstract_CKBX_g.png"
        
        if self.RTBN_all.isChecked():
            
            pixmap_all = QPixmap(img_path_all_g)
    #         pixmap = pixmap.scaled(self.LB_M12.size(), Qt.KeepAspectRatio)
            self.LB_all.setPixmap(pixmap_all)
            
            pixmap_title = QPixmap(img_path_title)
            self.LB_title.setPixmap(pixmap_title)
        
            pixmap_author = QPixmap(img_path_author)
            self.LB_authors.setPixmap(pixmap_author)
            
            pixmap_abstract = QPixmap(img_path_abstract)
            self.LB_abstract.setPixmap(pixmap_abstract)
        
        
        if self.RTBN_title.isChecked():
       
            pixmap_all = QPixmap(img_path_all)
            self.LB_all.setPixmap(pixmap_all)
            
            pixmap_title = QPixmap(img_path_title_g)
            self.LB_title.setPixmap(pixmap_title)
        
            pixmap_author = QPixmap(img_path_author)
            self.LB_authors.setPixmap(pixmap_author)
            
            pixmap_abstract = QPixmap(img_path_abstract)
            self.LB_abstract.setPixmap(pixmap_abstract)        
        
        if self.RTBN_authors.isChecked():
            
            pixmap_all = QPixmap(img_path_all)
            self.LB_all.setPixmap(pixmap_all)
            
            pixmap_title = QPixmap(img_path_title)
            self.LB_title.setPixmap(pixmap_title)
        
            pixmap_author = QPixmap(img_path_author_g)
            self.LB_authors.setPixmap(pixmap_author)
            
            pixmap_abstract = QPixmap(img_path_abstract)
            self.LB_abstract.setPixmap(pixmap_abstract)
        
        if self.RTBN_abstract.isChecked():
            
            pixmap_all = QPixmap(img_path_all)
            self.LB_all.setPixmap(pixmap_all)
            
            pixmap_title = QPixmap(img_path_title)
            self.LB_title.setPixmap(pixmap_title)
        
            pixmap_author = QPixmap(img_path_author)
            self.LB_authors.setPixmap(pixmap_author)
            
            pixmap_abstract = QPixmap(img_path_abstract_g)
            self.LB_abstract.setPixmap(pixmap_abstract)
                
    
    
    def firstpages(self):

        self.pagenum = 1
        self.LB_page.setText(str(self.pagenum)+' / '+str(self.pg))
        self.CMBX_page.setCurrentIndex(self.pagenum-1)
        ToTableView(self, self.rows[0:10])

    def prepages(self):
        if self.pagenum > 1:
            self.pagenum -= 1
            self.LB_page.setText(str(self.pagenum)+' / '+str(self.pg))
            self.CMBX_page.setCurrentIndex(self.pagenum-1)
            ToTableView(self, self.rows[10*(self.pagenum-1):self.pagenum*10])

    def nextpages(self):

        if self.pagenum < self.pg:
            self.pagenum += 1
            self.LB_page.setText(str(self.pagenum) + ' / ' + str(self.pg))
            self.CMBX_page.setCurrentIndex(self.pagenum-1)
            ToTableView(self, self.rows[10*(self.pagenum-1):self.pagenum*10])

    def lastpages(self):
        self.LB_page.setText(str(self.pg)+' / '+str(self.pg))
        self.CMBX_page.setCurrentIndex(self.pg-1)
        ToTableView(self, self.rows[10*(self.pg-1):])

    def PageNow(self, index=None):
     # 取cmbx中的 index

        #         count = len(self.rows)
        #         count = count // 10 + 1
        
        if index is None:
            self.pagenum = self.CMBX_page.currentIndex()+1
        else:
            self.pagenum = index+1
            
        start = 10*(self.pagenum-1)
        
#         end = self.pagenum*10

        if self.pagenum == self.pg:
            end = len(self.rows)
        
        else:
            end = self.pagenum*10
        
        self.LB_page.setText(str(self.pagenum) + ' / ' + str(self.pg))
        ToTableView(self, self.rows[start:end])

    # Slots

                
    def show_type(self, paperid):
        sql = "select eventtype from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            type = SQLExecute(self, sql)
            self.textBrowser_type.setText(type[0][0])
            
            
            

    def show_text(self, paperid):
        sql = f"select papertext from papers A, paperauthors B where paperid="+str(paperid)+" and A.id=B.paperid"
        with self.conn:
            text = SQLExecute(self, sql)
            
        self.LB_WC.clear() 

            
        # display Abstract on TextBrowser, then go fetch author names
        text_lst = text[0][0]
#         self.textBrowser_abstract.setText(Abstract_lst)
        
        self.txt = re.sub(r'[^\w\s]', '', str( text_lst).lower().strip()) 
        self.txt = self.txt.split() 
        
#        import pickle 這串註解為下載定義檔，但我另外打包在本機資料夾
#------------------------------------------------------
#         # 下載 stopwords 定義檔
#         nltk.download('stopwords')

#         # get stopwords list
#         lst_stopwords = nltk.corpus.stopwords.words("english")

#         # 儲存成 pickles stopwords list 不用每次都連網下載
#         with open('stopwords.pkl', 'wb') as f:
#             pickle.dump(lst_stopwords, f)
#------------------------------------------------------
#-----------------停止詞，像 and , or ,...這種沒意義的詞-------------------------------------

        with open('stopwords.pkl', 'rb') as f:
            lst_stopwords = pickle.load(f)     
            
        self.txt = [word for word in self.txt if word not in lst_stopwords]
        
#------------------------------------------------------         
        self.text_clean = self.utils_preprocess_text(self.txt, lst_stopwords= lst_stopwords) 
        
        lst_tokens = nltk.tokenize.word_tokenize((self.text_clean)) 

        dic_words_freq = nltk.FreqDist(lst_tokens) 
        self.df_uni = dic_words_freq.most_common()

        self.textBrowser_abstract.setText('\n'.join([f'{word}:{freq}' \
                                                     for word, freq in self.df_uni]))
#------------------------------------------------------
        wc = wordcloud.WordCloud(background_color='white', max_words=150,max_font_size=45,mask=self.mask,colormap='rainbow') 
        wc = wc.generate(str(self.text_clean)) 
        wc_1 =wc.to_image()
        self.wc_1 = ImageQt(wc_1)
        self.LB_WC.setPixmap(QtGui.QPixmap.fromImage(self.wc_1))

    def bye_(self):
        self.LB_WC.clear() 
        if self.lineEdit_key.text() == "love":
            lst_love=["My","Friend", "I", "Love", "You ", "Always"]
            wc = wordcloud.WordCloud(background_color='white'\
                                     ,contour_width=3,min_word_length=0, max_words=7,max_font_size=45,mask=self.mask,colormap='rainbow') 
            wc = wc.generate(''.join(lst_love))
            wc_1 = wc.to_image()
            self.wc_1 = ImageQt(wc_1)
            self.LB_WC.setPixmap(QtGui.QPixmap.fromImage(self.wc_1))

            
            
    def rowSelected(self, mi):
#         self.g_views.clear() 
        self.LB_WC.clear() 


        # print([mi.row(), mi.column()])
#         if 'Abstract' in self.df.columns:
#             col_list = list(self.df.columns)
#         else:
#             print('No Abstract from the Query')
#             return
        
        self.show_text(self.df.iloc[mi.row(),0])
            
        

    def selected_Data(self, paper_id):
        sql = "select A.id,C.name,A.title,A.abstract,A.papertext,imgfile from papers A,paperauthors B ,authors C"
        self.rows = SQLExecute(self, sql)

    def call_subWin(self,mi):
        # create a sub-window
        self.anotherwindow = AnotherWindow()
#         # pass information to sub-window
#         self.anotherwindow.passInfo(self.lineEdit_mu.text(), self.lineEdit_s.text()) 
#         name , details =
#         # ready to accept a singal from sub-window
#         self.anotherwindow.submitted.connect(self.update_info)
        self.anotherwindow.show_authors(self.df.iloc[mi.row(),0])
        self.anotherwindow.show_abstract(self.df.iloc[mi.row(),0])
        self.anotherwindow.show_paper(self.df.iloc[mi.row(),0])
        self.anotherwindow.show_img(self.df.iloc[mi.row(),0])
        self.anotherwindow.show_title(self.df.iloc[mi.row(),0])
        self.anotherwindow.show_type(self.df.iloc[mi.row(),0])


        self.anotherwindow.show()            
#         @QtCore.pyqtSlot(str) # respond to a signal emitted by the sub-window  
    
    
    def saveData(self):
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file',
                                                         "", "EXCEL files (*.xlsx)")
        if len(fname) != 0:
            self.df.to_excel(fname)

    def appEXIT(self):
        self.conn.close()  # close database
        self.close()  # close app

    def dialogBox(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Statistical Practice")
        dlg.setText("確定要離開這個 App")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('確定')
        buttonY = dlg.button(QMessageBox.StandardButton.No)
        buttonY.setText('取消')
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()
 
        if button == QMessageBox.StandardButton.Yes:
            self.close()
        else:
            print("No!")

    '''
    Preprocess a string. 
    :parameter 
        :param text: string - name of column containing text 
        :param lst_stopwords: list - list of stopwords to remove 
        :param flg_stemm: bool - whether stemming is to be applied 
        :param flg_lemm: bool - whether lemmitisation is to be applied 
    :return 
        cleaned text 
    ''' 
    def utils_preprocess_text(self, text, flg_stemm=False, flg_lemm=True, lst_stopwords=None): 
        ## clean (convert to lowercase and remove punctuations and characters and then strip) 
        text = re.sub(r'[^\w\s]', '', str(text).lower().strip()) 

        ## Tokenize (convert from string to list) 
        lst_text = text.split()    ## remove Stopwords 
        if lst_stopwords is not None: 
            lst_text = [word for word in lst_text if word not in lst_stopwords] 

        ## Stemming (remove -ing, -ly, ...) 
        if flg_stemm == True: 
            ps = nltk.stem.porter.PorterStemmer() 
            lst_text = [ps.stem(word) for word in lst_text] 

        ## Lemmatisation (convert the word into root word) 
        if flg_lemm == True: 
            lem = nltk.stem.wordnet.WordNetLemmatizer() 
            lst_text = [lem.lemmatize(word) for word in lst_text] 

        ## back to string from list 
        text = " ".join(lst_text) 
        return text            


 

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def SQLExecute(self, SQL):
    """
    Execute a SQL command
    :param conn: SQL command
    :return: None
    """
    self.cur = self.conn.cursor()
    self.cur.execute(SQL)
    rows = self.cur.fetchall()

    if len(rows) == 0:  # nothing found
        # raise a messageBox here
        dlg = QMessageBox(self)
        dlg.setWindowTitle("SQL Information: ")
        dlg.setText("No data match the query !!!")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes)
        buttonY = dlg.button(QMessageBox.StandardButton.Yes)
        buttonY.setText('OK')
        dlg.setIcon(QMessageBox.Icon.Information)
        button = dlg.exec()
        # return
    return rows


def ToTableView(self, rows):
    """
    Display rows on the TableView in pandas format
    """
    names = [description[0] for description in self.cur.description]  # extract column names
    self.df = pd.DataFrame(rows)
#     self.df = pd.DataFrame(columns=multi_index)
    self.model = TableModel(self.df)
    self.table.setModel(self.model)
    self.df.columns = names
    self.df.index = range(1, len(rows)+1)


    
def main():
#     database = r"./database_sample/database.sqlite" # 資料庫的位置
#     file_src = r"./database_sample/NIP2015_Images/"  # 圖片檔的位置
#     picName = os.listdir(file_src)
#     paperid = fetch_paperid(conn)
#     conn = create_connection(database)
#     with conn:
#         for i in range(len(paperid)):
#             update_papers(conn, (picName[i], paperid[i][0]))    
#     conn.close()
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

