import argparse
import json
import random
import re

def main ():
	parser = argparse.ArgumentParser()
	parser.add_argument('data_path', help='The path of the Wiktionary data file to use.')
	parser.add_argument('-w', '--word-count', default=4, type=int, help='The number of words to have in each password.')
	parser.add_argument('-c', '--char-max', default=8, type=int, help='The maximum number of characters a word may have.')
	parser.add_argument('-o', '--option-count', default=1, type=int, help='The number of passwords to generate.')
	parser.add_argument('-a', '--exclude-cats', nargs='+', default=[], help='Exclude words in the specified categories.')
	parser.add_argument('-t', '--exclude-tags', nargs='+', default=[], help='Exclude words with the specified tags.')
	inclusions = {
		('b', 'abbreviations', 'abbreviations', frozenset(), frozenset({'abbreviation'})),
		('l', 'alternative', 'alternative forms', frozenset(), frozenset({'alternative'})),
		('g', 'given-names', 'given names', frozenset({'English given names'}), frozenset()),
		('m', 'morphemes', 'morphemes (affixes, suffixes, etc.)', frozenset(), frozenset({'morpheme'})),
		('n', 'names', 'names of people, places, etc.', frozenset({'English diminutives of female given names', 'English diminutives of male given names', 'English diminutives of unisex given names'}), frozenset({'name'})),
		('s', 'nonstandard', 'nonstandard forms', frozenset(), frozenset({'nonstandard'})),
		('d', 'old', 'archaic and obsolete words', frozenset(), frozenset({'archaic', 'obsolete'})),
		('p', 'phrases', 'phrases which consist of multiple words', frozenset({'English multiword terms'}), frozenset()),
		('f', 'profanity', 'offensive words, vulgar words, and slurs', frozenset({'English swear words'}), frozenset({'offensive', 'slur', 'vulgar'})),
		('r', 'surnames', 'surnames', frozenset({'English surnames'}), frozenset()),
	}
	for inclusion in inclusions:
		parser.add_argument(f'-{inclusion[0]}', f'--{inclusion[1]}', action='store_true', help=f'Include {inclusion[2]} (which are excluded by default).')
	args = parser.parse_args()
	categoryExclusions = set(args.exclude_cats)
	tagExclusions = set(args.exclude_tags)
	tagExclusions.add('misspelling')
	options = vars(args)
	for inclusion in inclusions:
		if not options[inclusion[1].replace('-', '_')]:
			categoryExclusions |= inclusion[3]
			tagExclusions |= inclusion[4]

	words = loadWords(args.data_path)
	print(f'Loaded {len(words)} words.')

	print('Filtering words...')
	goodWords = []
	for i, word in enumerate(words):
		words[i]['categories'] = set(word.get('categories', []))
		if isDecentWord(words[i], args, categoryExclusions):
			for j, sense in enumerate(words[i]['senses']):
				words[i]['senses'][j]['categories'] = set(sense.get('categories', []))
				words[i]['senses'][j]['tags'] = set(sense.get('tags', []))
			words[i]['senses'] = [sense for sense in words[i]['senses'] if sense['categories'].isdisjoint(categoryExclusions) and sense['tags'].isdisjoint(tagExclusions)]
			if words[i]['senses']:
				goodWords.append(words[i])

	print(f'Selecting {args.word_count} words randomly from a pool of {len(goodWords)} words.')
	for i in range(args.option_count):
		print(f'=== OPTION {i} ===\n')
		chosenWords = [random.choice(goodWords) for _ in range(args.word_count)]
		print(' '.join([word['word'] for word in chosenWords]))

		for j, word in enumerate(chosenWords):
			# Words often have multiple entries, for example as a noun and as a
			# verb. I don't know if this strictly separates parts of speech, or
			# if it has to do with differing etymologies. All senses from all
			# entries for each chosen word should be printed.
			for other in goodWords:
				if other['word'] == chosenWords[j]['word'] and other['senses'][0]['id'] != chosenWords[j]['senses'][0]['id']:
					chosenWords[j]['categories'] |= set(other.get('categories', []))
					chosenWords[j]['senses'].extend(other['senses'])
			if chosenWords[j]['categories']:
				print(f'{chosenWords[j]["word"]} (categories: {", ".join(chosenWords[j]["categories"])})')
			else:
				print(f'{chosenWords[j]["word"]}')
			for k, sense in enumerate(chosenWords[j]['senses']):
				if len(sense['glosses']) == 1:
					print(f'\t{k}. {sense["glosses"][0]}', end='')
					printSenseCatsAndTags(sense)
				else:
					print(f'\t{k}.', end='')
					printSenseCatsAndTags(sense)
					for m, gloss in enumerate(sense['glosses']):
						print(f'\t\t{m}. {gloss}')
			print()

def loadWords (dataPath):
	print('Loading words...')
	with open(dataPath, 'r') as dataFile:
		words = [json.loads(line) for line in dataFile.readlines()]
	return words

def isDecentWord (word, args, categoryExclusions):
	if len(word['word']) > args.char_max:
		return False
	elif not args.phrases and ' ' in word['word'] or '-' in word['word']:
		return False
	elif not word['categories'].isdisjoint(categoryExclusions):
		return False
	# Initialisms are often not tagged as such, so assume all-caps words (with an optional 's' at the end making them plural) are abbreviations.
	elif not args.abbreviations and re.match(r'[A-Z][A-Z0-9&]+s?', word['word']):
		return False
	else:
		return True

def printSenseCatsAndTags (sense):
	if sense['categories']:
		print(f' (categories: {", ".join(sense["categories"])})', end='')
	if sense['tags']:
		print(f' (tags: {", ".join(sense["tags"])})', end='')
	print()

if __name__ == '__main__':
	main()
