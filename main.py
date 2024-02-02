# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool
# windows, actions, and settings.

import json
import os

import click
from check import Checks

import convert
import initialize
import update
from util import print_colored


@click.command()
@click.option('--directory', '-d', help="Backend name", default="backend")
@click.option('--sub_directory', '-s',
              help="Base name", default="base")
@click.option('--append', '-a', default=False, is_flag=True)
@click.option('--class_name', '-c', help="Class name", default=None)
@click.option('--primary_key', '-pk', help="Primary key for the table", default=None)
@click.option('--init', '-i', default=False, is_flag=True)
@click.option('--json_path', '-j', help="Json Path", default=None)
@click.option('--connect', '-con', help="Create Connection", default=False, is_flag=True)
@click.option('--from_database', '-f', help="From database", default=None)
@click.option('--to_database', '-to', help="To database", default=None)
@click.option('--con_type', '-ct', help="Type of connection.o2o for one to one,o2m for one to many,m2m for many to many", default=None)
def jApi(
        directory,
        sub_directory,
        init,
        append,
        class_name,
        primary_key,
        json_path,
        connect,
        from_database,
        to_database,
        con_type):
    
    # Initialising the shell scripts to create a demo django backend
    if init:

        print_colored('Starting Initialization', 'header', 'b')
        
        # Storing the flags inside init_data.json file for future use 
        print_colored('Storing flags as FIELDS inside initData.json', 'blue')
        c1 = convert.Convertor(False)
        c1.path = f'{directory}/{sub_directory}'
        c1.write_to_file()
        print_colored('Stored successfully', 'green')

        # Invoking the shell scripts to generate a boiler django backend
        print_colored('Running automated shellscripts (initialize.sh)', 'blue')
        initialize.InitializeShellScript(directory, sub_directory)
        print_colored('Created database Successfully!', 'green', 'b')

        # Updating files
        z = update.updateFiles(directory, sub_directory)
        z.updateSettingsFile()
        z.updateURLsFile()
        print_colored('Successfully completed files update!', 'green')

        print_colored('Running Server', 'green', 'b')
        os.system(f'python3 {directory}/manage.py runserver')

    elif append:
        # Providing json path is must
        if json_path is None:
            print_colored(f'Error! - Provide JsonPath with --append using --json_path option', 'fail')
            return

        # If not provided file name, then setting it to json-file name
        if class_name is None:
            class_name = json_path.split('/')[-1].split('.')[0]
            print_colored(f'Warning! - Default class name is {class_name}', 'warning')

        print_colored('Starting json checks', 'header', 'b')
        json_checks = Checks(json_path)

        # Check JSON file existence
        if json_checks.check_file_exists() == False:
            print_colored(f'Error! with path \'{json_path}\'. Please provide a valid path to json!', 'fail')
            return
        print_colored('Passed File exist check', 'green')
        
        # Check validity of JSON data format
        try:
            json_checks.load_json()
        except BaseException:
            print_colored(f'Error loading the JSON file. JSON data Format is wrong in \'{json_path}\' file', 'fail')
            return
        print_colored('Passed json load check', 'green')
            
        # Check validity of JSON data keys format
        if json_checks.check_keys() == False:
            print(f'Error! - Please provide a valid key in json file', 'fail')
            return
        print_colored('Passed json data key format check', 'green')

        # Check validity of JSON data values format
        if json_checks.check_values() == False:
            print(f'Error! - Please provide a valid value type in json file', 'fail')
            return
        print_colored('Passed json data value format check', 'green')
        print_colored('Passed all json checks successfully!', 'green', 'b')

        # Fetching stored flag fields
        print_colored('Accessing stored flags from initData.json', 'blue')
        c = convert.Convertor()
        print_colored('Accessed successfully', 'green')

        # TODO id feature
        with open(json_path, 'r') as file:
            data = json.load(file)
            c.ask_or_append(data, class_name,primary_key)
        c.code()
        c.write_to_file()
        
    if connect:
        assert from_database is not None, "Database to start connection from must be provided"
        assert to_database is not None, "Database to connect to must be provided"
        assert con_type is not None, "Connection type between the databases must be provided"
        c = convert.Convertor()
        c.create_connection(from_database,to_database,con_type)
        c.code()
        c.write_to_file()

if __name__ == '__main__':
    jApi()

