from flask import Flask, render_template, redirect , request ,  url_for, flash, jsonify , session
import json
import os
import time
import business_interface
import system_interface
from business_interface import AggregatedGraphs,ChatBotAPI
from system_interface import ReadFiles,DatabaseHandler
import system_interface.ReadFiles
import system_interface.DatabaseHandler
from functools import wraps

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = "your_unique_and_secret_key"
folder_to_save_csv="Uploads"



def login_required(function):
    @wraps(function)
    def check_if_user_is_signed_in(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('Login'))
        return function(*args, **kwargs)
    return check_if_user_is_signed_in


@app.route("/Register",methods=["GET","POST"])
def Register():
    return render_template("Register.html")

@app.route("/ProcessRegister",methods=["GET","POST"])
def ProcessRegister():
    try:
        username = request.form["Username_Register"]
        email = request.form["Email_Register"]
        forename = request.form["Forename_Register"]
        password = request.form["Password_Register"]

        print(username, email)
        databasehandler_obj=DatabaseHandler.DatabaseOperations()
        databasehandler_obj.create_connection()

        if not databasehandler_obj.check_uniqueness((username,),"username"):
            flash(f"Error Username has been used before, Pick a different one", "success")
            return redirect(url_for("Register"))
        if not databasehandler_obj.check_uniqueness((email,),"email"):
            flash(f"Error Email has been used before, Pick a different one", "success")
            return redirect(url_for("Register"))
        databasehandler_obj.CreateUser((username,email,forename,password,1))
    except Exception as e:
       print("Exception happened inside ProcessRegister",e)
       return redirect(url_for("Register"))
    session['username']=username
    session['role']="Guest"
    # session['permission']=[
    #             'HomePage',
    #             'RawData',
    #             'ImportantFeatures',
    #             'UploadData',
    #             'PredictMachineLearning',
    #             'TrainMachineLearning',
    #             'ManageAccounts',
    #             # 'Chat',
    # ]
    permission_list=databasehandler_obj.get_permission_list((session['role'],))
    session['permission']=[x[0] for x in permission_list]
    return redirect(url_for("HomePage"))



@app.route("/Login",methods=["GET", "POST"])
def Login():
    return render_template("Login.html")


@app.route("/ProcessLogin",methods=["GET", "POST"])
def ProcessLogin():
    databasehandler_obj=DatabaseHandler.DatabaseOperations()
    databasehandler_obj.create_connection()
    password = request.form["Password_Register"]
    username = request.form["Username_Register"]
    if  databasehandler_obj.check_password_and_username((username,password)):
        flash(f"Error Username or Password is incorrect", "success")
        return redirect(url_for("Login"))
    print("LOGIN DETAILS",databasehandler_obj.check_password_and_username((username,password)))
    session['username']=username
    session['role']=databasehandler_obj.get_user_role((username,))
    print("session role is",session['role'])
    permission_list=databasehandler_obj.get_permission_list((session['role'],))
    session['permission']=[x[0] for x in permission_list]
    # session['permission']=[
    #             'HomePage',
    #             'RawData',
    #             'ImportantFeatures',
    #             'UploadData',
    #             'PredictMachineLearning',
    #             'TrainMachineLearning',
    #             'ManageAccounts',
    #             'Chat',
    # ]
    return redirect(url_for("HomePage"))

@app.route("/RestPassword")
def RestPassword():
    return render_template("RestPassword.html")

@app.route("/RestPasswordProcess",methods=["GET", "POST"])
def RestPasswordProcess():
    Email = request.form["Email_Register"]
    if Email!="Ziad":
        flash(f"Error Details are incorrect", "success")
        return redirect(url_for("RestPassword"))
    
    return redirect(url_for("HomePage"))








@app.route("/RawData")
@login_required
def RawData():
    # rows=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    rows=ReadFiles.ReturnAllRecords()
    print("rows received!")
    current_page = request.args.get('page', 1, type=int)
    max_content = 8

    total_items = len(rows)
    total_pages = (total_items + max_content - 1) // max_content
    rows = rows[(current_page - 1) * max_content : (current_page - 1) * max_content + max_content]

    return render_template("RawData.html", rows=rows, current_page=current_page, total_pages=total_pages)


@app.route("/AggregationData")
@login_required
def AggregatedData():
    dataframe=ReadFiles.ReturnDataFrame()

    temperature_axilla_table=AggregatedGraphs.GetAggregatedTables(dataframe,'Axilla Temperature')
    SkinTemp_table=AggregatedGraphs.GetAggregatedTables(dataframe,'SkinTemp (Core)')
    respiratory_rate_table=AggregatedGraphs.GetAggregatedTables(dataframe,'*RR')
    heart_rate_table = AggregatedGraphs.GetAggregatedTables(dataframe,'*HR')
    FiO2_table= AggregatedGraphs.GetAggregatedTables(dataframe,'*FiO2')
    VentilationMode_table= AggregatedGraphs.GetAggregatedTables(dataframe,'Ventilation Mode')
    Pinsp_table = AggregatedGraphs.GetAggregatedTables(dataframe,'Pinsp (set PIP)')
    PEEP_table = AggregatedGraphs.GetAggregatedTables(dataframe,'Set PEEP (or CPAP)')
    length_of_stay_table= AggregatedGraphs.GetLengthOfStay(dataframe)
    number_of_data_instances= AggregatedGraphs.GetNumberOfDataInstances(dataframe)
    start_and_end_date = AggregatedGraphs.GetStartAndEndDate(dataframe)
    most_recent_patient = AggregatedGraphs.GetMostRecentPatient(dataframe)
    longest_length_of_stay_patient = AggregatedGraphs.GetLongestLengthOfStay(dataframe)
    return render_template("AggregationData.html",temperature_axilla_table=temperature_axilla_table,SkinTemp_table=SkinTemp_table\
                           ,respiratory_rate_table=respiratory_rate_table,heart_rate_table=heart_rate_table,FiO2_table=FiO2_table\
                           ,VentilationMode_table=VentilationMode_table, Pinsp_table=Pinsp_table,PEEP_table=PEEP_table\
                           ,number_of_data_instances=number_of_data_instances, start_and_end_date=start_and_end_date,\
                           most_recent_patient=most_recent_patient,longest_length_of_stay_patient=longest_length_of_stay_patient,\
                           length_of_stay_table=length_of_stay_table)



@app.route('/SearchPatient',methods=['GET'])
def SearchPatient():
    PatientID = request.get_json()
    PatientData=ReadFiles.ReturnPatientData(PatientID)


@app.route("/")
@login_required
def HomePage():
    if session['permission'] == []:
        return render_template('GuestPage.html')

    #term dataset means a dictionary including both labels and values

    dataframe=ReadFiles.ReturnDataFrame()
    gender_dataset=AggregatedGraphs.GetGenderDetails(dataframe)
    male_percentage,female_percentage=AggregatedGraphs.GetGenderPercentage(dataframe)
    features=AggregatedGraphs.GetAllAggregatedChartsDataset(dataframe)
    
    medicine_name, medicine_percentage = AggregatedGraphs.GetMedicalNameAndPercentage(dataframe,"DrugName")
    dose_name, dose_percentage = AggregatedGraphs.GetMedicalNameAndPercentage(dataframe,"DoseFormName")
    route_name, route_percentage = AggregatedGraphs.GetMedicalNameAndPercentage(dataframe,"RouteName")
    average_length_of_stay=AggregatedGraphs.GetAverageLengthOfStay(dataframe)
    return render_template("HomePage.html",features=features,gender_dataset=gender_dataset,male_percentage=male_percentage,female_percentage=female_percentage\
                           ,medicine_name=medicine_name,medicine_percentage=medicine_percentage,dose_name=dose_name,dose_percentage=dose_percentage\
                            ,route_name=route_name, route_percentage=route_percentage,average_length_of_stay=average_length_of_stay)


@app.route("/UpdateHomePageCharts",methods=["GET", "POST"])
def UpdateHomePageCharts():

    feature_name = request.get_json()
    print(feature_name)
    time.sleep(1)
    dataframe=ReadFiles.ReturnDataFrame()
    dataset=AggregatedGraphs.GetAggregatedChartsDataset(dataframe, feature_name)
    print("Dataset is:", dataset)
    return jsonify(dataset)



@app.route("/UploadData",methods=["GET", "POST"])
@login_required
def UploadData():
    return render_template("UploadData.html")

@app.route("/UploadDataProcess", methods=["GET", "POST"])
def UploadDataProcess():
    try:
        file = request.files["file"]
        file.save(os.path.join("Uploads",file.filename))
        print("file name is",file.filename)
        time.sleep(4)
    except Exception as e:
        print("Error Exception happened in UploadDataProcess",e)
        return jsonify({"UploadStatus": "Error has occurred"})

    return jsonify({"UploadStatus": "File has been uploaded successfully "})



@app.route("/ResearchPapers",methods=["GET", "POST"])
@login_required
def ResearchPapers():
    return render_template("ResearchPapers.html")


@app.route("/ChatBot",methods=["GET", "POST"])
@login_required
def ChatBot():
    return render_template("ChatBot.html")



@app.route("/ChatBotPrompt",methods=["GET", "POST"])
def ChatBotPrompt():
    print("not executing?")
    current_prompt = request.get_json()
    print("current_prompt is",current_prompt["prompt"])
    chatTreePrompt_obj=ChatBotAPI.ChatTreePrompt("root")
    all_nodes=chatTreePrompt_obj.return_all_nodes()
    options=chatTreePrompt_obj.search_for_node(current_prompt["prompt"],all_nodes)
    if options == []:
        print("options is None")
        return jsonify({"AskPrompt": current_prompt["prompt"],"options": ["Help me"]})
    else:
        return jsonify({"options": options})

@app.route("/ChatBotResponse",methods=["GET", "POST"])
def ChatBotResponse():
    message = request.get_json()
    print("message is",message)
    chatBot_obj=ChatBotAPI.ChatBotAPI_Handler()

    chatbot_response = chatBot_obj.GetResponseFromBot(message["message"])
    print("chatbot response is",chatbot_response)
    return jsonify({"chatbot_response": chatbot_response})


@app.route('/ManageAccounts',methods=["GET", "POST"])
@login_required
def ManageAccounts():
    # all_accounts =[
    #     [21,'Jane Doe1','janedoe@gmail.com','Unknown','Guest'],
    #     [333,'Mark Doe2','markdoe@gmail.com','Unknown','Guest'],
    #     [12,'John Doe3','johndoe@gmail.com','Unknown','Guest'],
    #     [233,'Jane Doe4','janedoe@gmail.com','Unknown','Guest'],
    #     [34444,'Mark Doe5','markdoe@gmail.com','Unknown','Guest'],        
    #     [22123,'Jane Doe6','janedoe@gmail.com','Unknown','Guest'],
    #     [3123,'Mark Doe7','markdoe@gmail.com','Unknown','Guest'],       
    #     [12312,'Jane Doe8','janedoe@gmail.com','Unknown','Guest'],
    #     [2223,'Mark Doe9','markdoe@gmail.com','Unknown','Guest'],    
    #     [4442,'Jane Doe10','janedoe@gmail.com','Unknown','Guest'],
    #     [35124,'Mark Doe11','markdoe@gmail.com','Unknown','Guest'],
    # ]
    databasehandler_obj=DatabaseHandler.DatabaseOperations()

    all_accounts=databasehandler_obj.get_all_rows("select * from user_and_role")
    guest_numbers=databasehandler_obj.get_role_count("select * from user_and_role where rolename='Guest'")
    nurse_numbers=databasehandler_obj.get_role_count("select * from user_and_role WHERE rolename='Nurse'")
    doctor_numbers=databasehandler_obj.get_role_count("select * from user_and_role WHERE rolename='Doctor'")
    return render_template("ManageAccounts.html",all_accounts=all_accounts,guest_numbers=guest_numbers,nurse_numbers=nurse_numbers,doctor_numbers=doctor_numbers)


@app.route('/UpdateAccount', methods=['GET','POST'])
def UpdateAccount():
    account_details = request.get_json()

    databasehandler_obj=DatabaseHandler.DatabaseOperations()
    all_roles={"Nurse":2,"Doctor":3,"Guest":1}
    account_id = account_details["userid"]
    username = account_details["username"]
    email = account_details["email"]
    forename = account_details["forename"]
    role = account_details["role"]
    role=all_roles[role]
    parameters=(username, email, forename ,role,account_id)
    print("para are",parameters)
    query="""
    UPDATE user
    SET username = %s, email = %s, forname = %s, roleid_fk = %s
    WHERE userid = %s

    """
    databasehandler_obj.update_user(query,parameters)
    return jsonify({"status": "success"})

@app.route('/DeleteAccount', methods=['GET','POST'])
def DeleteAccount():
    account_details = request.get_json()

    databasehandler_obj=DatabaseHandler.DatabaseOperations()
    query="DELETE FROM user WHERE userid = %s"
    account_id=account_details['userid']
    parameters=(account_id,)
    databasehandler_obj.update_user(query,parameters)
    return jsonify({"status": "success"})


@app.route('/Notification', methods=['GET', 'POST'])
def Notification():
    databasehandler_obj=DatabaseHandler.DatabaseOperations()
    guest_numbers=databasehandler_obj.get_role_count("select * from user_and_role where rolename='Guest'")

    return jsonify({"numberOfNotifications": guest_numbers})

@app.route('/SignOut', methods=['GET', 'POST'])
def SignOut():
    session.pop('username', None)
    session.pop('role', None)
    session.pop('permission', None)
    return redirect(url_for('Login'))

@login_required
@app.route('/TrainMachineLearning', methods=['GET', 'POST'])
def TrainMachineLearning():
    return render_template('TrainMachineLearning.html')


if __name__ == "__main__":
    app.run(debug=True)
