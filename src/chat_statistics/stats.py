import json
from collections import Counter, defaultdict
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize, sent_tokenize
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

    def rebuild_msg(self, content):
        """ Rebuild Messages that has mentions in them
        """
        text=""
        for sub_msg in content:
            if sub_msg is str:
                text += sub_msg
            elif sub_msg is dict:
                text += sub_msg['text']
        return text
    def is_question(self, msg):
        sentences = ""
        content = ""
        if not isinstance(msg['text'], str):
            content = self.rebuild_msg(msg['text'])
        else:
            content = msg['text']
        sentences += f" {' '.join(sent_tokenize(content))}"
        for sentence in sentences:
            if '?' in sentence or '؟' in sentence:
                return True
        return False

    def generate_stats(self):
        questions_id = defaultdict(bool)
        self.Users = {}
        logger.info('Evaluating Users Stats...')
        # Extracting stats from messages
        for msg in self.chat['messages']:
            questions_id[msg['id']] = self.is_question(msg)
            if not 'reply_to_message_id' in msg:
                continue
            if questions_id[msg['reply_to_message_id']] is False:
                continue
            if not msg['from_id'] in self.Users:
                self.Users[msg['from_id']] = {
                    'from': msg['from'],
                    'reply_to_id': [],
                    'id': []
                }
            self.Users[msg['from_id']]['reply_to_id'].append(msg['reply_to_message_id'])
            self.Users[msg['from_id']]['id'].append(msg['id'])
        return self.Users
    def get_top_ten(self, top_n = 10):
        logger.info(f'Getting Top {top_n} Users...')
        helper_users = defaultdict(int)
        for user in self.Users.values():
            helper_users[user['from']] = len(user['reply_to_id'])
        return dict(Counter(helper_users).most_common(top_n))

if __name__ == '__main__':
    tele_stats = ChatStatistics(DATA_DIR/'Pytopia.json')
    #tele_stats.generate_wordcloud(DATA_DIR)
    Users = tele_stats.generate_stats()
    print(tele_stats.get_top_ten())
    print('Done!')
