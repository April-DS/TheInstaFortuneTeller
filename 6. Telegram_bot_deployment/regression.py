# libraries
import pandas as pd
import numpy as np
import pickle
import subprocess

import glob
import json
from textblob import TextBlob

import xgboost as xgb


# First runs like_predictor function ->
# like_predictor runs user_input function ->
# like_predictor runs comments_df -> comments_df runs scraper
# results == returns: predict_range, predict_likes, predict_engagement, caption_text

# Get input from user
def user_input():
    with open("./User_info/username.txt","r") as username:
        username = username.read()
    with open("./User_info/caption.txt","r") as caption_new_post:
        caption_new_post = caption_new_post.read()
    with open("./User_info/carousel.txt","r") as is_carousel:
        is_carousel = is_carousel.read()
        if is_carousel == "Carousel":
            is_carousel = 1
        else:
            is_carousel = 0
    with open("./User_info/weekday.txt","r") as weekday_publish:
        weekday_publish = weekday_publish.read()
        if weekday_publish == "Monday":
            weekday_publish = 0
        elif weekday_publish == "Tuesday":
            weekday_publish = 1
        elif weekday_publish == "Wednesday":
            weekday_publish = 2
        elif weekday_publish == "Thursday":
            weekday_publish = 3
        elif weekday_publish == "Friday":
            weekday_publish = 4
        elif weekday_publish == "Saturday":
            weekday_publish = 5
        else:
            weekday_publish = 6
    with open("./User_info/hour.txt","r") as hour_publish:
        hour_publish = hour_publish.read()
    return username,caption_new_post,is_carousel,weekday_publish,int(hour_publish)

# Scrape info from Instagram profile
def scraper(username):
    """
    Scrapes data from user instagram account
    Save to json
    """
    subprocess.run(["instagram-scraper",
    username,
     "-m", "10", "-t", "none",
     "--media-metadata",
      "--profile-metadata"],
      shell=True)


# Upload scraped info from Instagram
# Extract useful info from uploaded file
# Return df
def comments_df(username):
    """
    Read json files with info about posts from instagram
    Extracting:
    - num_likes - number of likes
    - num_comments - number of comments
    - post_type - type of post: GraphSidecar=carousel, GraphVideo=video, GraphImage=image
    - photo_id - id of post

    Takes:
    on=False (bool) - on(True) or off(False) function

    Returns:
    df with info about posts
    """
    try:
        scraper(username)
    except Exception as e:
        print(e)
        print('Cannot find you on Instagram :( enter another username.')


    comments = []
    for path in glob.glob('./'+username+'/*.json'):
        file_name = path.split("\\")[1]
        with open('./'+username+'/'+file_name,encoding='utf8') as f:
            data = json.load(f)
            for i in data['GraphImages']:
                one_file = {}
                one_file['num_likes'] = i['edge_media_preview_like']['count']
                one_file['num_comments'] = i['edge_media_to_comment']['count']
                one_file['post_type'] = i['__typename']
                one_file['user_name'] = i['username']
                one_file['photo_id'] = i['shortcode']
                one_file['timestamp'] = i['taken_at_timestamp']
                try:
                    one_file['caption_text'] = i['edge_media_to_caption']['edges'][0]['node']['text']
                except:
                    one_file['caption_text'] = None

                one_file['followers'] = data['GraphProfileInfo']['info']['followers_count']
                comments.append(one_file)
    comments = pd.DataFrame.from_dict(comments)
    # comments.to_csv('netgeo.csv')
    return comments


print('Going to predict')

# Analise info from Instagram and inputs
# Predict number of likes and engagement rate
def like_predictor():
    """
    Predict number of likes and like engagement rate

    :param caption_new_post:
    :param is_carousel:
    :param weekday_publish:
    :param hour_publish
    :param df:
    :return: predicted number of likes, predicted like engagement rate in %
    """
    print('Looking in my crystal ball')

    username, caption_text, is_carousel, weekday_publish, hour_publish = user_input()
    df = comments_df(username)

    mean_likes = float(df['num_likes'].mean())
    num_followers = int(df['followers'].mean())
    comment_engagement = df['num_comments'].mean() / num_followers
    polarity_post_txt = TextBlob(caption_text).sentiment.polarity
    subjectivity_post_txt = TextBlob(caption_text).sentiment.subjectivity
    len_caption = len(caption_text)

    features_df = pd.DataFrame({
        'num_followers':num_followers,
        'mean_likes':mean_likes,
        'post_type_carousel':is_carousel,
        'comment_engagement_profile':comment_engagement,
        'len_post_text':len_caption,
        'weekday':weekday_publish,
        'hour':hour_publish,
        'polarity_post_txt':polarity_post_txt,
        'subjectivity_post_txt':subjectivity_post_txt
    }, index=[1])

    if num_followers > 1_000_000:
        print("Wow! You are so popular!")
        like_predictor = pickle.load(open('./regressors/xgb_likes_mega.pkl', "rb"))
        features_order = like_predictor.get_booster().feature_names
        features = features_df[features_order]
        like_prediction = like_predictor.predict(features)
        engagement_prediction = like_prediction[0]/num_followers*100

        predict_range = f'New post will have around {int(round(abs(like_prediction[0]-25000),0))}-' \
                        f'{int(round(like_prediction[0]+25000,0))} likes'
        predict_likes = f'But I bet there will be {int(round(like_prediction[0],0))} likes'
        predict_engagement = f'Like engagement rate of your new post will be around {round(abs(engagement_prediction),5)}%. Very impressive!'
        return predict_range, predict_likes, predict_engagement, caption_text, num_followers

    elif 100_000 <= num_followers < 1_000_000:
        print("Wow! Good post!")
        like_predictor = pickle.load(open('./regressors/xgb_likes_macro.pkl', "rb"))
        features_order = like_predictor.get_booster().feature_names
        features = features_df[features_order]
        like_prediction = like_predictor.predict(features)
        engagement_prediction = like_prediction[0]/ num_followers*100
        if like_prediction <0:
            predict_range = 'But I foresee that you can improve your post significantly...'
            predict_likes = f'For now I can predict only {str(7383)} likes'
            predict_engagement = 'But we believe that your Instagram profile will thrive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers
        else:
            predict_range = f'New post will have around {int(round(abs(like_prediction[0]-1800),0))}' \
                            f'-{int(round(like_prediction[0]+1800,0))} likes'
            predict_likes = f'But I bet there will be {int(round(like_prediction[0],0))} likes'
            predict_engagement = f'Like engagement rate of your new post will be around {round(abs(engagement_prediction),5)}%. Very impressive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers

    elif 20_000 <= num_followers < 100_000:
        print("Wow! you are so popular!")
        like_predictor = pickle.load(open('./regressors/xgb_likes_midi.pkl', "rb"))
        features_order = like_predictor.get_booster().feature_names
        features = features_df[features_order]
        like_prediction = like_predictor.predict(features)
        engagement_prediction = like_prediction[0]/ num_followers*100
        if like_prediction <0:
            predict_range = 'I foresee that you can improve your post significantly...'
            predict_likes = f'For now I can predict only {str(807)} likes'
            predict_engagement = 'But we believe that your Instagram profile will thrive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers
        else:
            predict_range = f'New post will have around {int(round(abs(like_prediction[0]-200),0))}-' \
                            f'{int(round(like_prediction[0]+200,0))} likes'
            predict_likes = f'But I bet there will be {int(round(like_prediction[0],))} likes'
            predict_engagement = f'Like engagement rate of your new post will be around {round(abs(engagement_prediction),5)}%. Very impressive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers

    elif 500 <= num_followers < 20_000:
        print("Wow! Nice account!")
        like_predictor = pickle.load(open('./regressors/xgb_likes_micro.pkl', "rb"))
        features_order = like_predictor.get_booster().feature_names
        features = features_df[features_order]
        like_prediction = like_predictor.predict(features)
        engagement_prediction = like_prediction[0]/ num_followers*100
        if like_prediction <0:
            predict_range = 'I foresee that you can improve your post significantly...'
            predict_likes = f'For now I can predict only less than {100} likes'
            predict_engagement = 'But we believe that your Instagram profile will thrive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers
        else:
            predict_range = f'New post will have around {round(abs(like_prediction[0]-30),0)}' \
                            f'-{round(like_prediction[0]+30,0)} likes'
            predict_likes = f'But I bet there will be {round(like_prediction[0],0)} likes'
            predict_engagement = f'Like engagement rate of your new post will be around {round(abs(engagement_prediction),5)}%. Very impressive!'
            return predict_range, predict_likes, predict_engagement, caption_text, num_followers


    else:
        predict_range = 'Oh! You are so new to Instagram.'
        predict_likes = 'Sorry, We cannot predict number of likes nor engagement rate for you :('
        predict_engagement = 'But we believe that your Instagram profile will thrive!'
        return predict_range, predict_likes, predict_engagement, caption_text, num_followers


# predict_range,predict_likes,predict_engagement,caption_text,num_followers = like_predictor()
# print(predict_range,predict_likes,predict_engagement,caption_text,num_followers)
