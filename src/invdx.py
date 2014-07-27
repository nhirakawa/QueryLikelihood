#invdx.py
# An inverted index
from collections import OrderedDict
from urllib2 import *
from json import *
from time import time

__author__ = 'Nick Hirakawa'


class InvertedIndex:

	def __init__(self):
		self.index = dict()
		self.count = 0
		self.build_db()

	def __contains__(self, item):
		return item in self.index

	def __getitem__(self, item):
		return self.index[item]

	def __len__(self):
		return self.count

	def build_db(self):
		try:
			urlopen('http://localhost:5984/search')
		except HTTPError:
			opener = build_opener(HTTPHandler)
			request = Request('http://localhost:5984/search')
			request.get_method = lambda: 'PUT'
			url = opener.open(request)

	def bulk_load(self, docs):
		self.build_db()
		data = dumps(docs)
		opener = build_opener(HTTPHandler)
		request = Request('http://localhost:5984/search/_bulk_docs', data=data)
		request.add_header('Content-Type', 'application/json')
		request.get_method = lambda: 'POST'
		opener.open(request)

	def to_db(self):
		docs = []
		for word in self.index:
			doc = self.index[word]
			doc['_id'] = word
			docs.append(doc)
		print len(docs)
		upload = {'docs': docs}
		self.bulk_load(upload)

	def write(self, filename='default.index'):
		with open(filename, 'w') as f:
			for word in self.index:
				line = word + ' '
				for docid in self.index[word]:
					line += '%s-%d ' % (docid, self.index[word][docid])
				line += '\n'
				f.write(line)

	def add(self, word, docid):
		if word in self.index:
			if docid in self.index[word]:
				self.index[word][docid] += 1
			else:
				self.index[word][docid] = 1
		else:
			d = dict()
			d[docid] = 1
			self.index[word] = d
		self.count += 1

	#frequency of word in document
	def get_document_frequency(self, word, docid):
		if word in self.index:
			if docid in self.index[word]:
				return self.index[word][docid]
			else:
				raise LookupError('%s not in document %s' % (str(word), str(docid)))
		else:
			raise LookupError('%s not in index' % str(word))

	#frequency of word in index, i.e. number of documents that contain word
	def get_index_frequency(self, word):
		if word in self.index:
			return len(self.index[word])
		else:
			raise LookupError('%s not in index' % word)

	#frequency of word across collection
	def get_total_frequency(self, word):
		result = 0
		if word in self.index:
			d = self.index[word]
			for doc in d:
				result += d[doc]
			return result
		else:
			return result


class WordFrequencyTable:

	def __init__(self):
		self.table = OrderedDict()

	def __len__(self):
		result = 0
		for word in self.table:
			result += self.table[word]
		return result

	def write(self, filename='default.ft'):
		with open(filename, 'w') as f:
			for word in self.table:
				line = '%s %d\n' % (word, self.table[word])
				f.write(line)

	def get_frequency(self, word):
		if word in self.table:
			return self.table[word]
		else:
			return 0

	def add(self, word):
		if word in self.table:
			self.table[word] += 1
		else:
			self.table[word] = 1


class DocumentLengthTable:

	def __init__(self):
		self.table = OrderedDict()

	def __len__(self):
		return len(self.table)

	def write(self, filename='default.dlt'):
		with open(filename, 'w') as f:
			for docid in self.table:
				line = '%s %d\n' % (docid, self.table[docid])
				f.write(line)


	def add(self, docid, length):
		self.table[docid] = length

	def get_length(self, docid):
		if docid in self.table:
			return self.table[docid]
		else:
			raise LookupError('%s not found in table' % str(docid))

	def get_average_length(self):
		sum = 0
		for length in self.table.itervalues():
			sum += length
		return float(sum) / float(len(self.table))


def build_data_structures(corpus):
	idx = InvertedIndex()
	dlt = DocumentLengthTable()
	ft = WordFrequencyTable()
	for docid in corpus:
		#build inverted index and word frequency table
		for word in corpus[docid]:
			idx.add(str(word), str(docid))
			ft.add(word)
		#build document length table
		length = len(corpus[str(docid)])
		dlt.add(docid, length)
	return idx, ft, dlt