__author__ = 'Nick Hirakawa'


from invdx import build_data_structures
from rank import *
from collections import OrderedDict
import operator


class QueryProcessor:
	def __init__(self, queries, corpus, score_function='BM25'):
		self.queries = queries
		self.index, self.ft, self.dlt = build_data_structures(corpus)
		self.score_function = score_function

	def run(self):
		results = []
		qid = 0
		for query in self.queries:
			if self.score_function == 'BM25':
				results.append(self.run_BM25(query))
			elif self.score_function == 'Query Likelihood':
				print 'running query %d' % qid
				qid += 1
				results.append(self.run_QueryLikelihood(query))
		return results

	def run_BM25(self, query):
		query_result = dict()
		for term in query:
			if term in self.index:
				doc_dict = self.index[term] # retrieve index entry
				for docid, freq in doc_dict.iteritems(): #for each document and its word frequency
					score = score_BM25(n=len(doc_dict), f=freq, qf=1, r=0, N=len(self.dlt),
									   dl=self.dlt.get_length(docid),
									   avdl=self.dlt.get_average_length()) # calculate score
					if docid in query_result: #this document has already been scored once
						query_result[docid] += score
					else:
						query_result[docid] = score
		return query_result

	def run_QueryLikelihood(self, query):
		query_result = OrderedDict()
		for mu in mu_values:
			mu_result = dict()
			for term in query:
				if term in self.index:
					docs = set()
					#score documents containing term
					for docid, freq in self.index[term].iteritems():
						score = score_query_likelihood(f=freq, mu=mu, c=self.ft.get_frequency(term),
													   C=len(self.index), D=len(self.dlt))
						docs.add(docid)
						if docid in mu_result:
							mu_result[docid] += score
						else:
							mu_result[docid] = score
					a = [str(x) for x in range(len(self.dlt))]
					s = set(a).difference(docs)
					#score documents not containing term
					for docid in s:
						score = score_query_likelihood(f=0, mu=mu, c=self.ft.get_frequency(term), C=len(self.index), D=len(self.dlt))
						if docid in mu_result:
							mu_result[docid] += score
						else:
							mu_result[docid] = score
				else:
					score = score_query_likelihood(f=0, mu=mu, c=self.ft.get_frequency(term), C=len(self.index), D=len(self.dlt))
					for i in range(len(self.dlt)):
						if i in mu_result:
							mu_result[i] += score
						else:
							mu_result[i] = score
			for docid in mu_result:
				mu_result[docid] = mu_result[docid]
			query_result[mu] = mu_result
		return query_result
