from PyQt5 import QtWidgets , uic , QtCore , QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QListWidget,  QListWidgetItem,QStackedWidget \
    , QMessageBox , QLineEdit ,  QToolButton, QLabel
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream , QDate
import sys
import sqlite3







class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi("WordWizard.ui",self)

        ########## all the necessary settings when open the program
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(808, 519)
        self.stackedWidget.setCurrentIndex(0)

        self.side_menu_scaling_status = False
        self.inventoryView_grabDataFromDatabase()

        self.chooseboxSelection_state = 0
        self.chooseboxSort_state = 0

        self.radioButton_4.setChecked(True)



        ##### all the button connections
        # title bar
        self.exit_btn.clicked.connect(lambda : self.close())
        self.min_btn.clicked.connect(lambda : self.showMinimized())

        # side menu
        self.sideMenu_control_btn.clicked.connect(lambda: self.side_menu_scaling_control())
        self.home_btn.clicked.connect(self.on_home_btn_1_clicked)
        self.inventory_btn.clicked.connect(self.on_inventory_btn_1_clicked)
        self.progress_btn.clicked.connect(self.on_progress_btn_1_clicked)
        self.settings_btn.clicked.connect(self.on_settings_btn_1_clicked)

        # home page
        self.vocTest_bind_pushButton.clicked.connect(self.vocTest_bind)

        # inventory page
        self.InventoryView_editCurrentButton.clicked.connect(self.editCurrentWord_inventoryView)
        self.InventoryView_addNewButton.clicked.connect(self.addNewWord_inventoryView)
        self.InventoryView_saveChoosebox_variationButton.clicked.connect(self.saveChoosebox_variation_inventoryView)
        self.InventoryView_deleteCurrentButton.clicked.connect(self.deleteCurrentWord_inventoryView)
        self.InventoryView_selectAll_chooseboxOnButton.clicked.connect(self.selectAll_chooseboxOn_inventoryView)
        self.promote_btn.clicked.connect(self.textBrowser_showcase)
        self.InventoryView_listSortbyAlpha_Button.clicked.connect(self.sort_words_alphabetically)

        # progress view
        self.save_note_btn.clicked.connect(self.save_note)

        # settings page
        self.save_font_btn.clicked.connect(self.save_font_settings)





    # side menu scaling control
    def side_menu_scaling_control(self):
        if self.side_menu_scaling_status == False:
            self.animation1 = QtCore.QPropertyAnimation(self.side_menu_frame, b"maximumWidth")
            self.animation1.setDuration(300)
            self.animation1.setStartValue(56)
            self.animation1.setEndValue(140)
            self.animation1.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation1.start()

            self.animation2 = QtCore.QPropertyAnimation(self.side_menu_frame, b"minimumWidth")
            self.animation2.setDuration(300)
            self.animation2.setStartValue(56)
            self.animation2.setEndValue(140)
            self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation2.start()

            self.side_menu_scaling_status = True

        else:
            self.animation1 = QtCore.QPropertyAnimation(self.side_menu_frame, b"maximumWidth")
            self.animation1.setDuration(300)
            self.animation1.setStartValue(140)
            self.animation1.setEndValue(56)
            self.animation1.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation1.start()

            self.animation2 = QtCore.QPropertyAnimation(self.side_menu_frame, b"minimumWidth")
            self.animation2.setDuration(300)
            self.animation2.setStartValue(140)
            self.animation2.setEndValue(56)
            self.animation2.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation2.start()

            self.side_menu_scaling_status = False


    # functions to control window dragging
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


    ######### functions for sidebars
    def on_home_btn_1_clicked(self):
        self.stackedWidget.setCurrentIndex(0)
    def on_inventory_btn_1_clicked(self):
        self.stackedWidget.setCurrentIndex(1)

        # remember to refresh the list widget!
        self.inventoryView_grabDataFromDatabase()

        # set the list Widget to the first item (just like when user click on the first item)
        #########  to avoid crash!! #########
        self.listWidget_InventoryView.setCurrentItem(self.listWidget_InventoryView.item(0))

        # set the text browser to the first item's definition
        self.textBrowser_showcase()

    def on_progress_btn_1_clicked(self):
        self.stackedWidget.setCurrentIndex(2)
        self.database_wordNumber_count()
        self.test_number_count()
        self.note_showcase()

    def on_settings_btn_1_clicked(self):
        self.stackedWidget.setCurrentIndex(3)


    ######## 2 functions in Home View
    def vocTest_bind(self):



        # error handling
        # if the user didn't select any word for test (all words' choosebox = 0)
        # then pop up a warning message
        # and don't open the test window
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()
        cursor.execute("SELECT choosebox FROM words")
        all_current_choosebox_objects = cursor.fetchall()
        db.close()
        all_current_choosebox = []
        for choosebox in all_current_choosebox_objects:
            all_current_choosebox.append(choosebox[0])

        if 1 not in all_current_choosebox:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("You haven't chosen any word for test!")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        query = "UPDATE others SET Value = Value + 1 WHERE Name = ?"
        cursor.execute(query, ("testCount",))
        db.commit()
        db.close()


        ###########################################
        # loding animation should be added here
        ###########################################


        self.vocTest_popup = VocTest()
        self.vocTest_popup.show()



    ##### all functions in Inventory View
    # 3-1 grab data from database
    def inventoryView_grabDataFromDatabase(self):
        self.listWidget_InventoryView.clear()

        # connect to database
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # grab only worksName from database
        cursor.execute("SELECT wordsName , choosebox FROM words")
        wordsName = cursor.fetchall()

        # add the results to the list widget (here "word" is a row in the database
        for word in wordsName:
            item = QtWidgets.QListWidgetItem(str(word[0])) # (item means what is to add in the listWidget)

            # add checkbox
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            # check choosebox value (0 for user_not_chosen, 1 for user_chosen)
            if word[1] == 1:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            self.listWidget_InventoryView.addItem(item)

    # 3-2 edit current word button function
    def editCurrentWord_inventoryView(self):
        # pointer saved to database
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # unsolved bug: ###########################################
        # when the database has nothing, the Program will crash ... (bug2)

        ##########################################################

        selectedWord = self.listWidget_InventoryView.currentItem().text()

        # change selectedWord's "pointer" value in database to 1
        cursor.execute("UPDATE words SET pointer = 1 WHERE wordsName = ?", (selectedWord,))
        db.commit()
        db.close()

        # connect the button to the popup window
        self.editCurrent_popup = EditCurrent()
        self.editCurrent_popup.show()

        # make the list widget "focus" on the first item (crash avoidance)
        self.listWidget_InventoryView.setCurrentItem(self.listWidget_InventoryView.item(0))

    # 3-3 add new word button function
    def addNewWord_inventoryView(self):
        self.addNewWord_popup = AddNew()
        self.addNewWord_popup.show()

        # make the list widget "focus" on the first item (crash avoidance)
        self.listWidget_InventoryView.setCurrentItem(self.listWidget_InventoryView.item(0))

    # 3-4 save choosebox variation button function
    def saveChoosebox_variation_inventoryView(self):
        # connect to database
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # grab all the wordsName from database
        cursor.execute("SELECT wordsName FROM words")
        wordsName = cursor.fetchall()


        # update choosebox value in database
        for i in range(len(wordsName)):
            # grab the item from listWidget
            item = self.listWidget_InventoryView.item(i)

            # check if the item is checked or not
            if item.checkState() == QtCore.Qt.Checked:
                # update choosebox value in database
                cursor.execute("UPDATE words SET choosebox = 1 WHERE wordsName = ?", (wordsName[i][0],))
                db.commit()
            else:
                # update choosebox value in database
                cursor.execute("UPDATE words SET choosebox = 0 WHERE wordsName = ?", (wordsName[i][0],))
                db.commit()

        db.close()

        # update listWidget
        # self.inventoryView_grabDataFromDatabase()

    # 3-5 delete current word button function
    def deleteCurrentWord_inventoryView(self):
        ## it will crash when the database have nothing in it (a damn bug ... )


        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Delete current word")
        popup.setText("Are you sure to delete this word?") # change it to minecraft style!!

        popup.setIcon(QtWidgets.QMessageBox.Warning)
        popup.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
        popup.setWindowIcon(QtGui.QIcon("icon.png"))
        popup.setStyleSheet("background-color: rgb(255, 255, 255);")
        popup = popup.exec_()

        if popup == QtWidgets.QMessageBox.No:
            print("No")
            return

        # connect to database
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # grab the selected word
        selectedWord = self.listWidget_InventoryView.currentItem().text()

        # delete the selected word from database
        cursor.execute("SELECT rowid FROM words WHERE wordsName = ?", (selectedWord,))
        rowid = cursor.fetchone()[0]
        cursor.execute("DELETE FROM words WHERE rowid = ?", (rowid,))

        db.commit()
        db.close()

        # update listWidget
        self.inventoryView_grabDataFromDatabase()

        # make the list widget "focus" on the first item (crash avoidance)
        self.listWidget_InventoryView.setCurrentItem(self.listWidget_InventoryView.item(0))

    # 3-6 set_all_choosebox_checked in listWidget (but not yet updated in database! )
    def selectAll_chooseboxOn_inventoryView(self):
        if self.chooseboxSelection_state == 0:
            for index in range(self.listWidget_InventoryView.count()):
                item = self.listWidget_InventoryView.item(index)
                item.setCheckState(QtCore.Qt.Checked)
            self.chooseboxSelection_state = 1
        else:
            for index in range(self.listWidget_InventoryView.count()):
                item = self.listWidget_InventoryView.item(index)
                item.setCheckState(QtCore.Qt.Unchecked)
            self.chooseboxSelection_state = 0

    # 3-7 promote chosen word to the textBrowser
    def textBrowser_showcase(self):
        self.textBrowser.clear()

        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        selectedWord = self.listWidget_InventoryView.currentItem().text()

        cursor.execute("SELECT wordsName, type, explanation , sentence , source FROM words WHERE wordsName = ?", (selectedWord,))
        wordObject = cursor.fetchone()
        db.close()

        # set the textBrowser
        self.textBrowser.append("<h1>" + wordObject[0] + "</h1>")
        self.textBrowser.append("<h2>" + wordObject[1] + "</h2>")
        self.textBrowser.append("<p>" + wordObject[2] + "</p>")
        self.textBrowser.append("<p style='font-style: italic;'>{}</p>".format(wordObject[3]))
        self.textBrowser.append("<p style='color: blue;'>{}</p>".format(wordObject[4]))

    # 3-8 sort words alphabetically in listWidget
    def sort_words_alphabetically(self):
        self.listWidget_InventoryView.clear()

        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # grab all the wordsName from database
        cursor.execute("SELECT wordsName ,choosebox FROM words")
        wordsName = cursor.fetchall()

        # sort wordsName alphabetically
        if self.chooseboxSort_state == 0:
            wordsName.sort()
            self.chooseboxSort_state = 1
        else:
            wordsName.sort(reverse=True)
            self.chooseboxSort_state = 0

        # update listWidget
        for word in wordsName:
            item = QtWidgets.QListWidgetItem(str(word[0])) # (item means what is to add in the listWidget)

            # add checkbox
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            # check choosebox value (0 for user_not_chosen, 1 for user_chosen)
            if word[1] == 1:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            self.listWidget_InventoryView.addItem(item)

        db.close()




    ######### Progress View Functions
    # 4-1 count the number of words in database
    def database_wordNumber_count(self):
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        # grab all the wordsName from database
        cursor.execute("SELECT wordsName FROM words")
        wordsName = cursor.fetchall()

        # count the number of words
        wordNumber = len(wordsName)
        str(wordNumber)
        # update wordNumber_label
        self.wordNumber_label.setText("Number of Words in Database: " + str(wordNumber))

        db.close()

    # 4-2 count how many tests have been taken (every time user click "take test" button, the number will increase by 1)
    def test_number_count(self):
        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        query = "SELECT Value FROM others where Name = ?"
        result = cursor.execute(query, ["testCount"])
        print(result)
        testCount = result.fetchone()

        print(testCount)
        self.testNumber_label.setText("Number of Tests Taken: " + str(testCount[0]))

        query = "SELECT type, explanation, sentence, source , wordsName FROM words WHERE pointer = 1"
        result = cursor.execute(query)

    # 4-3 show note from txt to textEdit
    def note_showcase(self):
        file_name = "saved_notes.txt"
        try:
            with open(file_name, 'r') as file:
                content = file.read()
                self.noteShown_textEdit.setPlainText(content)
        except FileNotFoundError:
            pass

    # 4-4 save note to txt file
    def save_note(self):
        content = self.noteShown_textEdit.toPlainText()
        file_name = "saved_notes.txt"
        with open(file_name, 'w') as file:
            file.write(content)




    ########### Settings View Functions
    def save_font_settings(self):
        if self.radioButton.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Arial;"
                                           "font-size: 16px;}")

            self.noteShown_textEdit.setStyleSheet("*{"
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Arial;"
                                                  "font-size: 16px;}")

        if self.radioButton_2.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Book Antiqua;"
                                           "font-size: 16px;}")

            self.noteShown_textEdit.setStyleSheet("*{" 
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Book Antiqua;"
                                                  "font-size: 16px;}")

        if self.radioButton_3.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Perpetua;"
                                           "font-size: 16px;}")

            self.noteShown_textEdit.setStyleSheet("*{" 
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Perpetua;"
                                                  "font-size: 16px;}")

        if self.radioButton_4.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Garamond;"
                                           "font-size: 17px;}")

            self.noteShown_textEdit.setStyleSheet("*{" 
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Garamond;"
                                                  "font-size: 16px;}")

        if self.radioButton_5.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Rockwell;"
                                           "font-size: 16px;}")

            self.noteShown_textEdit.setStyleSheet("*{" 
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Rockwell;"
                                                  "font-size: 16px;}")

        if self.radioButton_6.isChecked():
            self.textBrowser.setStyleSheet("*{background-color: rgb(243, 248, 252);"
                                           "border: 1px solid rgba(204, 204, 204, 0.5);"
                                           "border-radius: 10px;"
                                           "padding: 10px;}"
                                           "QTextBrowser:hover {"
                                           "border: 3px solid rgb(85, 170, 255, 0.2);"
                                           "padding: 7px;}"
                                           "QTextBrowser {"
                                           "font-family: Segoe Print;"
                                           "font-size: 14px;}")

            self.noteShown_textEdit.setStyleSheet("*{" 
                                                  "border-radius: 10px;"
                                                  "padding: 5px;}"
                                                  "QTextEdit:hover {"
                                                  "border: 1px solid rgb(19, 112, 243);"
                                                  "border-color: rgb(19, 112, 243);"
                                                  "color: rgb(53, 132, 245);"
                                                  "background-color: rgb(224, 234, 253);}"
                                                  "QTextEdit {"
                                                  "font-family: Segoe Print;"
                                                  "font-size: 16px;}")






# import editCurrent ui file
class EditCurrent(QMainWindow):
    def __init__(self):
        super(EditCurrent, self).__init__()

        # load ui file
        uic.loadUi("editCurrent_popup.ui", self)


        # use data from database to fill in all the lineEdit and textEdit when window open
        self.showPreviousData()

        # store all the data in textEdit and lineEdit to variables
        self.type = self.editCurrent_type.text()
        self.explanation = self.editCurrent_explanation.toPlainText()
        self.sentence = self.editCurrent_sentence.toPlainText()
        self.source = self.editCurrent_source.toPlainText()


        # bind save button to function
        self.editCurrent_Save.clicked.connect(self.saveChanges_editCurrent)

    def showPreviousData(self):
        # clear previous data
        self.clearall()

        # connect to the database
        connection = sqlite3.connect("wordwizard_database.db")
        cursor = connection.cursor()

        # fill in the data in database to the lineEdit and textEdit
        # only import the word which pointer value is 1
        query = "SELECT type, explanation, sentence, source , wordsName FROM words WHERE pointer = 1"
        result = cursor.execute(query)
        for i in result:
            self.editCurrent_type.setText(i[0])
            self.editCurrent_explanation.setText(i[1])
            self.editCurrent_sentence.setText(i[2])
            self.editCurrent_source.setText(i[3])
            self.wanted_label.setText(i[4])

        # set pointer value to 0
        query = "UPDATE words SET pointer = 0 WHERE pointer = 1"
        cursor.execute(query)
        connection.commit()

        # close the connection
        connection.close()

        # update listWidget
        window.inventoryView_grabDataFromDatabase()



    def clearall(self):
        self.editCurrent_type.clear()
        self.editCurrent_explanation.clear()
        self.editCurrent_sentence.clear()
        self.editCurrent_source.clear()


    def saveChanges_editCurrent(self):
        # grab the data from the lineEdit and textEdit
        type = self.editCurrent_type.text()
        explanation = self.editCurrent_explanation.toPlainText()
        sentence = self.editCurrent_sentence.toPlainText()
        source = self.editCurrent_source.toPlainText()
        wanted_label = self.wanted_label.text()

        # connect to the database
        connection = sqlite3.connect("wordwizard_database.db")
        cursor = connection.cursor()

        # update the data in database
        query = "UPDATE words SET type = ? , explanation = ? , sentence = ? , source = ? WHERE wordsName = ?"
        cursor.execute(query, (type, explanation, sentence, source, wanted_label))
        connection.commit()

        # close the connection
        connection.close()

        # close the window
        self.close()


# import addNew ui file
class AddNew(QMainWindow):
    def __init__(self):
        super(AddNew, self).__init__()

        # load ui file
        uic.loadUi("addNew_popup.ui", self)

        # bind save button to function
        self.addNew_Save.clicked.connect(self.saveChanges_addNew)

    def saveChanges_addNew(self):
        # grab the data from the lineEdit and textEdit
        wordsName = self.addNew_wordName.text()
        type = self.addNew_type.text()
        explanation = self.addNew_explanation.toPlainText()
        sentence = self.addNew_sentence.toPlainText()
        source = self.addNew_source.toPlainText()
        status = 0
        choosebox = 0
        pointer = 0


        # connect to the database
        connection = sqlite3.connect("wordwizard_database.db")
        cursor = connection.cursor()

        # insert the data to database
        query = "INSERT INTO words VALUES (?,?,?,?,?,?,?,?)" # 8 values !!!
        row = (wordsName, sentence, explanation, type , status , choosebox , source , pointer)
        cursor.execute(query, row)
        connection.commit()

        # close the connection
        connection.close()

        # close the window
        self.close()

        # update listWidget
        window.inventoryView_grabDataFromDatabase()


# import vocTest ui file
class VocTest(QMainWindow):
    def __init__(self):
        super(VocTest, self).__init__()

        # load ui file
        uic.loadUi("vocTest_popup.ui", self)

        self.vocTest_stackedWidget.setCurrentIndex(0)

        ##### data setup #####
        # search for the word in database that choosebox is 1 (ticked by user)
        # connect to the database
        connection = sqlite3.connect("wordwizard_database.db")
        cursor = connection.cursor()

        # grab the data from database
        # import all the words that choosebox is 1
        query = "SELECT rowid FROM words WHERE choosebox = 1"
        result = cursor.execute(query)   # here all satisfied words are stored in to objects
        self.rowid_list = []
        for i in result:
            self.rowid_list.append(i[0])   # all words' rowid index is stored into rowid_list

        # set choosebox value to 0
        query = "UPDATE words SET choosebox = 0 WHERE choosebox = 1"
        cursor.execute(query)
        connection.commit()
        connection.close()

        # here: for info_label_showcase
        self.total_words_count = len(self.rowid_list)  # number of added words (don't take into account revision words yet)
        self.current_word_count = 0  # number of words that have been tested
        self.remaining_words_count = self.total_words_count - self.current_word_count
        self.info_label_show(self.current_word_count, self.remaining_words_count)

        # here: current word's rowid
        self.index = 0  # to locate the current word in the rowid_list (in __init__ we add the first one)
        current_rowid = self.rowid_list[self.index]  # the current word's rowid
        self.set_current_word_into_query(current_rowid)

        # review checkbox must set to uncheck (default)
        self.review_checkBox.setChecked(False)


        # bind buttons
        self.pushButton1_1.clicked.connect(self.to_next_word)
        self.pushButton1_2.clicked.connect(self.go_to_page_2)
        self.pushButton2_1.clicked.connect(self.go_to_page_3)
        self.pushButton2_2.clicked.connect(self.dont_know_the_word)
        self.pushButton3_1.clicked.connect(self.pg3_go_to_page_1)

    def set_current_word_into_query(self, rowid_num):
        # connect to the database
        connection = sqlite3.connect("wordwizard_database.db")
        cursor = connection.cursor()

        # grab the data from database
        # import all the words that choosebox is 1
        query = "SELECT wordsName , sentence , explanation , type , status , choosebox , source FROM words where rowid = ?"
        result = cursor.execute(query, (rowid_num,))
        for i in result:
            self.showWordsName_label.setText(i[0])
            self.showSentence_textbrowser_pg2.append(i[1])      #### need to add: set stylesheet + bold the word
            # self.vocTest_sentence1.setText(i[1])
            # self.vocTest_explanation1.setText(i[2])
            # self.vocTest_type1.setText(i[3])
            # self.vocTest_source1.setText(i[6])


        # close the connection
        connection.close()



    def to_next_word(self):
        self.index += 1

        # below is for info_label
        self.total_words_count = len(self.rowid_list)
        self.current_word_count += 1
        self.remaining_words_count = self.total_words_count - self.current_word_count
        self.info_label_show(self.current_word_count, self.remaining_words_count)


        # exit vocTest
        if self.index == len(self.rowid_list):
            self.close()

            # add a popup window to show the test is finished
            popup = QMessageBox()
            popup.setWindowTitle("Test Finished")
            popup.setText("You have finished the test!")
            popup.setIcon(QMessageBox.Information)
            popup.setStandardButtons(QMessageBox.Ok)
            popup.exec_()
            return

        # also need to clear all the showcase in page 2&3 (use append method, so first clear the remaining text)
        self.showSentence_textbrowser_pg2.clear()

        # set up next word
        current_rowid = self.rowid_list[self.index]
        self.set_current_word_into_query(current_rowid)

        # avoid confusion
        self.review_checkBox.setChecked(False)



    def dont_know_the_word(self):
        self.review_checkBox.setChecked(True)

        self.go_to_page_3()



    def go_to_page_2(self):
        self.vocTest_stackedWidget.setCurrentIndex(1)




    def go_to_page_3(self):
        current_rowid = self.rowid_list[self.index]
        self.final_textBrowser_showcase(current_rowid)


        self.vocTest_stackedWidget.setCurrentIndex(2)

    def pg3_go_to_page_1(self):

        # check user's choice on review box
        if self.review_checkBox.isChecked() :
            # add the current word's rowid number to the rowid_list
            self.rowid_list.append(self.rowid_list[self.index])
            # in this case, user can review it later (no need to restart VocTest window)

        self.to_next_word()
        self.vocTest_stackedWidget.setCurrentIndex(0)


    def info_label_show(self, current_word_count, remaining_words_count):
        self.vocTest_info_label.setText("Done: " + str(current_word_count) + "   " + " Remaining words: " + str(remaining_words_count))

    def final_textBrowser_showcase(self,rowid):
        self.showAll_textbrowser.clear()

        db = sqlite3.connect("wordwizard_database.db")
        cursor = db.cursor()

        cursor.execute("SELECT wordsName, type, explanation , sentence , source FROM words WHERE rowid = ?", (rowid,))
        wordObject = cursor.fetchone()
        db.close()

        # set the textBrowser
        self.showAll_textbrowser.append("<h1>" + wordObject[0] + "</h1>")
        self.showAll_textbrowser.append("<h2>" + wordObject[1] + "</h2>")
        self.showAll_textbrowser.append("<p>" + wordObject[2] + "</p>")
        self.showAll_textbrowser.append("<p style='font-style: italic;'>{}</p>".format(wordObject[3]))
        self.showAll_textbrowser.append("<p style='color: blue;'>{}</p>".format(wordObject[4]))





app = QApplication(sys.argv)
window = Window()
window.show()
app.exec_()