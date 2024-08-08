import sys
import requests
import zipfile
import io
import pandas as pd
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


try:
    def process_url_and_recipients(url, recipients, email, password):
        # Step 1: Request the URL
        print(f"Processing URL: {url}")
        print(f"Recipients: {recipients}")
        print(f"Recipients: {email}")
        print(f"Recipients: {password}")
        # Your processing logic here
    
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
    
        # Step 2: Read the ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Step 3: Extract and read each CSV file into a DataFrame
            dataframes = {}
            for filename in z.namelist():
                if filename.endswith('.csv'):
                    with z.open(filename) as f:
                        df_name = filename.split('/')[-1].split('.')[0]  # Use the filename without extension as the key
                        dataframes[df_name] = pd.read_csv(f)
    
        # Store each DataFrame with its respective name
        for df_name, df in dataframes.items():
            globals()[df_name] = df
    
    
        email_df = []
        sms_df = []
        whatsapp_df = []
        pn_df =[]
    
        ###################################################################################################################################
    
        for name, df in dataframes.items():
            if '_EMAIL_' in name:
                if df["Total Sent"].sum() >0:
                    dataframes[name] = df[["Total Sent", "Total Delivered", "Total Open", "Unique opens", "Total clicks", "Unique clicks", "Total Hard bounces", "Total Soft bounces", "Unsubscribes", "Complaints" , "Campaign Delivery Type"]]
                    column_sums = dataframes[name].sum()
                    dataframes[name] = pd.DataFrame([column_sums], columns=column_sums.index)
                    dataframes[name]["Delivery Rate"] = ((dataframes[name]["Total Delivered"]/dataframes[name]["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Open Rate"] = ((dataframes[name]["Total Open"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Unique Open Rate"] = ((dataframes[name]["Unique opens"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Click Rate"] = ((dataframes[name]["Total clicks"]/dataframes[name]["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Unique Click Rate"] = ((dataframes[name]["Unique clicks"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["CTOR"] = ((dataframes[name]["Unique clicks"]/dataframes[name]["Unique opens"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Hard Bounce Rate"] = ((dataframes[name]["Total Hard bounces"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Soft Bounce Rate"] = ((dataframes[name]["Total Soft bounces"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Unsubscribe Rate"] = ((dataframes[name]["Total Soft bounces"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Complaints Rate"] = ((dataframes[name]["Complaints"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Channel"] = np.where(dataframes[name]["Campaign Delivery Type"].str.contains("Flows"), "Email Flows", "Email Campaign")
                    dataframes[name] = dataframes[name].drop(columns=["Campaign Delivery Type"])
                    email_df.append(dataframes[name])
                else:
                    pass
                
        if len(email_df)>0:
            email_df = pd.concat(email_df, ignore_index=True)
            email_df_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate" , "Total Open" , "Open Rate" , "Unique opens" , "Unique Open Rate", "Total clicks" , "Click Rate" , "Unique clicks", "Unique Click Rate" , "CTOR" , "Total Hard bounces", "Hard Bounce Rate", "Total Soft bounces", "Soft Bounce Rate", "Unsubscribes", "Unsubscribe Rate", "Complaints", "Complaints Rate"]  # Adjust with your actual column names
            email_df = email_df[email_df_column_order]
        else:
            pass
        #email_df.to_csv("email_df.csv")
    
    
        #####################################################################################################################################
    
        for name, df in dataframes.items():
            if '_SMS_' in name:
                if df["Sent"].sum() >0:
                    dataframes[name] = df[["Sent", "Total Delivered", "Clicks", "Campaign Delivery Type"]]
                    column_sums = dataframes[name].sum()
                    dataframes[name] = pd.DataFrame([column_sums], columns=column_sums.index)
                    dataframes[name]["Delivery Rate"] = ((dataframes[name]["Total Delivered"]/dataframes[name]["Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Click Rate"] = ((dataframes[name]["Clicks"]/dataframes[name]["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Channel"] = np.where(dataframes[name]["Campaign Delivery Type"].str.contains("Flows"), "SMS Flows", "SMS Campaign")
                    dataframes[name] = dataframes[name].drop(columns=["Campaign Delivery Type"])
                    sms_df.append(dataframes[name])
                else:
                    pass
                
        if len(sms_df)>0:
            sms_df = pd.concat(sms_df, ignore_index=True)
            sms_df_column_order = ["Channel", "Sent", "Total Delivered", "Delivery Rate" , "Clicks" , "Click Rate" ]  # Adjust with your actual column names
            sms_df = sms_df[sms_df_column_order]
            sms_df = sms_df.rename(columns= {"Sent": "Total Sent", "Clicks": "Total clicks"})
            #sms_df.to_csv("sms_df.csv")
        else:
            pass
    
    
        ######################################################################################################################################
    
        for name, df in dataframes.items():
            if '_WHATSAPP_' in name:
                if df["Total Sent"].sum() >0:
                    dataframes[name] = df[["Total Sent", "Total Delivered", "Total Read", "Total clicks", "Unique clicks", "Campaign Delivery Type"]]
                    column_sums = dataframes[name].sum()
                    dataframes[name] = pd.DataFrame([column_sums], columns=column_sums.index)
                    dataframes[name]["Delivery Rate"] = ((dataframes[name]["Total Delivered"]/dataframes[name]["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Open Rate"] = ((dataframes[name]["Total Read"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Click Rate"] = ((dataframes[name]["Total clicks"]/dataframes[name]["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Unique Click Rate"] = ((dataframes[name]["Unique clicks"]/dataframes[name]["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Channel"] = np.where(dataframes[name]["Campaign Delivery Type"].str.contains("Flows"), "WhatsApp Flows", "WhatsApp Campaign")
                    dataframes[name] = dataframes[name].drop(columns=["Campaign Delivery Type"])
                    whatsapp_df.append(dataframes[name])
                else:
                    pass
                
    
        if len(whatsapp_df)>0:
            whatsapp_df = pd.concat(whatsapp_df, ignore_index=True)
            whatsapp_df_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate", "Total Read", "Open Rate", "Total clicks", "Click Rate", "Unique clicks", "Unique Click Rate" ]  # Adjust with your actual column names
            whatsapp_df = whatsapp_df[whatsapp_df_column_order]
            whatsapp_df = whatsapp_df.rename(columns= {"Total Read": "Total Open"})
            #whatsapp_df.to_csv("whatsapp_df.csv")
        else:
            pass
    
    
        ###############################################################################################################################################
    
        for name, df in dataframes.items():
            if '_PUSH_' in name:
                if df["All Platform Sent"].sum() >0:
                    dataframes[name] = df[["All Platform Sent", "All Platform Impressions", "All Platform Clicks", "Campaign Delivery Type"]]
                    column_sums = dataframes[name].sum()
                    dataframes[name] = pd.DataFrame([column_sums], columns=column_sums.index)
                    dataframes[name]["Delivery Rate"] = ((dataframes[name]["All Platform Impressions"]/dataframes[name]["All Platform Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Click Rate"] = ((dataframes[name]["All Platform Clicks"]/dataframes[name]["All Platform Impressions"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    dataframes[name]["Channel"] = np.where(dataframes[name]["Campaign Delivery Type"].str.contains("Flows"), "PN Flows", "PN Campaign")
                    dataframes[name] = dataframes[name].drop(columns=["Campaign Delivery Type"])
                    pn_df.append(dataframes[name])
                else:
                    pass
                
        if len(pn_df)>0:
            pn_df = pd.concat(pn_df, ignore_index=True)
            pn_df_column_order = ["Channel", "All Platform Sent", "All Platform Impressions", "Delivery Rate" , "All Platform Clicks" , "Click Rate" ]  # Adjust with your actual column names
            pn_df = pn_df[pn_df_column_order]
            pn_df = pn_df.rename(columns= {"All Platform Sent": "Total Sent", "All Platform Impressions" : "Total Delivered", "All Platform Clicks" :"Total clicks"})
            #pn_df.to_csv("pn_df.csv")
        else:
            pass
    
    
        #########################################################################################################################################
    
        #concating all dataframes
    
        list = [email_df,sms_df,whatsapp_df,pn_df]
    
        Summary = pd.DataFrame()
        for i in list:
            if len(i)>0:
                Summary = pd.concat([Summary,i], ignore_index=True)
                
        Summary = Summary.replace("nan%", "")
        csv_file = 'Summary.csv'
        Summary.to_csv("Summary.csv", index = False)
    
        # Email configuration
        sender_email = email
        receiver_email = email
        email_list = recipients.split(',')
        cc_emails = email_list
        password = password  # Consider using an app password or environment variable for better security
        subject = 'Hey, Your Summary Report Is Ready!'
        body = 'Please find the attached report'
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Cc'] = ",".join(cc_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the CSV file
        attachment = open(csv_file, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {csv_file}')
        msg.attach(part)
        attachment.close()
    
        # Prepare the email addresses for sending
        all_recipients = [receiver_email] + cc_emails
        
        # Send the email
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, all_recipients, text)
            print('Email sent successfully.')
        except Exception as e:
            print(f'Error: {e}')
            sender_email = 'sahil@0101.today'
            password = 'zigcmfglmxthdvtn'
            recipient_email = email
            subject = "Incorrect Password Entered – Please Try Again"
            body = "Hi, the password you entered to generate the report was incorrect. Please try again with the correct password."
    
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient_email
    
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()  # Upgrade the connection to secure
                server.login(sender_email, password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print("Email sent successfully!")
            except Exception as e:
                print(f"Failed to send email: {e}")
            finally:
                server.quit()
                    
        finally:
            server.quit()

    if __name__ == '__main__':
        url = sys.argv[1]
        recipients = sys.argv[2]
        email = sys.argv[3]
        password = sys.argv[4]
        process_url_and_recipients(url, recipients, email, password)

except Exception as e:
    print(f'Error: {e}')
    sender_email = 'sahil@0101.today'
    password = 'zigcmfglmxthdvtn'
    recipient_email = email
    subject = "Error Occured – Please Try Again"
    body = "f'Error: {e}'"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")



