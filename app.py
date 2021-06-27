import firebase_admin
from firebase_admin import auth, credentials, firestore
from flask import Flask,jsonify,render_template,request
import json

##----------------firebase initialization--------------##


cred = credentials.Certificate("library.json")
firebase_admin.initialize_app(cred)
store = firestore.client()

##-----------------------------------------------------##


##-----------------Flask initialization-----------------##

app = Flask(__name__)

##------------------------------------------------------##


@app.route('/addBooks',methods=['GET','POST'])
def addBooks():
    book = {}
    if request.method == "POST":

        book["name"] = request.form["Name"]
        book["Author"] = request.form["author"]
        book["copies"] = request.form["copy"]
        book["publication_date"] = request.form["Date"]
        book["Available"] = request.form["available"]

    store.collection("BOOKS").add(book)

    return render_template("book.html")


@app.route('/userRecord',methods=['GET','POST'])
def total_users():
    total={}
    docs = store.collection("SLOTS").stream()
    for doc in docs:
        total["Slot"] = doc.to_dict().get("slot")
        total["Students"] = 0
        store.collection("total_users").add(total)




@app.route('/addSlots',methods=['GET','POST'])
def times():
    dit = {}
    if request.method == "POST":
        dit["slot"] = request.form["time"]
        dit["free_slot"] = bool(request.form["slot_avail"])

    store.collection("SLOTS").add(dit)

    return render_template("slot.html")


@app.route('/issue',methods=['GET','POST'])
def issue_book():
    record_lst=[]
    record={}
    dit={}
    new_slot={}
    if request.method == "POST":
        your_name = request.form["Name"]
        Name = request.form["Book"]
        ncopy = int(request.form["copy"])
        Author = request.form["author"]
        book_search = store.collection("BOOKS").stream()
        for doc in book_search:
            if doc.to_dict().get("name") == Name and (doc.to_dict().get("Author") == Author and doc.to_dict().get("copies") != 0):
                #print("Book found")
                ID = doc.id
                dit = doc.to_dict()
                dit["copies"] = dit["copies"]-ncopy
                if dit["copies"] == 0:
                    dit["Available"] = False
                store.collection("BOOKS").document(ID).update(dit)


                time = firestore.SERVER_TIMESTAMP
                record["Issuer_name"] = your_name
                record["Book_name"] = Name
                record["Author"] = Author
                record["Date of issue"] = time
                record["Copies_issued"] = ncopy
                slots = store.collection("SLOTS").stream()
                for slot in slots:
                    if slot.to_dict().get("free_slot") == True:
                        record["Slot_assigned"] = slot.to_dict().get("slot")
                        id = slot.id
                        new_slot = slot.to_dict()
                        users = store.collection("total_users").stream()
                        for user in users:
                            if user.to_dict().get("Slot") == record["Slot_assigned"]:
                                dit2 = user.to_dict()
                                dit2["Students"] = dit2["Students"] + 1
                                store.collection("total_users").document(user.id).update(dit2)
                                if dit2["Students"] == 2:
                                    new_slot["free_slot"] = False
                                    store.collection("SLOTS").document(slot.id).update(new_slot)
                                break
                            break

                    break

        if record == None:
            return {"message":"No book found for your interest, get back after 7 days"}
        else:
            record_lst.append(record)
            store.collection("USER_RECORD").add(record)
    
    return render_template("issue.html",RECORDS = record_lst)


if __name__ == '__main__':
    app.run(host="127.0.0.1",port="5000",debug=False)