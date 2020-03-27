#Import packages this app will need
import pandas as pd
import numpy as np
import dash
import flask
import math
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pickle
import plotly.graph_objs as go
import joblib

#Import files the app runs on 
ndf = pd.read_csv('combined_backup_2.csv')
count_first=pd.read_csv('1st Innings_run_rate.csv').set_index('country')
count_second=pd.read_csv('2nd Innings_run_rate.csv').set_index('country')
stad_first=pd.read_csv('1st Innings_stadium_run_rate.csv').set_index('stadium')
stad_second=pd.read_csv('2nd Innings_stadium_run_rate.csv').set_index('stadium')
with open('first_innings_rmse.pkl', 'rb') as file1:
    first_rmse = pickle.load(file1)
with open('second_innings_rmse.pkl', 'rb') as file2:
    second_rmse = pickle.load(file2)    
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Set up app and rename it to application (this helps AWS find the file)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 
application = app.server

#Set the colours for the various parts of application 
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'figure':'#D3D3D3',
    'header':'#33F9FF' 
}

#Function to enable switching of tabs in app
def serve_layout():

    # send initial layout if there is flask request context
    if flask.has_request_context():
        return layout_index

    # otherwise send every element to dash validator to prevent callback exceptions
    return html.Div([
        layout_index,
        layout_tab_1,
        layout_tab_2

    
    
    ])
    
#Creates tabs at top of page
layout_index = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Historical', value='tab-1'),
        dcc.Tab(label='Predict', value='tab-2')  
    ]),
    html.Div(id='tabs-content')])
    
#Tab 1 content
layout_tab_1  = html.Div(style={'backgroundColor': colors['background']},children=[
    html.Div(style={'backgroundColor': colors['figure'],
                     'fontColor':  colors['text']},
            children=[
                dcc.Dropdown(
                    id='country',
                    options=[{'label': i, 'value': i} for i in ndf.country.unique()],
                    value='Australia',
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '49%'}
                ),

                dcc.Dropdown(
                    id='year',
                    options=[{'label': i, 'value': i} for i in ndf.year.unique()],
                    value=2020,
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '49%'}
                ),
                dcc.Dropdown(
                    id='stadium',
                    
                   
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '49%'}
                ),
                dcc.Dropdown(
                    id='int_dom',
                    options=[{'label': i, 'value': i} for i in ndf.international.unique()],
                    value='Domestic',
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '49%'}
                ),
       
                dcc.Dropdown(id='title',
                            style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '49%'}),

                dcc.Dropdown(
                    id='innings_drop',
                    options=[{'label': k, 'value': k} for k in ['1st Innings','2nd Innings']],
                    value='1st Innings',
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                                   'width': '49%'})
    ]),
    html.H1(id='header',
        
            style={
                'textAlign': 'center',
                'color': colors['header'],
                'fontSize':20
        }),
                     
    
    html.Div([
        html.H1(id='innings',
                
                style={
                    'textAlign': 'center',
                    'color': colors['header'],
                    'fontSize':20}),
        html.H1(id='score',
               style={
                    'textAlign': 'center',
                    'color': colors['header'],
                    'fontSize':20}),
        dcc.RadioItems(id='speed',
                   options=[{'label': 'PLAY', 'value': 1*1000},
                        
                           {'label': 'RESET', 'value': 60 * 60 * 1000}
                           ],
                   style={
                    'textAlign': 'left',
                    'color': colors['header']},
                           
                           
                   value=60 * 60 * 1000
                ),
        html.Div([
            dcc.Graph(id='graph-with-slider')],
                            style={'display': 'inline-block', 
                                   'width': '49%','height':'49%'
                                  }),
        html.Div([
            dcc.Graph(id='wick_with-slider')],style={'display': 'inline-block', 
                                                     'width': '49%',
                                                     }),
        html.Div([
            dcc.Graph(id='manhatten')],style={'display': 'inline-block', 
                                                     'width': '49%',
                                                     }),
        html.Div([
            dcc.Graph(id='cumulative')
        ],
            
            style={'display': 'inline-block','width': '49%'}
                                                                                                    
    )
                
    ]),
                            
    dcc.Slider(
                id='year-slider',
                min=ndf['over'].min(),
                max=ndf['over'].max(),
                value=0,
                marks={str(over): str(over) for over in ndf['over'].unique()},
                step=None,
            

            ),
    dcc.Interval(
            id='interval-component',
            n_intervals=0,
            max_intervals=20
             # in milliseconds
            
        ),
    html.Div([html.H1(id='results',style={
                'textAlign': 'center',
                'color': colors['header'],
                'fontSize':20
        })])
    
                    
     

])
#Tab 2 content
layout_tab_2 = html.Div(style={'backgroundColor': colors['background']},children=[
            html.Div(style={'backgroundColor': colors['figure'],
                     'fontColor':  colors['text']},
                children=[
                dcc.Dropdown(
                    id='country_pred',
                    options=[{'label': i, 'value': i} for i in ndf.country.unique()],
                    placeholder="Country",
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '50%'}
                ),

                dcc.Dropdown(
                    id='stadium_pred',
                    placeholder="Stadium",
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '50%'}
                ),
                dcc.Dropdown(
                    id='tod',
                    options=[{'label': i, 'value': i} for i in ['Day','Day/Night','Night']],
                    placeholder="Time of Day",
                    style={'backgroundColor': colors['figure'],
                           'fontColor':  colors['text'],
                           'display': 'inline-block',
                           'width': '50%'}
                ),
       
                dcc.Dropdown(id='inn',
                            options=[{'label': i, 'value': i} for i in ndf.innings.unique()],
                            placeholder="Innings",
                            style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '50%'}),
                dcc.Input(id='over',type='text',placeholder='Over',
                          style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '25%'}),
                dcc.Input(id='runs',type='text',placeholder='Score at Over',
                         style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '25%'}),
                dcc.Input(id='wickets',type='text',placeholder='Wickets Lost',
                         style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '25%'}),
                dcc.Input(id='target',type='text',placeholder='Target (if second innings)',
                         style={'backgroundColor': colors['figure'],
                                   'fontColor': colors['text'],
                                   'display': 'inline-block',
                                   'width': '25%'})
    
                    ]),
            html.Div(style={'backgroundColor': colors['background']},children=[
                html.H1(id='instruct',
                       children=["T20 Innings Score and Win Predictor",
                                  html.Br(),
                                 "Input the match state above to receive predicted final innings score and likelihood of winning",
                                  html.Br(),
                                 "Note: This is not the probability of winning but the likelihood.",
                                 html.Br(),
                                 'For example, if the likelihood of winning is 70% that means that if this situation is played out 100 times, then you would expect the batting team to win 70 times',
                                 html.Br(),
                                 "If over to over this likelihood increases, then the batting team's chances of winning has increased."],
                       style={'textAlign': 'center',
                              'color': colors['text'],
                              'fontSize':20})
            ]),
            html.Div(children=[
            html.Div(style={'backgroundColor': colors['background']},children=[
                html.H1(id='predict',
                       style={'textAlign': 'center',
                              'color': colors['header'],
                              'fontSize':20}),
            ]),
                
            html.Div(id='p_pie'
            ),
            ]
            )          
                            
            
])


app.layout = serve_layout
#callback index
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return layout_tab_1
    elif tab == 'tab-2':
        return layout_tab_2

 #callback tab 1
@app.callback(
    Output('stadium', 'options'),
    [Input('country', 'value'),
     Input('year','value'),
     ])    
def set_options2(country,year):
    options=ndf[(ndf.year==year)&(ndf.country==country)]
    return [{'label': i, 'value': i} for i in options.Stadium.unique()]
@app.callback(
    Output('stadium', 'value'),
    [Input('stadium', 'options')])
def set_value2(available_options):
    return available_options[0]['value']
@app.callback(
    Output('title', 'options'),
    [Input('country', 'value'),
     Input('year','value'),
     Input('stadium','value'),
     Input('int_dom','value')
     ])   
def set_options(country,year,stadium,dom):
    options=ndf[(ndf.year==year)&(ndf.country==country)&(ndf.Stadium==stadium)&(ndf.international==dom)]
    return [{'label': i, 'value': i} for i in options.title.unique()]
@app.callback(
    Output('title', 'value'),
    [Input('title', 'options')])
def set_value(available_options):
    return available_options[0]['value']
@app.callback(
    Output('header', 'children'),
    [Input('title', 'value')])
def set_title(title):
    df=ndf[ndf.title==title]
    df.reset_index(drop=True,inplace=True)
    return df.title[0]
@app.callback(
    Output('innings', 'children'),
    [Input('title', 'value'),
     Input('innings_drop', 'value')])
def set_innings(title,innings_radio):
    df=ndf[(ndf.title==title)]
    df.reset_index(drop=True,inplace=True)
    if innings_radio=='1st Innings':
        heading=df.bat_first[0] + ' Innings'
    elif innings_radio=='2nd Innings':
        heading=df.bat_second[0] + ' Innings'
    return heading
@app.callback(
    Output('interval-component', 'interval'),
    
    [Input('speed', 'value')
     ]
    )
def update_output(speed):
    return speed
@app.callback(
    Output('interval-component', 'n_intervals'),
    [Input('speed', 'value'),
    Input('innings_drop','value')])
def update_output2(speed,innings):
    if speed==60*60*1000:
        return 0
    elif innings=='1st Innings' or innings=='2nd Innings':
        return 0
@app.callback(Output('speed','value'),
             [Input('innings_drop','value')
              ])
def speed_reset(value):
    if value=='1st Innings' or value=='2nd Innings':
        return 60 * 60 * 1000
@app.callback(
    Output('year-slider', 'value'),
    
    [Input('interval-component', 'n_intervals')
     ]
    )
def update_output(speed):
    return speed       
@app.callback(
    Output('score', 'children'),
    [Input('year-slider', 'value'),
     Input('title', 'value'),
     Input('innings_drop', 'value')])
def set_score(selected_over,title,innings_radio):
    df=ndf[(ndf.title==title)&(ndf.innings==innings_radio)&(ndf.over==selected_over)]
    df.reset_index(drop=True,inplace=True)
    required=round((df['2nd_target'][0]-df.score_at_over[0])/(20-selected_over),2)
    if df.wickets_lost[0]!=10:
        if innings_radio=='1st Innings':
            score= [str(df.score_at_over[0]) + ' for ' + str(df.wickets_lost[0]) + ', over ' + str(df.over[0]),
                   html.Br(), 'Run Rate: ' + str(round(df.run_rate[0],2))]
        elif innings_radio=='2nd Innings':
            score= [str(df.score_at_over[0]) + ' for ' + str(df.wickets_lost[0]) + ', over ' + str(df.over[0]) +', target ' + str(df['2nd_target'][0]).split('.')[0],
                   html.Br(), 'Run Rate: ' + str(round(df.run_rate[0],2)), '  Required Run Rate: ' +str(required)]
    elif df.wickets_lost[0]==10:
        if innings_radio=='1st Innings':
            score= str(df.score_at_over[0]) + ' all out' + ', over ' + str(df.over[0]) 
        elif innings_radio=='2nd Innings':
            score= str(df.score_at_over[0]) + ' all out' + ', over ' + str(df.over[0]) +', target ' + str(df['2nd_target'][0]).split('.')[0]
    
    
    
    return score
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('title','value'),
     Input('innings_drop','value')])
def update_figure(selected_over,title,innings_radio):
    df = ndf[(ndf.title==title)&(ndf.over <= selected_over)&(ndf.innings==innings_radio)]
    if innings_radio=='1st Innings':
        return {
            'data': [{'x':df['over'],'y':df['predict'],'name':'Prediction'},
                     {'x':df['over'],'y':df['score_at_over'],'name':'Score','line':{'color':'firebrick'}},
                     {'x':df['over'],'y':df['one_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['two_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['three_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['four_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},

                     ],
            'layout': {'title':'Prediction Per Over',
                       'xaxis':{'title': 'Over','range':[0,20]},
                       'yaxis':{'title': 'Runs','range':[0,250]},
                       'margin':{'l': 40, 'b': 40, 't': 80, 'r': 10},
                       'hovermode':'closest',
                       'plot_bgcolor': colors['figure'],
                       'paper_bgcolor': colors['background'],
                       'font': {'color': colors['text']
                    }}}
    elif innings_radio=='2nd Innings':
    
    

        return {
            'data': [{'x':df['over'],'y':df['predict'],'name':'Prediction'},
                     {'x':df['over'],'y':df['score_at_over'],'name':'Score','line':{'color':'firebrick'}},
                     {'x':df['over'],'y':df['2nd_target'],'name':'Target'},
                     {'x':df['over'],'y':df['one_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['two_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['three_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                     {'x':df['over'],'y':df['four_wicket'],'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},

                     ],
            'layout': {'title':'Prediction Per Over',
                       'xaxis':{'title': 'Over','range':[0,20]},
                       'yaxis':{'title': 'Runs','range':[0,250]},
                       'margin':{'l': 40, 'b': 40, 't': 80, 'r': 10},
                       'hovermode':'closest',
                       'plot_bgcolor': colors['figure'],
                       'paper_bgcolor': colors['background'],
                       'font': {'color': colors['text']
                    }}}
@app.callback(
    Output('wick_with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('title','value'),
     Input('innings_drop','value')])
def update_figure_2(selected_over,title,innings_radio):
    df = ndf[(ndf.title==title)&(ndf.over == selected_over)&(ndf.innings==innings_radio)]
    df.reset_index(drop=True,inplace=True)
    figure=go.Figure(data= go.Pie(title='Outcome Probabilities',
                                  hole=0.6,
                                  labels=['Win %','Loss %','Draw %'],
                                  values=[df.win_perc[0],df.loss_perc[0],df.draw_perc[0]],
                                  marker= {'colors': [
                                                 'rgb(0, 204, 0)',  # Green
                                                 'rgb(215,11,11)',  # Yellow
                                                 'rgb(255,255,0)']}
                                 ),
                     layout={'plot_bgcolor': colors['background'],
                             'paper_bgcolor': colors['background'],
                             'font':{'color':colors['text']}}
                     )
    
    

    return figure
@app.callback(
    Output('manhatten', 'figure'),
    [Input('year-slider', 'value'),
     Input('title','value'),
     Input('innings_drop','value')])
def update_figure_3(selected_over,title,innings_radio):
    df = ndf[(ndf.title==title)&(ndf.over <= selected_over)&(ndf.innings==innings_radio)]
    df.reset_index(drop=True,inplace=True)
    figure={
            'data': [
                {'x': [j for j in df.over], 'y': [i for i in df.runs], 'type': 'bar', 'name': 'Runs'},
                {'x': [j for j in df.over], 'y': [i for i in df.wickets], 'type': 'bar', 'name': u'Wickets'},
            ],
            'layout': {
                'title':'Manhatten',
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'xaxis':{'title': 'Over','range':[0,20]},
                'yaxis':{'range':[0,25]},
                'font': {
                    'color': colors['text']
                }
            }
        }
    

    return figure
@app.callback(
    Output('cumulative', 'figure'),
    [Input('year-slider', 'value'),
     Input('title','value'),
     Input('innings_drop','value')])
def update_figure_4(selected_over,title,innings_radio):
    df = ndf[(ndf.title==title)&(ndf.over <= selected_over)&(ndf.innings==innings_radio)]
    df.reset_index(drop=True,inplace=True)
    if innings_radio=='1st Innings':
        
        figure=go.Figure(data=[
                        go.Bar(name='Score Progression', x=[i for i in df.over], y=[j for j in df.score_at_over]),
                        {'x':df['over'],'y':df['one_wicket']+5,'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                         {'x':df['over'],'y':df['two_wicket']+10,'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                         {'x':df['over'],'y':df['three_wicket']+15,'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
                         {'x':df['over'],'y':df['four_wicket']+20,'mode':'markers','marker': {'size': 12,'color':'firebrick'},'showlegend':False},
            
                        ],layout={'plot_bgcolor': colors['background'],
                                 'paper_bgcolor': colors['background'],
                                 'font':{'color':colors['text']},
                                 'xaxis':{'title':'Over'},
                                 'yaxis':{'title':'Runs'}})
    elif innings_radio=='2nd Innings':
        
        figure=go.Figure(data= go.Pie(title='Chase',
                                      direction='clockwise',
                                      labels=['1st Score','2nd Score'],
                                      values=[df['2nd_target'].max()-df.score_at_over.max(),df.score_at_over.max()],
                                      marker= {'colors': [
                                                     'rgb(0, 204, 0)', 
                                                     'rgb(215,11,11)' 
                                                    ]}
                                     ),
                         layout={'plot_bgcolor': colors['background'],
                                 'paper_bgcolor': colors['background'],
                                 'font':{'color':colors['text']}}
                         )



    return figure
@app.callback(Output('results','children'),
              [Input('innings_drop','value')])
def explain(innings):
    if innings=='1st Innings':
        children=['1st Innings Visualisations:',
                  html.Br(),
                  'Top Left: Worm of predicted score vs actual score per over',
                  html.Br(),
                  'Top Right: Pie chart showing likelihood of batting team winning',
                  html.Br(),
                  html.Br(),
                  "*Note* Interpretation: If likelihood of winning increases, then the batting team's most recent action has increased their chance of winning",
                  html.Br(),
                  html.Br(),
                  'Bottom Left: Manhatten of runs scored and wicket lost each over',
                  html.Br(),
                  'Bottom Right: Expanding bar chart showing score progression throughout innings']
        return children
    elif innings=='2nd Innings':
        children=['2nd Innings Visualisations:',
                  html.Br(),
                  'Top Left: Worm of predicted score vs actual score per over and target score',
                  html.Br(),
                  'Top Right: Pie chart showing likelihood of batting team winning',
                  html.Br(),
                  html.Br(),
                  "*Note* Interpretation: If likelihood of winning increases, then the batting team's most recent action has increased their chance of winning", 
                  html.Br(),
                  html.Br(),
                  'Bottom Left: Manhatten of runs scored and wicket lost each over',
                  html.Br(),
                  'Bottom Right: Pie chart showing % of target runs batting team has achieved']
        return children
    
#callback tab 2
@app.callback(
    Output('stadium_pred', 'options'),
    [Input('country_pred', 'value'),
     ])    
def set_options3(country):
    options=ndf[(ndf.country==country)]
    return [{'label': i, 'value': i} for i in options.Stadium.unique()]
@app.callback(
    Output('predict', 'children'),
    [Input('country_pred', 'value'),
     Input('stadium_pred', 'value'),
     Input('tod', 'value'),
     Input('inn', 'value'),
     Input('over', 'value'),
     Input('runs', 'value'),
     Input('wickets', 'value'),
     Input('target', 'value')])
def set_predict(cr,sr,tod,inn,over,runs,wickets,target):
    if int(over)>21:
        return 'Maxiumum number of overs is 20'
    else:
        if int(wickets)>9:
            return 'Maximum number of wickets for prediction is 9'
        if tod=='Day':
            dn=0
            ng=0
        elif tod=='Day/Night':
            dn=1
            ng=0
        elif tod=='Night':
            dn=0
            ng=1
        if inn=='1st Innings':
            crr=count_first.run_rate[cr]
            srr=stad_first.run_rate[sr]
            df=pd.DataFrame({'1':dn,'2':ng,'3':runs,'4':wickets,'5':crr,'6':srr},index=[0])
            print(df)
            load=str(over)+'_first_regress.jlib'
            model_reg=joblib.load(load)
            pred=model_reg.predict(df)[0]
            if pred>int(runs):
                out=round(pred,0)
                lower=int(round(out-1.96*first_rmse[int(over)],0))
                if lower<int(runs):
                    lower=int(runs)
                upper=int(round(out+1.96*first_rmse[int(over)],0))
            else:
                lower=int(runs)
                upper=int(round(int(runs)+1.96*first_rmse[int(over)],0))
         

        elif inn=='2nd Innings':
            crr=count_second.run_rate[cr]
            srr=stad_second.run_rate[sr]
            df=pd.DataFrame({'1':dn,'2':ng,'3':runs,'4':wickets,'5':crr,'6':srr,'7':target},index=[0])
            load=str(over)+'_second_regress.jlib'
            model_reg=joblib.load(load)
            pred=model_reg.predict(df)[0]
            if pred>int(runs):
                out=round(pred,0)
                lower=int(round(out-1.96*first_rmse[int(over)],0))
                if lower<int(runs):
                    lower=int(runs)
                upper=int(round(out+1.96*first_rmse[int(over)],0))
            else:
                lower=int(runs)
                upper=int(round(int(runs)+1.96*first_rmse[int(over)],0))
  

        return ['Predicted Score: ' + str(out),
                html.Br(),
                'Confidence Interval: (' + str(lower) + ', ' + str(upper) + ')']


@app.callback(
    Output('p_pie', 'children'),
    [Input('country_pred', 'value'),
     Input('stadium_pred', 'value'),
     Input('tod', 'value'),
     Input('inn', 'value'),
     Input('over', 'value'),
     Input('runs', 'value'),
     Input('wickets', 'value'),
     Input('target', 'value')])
def update_figure_5(cr,sr,tod,inn,over,runs,wickets,target):
    if tod=='Day':
        dn=0
        ng=0
    elif tod=='Day/Night':
        dn=1
        ng=0
    elif tod=='Night':
        dn=0
        ng=1
   
    if inn=='1st Innings':
        crr=count_first.run_rate[cr]
        srr=stad_first.run_rate[sr]
        df=pd.DataFrame({'1':dn,'2':ng,'3':runs,'4':wickets,'5':crr,'6':srr},index=[0])
        load=str(over)+'_first_regress.jlib'
        model_reg=joblib.load(load)
        pred1=model_reg.predict(df)[0]
        if pred1<int(runs):
            ndf=pd.DataFrame({'1':dn,'2':ng,'5':crr,'6':srr,'7':runs},index=[0])
        else:
            ndf=pd.DataFrame({'1':dn,'2':ng,'5':crr,'6':srr,'7':pred1},index=[0])
            
        load=str(over)+'_first_class.jlib'
        model_class=joblib.load(load)
        pred=model_class.predict_proba(ndf)[0]
        
    elif inn=='2nd Innings':
        crr=count_second.run_rate[cr]
        srr=stad_second.run_rate[sr]
        df=pd.DataFrame({'1':dn,'2':ng,'3':runs,'4':wickets,'5':crr,'6':srr,'7':target},index=[0])
        load=str(over)+'_second_regress.jlib'
        model_reg=joblib.load(load)
        pred1=model_reg.predict(df)[0]
        if pred1<int(runs):
            ndf=pd.DataFrame({'1':dn,'2':ng,'5':crr,'6':srr,'7':target,'8':runs},index=[0])
        else:
            ndf=pd.DataFrame({'1':dn,'2':ng,'5':crr,'6':srr,'7':target,'8':pred1},index=[0])
        
        load=str(over)+'_second_class.jlib'
        model_class=joblib.load(load)
        pred=model_class.predict_proba(ndf)[0]

        


   
    children=dcc.Graph(figure=go.Figure(data= go.Pie(title='Outcome Probabilities',
                                  hole=0.6,
                                  labels=['Win %','Loss %','Draw %'],
                                  values=[pred[2],pred[1],pred[0]],
                                  marker= {'colors': [
                                                 'rgb(0, 204, 0)',  # Green
                                                 'rgb(215,11,11)',  # Yellow
                                                 'rgb(255,255,0)']}
                                 ),
                     layout={'plot_bgcolor': colors['background'],
                             'paper_bgcolor': colors['background'],
                             'font':{'color':colors['text']}}
                                        
                     )
                      )  
    return children

       
        
    
if __name__ == '__main__':
    application.run(debug=False)
