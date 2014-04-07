__author__ = 'Nick Hirakawa'


from parse import *
from query import *
import operator


def main():
	qp = QueryParser(filename='../text/queries.txt')
	cp = CorpusParser(filename='../text/corpus.txt')
	qp.parse()
	print 'parsing queries'
	queries = qp.get_queries()
	print 'parsing corpus'
	cp.parse()
	corpus = cp.get_corpus()
	proc = QueryProcessor(queries, corpus, score_function='Query Likelihood')
	print 'running queries'
	results = proc.run()
	num = 0
	for result in results:
		for key, value in result.iteritems():
			scores = sorted(value.iteritems(), key=operator.itemgetter(1))
			scores.reverse()
			#print key, scores[:10]
			num += 1
	print num


if __name__ == '__main__':
	import timeit
	#print timeit.timeit('main()', setup='from __main__ import main', number=5)
	main()
