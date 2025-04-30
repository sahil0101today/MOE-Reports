# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 09:29:18 2025

@author: sahil_pc
"""

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
    def process_url_and_recipients(url, recipients, TCHFL_FLAG, SERVICE_FLAG, password):
        
        EMAIL_SENT_COUNT_ZERO_CAMPAIGNS = 0
        SMS_SENT_COUNT_ZERO_CAMPAIGNS = 0
        WHATSAPP_SENT_COUNT_ZERO_CAMPAIGNS = 0
        PN_SENT_COUNT_ZERO_CAMPAIGNS = 0
        
        SMS_TEST_DF = []
        SMS_DF = []
        SMS_COMBINED_DF = []
        
        EMAIL_TEST_DF = []
        EMAIL_DF = []
        EMAIL_COMBINED_DF = []
        
        WHATSAPP_TEST_DF = []
        WHATSAPP_DF = []
        WHATSAPP_COMBINED_DF = []
        
        PN_TEST_DF = []
        PN_DF = []
        PN_COMBINED_DF = []
        
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
            
        
        sheet_id = "1m_BeiLm-PyXl5MUm-Ku64uMiy8b75IbYJIo5-n_brD8"
        sheet_name = "Sheet1"  # change as per your sheet
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"    
        billable_count_df = pd.read_csv(csv_url)
        billable_count_df = billable_count_df.groupby('Campaign ID')['BILLABLE COUNT'].sum().reset_index()
        
        #############################################################################################################
        
        for name, df in dataframes.items():
            if '_EMAIL_' in name:
                if df["Sent"].sum() >0:
                    if TCHFL_FLAG == "NO":
                        df = df[~df['Campaign Name'].str.contains('TCHFL', na=False)]
                    else:
                        df = df[df['Campaign Name'].str.contains('TCHFL', na=False)]
                        
                    df["COST"] = df["Total Sent"]*0.03
                    
                    zero_campaigns = df[df["Sent"] == 0].shape[0]
                    EMAIL_SENT_COUNT_ZERO_CAMPAIGNS = EMAIL_SENT_COUNT_ZERO_CAMPAIGNS + zero_campaigns
                    
                    #Summary creation test
                    df_test = df
                    df_test = df_test[df_test['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_test = df_test[["Total Sent", "Total Delivered", "Total Open", "Unique opens", "Total clicks", "Unique clicks", "Total Hard bounces", "Total Soft bounces", "Unsubscribes", "Complaints" , "Campaign Delivery Type"]]
                    column_sums = df_test.sum()
                    df_test = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_test["Delivery Rate"] = ((df_test["Total Delivered"]/df_test["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Open Rate"] = ((df_test["Total Open"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Unique Open Rate"] = ((df_test["Unique opens"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Click Rate"] = ((df_test["Total clicks"]/df_test["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_test["Unique Click Rate"] = ((df_test["Unique clicks"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["CTOR"] = ((df_test["Unique clicks"]/df_test["Unique opens"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_test["Hard Bounce Rate"] = ((df_test["Total Hard bounces"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Soft Bounce Rate"] = ((df_test["Total Soft bounces"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Unsubscribe Rate"] = ((df_test["Total Soft bounces"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Complaints Rate"] = ((df_test["Complaints"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Campaign Delivery Type"] = df_test["Campaign Delivery Type"].astype(str)
                    df_test["Channel"] = np.where(df_test["Campaign Delivery Type"].str.contains("Flows"), "Email Flows", "Email Campaign")
                    df_test = df_test.drop(columns=["Campaign Delivery Type"])
                    
                    EMAIL_TEST_DF.append(df_test)
                    
                    # Actual Summary Creation 
                    df_copy = df
                    
                    df_copy = df_copy[~df_copy['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_copy = df_copy[["Total Sent", "Total Delivered", "Total Open", "Unique opens", "Total clicks", "Unique clicks", "Total Hard bounces", "Total Soft bounces", "Unsubscribes", "Complaints" , "Campaign Delivery Type"]]
                    column_sums = df_copy.sum()
                    df_copy = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_copy["Delivery Rate"] = ((df_copy["Total Delivered"]/df_copy["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Open Rate"] = ((df_copy["Total Open"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Unique Open Rate"] = ((df_copy["Unique opens"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Click Rate"] = ((df_copy["Total clicks"]/df_copy["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_copy["Unique Click Rate"] = ((df_copy["Unique clicks"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["CTOR"] = ((df_copy["Unique clicks"]/df_copy["Unique opens"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_copy["Hard Bounce Rate"] = ((df_copy["Total Hard bounces"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Soft Bounce Rate"] = ((df_copy["Total Soft bounces"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Unsubscribe Rate"] = ((df_copy["Total Soft bounces"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Complaints Rate"] = ((df_copy["Complaints"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Campaign Delivery Type"] = df_copy["Campaign Delivery Type"].astype(str)
                    df_copy["Channel"] = np.where(df_copy["Campaign Delivery Type"].str.contains("Flows"), "Email Flows", "Email Campaign")
                    df_copy = df_copy.drop(columns=["Campaign Delivery Type"])
                    
                    EMAIL_DF.append(df_copy)
                    
                    
                    # Combined Summary Creation 
                    df_combined = df
                    
                    df_combined = df_combined[["Total Sent", "Total Delivered", "Total Open", "Unique opens", "Total clicks", "Unique clicks", "Total Hard bounces", "Total Soft bounces", "Unsubscribes", "Complaints" , "Campaign Delivery Type"]]
                    column_sums = df_combined.sum()
                    df_combined = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_combined["Delivery Rate"] = ((df_combined["Total Delivered"]/df_combined["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Open Rate"] = ((df_combined["Total Open"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Unique Open Rate"] = ((df_combined["Unique opens"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Click Rate"] = ((df_combined["Total clicks"]/df_combined["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_combined["Unique Click Rate"] = ((df_combined["Unique clicks"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["CTOR"] = ((df_combined["Unique clicks"]/df_combined["Unique opens"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_combined["Hard Bounce Rate"] = ((df_combined["Total Hard bounces"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Soft Bounce Rate"] = ((df_combined["Total Soft bounces"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Unsubscribe Rate"] = ((df_combined["Total Soft bounces"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Complaints Rate"] = ((df_combined["Complaints"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Campaign Delivery Type"] = df_combined["Campaign Delivery Type"].astype(str)
                    df_combined["Channel"] = np.where(df_combined["Campaign Delivery Type"].str.contains("Flows"), "Email Flows", "Email Campaign")
                    df_combined = df_combined.drop(columns=["Campaign Delivery Type"])
                    
                    EMAIL_COMBINED_DF.append(df_combined)
                    
                else:
                    pass
                
        if len(EMAIL_TEST_DF)>0:
            EMAIL_TEST_DF = pd.concat(EMAIL_TEST_DF, ignore_index=True)
            EMAIL_TEST_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate" , "Total Open" , "Open Rate" , "Unique opens" , "Unique Open Rate", "Total clicks" , "Click Rate" , "Unique clicks", "Unique Click Rate" , "CTOR" , "Total Hard bounces", "Hard Bounce Rate", "Total Soft bounces", "Soft Bounce Rate", "Unsubscribes", "Unsubscribe Rate", "Complaints", "Complaints Rate"]  # Adjust with your actual column names
            EMAIL_TEST_DF = EMAIL_TEST_DF[EMAIL_TEST_DF_column_order]
        else:
            pass
        
        if len(EMAIL_DF)>0:
            EMAIL_DF = pd.concat(EMAIL_DF, ignore_index=True)
            EMAIL_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate" , "Total Open" , "Open Rate" , "Unique opens" , "Unique Open Rate", "Total clicks" , "Click Rate" , "Unique clicks", "Unique Click Rate" , "CTOR" , "Total Hard bounces", "Hard Bounce Rate", "Total Soft bounces", "Soft Bounce Rate", "Unsubscribes", "Unsubscribe Rate", "Complaints", "Complaints Rate"]  # Adjust with your actual column names
            EMAIL_DF = EMAIL_DF[EMAIL_DF_column_order]
        else:
            pass
        
        if len(EMAIL_COMBINED_DF)>0:
            EMAIL_COMBINED_DF = pd.concat(EMAIL_COMBINED_DF, ignore_index=True)
            EMAIL_COMBINED_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate" , "Total Open" , "Open Rate" , "Unique opens" , "Unique Open Rate", "Total clicks" , "Click Rate" , "Unique clicks", "Unique Click Rate" , "CTOR" , "Total Hard bounces", "Hard Bounce Rate", "Total Soft bounces", "Soft Bounce Rate", "Unsubscribes", "Unsubscribe Rate", "Complaints", "Complaints Rate"]  # Adjust with your actual column names
            EMAIL_COMBINED_DF = EMAIL_COMBINED_DF[EMAIL_COMBINED_DF_column_order]
        else:
            pass
        
        
        ######################################################################################################
        
        for name, df in dataframes.items():
            if '_SMS_' in name:
                if df["Sent"].sum() >0:
                    df = pd.merge(df, billable_count_df, on='Campaign ID', how='left')
                    if TCHFL_FLAG == "NO":
                        df = df[~df['Campaign Name'].str.contains('TCHFL', na=False)]
                    else:
                        df = df[df['Campaign Name'].str.contains('TCHFL', na=False)]
                        
                    df["COST"] = df["BILLABLE COUNT"]*0.11
                    
                    zero_campaigns = df[df["Sent"] == 0].shape[0]
                    SMS_SENT_COUNT_ZERO_CAMPAIGNS = SMS_SENT_COUNT_ZERO_CAMPAIGNS + zero_campaigns
                    
                    #Summary creation test
                    df_test = df
                    df_test = df_test[df_test['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_test = df_test[["Sent", "Total Delivered", "Clicks", "Campaign Delivery Type"]]
                    column_sums = df_test.sum()
                    df_test = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_test["Delivery Rate"] = ((df_test["Total Delivered"]/df_test["Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Click Rate"] = ((df_test["Clicks"]/df_test["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_test["Campaign Delivery Type"] = df_test["Campaign Delivery Type"].astype(str)
                    df_test["Channel"] = np.where(df_test["Campaign Delivery Type"].str.contains("Flows"), "SMS Flows", "SMS Campaign")
                    df_test = df_test.drop(columns=["Campaign Delivery Type"])
                    
                    SMS_TEST_DF.append(df_test)
                    
                    # Actual Summary Creation 
                    df_copy = df
                    
                    df_copy.columns
                    
                    df_copy = df_copy[~df_copy['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_copy = df_copy[["Sent", "Total Delivered", "Clicks", "Campaign Delivery Type"]]
                    column_sums = df_copy.sum()
                    df_copy = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_copy["Delivery Rate"] = ((df_copy["Total Delivered"]/df_copy["Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Click Rate"] = ((df_copy["Clicks"]/df_copy["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_copy["Campaign Delivery Type"] = df_copy["Campaign Delivery Type"].astype(str)
                    df_copy["Channel"] = np.where(df_copy["Campaign Delivery Type"].str.contains("Flows"), "SMS Flows", "SMS Campaign")
                    df_copy = df_copy.drop(columns=["Campaign Delivery Type"])
                    
                    SMS_DF.append(df_copy)
                    
                    # Combined Summary Creation 
                    df_combined = df
                    
                    df_combined.columns
                    df_combined = df_combined[["Sent", "Total Delivered", "Clicks", "Campaign Delivery Type"]]
                    column_sums = df_combined.sum()
                    df_combined = pd.DataFrame([column_sums], columns=column_sums.index)
                    df_combined["Delivery Rate"] = ((df_combined["Total Delivered"]/df_combined["Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Click Rate"] = ((df_combined["Clicks"]/df_combined["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_combined["Campaign Delivery Type"] = df_combined["Campaign Delivery Type"].astype(str)
                    df_combined["Channel"] = np.where(df_combined["Campaign Delivery Type"].str.contains("Flows"), "SMS Flows", "SMS Campaign")
                    df_combined = df_combined.drop(columns=["Campaign Delivery Type"])
                    
                    SMS_COMBINED_DF.append(df_combined)
                    
                    
                else:
                    pass
                
        if len(SMS_TEST_DF)>0:
            SMS_TEST_DF = pd.concat(SMS_TEST_DF, ignore_index=True)
            SMS_TEST_DF_column_order = ["Channel", "Sent", "Total Delivered", "Delivery Rate" , "Clicks" , "Click Rate" ]  # Adjust with your actual column names
            SMS_TEST_DF = SMS_TEST_DF[SMS_TEST_DF_column_order]
            SMS_TEST_DF = SMS_TEST_DF.rename(columns= {"Sent": "Total Sent", "Clicks": "Total clicks"})
        else:
            pass
        
        if len(SMS_DF)>0:
            SMS_DF = pd.concat(SMS_DF, ignore_index=True)
            SMS_DF_column_order = ["Channel", "Sent", "Total Delivered", "Delivery Rate" , "Clicks" , "Click Rate" ]  # Adjust with your actual column names
            SMS_DF = SMS_DF[SMS_DF_column_order]
            SMS_DF = SMS_DF.rename(columns= {"Sent": "Total Sent", "Clicks": "Total clicks"})
        else:
            pass
        
        if len(SMS_COMBINED_DF)>0:
            SMS_COMBINED_DF = pd.concat(SMS_COMBINED_DF, ignore_index=True)
            SMS_COMBINED_DF_column_order = ["Channel", "Sent", "Total Delivered", "Delivery Rate" , "Clicks" , "Click Rate" ]  # Adjust with your actual column names
            SMS_COMBINED_DF = SMS_COMBINED_DF[SMS_COMBINED_DF_column_order]
            SMS_COMBINED_DF = SMS_COMBINED_DF.rename(columns= {"Sent": "Total Sent", "Clicks": "Total clicks"})
        else:
            pass
        
        
        #########################################################################################################################
        
        
        for name, df in dataframes.items():
            if '_WHATSAPP_' in name:
                if df["Sent"].sum() >0:
                    if TCHFL_FLAG == "NO":
                        df = df[~df['Campaign Name'].str.contains('TCHFL', na=False)]
                    else:
                        df = df[df['Campaign Name'].str.contains('TCHFL', na=False)]
                        
                    if SERVICE_FLAG == "YES":
                        df["COST"] = df["Total Delivered"]*0.13
                    else:
                        df["COST"] = df["Total Delivered"]*0.78
                    
                    zero_campaigns = df[df["Total Sent"] == 0].shape[0]
                    WHATSAPP_SENT_COUNT_ZERO_CAMPAIGNS = WHATSAPP_SENT_COUNT_ZERO_CAMPAIGNS + zero_campaigns
                    
                    #Summary creation test
                    df_test = df
                    df_test = df_test[df_test['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_test = df_test[["Total Sent", "Total Delivered", "Total Read", "Total clicks", "Unique clicks", "Campaign Delivery Type"]]
                    column_sums = df_test.sum()
                    df_test = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_test["Delivery Rate"] = ((df_test["Total Delivered"]/df_test["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Open Rate"] = ((df_test["Total Read"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Click Rate"] = ((df_test["Total clicks"]/df_test["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_test["Unique Click Rate"] = ((df_test["Unique clicks"]/df_test["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Campaign Delivery Type"] = df_test["Campaign Delivery Type"].astype(str)
                    df_test["Channel"] = np.where(df_test["Campaign Delivery Type"].str.contains("Flows"), "WhatsApp Flows", "WhatsApp Campaign")
                    df_test = df_test.drop(columns=["Campaign Delivery Type"])
                    
                    WHATSAPP_TEST_DF.append(df_test)
                    
                    # Actual Summary Creation 
                    df_copy = df
                    
                    df_copy.columns
                    
                    df_copy = df_copy[~df_copy['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_copy = df_copy[["Total Sent", "Total Delivered", "Total Read", "Total clicks", "Unique clicks", "Campaign Delivery Type"]]
                    column_sums = df_copy.sum()
                    df_copy = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_copy["Delivery Rate"] = ((df_copy["Total Delivered"]/df_copy["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Open Rate"] = ((df_copy["Total Read"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Click Rate"] = ((df_copy["Total clicks"]/df_copy["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_copy["Unique Click Rate"] = ((df_copy["Unique clicks"]/df_copy["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Campaign Delivery Type"] = df_copy["Campaign Delivery Type"].astype(str)
                    df_copy["Channel"] = np.where(df_copy["Campaign Delivery Type"].str.contains("Flows"), "WhatsApp Flows", "WhatsApp Campaign")
                    df_copy = df_copy.drop(columns=["Campaign Delivery Type"])
                    
                    WHATSAPP_DF.append(df_copy)
                    
                    
                    # Actual Summary Creation 
                    df_combined = df
                    
                    df_combined.columns
                    
                    df_combined = df_combined[["Total Sent", "Total Delivered", "Total Read", "Total clicks", "Unique clicks", "Campaign Delivery Type"]]
                    column_sums = df_combined.sum()
                    df_combined = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_combined["Delivery Rate"] = ((df_combined["Total Delivered"]/df_combined["Total Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Open Rate"] = ((df_combined["Total Read"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Click Rate"] = ((df_combined["Total clicks"]/df_combined["Total Delivered"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_combined["Unique Click Rate"] = ((df_combined["Unique clicks"]/df_combined["Total Delivered"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Campaign Delivery Type"] = df_combined["Campaign Delivery Type"].astype(str)
                    df_combined["Channel"] = np.where(df_combined["Campaign Delivery Type"].str.contains("Flows"), "WhatsApp Flows", "WhatsApp Campaign")
                    df_combined = df_combined.drop(columns=["Campaign Delivery Type"])
                    
                    WHATSAPP_COMBINED_DF.append(df_combined)
                    
                    
                else:
                    pass
                
        if len(WHATSAPP_TEST_DF)>0:
            WHATSAPP_TEST_DF = pd.concat(WHATSAPP_TEST_DF, ignore_index=True)
            WHATSAPP_TEST_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate", "Total Read", "Open Rate", "Total clicks", "Click Rate", "Unique clicks", "Unique Click Rate" ]  # Adjust with your actual column names
            WHATSAPP_TEST_DF = WHATSAPP_TEST_DF[WHATSAPP_TEST_DF_column_order]
            WHATSAPP_TEST_DF = WHATSAPP_TEST_DF.rename(columns= {"Total Read": "Total Open"})
        else:
            pass
        
        if len(WHATSAPP_DF)>0:
            WHATSAPP_DF = pd.concat(WHATSAPP_DF, ignore_index=True)
            WHATSAPP_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate", "Total Read", "Open Rate", "Total clicks", "Click Rate", "Unique clicks", "Unique Click Rate" ] # Adjust with your actual column names
            WHATSAPP_DF = WHATSAPP_DF[WHATSAPP_DF_column_order]
            WHATSAPP_DF = WHATSAPP_DF.rename(columns= {"Total Read": "Total Open"})
        else:
            pass
        
        if len(WHATSAPP_COMBINED_DF)>0:
            WHATSAPP_COMBINED_DF = pd.concat(WHATSAPP_COMBINED_DF, ignore_index=True)
            WHATSAPP_COMBINED_DF_column_order = ["Channel", "Total Sent", "Total Delivered", "Delivery Rate", "Total Read", "Open Rate", "Total clicks", "Click Rate", "Unique clicks", "Unique Click Rate" ] # Adjust with your actual column names
            WHATSAPP_COMBINED_DF = WHATSAPP_COMBINED_DF[WHATSAPP_COMBINED_DF_column_order]
            WHATSAPP_COMBINED_DF = WHATSAPP_COMBINED_DF.rename(columns= {"Total Read": "Total Open"})
        else:
            pass
        
        
        ##########################################################################################################################################
        
        
        for name, df in dataframes.items():
            if '_PUSH_' in name:
                if df["All Platform Sent"].sum() >0:
                    if TCHFL_FLAG == "NO":
                        df = df[~df['Campaign Name'].str.contains('TCHFL', na=False)]
                    else:
                        df = df[df['Campaign Name'].str.contains('TCHFL', na=False)]
                        
                    df["COST"] = 0
                    
                    zero_campaigns = df[df["All Platform Sent"] == 0].shape[0]
                    PN_SENT_COUNT_ZERO_CAMPAIGNS = PN_SENT_COUNT_ZERO_CAMPAIGNS + zero_campaigns
                    
                    #Summary creation test
                    df_test = df
                    df_test = df_test[df_test['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_test = df_test[["All Platform Sent", "All Platform Impressions", "All Platform Clicks", "Campaign Delivery Type"]]
                    column_sums = df_test.sum()
                    df_test = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_test["Delivery Rate"] = ((df_test["All Platform Impressions"]/df_test["All Platform Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_test["Click Rate"] = ((df_test["All Platform Clicks"]/df_test["All Platform Impressions"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_test["Campaign Delivery Type"] = df_test["Campaign Delivery Type"].astype(str)
                    df_test["Channel"] = np.where(df_test["Campaign Delivery Type"].str.contains("Flows"), "PN Flows", "PN Campaign")
                    df_test = df_test.drop(columns=["Campaign Delivery Type"])
                    
                    
                    PN_TEST_DF.append(df_test)
                    
                    # Actual Summary Creation 
                    df_copy = df
                    df_copy = df_copy[~df_copy['Campaign Name'].str.contains('test', case=False, na=False)]
                    df_copy = df_copy[["All Platform Sent", "All Platform Impressions", "All Platform Clicks", "Campaign Delivery Type"]]
                    column_sums = df_copy.sum()
                    df_copy = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_copy["Delivery Rate"] = ((df_copy["All Platform Impressions"]/df_copy["All Platform Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_copy["Click Rate"] = ((df_copy["All Platform Clicks"]/df_copy["All Platform Impressions"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_copy["Campaign Delivery Type"] = df_copy["Campaign Delivery Type"].astype(str)
                    df_copy["Channel"] = np.where(df_copy["Campaign Delivery Type"].str.contains("Flows"), "PN Flows", "PN Campaign")
                    df_copy = df_copy.drop(columns=["Campaign Delivery Type"])
                    
                    PN_DF.append(df_copy)
                    
                    
                    # Actual Summary Creation 
                    df_combined = df
                    df_combined = df_combined[["All Platform Sent", "All Platform Impressions", "All Platform Clicks", "Campaign Delivery Type"]]
                    column_sums = df_combined.sum()
                    df_combined = pd.DataFrame([column_sums], columns=column_sums.index)
                    
                    df_combined["Delivery Rate"] = ((df_combined["All Platform Impressions"]/df_combined["All Platform Sent"])*100).apply(lambda x: f"{x:.2f}%")
                    df_combined["Click Rate"] = ((df_combined["All Platform Clicks"]/df_combined["All Platform Impressions"])*100).round(2).apply(lambda x: f"{x:.2f}%")
                    df_combined["Campaign Delivery Type"] = df_combined["Campaign Delivery Type"].astype(str)
                    df_combined["Channel"] = np.where(df_combined["Campaign Delivery Type"].str.contains("Flows"), "PN Flows", "PN Campaign")
                    df_combined = df_combined.drop(columns=["Campaign Delivery Type"])
                    PN_COMBINED_DF.append(df_combined)
                    
                else:
                    pass
                
        if len(PN_TEST_DF)>0:
            PN_TEST_DF = pd.concat(PN_TEST_DF, ignore_index=True)
            PN_TEST_DF_column_order = ["Channel", "All Platform Sent", "All Platform Impressions", "Delivery Rate" , "All Platform Clicks" , "Click Rate" ]  # Adjust with your actual column names
            PN_TEST_DF = PN_TEST_DF[PN_TEST_DF_column_order]
            PN_TEST_DF = PN_TEST_DF.rename(columns= {"All Platform Sent": "Total Sent", "All Platform Impressions" : "Total Delivered", "All Platform Clicks" :"Total clicks"})
        else:
            pass
        
        if len(PN_DF)>0:
            PN_DF = pd.concat(PN_DF, ignore_index=True)
            PN_DF_column_order = ["Channel", "All Platform Sent", "All Platform Impressions", "Delivery Rate" , "All Platform Clicks" , "Click Rate" ]  # Adjust with your actual column names
            PN_DF = PN_DF[PN_DF_column_order]
            PN_DF = PN_DF.rename(columns= {"All Platform Sent": "Total Sent", "All Platform Impressions" : "Total Delivered", "All Platform Clicks" :"Total clicks"})
        else:
            pass
        
        
        if len(PN_COMBINED_DF)>0:
            PN_COMBINED_DF = pd.concat(PN_COMBINED_DF, ignore_index=True)
            PN_COMBINED_DF_column_order = ["Channel", "All Platform Sent", "All Platform Impressions", "Delivery Rate" , "All Platform Clicks" , "Click Rate" ]  # Adjust with your actual column names
            PN_COMBINED_DF = PN_COMBINED_DF[PN_COMBINED_DF_column_order]
            PN_COMBINED_DF = PN_COMBINED_DF.rename(columns= {"All Platform Sent": "Total Sent", "All Platform Impressions" : "Total Delivered", "All Platform Clicks" :"Total clicks"})
        else:
            pass
        
        ########################################################################################################################
        
        #concanating all summary dataframes
        
        TEST_SUMMARY_LIST = [EMAIL_TEST_DF,SMS_TEST_DF,WHATSAPP_TEST_DF,PN_TEST_DF]
        
        TEST_SUMMARY = pd.DataFrame()
        for i in TEST_SUMMARY_LIST:
            if len(i)>0:
                TEST_SUMMARY = pd.concat([TEST_SUMMARY,i], ignore_index=True)
                
        TEST_SUMMARY = TEST_SUMMARY.replace("nan%", "")
        TEST_SUMMARY = TEST_SUMMARY[TEST_SUMMARY['Total Sent']>0]
                
        
        SUMMARY_LIST = [EMAIL_DF,SMS_DF,WHATSAPP_DF,PN_DF]
        
        SUMMARY = pd.DataFrame()
        for i in SUMMARY_LIST:
            if len(i)>0:
                SUMMARY = pd.concat([SUMMARY,i], ignore_index=True)
                
        SUMMARY = SUMMARY.replace("nan%", "")
                
        
        COMBINED_SUMMARY_LIST = [EMAIL_COMBINED_DF,SMS_COMBINED_DF,WHATSAPP_COMBINED_DF,PN_COMBINED_DF]
        
        COMBINED_SUMMARY = pd.DataFrame()
        for i in COMBINED_SUMMARY_LIST:
            if len(i)>0:
                COMBINED_SUMMARY = pd.concat([COMBINED_SUMMARY,i], ignore_index=True)
            
        COMBINED_SUMMARY = COMBINED_SUMMARY.replace("nan%", "")
                
        ##########################################################################################################################
        
        # converting variables into dictionary to create df
        # Convert variables into a dictionary
        data_dict = {
            'EMAIL_SENT_COUNT_ZERO_CAMPAIGNS': EMAIL_SENT_COUNT_ZERO_CAMPAIGNS,
            'SMS_SENT_COUNT_ZERO_CAMPAIGNS': SMS_SENT_COUNT_ZERO_CAMPAIGNS,
            'WHATSAPP_SENT_COUNT_ZERO_CAMPAIGNS': WHATSAPP_SENT_COUNT_ZERO_CAMPAIGNS,
            'PN_SENT_COUNT_ZERO_CAMPAIGNS': PN_SENT_COUNT_ZERO_CAMPAIGNS
        }
        
        # Converting dictionary to DataFrame
        SENT_COUNT_ZERO_CAMPAIGNS = pd.DataFrame(data_dict, index=[0])
        
        ############################################################################################################################
                
        #Adding Summary sheet in dataframe
        dataframes['TEST_SUMMARY'] = TEST_SUMMARY
        dataframes['SUMMARY'] = SUMMARY
        dataframes['COMBINED_SUMMARY'] = COMBINED_SUMMARY
        dataframes['SENT_COUNT_ZERO_CAMPAIGNS'] = SENT_COUNT_ZERO_CAMPAIGNS
        
        ######################################################################################################################
        
        
        def truncate_sheet_name(name, max_length=31):
            if len(name) > max_length:
                return name[:max_length]
            return name
        
        def drop_unnamed_column(df):
            if 'Unnamed: 0' in df.columns:
                df = df.drop(columns=['Unnamed: 0'])
            return df
        
        
        # Create a Pandas Excel writer using XlsxWriter as the engine
        with pd.ExcelWriter('SUMMARY_MIS.xlsx', engine='xlsxwriter') as writer:
            # Iterate through the dictionary of DataFrames
            for sheet_name, df in dataframes.items():
                if '_EMAIL_' in sheet_name and '_flows_EMAIL_' not in sheet_name:
                    truncated_sheet_name = "Email Campaigns"
                elif '_CONNECTOR_' in sheet_name:
                    truncated_sheet_name = "_CONNECTOR_"
                elif '_flows_EMAIL_' in sheet_name:
                    truncated_sheet_name = "Email Flows"
                elif '_SMS_' in sheet_name and '_flows_SMS_' not in sheet_name:
                    truncated_sheet_name = "SMS Campaign"
                elif '_flows_SMS_' in sheet_name:
                    truncated_sheet_name = "SMS Flows"
                elif '_WHATSAPP_' in sheet_name and '_flows_WHATSAPP_' not in sheet_name:
                    truncated_sheet_name = "Whatsapp Campaign"
                elif '_flows_WHATSAPP_' in sheet_name:
                    truncated_sheet_name = "Whatsapp Flows"
                elif '_PUSH_' in sheet_name and '_flows_PUSH_' not in sheet_name:
                    truncated_sheet_name = "Push Campaign"
                elif '_flows_PUSH_' in sheet_name:
                    truncated_sheet_name = "Push Flows"
                else:
                    truncated_sheet_name = truncate_sheet_name(sheet_name)
                #truncated_sheet_name = truncate_sheet_name(sheet_name)
                df = drop_unnamed_column(df)
                df.to_excel(writer, sheet_name=truncated_sheet_name, index=False)
        print("Excel file created successfully.")
        
        excel_file = 'SUMMARY_MIS.xlsx'
        
        ###############################################################################################################
        
        # Email configuration
        sender_email = "3rdi@0101.today"
        receiver_email = "3rdi@0101.today"
        email_list = recipients.split(',')
        cc_emails = email_list
        password = password  # Consider using an app password or environment variable for better security
        subject = 'Hey Superhero, Your Personalized Summary Report Is Ready – View Now!'
        body = "Your summary report is ready, and we've attached it for your convenience. Take a moment to review the insights we've prepared just for you. If you have any questions or need further details, feel free to reach out!"
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Cc'] = ",".join(cc_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach the CSV file
        attachment = open(excel_file, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {excel_file}')
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
        finally:
            server.quit()
            
        
    if __name__ == '__main__':
        url = sys.argv[1]
        recipients = sys.argv[2]
        tchfl = sys.argv[3]
        service = sys.argv[4]
        process_url_and_recipients(url, recipients, tchfl, service, "nkwf lbtt msxr ypjg")
        
        
########################################################################################################################
                

except:
    pass
