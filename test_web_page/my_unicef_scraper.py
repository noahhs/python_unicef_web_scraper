from lxml import html
import requests

write_csv = True
write_sqlite = False
csv_filename = 'countries.csv'
sqlite_filename = 'countrydb.db'

url="http://www.unicef.org/statistics/index_countrystats.html"
response=requests.get(url)
tree=html.fromstring(response.text)

#Get links to country pages
links=tree.cssselect('div#bodyarea a')[:5]

if write_sqlite:
	import sqlite3
	conn=sqlite3.connect(sqlite_filename)
	c=conn.cursor()
	c.execute("DROP TABLE IF EXISTS countrydata")
	c.execute('''CREATE TABLE countrydata (cname TEXT, ind_cat TEXT, ind TEXT, \
	val text, source text)''')
if write_csv:
	csvfile=open(csv_filename,'wb')
	import csv
	csvwriter=csv.writer(csvfile)
def parse_and_store_page(link):
	cname=link.text
	cname=str(cname)
	#get unicef domain in here somehow
	url = "http://www.unicef.org" + link.get("href")
	print cname
	response=requests.get(url)
	tree=html.fromstring(response.text)
	tables=tree.cssselect('TABLE.statisticsn')

	def parse_and_store_table(table):
		title=table.cssselect('TD.tabletitle p.title')[0].text
		#title=title.encode('utf8')
		def str_txt(element):
			if element.text is None:
				print html.tostring(element)
				return ""
			elif element.text.find(u'\u2020')!=-1:
				print element.text.encode('utf8')
				return element.text.encode('utf8')
			elif isinstance(element.text, unicode):
				return element.text.encode('utf8')
			else:
			#	print element.text
			#	return '-'
			#elseif isinstance(element.text,unicode):
			#No, let's try encoding everyting
			#No, let's try not encoding anything
			#	print element.text
				return element.text
		temp=table.cssselect('td.left p')
		#print temp[0].text
		indicators=map(str_txt, table.cssselect('TD.left p'))
		values=map(str_txt, table.cssselect('TD p.statsnumber'))
		if isinstance(values[1],unicode):
			print values[1]
		l=len(values)
		tuples=zip([cname]*l,[title]*l,indicators,values,['Unicef']*l)
		#print tuples[0]
		if write_sqlite:
			c.executemany("INSERT INTO countrydata VALUES (?,?,?,?,?)", tuples)
			conn.commit()
		if write_csv:
			csvwriter.writerows(tuples)

	map(parse_and_store_table, tables)

map(parse_and_store_page, links[1:])

#if write_csv:
#	csvwriter.close()
if write_sqlite:
	conn.close()

#And we're done.


