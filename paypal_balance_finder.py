'''Finds ending balances of accounts contained in a PayPal Settlement Report on a user defined date.
File specs can be found here: https://www.paypalobjects.com/webstatic/en_US/developer/docs/pdf/PP_LRD_Gen_SettlementReport.pdf'''

import pyperclip, pprint, os, sys, re
from tkinter import filedialog

#generates PayPal file's date format & matches files' naming conventions
def create_file_names(date):
	date = date.split('/')
	date[0] = "{0:02d}".format(int(date[0]))			#reformatting day to match file naming convention of 2 digit dates
	date[1] = "{0:02d}".format(int(date[1]))			#reformatting month to have ave 2 digits
	date = (date[2]+date[0]+date[1])					#reformatting to match YYYYMMDD date convention
	paypal_file_types = ['R','H','A','X']				#four file types (as per specs)
	file_names = ["STL-{0}.{1}.01.01.009.CSV".format(date, file_type) for file_type in paypal_file_types]
	return file_names									#return a list of file names to search working directory for

#run through line of file to find account & corresponding 
def accounts_and_values(file_names,date):
	accts_and_balances = {}
	for file_name in file_names:
		try:
			with open(file_name) as balance_file:
				for line in balance_file:
					row = line.replace('"',"").split(',')			
					if(row[0]) == 'SH':						#find section header row that contains account IDs
						account_name = row[3]
						accts_and_balances.setdefault(account_name, {})
					elif row[0] == 'SF' and int(row[13]):								#only add if balance != 0
						accts_and_balances[account_name][row[1]] = int(row[13])/100		#find section footer row that contains account balances

		except FileNotFoundError:		# if file not found, print list of dates that there are files for in cwd
			other_file_dates = []						
			print()
			print("No file for {0} found.".format(date))				#tell user the date they entered does not match any file in cwd
			fname_regex = re.compile('^STL-(\d{8})')					#make regex to match file naming convention
			for file_name in os.listdir():								#search the cwd for any files that match for other dates
				if fname_regex.search(file_name) != None:
					date = fname_regex.search(file_name).group().lstrip('STL-')
					formatted_date = "/".join([date[4:6], date[-2:], date[0:4]])	#add date to list after reformatting to be readable
					if formatted_date not in other_file_dates:
						other_file_dates.append(formatted_date)
			print("Downloaded files were found for the following dates:" )
			for date in other_file_dates:
				print(date)
			break
	return accts_and_balances

def main():
	os.chdir(filedialog.askdirectory())		#change directory to pull files straight from Download folder
	while True:
		date = input("What is the date of the files? (MM/DD/YYYY) Press <ENTER> to quit program: ")
		if date:
			file_names = create_file_names(date)
			closing_balances = accounts_and_values(file_names, date)

			print()
			print("Final closing available PayPal balances as of {0}:\n".format(date))
			for k, v in sorted(closing_balances.items()):
				if v:
					print(k)
					for currency, value in v.items():
						value = str("{0:0,.2f}".format(value)).rjust(len("10,000,000.00"))
						print("{0}: {1}".format(currency, value))
					print()
				
		else:
			sys.exit()

if __name__ == '__main__':
	main()
