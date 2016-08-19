# -*- coding: utf-8 -*-

import pickle
import re
import sys
import time
from datetime import datetime
import facebook_part
import vk
import config


class Worker:
    def __init__(self, email, password):
        self.app_id = config.client_id
        self.user_login = email
        self.user_password = password
        self.scope = config.scope
        self.tm = 9000
        self.line = '\n--------------------\n'
        self.double_line = '\n====================\n'

    def main(self):
        self.start_session()
        self.post = self.get_last_vk_post(self.api)
        if not self.check_repost():
            self.date = self.get_date(self.post)
            if not self.check_date(self.date):
                self.display_new()
                if self.check_wiki(self.post):
                    if not self.check_wiki_photos(self.post):
                        self.text = self.wiki(self.post)
                        jpeg_link = self.get_jpeg_link(self.post)
                        facebook_part.main(self.text, jpeg_link)
                        self.save_date(self.date)
                        text = self.text[:200]
                        self.display_posted(text)
                        self.display_time_to_next(self.tm)
                    else:
                        self.text = self.wiki(self.post)
                        text = self.text[:200]
                        self.display_wiki_photo(text)
                        self.display_time_to_next(self.tm)
                else:
                    text = self.get_text(self.post)
                    text = self.get_text(self.post)
                    self.text = self.edit_post(text)
                    print(self.text)
                    try:
                        video = self.check_video(self.post, self.api)
                        self.text += '\n' + video
                    except:
                        pass
                    try:
                        jpeg_link = self.get_jpeg_link(self.post)
                        facebook_part.main(self.text, jpeg_link)
                    except KeyError:
                        facebook_part.main2(self.text)
                    self.save_date(self.date)

                    txt = self.text[:200]
                    self.display_posted(txt)
                    self.display_time_to_next(self.tm)
            else:
                text = self.get_text(self.post)
                text = text[:200]
                self.display_exist(text)
                self.display_time_to_next(self.tm)
        else:
            text = self.get_text(self.post)
            text = text[:200]
            self.display_repost(text)
            self.display_time_to_next(self.tm)

    def start_session(self):
        try:
            self.session =vk.AuthSession(app_id=self.app_id, user_login=self.user_login, user_password=self.user_password,\
                                scope=self.scope)
            self.api = vk.API(self.session)
        except vk.exceptions.VkAuthError as e:
            self.display_session_fail()

    def get_last_vk_post(self,api):  #получаем сам пост через апи
        try:
            post = api.wall.get(domain=config.domain, offset=1, count=1)
            return post
        except:
            print('No answer')
            pass

    def check_repost(self):
        try:
            if self.post[1]['copy_owner_id']:
                return True
        except KeyError:
            return False

    def get_date(self, post):  #получаем номер поста
        date = self.post[1]['date']
        return date

    def check_date(self, date):
        try:
            with open('log', 'rb') as file:
                pages = pickle.load(file)
                if date in pages:
                    return True
                else:
                    return False
        except:
            return False

    def check_wiki(self, post):
        try:
            if post[1]['attachments'][1]['type'] == 'page':
                return True
        except:
            return False

    def check_wiki_continue(self, post):
        p_id = post[1]['attachments'][1]['page']['pid']
        page = self.api.pages.get(owner_id=config.o_id, page_id=p_id)
        wiki_text = page['source']
        pattern = re.compile(r'Продолжение:[\s\S]*\[\[[\d]*|')
        if re.match(pattern,wiki_text):
            return True

    def wiki(self, post):
        text_for_tag = self.get_text(post)
        tag_pattern = re.compile('[\w|#]*@skepdic')
        tag = re.findall(tag_pattern, text_for_tag)
        tag = tag[0]
        tag = tag.replace('@', '_')
        p_id = post[1]['attachments'][1]['page']['pid']
        page = self.api.pages.get(owner_id=config.o_id, page_id=p_id)
        title = post[1]['attachments'][1]['page']['title']
        wiki_text = page['source']
        text_source_index = wiki_text.rfind('Источник:')
        text=wiki_text[:text_source_index]
        text_source=wiki_text[text_source_index:]
        source = re.sub(r'\|[\w\s\S]*]','',text_source)
        source = source.replace('[','')
        text = self.wiki_to_plain(text)
        text = title + '\n\n' + 'Рубрика: ' + tag + '\n\n' + text +'\n\n'+source
        return text


    def wiki_to_plain(self,text):
        if 'http' in text:
            link_pattern = re.compile(r'http[s]?:\/\/[\w\.\/%\?\=\&\;\#\-\-]*\|')
            text = re.sub(link_pattern,'', text)
        if 'photo' in text:
            photo_pattern = re.compile(r'\[\[photo[\w|\|\s]*\]\]')
            text = re.sub(photo_pattern,'', text)
        if '[[id' in text:
            author_pattern = re.compile(r'\[\[id[\w]*\|')
        #all = re.findall(link_pattern, text)
            text = re.sub(author_pattern,'',text)
        if '<br><br><br><br>' in text:
            text = text.replace('<br><br><br><br>','\n')
        if '<br>' in text:
            text = text.replace('<br>','\n')
        if ']' in text:
            text = text.replace(']','')
        if '&lt;' in text:
            text = text.replace('&lt;','')
        if 'blockquote&gt;' in text:
            text = text.replace('blockquote&gt;','')
        if '/blockquote&gt;' in text:
            text = text.replace('/blockquote&gt;','')
        if 'center&gt' in text:
            pattern = re.compile('center[\[\w|&|;]*\|')
            text = re.sub(pattern,'',text)
            text = text.replace('/center&gt','')
        if 'center&gt' in text:
            pattern = re.compile(r'center[\&\w]*;[\w\s\,\—\.\'\-]*;')
            text = re.sub(pattern, '',text)

        text = text.replace('[','')
        if '\n\n' in text:
            text= text.replace('\n\n\n\n','\n')
        if "''" in text:
            text = text.replace("''",'')
        if '\\' in text:
            text = text.replace('\\','\n')

        return text

    def check_wiki_photos(self, post):
        p_id = post[1]['attachments'][1]['page']['pid']
        page = self.api.pages.get(owner_id=config.o_id, page_id=p_id)
        wiki_text = page['source']
        if 'photo' in wiki_text:
            return True

    def get_text(self, post):  # получаем текст поста
        text = post[1]['text']
        return text

    def edit_post(self, post):  # редактируем пост
        text = post.replace('[club34689126|', '')
        text = text.replace('<br>', '\n')
        text = text.replace(']', '')
        text = text.replace('&gt;', '')

        index = text.find('@')
        if index != -1:
            text1 = text[:index]
            text2 = text[index + 1:]
            text = text1 + '_' + text2

        translator_pattern = re.compile('\[[\w]*\|')
        text = re.sub(translator_pattern, '', text)

        text = text.replace('[', '')
        return text

    def check_video(self,post,api):
        v_id = post[1]['attachment']['video']['vid']
        query = str(config.o_id)+'_'+str(v_id)
        video = api.video.get(owner_id=config.o_id,videos=query)
        if video[1]['player'].startswith('http://www.youtube'):
            video_url = video[1]['player']
            return video_url

    def get_jpeg_link(self,post):  #получаем ссылку на картинку поста
        jpeg_link = post[1]['attachment']['photo']['src_big']
        return jpeg_link

    def save_date(self,date):
        try:
            with open('log', 'rb') as file:
                pages = pickle.load(file)
                pages.append(date)
            with open('log', 'wb') as file:
                pickle.dump(pages, file)
        except:
            pages = []
            pages.append(date)
            with open('log','wb') as file:
                pickle.dump(pages, file)

    def start(self):
        print('Запуск сессии...\n')

    def display_session_fail(self):
        print('Неправильно введен пароль\n')

    def display_repost(self, text):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M')
        text = dt + self.line + text + self.line + 'Это репост' + self.double_line
        print(text)

    def display_exist(self, text):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M')
        text = dt + self.line + text + self.double_line + 'Эта страница уже опубликована' + self.double_line
        print(text)

    def display_new(self):
        text = 'Ура, новая страница!\n'
        print(text)

    def display_posted(self, text):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M')
        text = dt + self.line + text + self.line + 'Эта страница успешно опубликована' + self.double_line

        print(text)

    def display_wiki_photo(self, text):
        dt = datetime.now().strftime('%Y-%m-%d %H:%M')
        text = dt + self.line + text + self.line \
               + 'Это вики-страница со множеством фотографий\nПожалуйста, выложите ее вручную' + self.double_line
        print(text)

    def display_time_to_next(self, tm):
        tm = str(int(tm) // 60 // 60)
        text = 'Следующая проверка через ' + tm + ' часа' + self.double_line
        print(text)


email = config.email    
password = config.password

reposter = Worker(email, password)
reposter.main()

