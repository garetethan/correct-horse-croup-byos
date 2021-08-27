import argparse
import gen

USEFUL_KEYS = frozenset({'categories', 'senses', 'word'})

def main ():
	parser = argparse.ArgumentParser()
	parser.add_argument('data_path', help='The filepath of the data file to remove baggage from.')
	args = parser.parse_args()
	words = gen.loadWords(args.data_path)

	print('Removing baggage and sorting...')
	for i, word in enumerate(words):
		words[i] = {k: v for (k, v) in word.items() if k in USEFUL_KEYS}
	words.sort(key=lambda word: word['word'])

	print('Overwriting data file...')
	with open(args.data_path, 'w') as dataFile:
		dataFile.write('\n'.join(json.dumps(word) for word in words))

if __name__ == '__main__':
	main()
