#!/usr/bin/env python3

from datetime import datetime, timedelta
import pandas as pd
import requests
from getpass import getpass

class ReviewReport:
    def __init__(self):
        pass

    def get_week_start_end(self, current_time=None):
        """
        Returns the start and end of the week (Monday to Sunday) based on the provided datetime object
        or the current time if no input is provided. The start of the week is set to 12:00 AM on Monday,
        and the end of the week is set to 11:59:59 PM on Sunday.

        :param current_time: datetime object, optional. If None, uses datetime.now().
        :return: tuple of (start_of_week, end_of_week)
        """
        # Use current time or provided time
        if current_time is None:
            current_time = datetime.now()

        # Get the start of the week (Monday) and set time to 12:00 AM
        start_of_week = (current_time - timedelta(days=current_time.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

        # Get the end of the week (Sunday) at 11:59:59 PM
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)

        return start_of_week, end_of_week
    
    def read_url_file(self, url, username=None, password=None):
        """
        Reads an Excel file from the given URL with optional Basic Authentication.

        :param url: str, URL of the Excel file to read
        :param username: str, username for Basic Authentication (optional)
        :param password: str, password for Basic Authentication (optional)
        :return: DataFrame containing the content of the Excel file
        """
        try:
            if username and password:
                response = requests.get(url=url, auth=(username,password))
            else:
                response = requests.get(url=url)

            # Raise an exception for HTTP errors
            response.raise_for_status()

            df = pd.read_excel(pd.compat.BytesIO(response.content), engine='openpyxl')
            return df
        
        except Exception as e:
            print(f"Error reading the Excel file: {e}")
            return None
            
    def get_local_excel_file(selt, file_path):
        """
        Reads an Excel file from the given local file path and returns it as a DataFrame.

        :param file_path: str, local path to the Excel file to read
        :return: DataFrame containing the content of the Excel file
        """
        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(file_path, engine="openpyxl")
            return df
        except Exception as e:
            print(f"Error reading Excel file : {e}")           
            return None
    
    def filter_by_date_column(self, df, date_column, start_date, end_date, reviewed=None):
        """
        Filters the DataFrame by a specified date column based on the start and end dates.

        :param df: DataFrame, the DataFrame to filter
        :param date_column: str, the name of the column to filter on
        :param start_date: datetime, the start date to filter
        :param end_date: datetime, the end date to filter
        :param reviewed: bolean, reviewed cards
        :return: DataFrame containing filtered results
        """
        if date_column not in df.columns:
            print(f"The column '{date_column}' does not exist in the DataFrame.")
            return None
        
        # Convert the specified date column to datetime format if it is not already
        # df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        filtered_df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

        if reviewed:
            filtered_df = filtered_df[(df['Reviewer'].notnull())]


        filtered_df = filtered_df['Card Link']
        row_count = filtered_df.shape[0]

        return filtered_df, row_count

if __name__ == "__main__" : 
    report = ReviewReport()
    start_of_week, end_of_week = report.get_week_start_end()
    print("Start of the week (Monday at 12 AM):", start_of_week)
    print("End of the week (Sunday at 11:59:59 PM):", end_of_week)
    # excel_url = "https://docs.google.com/spreadsheets/d/1heEGDtEh7EGK5enaB0WBFe9lg1AOweqA1ohDeGa-65M/edit?gid=100981539#gid=100981539"
    # username = input("Enter your username: ")
    # password = getpass("Enter your password: ")
    # result_set = report.read_file(excel_url, username, password)

    # Get local path for the Excel file
    # excel_file_path = input("Enter the local path of the Excel file: ")
    excel_file_path = "/home/elnaz.ghasemi/Downloads/DBAReview.xlsx"

    # Read the Excel file
    result_set= report.get_local_excel_file(excel_file_path)
    if result_set is not None:
        print("Result set from Excel file:")
        # print(result_set)
        date_column = "Request Time"

        filtered_result, row_count = report.filter_by_date_column(result_set, date_column, start_of_week, end_of_week)
        print("Filtered result set based on new requests added to file:")
        print(filtered_result)
        print("New DBA review requests count : ", row_count)

        date_column = "Review Done Time"
        filtered_result, row_count = report.filter_by_date_column(result_set, date_column, start_of_week, end_of_week, True)
        print("Filtered result set based on Review Done Time:")
        print(filtered_result)
        print("Reviewd requests count : ", row_count)
