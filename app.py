from types import NoneType
from flask import Flask, render_template, request, Response, send_from_directory, url_for, send_file
from flask_wtf.csrf import CSRFProtect
import flask
import docx2pdf
from docxtpl import DocxTemplate , RichText
from docx2pdf import convert
import pythoncom
import subprocess
import time
import datetime
import json
import urllib.request as req
import requests
import os, sys

app = Flask(__name__)
csrf = CSRFProtect()

status = ""

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1

#These are the main routes 
@csrf.exempt
@app.route('/ABN' , methods=['GET' ,  'POST'])
def ABN():

    status="Search for an ABN"

    if 'ABN' in request.args:

        ABN = request.args.get('ABN' , "None")

        print(ABN)


            
        response = requests.get("https://abr.business.gov.au/json/AbnDetails.aspx?abn=" + ABN + "&callback=callback&guid=d2dd8255-a45a-4868-8c45-45a82e863dc6")
        status = json.loads(response.text.strip("Callback( )"))

        if status["Message"] == "Search text is not a valid ABN or ACN":
            for i in status:
                status[i] = "ABN searched is not active / real"

    return render_template("ABN.html" , lookup=status)

   
    




@app.route('/' , methods=['GET', 'POST'])
def hello():
    return render_template("Index.html")

@app.route('/Lodgement')
def Lodgement():
    return render_template("LodgementLetter.html")


@app.route('/KM')
def KMPages():
    return render_template("KMPages.html")


@app.route('/SN')
def SN():
    return render_template("SN.html")

@app.route('/bom')
def bom():
    return render_template("bom.html")

@app.route('/TemplatesPage')
def Templates():
    return render_template("TemplatesPage.html")

@app.route('/Limits')
def Limits():
    return render_template("Limits.html")

@app.route('/XS')
def XS():
    return render_template("XS.html")






@app.route('/accounting')
def Accounting():
    return render_template("ACC.html")

@app.route('/resources')
def resources():
    return render_template("resourcehome.html")











#This is the lodgement letter functionality

def SetClaimText(index, extra):
    match index:
        case 0:
            ClaimTypeText = ("If you need additional support or assistance in dealing with us due to your personal circumstances "
                            "and you are comfortable, you can tell us about your situation, and we will work with you to arrange support. This could be due to your physical or mental health, family or financial situation or cultural background."
                            "\a\nplease do not dispose of any damaged items without our consent unless you cannot contact us and it is necessary for health and safety reasons. Please also do not complete or authorise any repairs unless you cannot "
                            "contact us and need to make emergency repairs to protect the building or it is necessary for health and safety reasons.\a"+ extra + "\n")

        case 1:
            ClaimTypeText = ("If you have obtained a plumber’s report or quote which specifies the cause of the damage,"
                            " please ensure that it is on the plumbing company’s letterhead with their contact details and ABN displayed.\a\n"
                            "The report or quote should be itemised to show the item(s) that were repaired/replaced and the cost.\a\nOur policy also covers exploratory works to find the source of the escaping liquid if this hasen't been done so. Please consult the relevant policy book for more details.\a\n") + extra + "\n"
        case 2:
                
            ClaimTypeText = ("We are now in the process of reviewing your claim and determining the next steps from here. Please do not dispose of any damaged items or complete " 
                            "any repairs unless authorised by us first \a\n the situation needs be assessed by us beforehand unless there is urgent need to rectify or dispose of damage items/goods "
                "In which case please provide sufficient photos and reports for us to review and validate + model numbers for any electronic items\a")+ extra + "\n"
        case 3:
            ClaimTypeText = ("We are now in the process of reviewing your claim. Below there is a table that indicates the rental documents required for your claim to progress "
            "Please forward these documents as soon as possible for us to continue the process.\a") + extra + "\n"
        
        case 4:
            ClaimTypeText = "There are some important updates for you to be aware of that are listed below:\a\n"+ extra + "\n"
        case 5:
            ClaimTypeText = """Thank you for lodging your theft claim with us today. Your claim is currently with out claims team for review. Please begin collating a list of items that have been taken for us to review. \a\nIf you feel that your property is unsecure in any way, please let us know and we can arrange assistance. \a\nThe next step for your claim is gathering evidence of ownership. What we can accept as evidence of ownership is listed below\a""" + extra + "\n"
        case 6:
            ClaimTypeText = "Thank you for lodging a claim with us today. We have sent the claims to our review team and will be in touch as soon as possible. please do not dispose of any damaged items without our consent unless you cannot contact us and it is necessary for health and safety reasons. Please also do not complete or authorise any repairs unless you cannot contact us and need to make emergency repairs to protect the building or it is necessary for health and safety reasons.\a " + extra + "\n"
        case 7:
            ClaimTypeText = "Thank you for lodging a claim with us today. Your claim has been sent off to our claims teams for review. If your claim relates to third party driver damage, so long as you can provide us with: \nA) The registration of the vehicle \nB) The full name and address of the driver \n or \nC) A police report number that will contain these details. \n We will waive your excess. \nPlease do not dispose of any damaged items or perform any repairs until we can assess the situation." + extra + "\n"
        case 8: 
            ClaimTypeText = "Thank you for lodging a claim for motor burnout with us today. The claim has been sent to our claims team for review and we will determine the next steps. Please ensure you view the relevant product disclosure statement for your full coverage conditions." + extra + "\n"
        case 9:
            ClaimTypeText = "Thank you for lodging a home assist call out with us today. HomeRepair (Building company) will be in touch shortly to assist with your home emergency. Please find there contact details below" + extra + "\n"
            
    return ClaimTypeText

def OpeningSentence(dets):
  String = ""
  if dets['Loss'] == 4:
      String = "We are contacting you regarding your existing claim. Claim number: " + dets["Claim"] + ""
  else:
      String = "Thank you for lodging your claim with " + dets['Brand'] + ". Your claim number is " + dets["Claim"] + ". Please see below important next steps and contact details for your claim."
  return String
  
def More(dets):
    #Clain all of this text up so it is presentable
    String = ""
    if dets['EOO'] is True:
        String += """You will need to provide evidence of ownership for your items. If you do not have evidence of an item please provide details such as where, when and how much you purchased the item for.\n
Evidence of ownership that we may accept can vary depending on the value of the item being claim. The most common types being: Receipts of purchase / banks statements, Original boxes / manuals, valuations.
Please consult with one of our specialist in regards to what we can accept\a\n"""
    if dets['IA'] is True: 
        String += "An assessor has been appointed to your claim and will be in contact to organise a suitable to perform an assessment\a\n"
    if dets['PR'] is True:
        String += """If you haven’t already provided a police report number, please send notify us.\a\n"""
    if dets['RR'] is True:
        String += """To progress your claim please obtain a repair report and quote for the damage as per the below requirements.\n 
        Evidence:
        1. A report that states the cause of the damage
        2. Name, address and ABN of the business that supplied the report/quote
        3. Itemised quote for repair or replacement cost, including GST
        4. Clear photos of the damage
        For contents:
        Include Make/Model and detailed specifications of the item (Serial number/IMEI)
                """       
    return String
  
def Jobs(dets):
  VendorsList = dets["Vendors"]
  if len(VendorsList) == 0:
      return ""
  else:
      RTT = ""
      JobString = "We've appointed the following vendor(s) to your claim. Below you will find important contact information \a\n"
      for v in VendorsList:
          rt = RichText()
          rt.add(v[0] ,bold=True , size= 23)
          rt.add(" will be in contact within ", size= 23)
          rt.add(v[1] , bold=True , size= 23)
          rt.add(" for ", size= 23)
          rt.add(v[2] , bold=True , size= 23)
          rt.add(" Phone: ", size= 23)
          rt.add(v[3] , bold=True , size= 23)
          rt.add("\n\n")
            
          RTT += str(rt)
    
      JobString += RTT   
      return JobString  
       
def XS(dets):
    if dets['XS'] != 0:
        temp = "Your Excess:" + """\nYour claim has an excess of $""" + dets["XS"] +  """, you must pay this before we finalise your claim; or the excess can be deducted from the amount we pay you for your claim (if any). You can visit the My Claim Manager portal on our website www.""" + dets['Brand'] +  """.com.au to pay your excess by credit card."""
        return temp
    else:
        return ""
    
def CM(dets):
    String = ""
    if dets['Loss'] != 4:
        if dets['Managed'] == 1:
            String = ("\nYour assigned Client Manager "+ dets["Management"][0] + " will"
                                 " contact you within "+ dets["Management"][2] +" for an introduction and will support you through "
                                 " your claim and answer any questions you have along the way. For any enquiries, you can contact them on " + dets["Management"][1] + ".\a")
        elif dets["Managed"] == 2: 
            String = ("\nas discussed with you, your claim has been allocated to one of our claim teams."
                                    " For any enquiries, you can contact us on "+ dets['Management'][0] + "\a")
        else:
            String = ""
    return String 










#This is the lodgement letter routing and JSON logic

@csrf.exempt
@app.route('/receive', methods=["POST" , "GET"])
def receive():
    
    if request.method == "POST":
        result = flask.request.get_json()

        document = DocxTemplate("BaseLetters/" + result['Brand']+".docx")
        
        document.render({
                "Brand" : result['Brand'],
                "Date": datetime.datetime.now().strftime("%x"),
                "Claim":result["Claim"],
                "Name":result["Greeting"].split(" " , 1)[1].upper(),#Use string manipulation for the name
                "Greeting": result["Greeting"], #This will be the main
                "Address":result["Address"].upper(),
                "CCTD":SetClaimText(result["Loss"] , result["ExtraNotes"]),
                "CMPlaceholder":CM(result),
                "First":OpeningSentence(result),
                "More":More(result),
                "Jobs":Jobs(result),
                "Excess":XS(result),
                "Policy":result["Policy"]
            })
            
        LandlordDocs = (
        ("Tenancy Agreement (valid and current at time of loss)", '✓', '', '✓'),
        ("Tenant Ledger of payments (confirming rent paid to date and evidence of rent received) ", '✓', '', '✓'),
        ("For a self-managed rental property, evidence of rent received may include: Bank statements showing the rental payment \nCopies of receipts issued to the tenant (if rent is paid in cash)\nNotice of Income Tax Assessment for rental income received from the property for the relevant period of the claim", '', '' , '✓'),
        ('Breach Notices or Tribunal/Court orders (evidence you have attempted to recover the rent/damages)' , '' , '', '✓'),
        ('Evidence of advertising, or New Tenancy Agreement (evidence that you have or intend to re-let property)' , '' , '', '✓'),
        ('Management agreement (if property is Agency Managed)' , '✓' , '', '✓'),
        ('Death Certificate' , '' , '', '✓'),
        ('Entry and exit Property Condition reports' , '' , '✓', ''),
        ('Bond Invoices' , '' , '✓', ''),
        ('Police report number (phone: 131 444 [Police Assistance Line]; otherwise obtain details of Police Officer spoken to:  name, police station, date/time, etc)' , '' , '✓', ''),
        ('List of damages/items stolen' , '' , '✓', ''),
        ('Photos (colour) of the malicious damage (clearly labelled highlighting malicious damaged areas)' , '' , '✓', ''),
        ('Evidence of contents items damaged/stolen' , '' , '✓', ''),
        ("Quotes, if you wish to provide your own (itemised & detailed), for impending repairs/replacements including:\nCompany name displayed on quote\n•ABN of repairer\n•Phone number of repairer\n•Itemised costs for each item repaired/replaced\n•Scope of the repairs (room by room)\n•Repairers opinion on cause of damage and why? " , '' , '✓', '')
    )
        
        
        if result['Loss'] == 3:
                
            document.add_page_break()
                
            table = document.add_table(rows=1, cols=4)
            table.style = 'Table Grid'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Information Required'
            hdr_cells[1].text = 'Loss of Rent Insured Event'
            hdr_cells[2].text = 'Loss of Rent Tenant Default'
            hdr_cells[3].text = 'Tenant Malicious damage / theft'
            for qty, id, desc, more in LandlordDocs:
                row_cells = table.add_row().cells
                row_cells[0].text = qty
                row_cells[1].text = id
                row_cells[2].text = desc
                row_cells[3].text = more
        
        print(result['Brand'])
        
        pythoncom.CoInitialize()
            
        document.save("letter.docx")



    


@app.route("/download")
def download():
    return send_file("Letter.docx", as_attachment=True)



	










#Run the webapp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
