import pandas as pd
import ast
import photo_recognition
import text_preprocess
import regression

# Это последняя часть программы
# она должна по идеи вызывать все функции
# запускает regression - потом печатает результат (результат сохраняется в переменные, печать для проверки)
# потом запускает photo_recognition (фотография у меня находится сразу в папке, пока нигде нет запроса на скачку фото)
# потом запускает text_preprocess берёт caption_text из результата работы regression
# потом полученная информация что на фото и обработанный текст складываются в один лист
# потом загружает файл с хэштэгами
# потом происходит поиск и пока что поиск только печатает результат
# в итоге я хочу передать этот результат на сайт (сделаю лист из таплов с хэштэгом и популярностью хэштэга)

# Last script which runs all scripts
# 1. Runs regression to take all info from there, most important caption_text
# 2. Runs photo_recognition (take path to photo as a parameter) - returns list of words
# 3. Runs text_preprocess - take caption_text from point 1, returnd caption - list of words
#
# Make one list from what_on_photo and caption
# Uploaded hashtag database
# Search for similar hashtags
# print hashtags

# I want to form list of tuple of hashtags and popularity of hashtag


# Runs photo_recognition and text_preprocess files
def start_all():
    """
    Function runs all other functions
    Searching for useful hashtags (with popularity
    :return:
    """
    predict_range,predict_likes,predict_engagement,caption_text,num_followers = regression.like_predictor()
    print(predict_range, predict_likes, predict_engagement)
    # User_info path to photo
    what_on_photo = photo_recognition.what_on_photo('User_info')
    caption = text_preprocess.process_words(caption_text)
    user_words = what_on_photo + caption

    what_on_photo_message = 'I see on your photo .. ' + ', '.join(set(what_on_photo))
    # Upload hashtag database
    all_hashtags = pd.read_csv('./datasets/all_hashtag_database.csv')
    all_hashtags['similar'] = all_hashtags['similar'].apply(ast.literal_eval)
    all_hashtags['num_posts'] = all_hashtags['num_posts'].apply(ast.literal_eval)

    # check hashtags for user
    all_indices = []
    for word in set(user_words):
        indx = all_hashtags[all_hashtags['base_hash'] == word].index.values.tolist()
        if len(indx) > 0:
            all_indices.extend(indx)

    usefull_hashtags = []
    other_hashtags = []
    for _, row in all_hashtags.loc[set(all_indices), :].iterrows():
        other_hashtags.append('#' + row.original_hash)
        for i in range(len(row)):
            if num_followers * 1000 > int(row.num_posts[i]):
                usefull_hashtags.append('#' + row['similar'][i])
            else:
                other_hashtags.append('#' + row['similar'][i])
    if len(usefull_hashtags) == 0 and len(other_hashtags) == 0:
        hashtags_message_useful = 'Hmmm... I don\'t see anything on your photo or in your text :('
        hashtags_message_other = 'Maybe try write a bit longer caption.'
    else:
        if len(usefull_hashtags) > 0:
            hashtags_message_useful = ', '.join(hashtags for hashtags in usefull_hashtags)
        else:
            hashtags_message_useful = 'I can suggest you only very popular hashtags'

        if len(other_hashtags) > 0:
            hashtags_message_other = ', '.join(hashtags for hashtags in other_hashtags)
        else:
            hashtags_message_other = 'You don\'t need any other hashtags. Those above are just right!'


    return predict_range, predict_likes, predict_engagement, what_on_photo_message, hashtags_message_useful, hashtags_message_other
