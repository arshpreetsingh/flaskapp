
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
from time import mktime 
from flask import send_file, make_response
from flask import Flask, render_template, redirect, request
from filesystem import Folder, File
from action import *
from flask import request
from os import error

import logging
from logging.handlers import RotatingFileHandler
from collections import Counter
from flask import Flask, redirect, url_for, session, request, jsonify
from flask_oauthlib.client import OAuth

from flask.ext.script import Server, Manager, Shell

from flask import render_template
from imaplib import IMAP4_SSL
import imaplib 
from datetime import date, timedelta, datetime 
from time import mktime 
from email.utils import parsedate 
import email
import pygal
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)

app.config.update(
    DEBUG=True,
    FILES_ROOT=os.path.dirname(os.path.abspath(__file__)),
)

auth = HTTPBasicAuth()

users = {
    "admin": "survey@optoseo.com",
    "susan": "bye"
}
app.config['GOOGLE_ID'] = '458156809693-fbmbg64nseq5m83c43ne2vu02mup676f.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = 'nW7tSPqvxTTGZ19yjfGQDgE2'

app.config['daily'] = '/var/www/flaskapp/ANALYSIS/flow-analysis-daily'
app.config['weekly'] = '/var/www/flaskapp/ANALYSIS/flow-analysis-weekly'
app.config['daily_ratio'] = '/var/www/flaskapp/ANALYSIS/email-ratio-daily'
app.config['weekly_ratio'] = '/var/www/flaskapp/ANALYSIS/email-ratio-weekly'

app.config['daily_wordcount'] = '/var/www/flaskapp/ANALYSIS/wordcount-daily'

app.config['weekly_wordcount'] = '/var/www/flaskapp/ANALYSIS/wordcount-weekly'

app.config['monthly-activity-inbox'] = '/var/www/flaskapp/ANALYSIS/monthly-activity-inbox'

app.config['monthly-activity-outbox'] = '/var/www/flaskapp/ANALYSIS/monthly-activity-outbox'


app.debug = True


app.secret_key = 'development'

# OAuth class da instance create kitta hoya hai...
# app argument ditta hai, app apni application da name hai
oauth = OAuth(app)

# next remote_app feature  nu use kitta hoya hai and esnnu e use karna hai apan all the time
google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': [
             'https://mail.google.com/',
             'https://www.googleapis.com/auth/admin.directory.user.readonly',
             'https://www.googleapis.com/auth/admin.directory.orgunit.readonly',
             'https://www.googleapis.com/auth/admin.directory.group.readonly',
             'https://www.googleapis.com/auth/userinfo.email',
             'https://www.googleapis.com/auth/userinfo.profile',
             'https://www.googleapis.com/auth/plus.profile.emails.read',
 
],
        'access_type': 'offline'
    },

    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None



#ACCESS_TOKEN = 0
#EMAIL = 0


def week_list_func():
    """ A function returning list of last 6 days in 3-tuple"""
    
    date_list = [] 
    for i in xrange(7):
        d=date.today() - timedelta(i)
        t = d.year, d.month, d.day
        date_list.append(t)
    return list(reversed(date_list))


@app.route('/')

    
@app.route('/index')

def index():

# eh function dass riha hai sab kuch vi j google_token session 
#0vich hai tan ki karo
 
#    if 'google_token' in session:
 #       me = google.get('userinfo')


  #      return jsonify({"data": me.data})
 
#    return redirect(url_for('login'))
    return render_template('index.html',title = 'Gmail Analysis')

@app.route('/login')

def login():
    return google.authorize(callback=url_for('authorized', _external=True))
    

@app.route('/logout')

def logout():
    
    session.pop('google_token', None)

    return redirect(url_for('index'))













@app.route('/daily')

def graph_data():
    
    aa,bb,cc,dd,date = inbox_data()
    a,b,c,d = outbox_data()
    
    "Start making Graphs"
    
    stackedline_chart = pygal.StackedLine(fill=True)
    stackedline_chart.title = 'Daily Email Analysis' + ' \n Date = '+date

    stackedline_chart.x_labels = ('Midnight','6 AM','Noon','6 PM')

    stackedline_chart.add('Received', [aa,bb,cc,dd])

    stackedline_chart.add('Sent', [a,b,c,d])
    
    chart = stackedline_chart.render(is_unicode=True)
    
    stackedline_chart.render_to_file(os.path.join(app.config['daily'],'dalily_'+EMAIL+'_.svg'))
    
    return render_template('daily.html', chart = chart)

@app.route('/weekly')

def week_graph_data():

    # shorten the dates and tuple
    
    try:
        dates_outbox = tuple(b[:-7] for b in outbox_week())
        dates_inbox = tuple(a[:-7] for a in inbox_week())
    
        week_list = week_list_func()
    
        bar_chart = pygal.Bar()
    
        bar_chart.title = 'Weekly Email Analysis'
    
        bar_chart.x_labels = (week_list_func())
    
        bar_chart.add('Sent', [sum(t==i for t in dates_outbox) for i in week_list])
    
        bar_chart.add('Received', [sum(m==n for n in dates_inbox) for m in week_list])
    
        week_chart = bar_chart.render(is_unicode = True)
    
        bar_chart.render_to_file(os.path.join(app.config['weekly'],'weekly_'+EMAIL+'_.svg'))

        return render_template('weekly.html',week_chart = week_chart)
    except:
		pass

@app.route('/weekly-pieAnalysis')

def week_pie_data_graph():

    a = weekly_inbox_data_piechart()
    b = weekly_outbox_data_piechart()
    c = weekly_important_data_piechart()
    d = weekly_archieved_data_piechart()
    e = weekly_trashed_data_piechart()


    pie_chart = pygal.Pie()
    pie_chart.title = 'Different Parts of your Gmail'+ '\n'+'Date Range = From '+ \
    str(datetime.now() - timedelta(6)) + ' '+'to'+ ' ' + str(datetime.now())
    pie_chart.add('Inbox', a)
    pie_chart.add('Sent', b)
    pie_chart.add('Important',c )
    pie_chart.add('Archived', d)
    pie_chart.add('Trashed',e)
    week_chart = pie_chart.render(is_unicode = True)
    pie_chart.render_to_file(os.path.join(app.config['weekly_ratio'],'weekly_'+EMAIL+'_.svg'))

    return render_template('weekly_pie.html',week_chart = week_chart)





@app.route('/daily-pieAnalysis')

def daily_pie_data_graph():

    a = daily_inbox_data_piechart()
    b = daily_outbox_data_piechart()
    c = daily_important_data_piechart()
    d = daily_archieved_data_piechart()
    e = daily_trashed_data_piechart()


    pie_chart = pygal.Pie()
    pie_chart.title = 'Different Parts of your Gmail'+'\n'+'Date='+str(datetime.now())
    pie_chart.add('Inbox', a)
    pie_chart.add('Sent', b)
    pie_chart.add('Important',c )
    pie_chart.add('Archived', d)
    pie_chart.add('Trashed',e)
    chart = pie_chart.render(is_unicode = True)
    pie_chart.render_to_file(os.path.join(app.config['daily_ratio'],'daily_'+EMAIL+'_.svg'))


    return render_template('daily_pie.html',chart = chart)

@app.route('/daily-wordcount')

def word_count_daily_data():
	 
    a,b,c,d,e = word_count_daily_inbox()
    
    a1,b1,c1,d1,e1 = word_count_daily_outbox()
    
    bar_chart = pygal.Bar()
    bar_chart.title = 'Word Count Analysis'+'\n'+'Date='+str(datetime.now())
    bar_chart.x_labels = ('Words < 10','Words < 30','Words < 50','Words < 100','More than 100s')
    bar_chart.add('Received', [a,b,c,d,e])
    bar_chart.add('Sent',[a1,b1,c1,d1,e1])
    
    word_chart = bar_chart.render(is_unicode = True)

    bar_chart.render_to_file(os.path.join(app.config['daily_wordcount'],'daily_'+EMAIL+'_.svg'))


    return render_template('daily_word.html',word_chart = word_chart)

   

@app.route('/weekly-wordcount')

def word_count_weekly_data():
	 
    a,b,c,d,e = word_count_weekly_inbox()
    
    a1,b1,c1,d1,e1 = word_count_weekly_outbox()
    
    bar_chart = pygal.Bar()
    bar_chart.title = 'Word Count Analysis'+ '\n'+'Date Range = From '+ \
    str(datetime.now() - timedelta(6)) + ' '+'to'+ ' ' + str(datetime.now())
    bar_chart.x_labels = ('Words < 10','Words < 30','Words < 50','Words < 100','More than 100s')
    bar_chart.add('Received', [a,b,c,d,e])
    bar_chart.add('Sent',[a1,b1,c1,d1,e1])
    
    word_chart = bar_chart.render(is_unicode = True)
    bar_chart.render_to_file(os.path.join(app.config['weekly_wordcount'],'weekly_'+EMAIL+'_.svg'))


    return render_template('weekly_word.html',word_chart = word_chart)

@app.route('/month_inbox')

def month_inbox():
    activity_inbox  = monthly_activity_inbox()
    
	
    stackedline_chart = pygal.StackedLine(fill=True)
    
    stackedline_chart.title = 'Monthly Email Analysis'+ '\n'+'Date Range = From '+ \
    str(datetime.now() - timedelta(30)) + ' '+'to'+ ' ' + str(datetime.now())

    stackedline_chart.x_labels = ('1','2','3','4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', 
    '16' ,'17', '18' ,'19', '20' ,'21', '22', '23' ,'24', '25', '26', '27', '28', '29', '30')

    stackedline_chart.add('Received', activity_inbox)
     
    chart = stackedline_chart.render(is_unicode=True)
    stackedline_chart.render_to_file(os.path.join(app.config['monthly-activity-inbox'],'monthly_'+EMAIL+'_.svg'))

    return render_template('monthly_inbox.html', chart = chart)


@app.route('/month_outbox')

def month_outbox():
    activity_outbox  = monthly_activity_outbox()
    
	
    stackedline_chart = pygal.StackedLine(fill=True)
    
    stackedline_chart.title = 'Monthly Email Analysis'+ '\n'+'Date Range = From '+ \
    str(datetime.now() - timedelta(30)) + ' '+'to'+ ' ' + str(datetime.now())

    stackedline_chart.x_labels = ('1','2','3','4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', 
    '16' ,'17', '18' ,'19', '20' ,'21', '22', '23' ,'24', '25', '26', '27', '28', '29', '30')

    stackedline_chart.add('Sent', activity_outbox)
    stackedline_chart.render_to_file(os.path.join(app.config['monthly-activity-outbox'],'monthly_'+EMAIL+'_.svg'))

    chart = stackedline_chart.render(is_unicode=True)
    
    return render_template('monthly_outbox.html', chart = chart)



def inbox_data():
	
    "Daily analysis"

    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=1
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select("[Gmail]/All Mail")

    interval = (date.today()-timedelta(d)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None,'(SENTSINCE {date})'.format(date=interval))

    xday = []
    Start_Day = (00,00,00)
    Start_Day_List = []

    Mid_Morning = (06,00,00)
    Mid_Morning_List = [] 

    Mid_Day = (12,00,00)
    Mid_Day_List = []

    End_Day = (18,00,00)
    End_Day_List = []

    Dead_End = (24,00,00)
    Dead_End_List = []
    
    for num in data[0].split():

        result, data = mail.uid('fetch',num,'(BODY.PEEK[])')    
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                for header in ['to']:
                    if (EMAIL in str(msg[header])):                 
                        
                        result, data = mail.uid('fetch',num,'(BODY.PEEK[])') 
                        msg = email.message_from_string(data[0][1]) 

                        try:
							
                            main_tuple = email.utils.parsedate_tz(msg['Date'])        
                        # we need to convert main tuple into time tuple
                        
                            Date_Tuple = main_tuple[0],main_tuple[1],main_tuple[2]
                            Time_Tuple = main_tuple[3],main_tuple[4],main_tuple[5]    
                        
                        except:
							pass
							
							
                        Today = datetime.today().timetuple()
                        Today_tuple = Today[0],Today[1],Today[2]
    
                        if Date_Tuple==Today_tuple:
                            xday.append(Date_Tuple)
                       
                        if Time_Tuple>Start_Day:
                            if Time_Tuple<Mid_Morning:
                                Start_Day_List.append(Time_Tuple)
                       
                        if Time_Tuple>Mid_Morning:
                            if Time_Tuple<Mid_Day:
                                Mid_Morning_List.append(Time_Tuple)
                       
                        if Time_Tuple>Mid_Day:
                            if Time_Tuple<End_Day:
                                Mid_Day_List.append(Time_Tuple)
                 
                            if Time_Tuple>End_Day:
                                if Time_Tuple<Dead_End:
           
                                    End_Day_List.append(Time_Tuple)
                 
                 
    Start_day = len(Start_Day_List)
    Mid_morning = len(Mid_Morning_List)
    Mid_day = len(Mid_Day_List)  
    End_day = len(End_Day_List)  
    
    return Start_day,Mid_morning,Mid_day,End_day,msg['Date']

def outbox_data():
    "Daily analysis"

    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=1
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select( '[Gmail]/Sent Mail')
    interval = (date.today()-timedelta(d)).strftime("%d-%b-%Y")
    result, data = mail.uid('search', None,'(SENTSINCE {date})'.format(date=interval))

    xday = []
    Start_Day = (00,00,00)
    Start_Day_List = []

    Mid_Morning = (06,00,00)
    Mid_Morning_List = [] 

    Mid_Day = (12,00,00)
    Mid_Day_List = []

    End_Day = (18,00,00)
    End_Day_List = []

    Dead_End = (24,00,00)
    Dead_End_List = []
    
    for num in data[0].split():

        result, data = mail.uid('fetch',num,'(BODY.PEEK[])')
        msg = email.message_from_string(data[0][1])
    
        try:  
            main_tuple = email.utils.parsedate_tz(msg['Date'])        
            
            
                        # we can use this message msg['Date'] and put it in Graph or date Tuple.
                        
                        
            Date_Tuple = main_tuple[0],main_tuple[1],main_tuple[2]
            Time_Tuple = main_tuple[3],main_tuple[4],main_tuple[5]
        except:
			
			pass 
    
        Today = datetime.today().timetuple()
        Today_tuple = Today[0],Today[1],Today[2]
    
        if Date_Tuple==Today_tuple:
            xday.append(Date_Tuple)
        
        
            if Time_Tuple>Start_Day:
                if Time_Tuple<Mid_Morning:
                
                
                    Start_Day_List.append(Time_Tuple)
                
            if Time_Tuple>Mid_Morning:
                if Time_Tuple<Mid_Day:
                
                
                    Mid_Morning_List.append(Time_Tuple)
         
         
            if Time_Tuple>Mid_Day:
                if Time_Tuple<End_Day:
                
                     Mid_Day_List.append(Time_Tuple)
                 
            if Time_Tuple>End_Day:
                if Time_Tuple<Dead_End:
           
                    End_Day_List.append(Time_Tuple)
                 
                 
    Start_day = len(Start_Day_List)
    Mid_morning = len(Mid_Morning_List)
    Mid_day = len(Mid_Day_List)  
    End_day = len(End_Day_List)  
    
    return Start_day,Mid_morning,Mid_day,End_day




def inbox_week():
    "Weekly analysis inbox"
    try:
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
        d=6
        user = EMAIL
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.debug = 4
        mail.authenticate('XOAUTH2', lambda x: auth_string)
        mail.select("[Gmail]/All Mail")
    
    # if I will select [Gmail]/All-mail then how to find Inbox messages in imaplib
    
        interval = (date.today()-timedelta(d)).strftime("%d-%b-%Y")
    
    
        result, data = mail.uid('search', None,'(SENTSINCE {date})'.format(date=interval))
        
        for num in data[0].split():
            result, data = mail.uid('fetch', num, '(BODY.PEEK[])')
    
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_string(response_part[1])
                    for header in ['to']:
                        if (EMAIL in str(msg[header]) or 'danielr@eyecarepro.net' in str(msg[header])):
                            main_tuple = email.utils.parsedate_tz(msg['Date'])                                   
                            yield main_tuple
    except:
		pass

def outbox_week():
    try:
        auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
        d=6
        user = EMAIL
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.debug = 4
        mail.authenticate('XOAUTH2', lambda x: auth_string)
    
        mail.select('[Gmail]/Sent Mail')


        interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
        result, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=interval))
 # retrieving the headers
        for num in data[0].split():
			
            result, data = mail.uid('fetch', num,'(BODY.PEEK[])')
        
            for response_part in data:
                if isinstance(response_part, tuple):
   
                    msg = email.message_from_string(response_part[1])
                    main_tuple = email.utils.parsedate_tz(msg['Date'])
                    yield main_tuple
    except:
		pass 

 
def word_count_daily_inbox():
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=1
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('INBOX')
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, uid = mail.uid('search', None, \
                          '(SENTSINCE {date})'.format(date=interval))

    x = uid[0].split()

    first = []
    second = []
    third = []
    fourth = []
    fifth = []
    word_counts = []
    final_list = []



    for i in x:    
            
        result, data = mail.uid('fetch', i, '(BODY.PEEK[])')
    
    
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
    
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)

                head,sep,tail = body.partition('--')
            
                word_count_length = len(head.split())
            
     
                if (word_count_length<=10):
                    first.append(word_count_length)
               

                elif(word_count_length<=30):
                    second.append(word_count_length)
       
           
                elif(word_count_length<=50):

                    third.append(word_count_length)
        
                elif(word_count_length<=100):

                    fourth.append(word_count_length)
               
            
                else:
                    fifth.append(word_count_length)   

# we can use msg['Date'] function here

    return len(first),len(second),len(third),len(fourth),len(fifth)




def word_count_daily_outbox():

    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=1
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('[Gmail]/Sent Mail')
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, uid = mail.uid('search', None, \
                          '(SENTSINCE {date})'.format(date=interval))

    x = uid[0].split()

    first = []
    second = []
    third = []
    fourth = []
    fifth = []
    word_counts = []
    final_list = []



    for i in x:    
            
        result, data = mail.uid('fetch', i, '(BODY.PEEK[])')
    
    
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
    
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)

                head,sep,tail = body.partition('--')
            
                word_count_length = len(head.split())
            
     
                if (word_count_length<=10):
                    first.append(word_count_length)
               

                elif(word_count_length<=30):
                    second.append(word_count_length)
       
           
                elif(word_count_length<=50):

                    third.append(word_count_length)
        
                elif(word_count_length<=100):

                    fourth.append(word_count_length)
               
            
                else:
                    fifth.append(word_count_length)   


    return len(first),len(second),len(third),len(fourth),len(fifth)



def word_count_weekly_inbox():

    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('INBOX')
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, uid = mail.uid('search', None, \
                          '(SENTSINCE {date})'.format(date=interval))

    x = uid[0].split()

    first = []
    second = []
    third = []
    fourth = []
    fifth = []
    word_counts = []
    final_list = []



    for i in x:    
            
        result, data = mail.uid('fetch', i,'(BODY.PEEK[])')
    
    
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
    
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)

                head,sep,tail = body.partition('--')
            
                word_count_length = len(head.split())
            
     
                if (word_count_length<=10):
                    first.append(word_count_length)
               

                elif(word_count_length<=30):
                    second.append(word_count_length)
       
           
                elif(word_count_length<=50):

                    third.append(word_count_length)
        
                elif(word_count_length<=100):

                    fourth.append(word_count_length)
               
            
                else:
                    fifth.append(word_count_length)   


    return len(first),len(second),len(third),len(fourth),len(fifth)






def word_count_weekly_outbox():

    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('[Gmail]/Sent Mail')
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, uid = mail.uid('search', None, \
                          '(SENTSINCE {date})'.format(date=interval))

    x = uid[0].split()

    first = []
    second = []
    third = []
    fourth = []
    fifth = []
    word_counts = []
    final_list = []



    for i in x:    
            
        result, data = mail.uid('fetch', i, '(BODY.PEEK[])')
    
    
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
    
        for part in email_message.walk():
            if part.get_content_type() == "text/plain": # ignore attachments/html
                body = part.get_payload(decode=True)

                head,sep,tail = body.partition('--')
            
                word_count_length = len(head.split())
            
     
                if (word_count_length<=10):
                    first.append(word_count_length)
               

                elif(word_count_length<=30):
                    second.append(word_count_length)
       
           
                elif(word_count_length<=50):

                    third.append(word_count_length)
        
                elif(word_count_length<=100):

                    fourth.append(word_count_length)
               
            
                else:
                    fifth.append(word_count_length)   


    return len(first),len(second),len(third),len(fourth),len(fifth)








def monthly_activity_inbox():
	    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=30
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select("[Gmail]/All Mail")

    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")

    result, uid = mail.uid('search', None, \
     '(SENTSINCE {date})'.format(date=interval))


    x = uid[0].split()

    all_dates_list = []
    for i in x:

        result, data = mail.uid('fetch', i, '(BODY.PEEK[])')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1])
                for header in ['to']:
					
                    if (EMAIL in str(msg[header]) or '@eyecarepro.net' in str(msg[header])):
		                
                        try:
							
                            result, data = mail.uid('fetch', i, '(BODY.PEEK[])')
        				
                            msg = email.message_from_string(data[0][1])                      
                            date_tuple = email.utils.parsedate_tz(msg['Date'])
                            all_dates_list.append(date_tuple[2])
                            dates_dict = dict(Counter(all_dates_list))
                        except:
							pass
    final_list = dates_dict.values()                                              
         
    return final_list



def monthly_activity_outbox():
	    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d=30
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('[Gmail]/Sent Mail')

    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")

    result, uid = mail.uid('search', None, \
     '(SENTSINCE {date})'.format(date=interval))


    x = uid[0].split()

    all_dates_list = []
    
    for i in x:
        try:
            result, data = mail.uid('fetch', i, '(BODY[HEADER.FIELDS (DATE)])')
            msg = email.message_from_string(data[0][1])                      
            date_tuple = email.utils.parsedate_tz(msg['Date'])
            all_dates_list.append(date_tuple[2])
            dates_dict = dict(Counter(all_dates_list))
        except:
			pass
    final_list = dates_dict.values()                                              
    
         
    return final_list




@app.route('/login/authorized')

def authorized():

# authorized response nu dekhna jaroori hai.. ? mil tan gea authorized response
    resp = google.authorized_response()


    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )


    session['google_token'] = (resp['access_token'],'')
    
    p = session['google_token']
    
    me = google.get('userinfo')
    
#    q = jsonify({"data":p})
   
    global ACCESS_TOKEN 
    ACCESS_TOKEN = p[0]
    global EMAIL
    EMAIL = str(me.data['email'])
    name = str(me.data['name'])
#u'name': u'Great Avenger Singh', u'picture': u'
#u'email': u'arsh840@gmail.com'    
   # return str(me.data['email'])
    return render_template("done.html",name=name) 
   
   # return type(p)
    
   
   # return jsonify({"data": me.data})

 #   return type(resp   )

         
@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/admin')
@auth.login_required

#def index():
 #   return "Hello, %s!" % auth.username()


@app.route('/files/<path:path>')

def hello(path=''):
    path_join = os.path.join(app.config['FILES_ROOT'], path)

#if path_join is folder
 
    if os.path.isdir(path_join):
        folder = Folder(app.config['FILES_ROOT'], path)
        folder.read()
        return render_template('folder.html', folder=folder)
    else:
    # if path join is  a file
    
        my_file = File(app.config['FILES_ROOT'], path)
        
        context = my_file.apply_action(View)
        folder = Folder(app.config['FILES_ROOT'], my_file.get_path())
        if context == None:

            folder = my_file.path
            return send_file(folder)
#                return render_template('file_unreadable.html', folder=folder)
        
        # text = context['text'] file da text return karda hai.
        #eh text e pure svg hai
       
       
        return render_template('file_view.html', text=context['text'], \
        file=my_file, folder=folder)
       

@app.route('/search', methods=['POST'])
def search():
    q = request.form['q']
    return render_template('search.html', request = q)








def daily_inbox_data_piechart():

    inbox = 'INBOX'
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 0
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    mail.select(inbox)
       
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, inbox_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))
    
    
    return len(inbox_uids[0].split())

def daily_outbox_data_piechart():
    
    
    outbox = '[Gmail]/Sent Mail'
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 0
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    
    mail.select(outbox)
    
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, outbox_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    return len(outbox_uids[0].split())
    
def daily_important_data_piechart():
    
   
    important = '[Gmail]/Important'
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 0
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

   
   
    mail.select(important)
    
   
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, important_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    
    return len(important_uids[0].split())

def daily_archieved_data_piechart():
   
    archieved =  '[Gmail]/All Mail'
   
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 0
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

   
   
    
    mail.select(archieved)
    
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, archieved_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    return len(archieved_uids[0].split())
    
def daily_trashed_data_piechart():

   
    trashed = '[Gmail]/Trash'
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 0
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    
    mail.select(trashed)
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, trashed_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    return len(trashed_uids[0].split())







def weekly_inbox_data_piechart():

    inbox = 'INBOX'
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    mail.select(inbox)
       
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, inbox_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))
    
    
    return len(inbox_uids[0].split())



def weekly_outbox_data_piechart():
    
    
    outbox = '[Gmail]/Sent Mail'
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    
    mail.select(outbox)
    
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, outbox_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    return len(outbox_uids[0].split())
    
def weekly_important_data_piechart():
    
   
    important = '[Gmail]/Important'
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

   
   
    mail.select(important)
    
   
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, important_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    
    return len(important_uids[0].split())

def weekly_archieved_data_piechart():
   
    archieved =  '[Gmail]/All Mail'
   
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

   
   
    
    mail.select(archieved)
    
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, archieved_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    return len(archieved_uids[0].split())
    
def weekly_trashed_data_piechart():

   
    trashed = '[Gmail]/Trash'
    
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (EMAIL,ACCESS_TOKEN)
    d = 6
    user = EMAIL
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.debug = 4
    mail.authenticate('XOAUTH2', lambda x: auth_string)

    
    mail.select(trashed)
   
    interval = (date.today() - timedelta(d)).strftime("%d-%b-%Y")
    result, trashed_uids = mail.uid('search', None, 
                      '(SENTSINCE {date})'.format(date=interval))

    
    return len(trashed_uids[0].split())







if __name__ == '__main__':

    app.run()
    ADMINS = ['arsh840@gmail.com']
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@example.com',
                               ADMINS, 'YourApplication Failed')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


#    ctx = google.test_request_context('/waheguru',method='POST')
 #   ctx.push()
  #  p = google.get_google_oauth_token()
   # print p
#    app.run()
