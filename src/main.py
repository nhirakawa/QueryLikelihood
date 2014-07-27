__author__ = 'Nick Hirakawa'


from parse import *
from query import *
import operator
import os
import subprocess


def main():
	qp = QueryParser(filename='../text/queries.txt')
	cp = CorpusParser(filename='../text/corpus.txt')
	qp.parse()
	print 'parsing queries'
	queries = qp.get_queries()
	print 'parsing corpus'
	cp.parse()
	corpus = cp.get_corpus()

	#step 1: build inverted index
	print 'building data structures'
	idx, ft, dlt = build_data_structures(corpus)
	idx.to_db()

	#step 2: run queries against inverted index file
	proc = QueryProcessor(queries, idx='../default.idx', dlt=dlt, ft=ft, score_function='Query Likelihood')
	print 'running queries'
	results = proc.run()
	lines = OrderedDict()
	for index, result in enumerate(results):
		for mu, l in result.iteritems():
			s = sorted([(k, v) for k, v in l.iteritems()], key=operator.itemgetter(1))
			s.reverse()
			for rank, x in enumerate(s[:10]):
				tmp = index+1, x[0], rank+1, x[1]
				line = '{:<} Q0 {:<} {:<} {:<} NH-QL\n'.format(*tmp)
				if mu in lines:
					lines[mu].append(line)
				else:
					lines[mu] = [line]
	for mu, txt in lines.iteritems():
		filename = '../results/run.%d' % mu
		with open(filename, 'w') as f:
			f.writelines(txt)


def make_dir():
	if not os.path.exists('../results'):
		os.makedirs('../results')


if __name__ == '__main__':
	make_dir()
	main()
	# subprocess.call(['java', '-jar', '../tool/eval.jar', '-d', '../results'])
