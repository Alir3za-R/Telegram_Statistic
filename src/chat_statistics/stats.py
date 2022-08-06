import json
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.Data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """ This Class is used for generating a wordcloud from a chat file with json format
    """
    def __init__(self, chat_json):
        logger.info('Reading Chat File...')
        # Reading chat file
        with open(chat_json) as f:
            self.chat = json.load(f)
        # Creating a stop-Words list
        self.normalizer = Normalizer()
        self.stop_words = open(DATA_DIR / 'StopWords.txt').readlines()
        self.stop_words = list(map(str.strip, self.stop_words))
        self.stop_words = list(map(self.normalizer.normalize, self.stop_words))

    def generate_wordcloud(self, output):
        output = Path(output)
        logger.info('Generating Chat...')
        text_content = ""
        # extracting texts from messages
        for msg in self.chat['messages']:
            if isinstance(msg['text'], str):
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda word: word not in self.stop_words, tokens))
                text_content += f" {' '.join(tokens)}"
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)
        # Generating WordCloud
        wordcloud = WordCloud(width=600, height=500, font_path=str(DATA_DIR/'BHoma.ttf'), background_color='White').generate(text_content)
        wordcloud.to_file(str(output/'WORD_CLOUD.png'))


if __name__ == '__main__':
    tele_stats = ChatStatistics(DATA_DIR/'SM_Group.json')
    tele_stats.generate_wordcloud(DATA_DIR)
    print('Done!')
