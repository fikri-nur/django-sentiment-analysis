import os
from wordcloud import WordCloud
from django.conf import settings
from preprocessing.models import Preprocessing

def generate_word_cloud(text, output_path):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    wordcloud.to_file(output_path)

def generate_wordcloud(sentiment, text):
    wordcloud_dir = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'wordclouds')
    os.makedirs(wordcloud_dir, exist_ok=True)
    
    wc_path = os.path.join(wordcloud_dir, f'{sentiment}_wordcloud.png')
    generate_word_cloud(text, wc_path)

    # Save or update the path in the database
    from preprocessing.models import WordCloud as WordCloudPath
    wc_path_obj, created = WordCloudPath.objects.get_or_create(sentiment=sentiment)
    wc_path_obj.path = wc_path
    wc_path_obj.save()
