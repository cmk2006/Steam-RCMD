from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import pandas as pd
import numpy as np
import csv
app = Flask(__name__)
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
ubyi = pd.read_csv('./static/userbyitem.csv', index_col=0)
ubyi_norm = np.log(ubyi)
ubyi_norm += abs(ubyi_norm.min().min())
ubyi_norm = ubyi_norm[(~ubyi_norm.isnull()).sum(axis=1) >= 3]
categorys = pd.read_csv('./static/game_category.csv')
ubyi_mf = pd.read_csv('./static/corr.csv')
ubyi_mf = ubyi_mf.set_index('Unnamed: 0')
dick = dict(zip(categorys.Game,categorys.Genre))
cate_time = dict(zip(categorys.Genre.unique(), len(categorys.Genre.unique()) * [0]))
indexusers = ubyi_mf.index.values.tolist()
def recommend_a_game3(user):

    games_to_consider = ubyi_norm.loc[user][ubyi_norm.loc[user].isna()].index.values
    print('We recommend:')
    top5 = ubyi_mf.loc[user, games_to_consider].sort_values(ascending=False)[:5].index.values
    predict_top_5 = {}
    for idx, game in enumerate(top5):
        print('{0}: {1}'.format(idx+1, game))
        if dick[game] in cate_time:
            predict_top_5[game] = dick[game]
        else:
            predict_top_5[game] = 'other'

    return predict_top_5


def get_Pie_chart_data(id):
    user_to_recommend = id
    games_to_consider = ubyi_norm.loc[user_to_recommend][ubyi_norm.loc[user_to_recommend].notna()].index.values
    cate_time = dict(zip(categorys.Genre.unique(), len(categorys.Genre.unique()) * [0]))

    cate_time['other'] = 0

    print(cate_time)
    for games in games_to_consider:
        print(games)
        if dick[games] in cate_time:
            cate_time[dick[games]] += int(ubyi_norm.loc[user_to_recommend][games])
        else:
            cate_time['other'] += int(ubyi_norm.loc[user_to_recommend][games])
    return cate_time
class Input_FORM(FlaskForm):
    """"
    This use for input index
    """
    name = StringField('Nhập số thứ tự ',validators=[DataRequired()])
    submit = SubmitField('Enter')


@app.route('/')
def index():
    return render_template('index.html')

# Crete InputPage
@app.route('/input',methods=['GET', 'POST'])
def name():
    name = None
    data = None
    form = Input_FORM()
    rcmd = {}
    allgameid={}
    gamelink={}
    if form.validate_on_submit():
        name = form.name.data
        name = indexusers[int(name)]
        print(name)
        form.name.data = ''
        data = {}
        user_data = get_Pie_chart_data(int(name))
        rcmd = recommend_a_game3(int(name))
        for j in rcmd:
            print(j)
            gameid=0
            with open('./static/steamcmd_appid.csv') as file_obj:
                reader_obj = csv.reader(file_obj,delimiter=';')
                for row in reader_obj:
                    if (row[1]==j):
                        gameid=row[0]
                        break
            allgameid[j]='https://steamcdn-a.akamaihd.net/steam/apps/'+str(gameid)+'/header.jpg'
            gamelink[j]='https://store.steampowered.com/app/'+str(gameid)
        #print(allgameid)
        #print(gamelink)
        print(rcmd)
        for i in user_data:
            data[i] = user_data[i]

    return render_template('input.html',name = name, form = form,data_id = data, data_predict = rcmd, app_id=allgameid, app_link=gamelink )

if __name__ == "__main__":
    app.run(debug=True)