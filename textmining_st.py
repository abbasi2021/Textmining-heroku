import json 
import urllib3
import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import requests
import lxml
import string
import xmltodict,json
import xml.etree.ElementTree as ET
import urllib.request
from hazm import *
import numpy as np
from Levenshtein import * 
from fuzzywuzzy import fuzz
import re
import base64
import pyodbc
#import MySQLdb
import sqlite3
import mysql.connector
from mysql.connector import errorcode
import time
#from persian_tools.bank import card_number
import base64
from io import BytesIO
import streamlit_authenticator as stauth

st.set_page_config(page_title="textmining",layout="wide",) 



try:
    # Fix UTF8 output issues on Windows console.
    # Does nothing if package is not installed
    from win_unicode_console import enable
    enable()
except ImportError:
    pass


st.markdown('<div style="font-size: 250%;font-family:  B Nazanin ;text_align:center;direction: center; width:100% ; height:100px;border: 10px solid #2c7da0;margin-left: auto;margin-right: auto">سامانه متن کاوی</div> ', unsafe_allow_html=True)
st.write("""
""")
st.markdown('<div style="direction: center; width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
#st.sidebar.write("")

names = ['zahra abbasi','hossein khandani','mahdi ghasemi','mohamad hadi moghadasin']
usernames = ['z.abbasi','h.khandani','ma.ghasemi','m.moghadasin']
passwords = ['1234','1234','1234','1234']
hashed_passwords = stauth.hasher(passwords).generate()
authenticator = stauth.authenticate(names,usernames,hashed_passwords,'some_cookie_name','some_signature_key',cookie_expiry_days=1)
name, authentication_status = authenticator.login('Login','main')



#افقی کردن radio
#cn.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)






############download link
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


#@st.cache
def download_link_csv(df,download_filename):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False,encoding="utf-8")
    b64 = base64.b64encode(csv.encode("utf-8")).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a style=color:#f77f00 href="data:file/csv;base64,{b64}"  download="{download_filename}">Download  file</a>'   
    return href


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

#@st.cache
def download_link_excel(df,download_filename):
    val = to_excel(df)
    b64 = base64.b64encode(val) 
    href= f'<a style=color:#f77f00 href="data:application/octet-stream;base64,{b64.decode()}" download="{download_filename}">Download excel file</a>' # decode b'abc' => abc
    return href
 




######database
    
#@st.cache
def connection_db(sql_server=False,my_sql=False,sqllit=False,server=None,database=None,table=None,username=None,password=None,Q=None):
    if my_sql:
        try:
            cnx= mysql.connector.connect(
                host=str(server),
                     user=str(username),            
                     passwd=str(password),  
                     db=str(database))     
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        cursor = cnx.cursor()
        if Q:
            data=pd.read_sql(Q,cnx)
        else:
            query='select * from {}'.format(table)
            data=pd.read_sql(query,cnx)
        return data
    
    elif sql_server:
        cnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s'%(server,database,username,password))
        cursor = cnx.cursor()
        if Q:
            data=pd.read_sql(Q,cnx)
        else:
            query='select * from {}'.format(table)
            data=pd.read_sql(query,cnx)
        return data
    
    
    elif sqllit:
        cnx= sqlite3.connect(str(database)+".db")
        cursor= cnx.cursor()
        if Q:
            data=pd.read_sql(Q,cnx)
        else:
            query='select * from {}'.format(table)
            data=pd.read_sql(query,cnx)
        return data



#####html

#st.sidebar.text_input('query-threshold-column-new_col')     
class html_json:
    def read_html(self,html_file):
        data = pd.read_html(html_file)
        #st.write("تعداد جدول ها :   ",len(data))
       # st.markdown('<div style="font-size: 120%;font-family:  B Nazanin ;text_align:left;background-color: white;width:100% ; height:50px;">تعداد جدول ها : %d </div> '%len(data), unsafe_allow_html=True)
        try:
            if len(data)>=1:
                table_num=st.sidebar.number_input('عدد جدول مورد نظر را وارد کنید',min_value=0, max_value=len(data),step=1)

                return data[table_num]
        except IndexError:
            st.write("عدد وارد شده بزرگ تر از تعداد جداول است")

            #print('The number entered is greater than the number of tables')
            
    def read_text(self,file):
        #file_path = file
        #with open(file_path, 'r') as f:
            #st.write(len(data),"تعداد جدول ها :   ")
        data= pd.read_html(file.read())
        try:
            if len(data)>=1:
                table_num=st.sidebar.number_input('عدد جدول مورد نظر را وارد کنید',min_value=0, max_value=len(data),step=1)
                return data[table_num]
        except IndexError:
            st.write("عدد وارد شده بزرگ تر از تعداد جداول است")

    def read_url(self,url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        response = requests.get(url, headers=headers)
        data= pd.read_html(response.content)
        try:
            if len(data)>=1:
                table_num=st.sidebar.number_input('عدد جدول مورد نظر را وارد کنید',min_value=0, max_value=len(data),step=1)
                return data[table_num]
        except IndexError:
            st.write("عدد وارد شده بزرگ تر از تعداد جداول است")
    
  
    
    def create_table(self,url=None,string=None,html_file=None,n=1,t=[]):
        if url:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
        elif string:
            #with open(string) as string:
            soup = BeautifulSoup(string, 'html.parser')
        elif html_file:
            soup = BeautifulSoup(html_file, 'html.parser')
        
           # with open(html_file) as fp:
            
        
        #n=int(input("enter number of tags  : "))
        #l=[]
        if n>0:
         #   for i in range(n):
                #t=input('enter tag name : ')
          #      l.append(t[i])
            data=pd.DataFrame()
            for j in range(len(l)):
                d=[]
                for child in soup.find_all(l[j]):
                    d.append(child.string) 
                data[l[j]]=d
            return data
        else:
            return(" ")
        
    def read_json(self,json_file):
       # with open(json_file, "r") as f:
        data=json.load(json_file)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
            #max_l=(int(input("Please enter the maximum data extraction depth number : ")))
        data=pd.json_normalize(data,max_level=max_l)
        return data
    
    def read_json_text(self,text_file):
        #with open(text_file, "r") as f:
        data=(text_file.read())
        data=json.loads(data)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
        data=pd.json_normalize(data,max_level=max_l)
        return data
    def read_json_url(self,url=""):
        response = requests.get(url)
        data = json.loads(response.content)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
        data=pd.json_normalize(data)
        return data
    
 ####xml
    def read_xml(self,xmlfile):
        #with open(xmlfile, 'r') as myfile:
        obj = xmltodict.parse(xmlfile.read())
        data=json.dumps(obj)
        data=json.loads(data)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
        data=pd.json_normalize(data,max_level=max_l)
        return data
    
    def read_xml_text(self,text_file):
        #with open(text_file, 'r') as myfile:
        obj = xmltodict.parse(text_file.read())                               
        data=json.dumps(obj)
        data=json.loads(data)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
        data=pd.json_normalize(data,max_level=max_l)
        return data
        
    def read_xml_url(self,url=''):
   
        xml_url= urllib.request.urlopen(url)
        obj = xmltodict.parse(xml_url.read())
        data=json.dumps(obj)
        data=json.loads(data)
        max_l=st.sidebar.number_input('لطفاً حداکثر عدد عمق استخراج داده را وارد کنید',min_value=0,step=1)
        data=pd.json_normalize(data,max_level=max_l)
        return data

    def parse_xml(self,xml_file):
        a=st.sidebar.number_input('لطفاً عدد زیر شاخه مورد نظر خود را از بین 1 تا 5 انتخاب کنید',min_value=1,max_value=5,step=1)
        #xml_d=open(xml_file,'r').read()
        root=ET.XML(xml_file.read())
        data=[]
        cols=[]
        for child in root:
            if a==1:
                data.append([subchild.text for subchild in child])
                cols.append(child.tag)
                continue
            for ch in child:
                if a==2:
                    data.append([subchild.text for subchild in ch])
                    cols.append(ch.tag)
                    continue
                for ch in child:
                    if a==3:
                        data.append([subchild.text for subchild in ch])
                        cols.append(ch.tag)
                        continue
                    for ch in child:
                        if a==4:
                            data.append([subchild.text for subchild in ch])
                            cols.append(ch.tag)
                            continue
                        for ch in child:
                            if a==5:
                                data.append([subchild.text for subchild in ch])
                                cols.append(ch.tag)
                                continue
                            
        data=pd.DataFrame(data).T
        data.columns=cols
        return data
    
H=html_json()


def preproccessing(data,prep_fields=[],prep_nfields=[],preproccess=[]):
    
    def normalizing(text):
        normalizer = Normalizer()
        text=normalizer.normalize(str(text))
        return text
    def tokenizing(text):
        text=[w for w in word_tokenize(str(text))]
        return text
    def remove_stopwords(text):
        with open(r'C:\Users\z.abbasi\Downloads\stopwords.txt',newline='\n',encoding='utf-8') as file:
            stopwords=file.read().splitlines()

        text=[w for w in text if not w in stopwords]
        return text
    
    def lemmatizing(text):
        lemmatizer=Lemmatizer()
        text=[lemmatizer.lemmatize(word) for word in text]
        return text
    
    def remove_punctuation(text):
        words=[w for w in text if not w in string.punctuation]
        return words  

    def STemmer(text):
        stemmer = Stemmer()
        text=[stemmer.stem(word) for word in text]     
        return text
    

    for i in range(len(prep_fields)):
        
        def preprocessor(T):
            if T==np.nan:
                text=T.replace(np.nan,'')
            else:
                text=T
            text=text
                
            if 'normalizing' in preproccess[i]:
                text=normalizing(text)
            if 'tokenizing' in preproccess[i]:
                text=tokenizing(text)
            if 'remove_stopwords' in preproccess[i]:
                if 'tokenizing' not in preproccess[i]:
                    text=tokenizing(text)
                else:
                    pass
                text=remove_stopwords(text)
            if 'lemmatizing' in preproccess[i]: 
                if 'tokenizing' not in preproccess[i]:
                    text=tokenizing(text)
                else:
                    pass
                text=lemmatizing(text)
            if 'stemming' in preproccess[i]: 
                if 'tokenizing' not in preproccess[i]:
                    text=tokenizing(text)
                else:
                    pass
                text=STemmer(text)
                
            if 'remove_punctuation' in preproccess[i]:
                text=remove_punctuation(text)
           
            text=str(text)
           
            text=text.strip('[').strip(']').replace("'",'')
            #text=' '.join([str(elem) for elem in text])
            return text
    
        
        
        
        
        
    
        if prep_nfields[i]!="":
            data[prep_nfields[i]] = data[prep_fields[i]].apply(preprocessor)
              
          #  data[prep_nfields] = [','.join(map(str, l)) for l in data[prep_nfields]]
        elif prep_nfields[i]=="":
            data[prep_fields[i]] = data[prep_fields[i]].apply(preprocessor)
        
       # data[prep_fields] = [','.join(map(str, l)) for l in data[prep_fields]]
        
    return data                
  


def proccessing(data,col='',n_col='',proccess='',p='',kw='',nmx=0,nmn=0,count=0,cl=False,ibcode=False,poscode=False,mobilecode=False,nationcode=False,cardcode=False,samen_code=False,vehiclecode=False,sh_date=False,m_date=False,numcount=False,num=False,user_patern=False,user_patern_kw_cl=False,user_patern_kw_noncl=False):
    c=count
        
#   def find_input(df,p,col,n_col,regex_type,kw='',nmx=0,nmn=0,cl=False):
    def user_pat_apply(x):  
        text=''
        for n in re.findall(r'%s'%p,str(x)):
            text+=n+" , "
        return text

    def user_pattern_kw_clean(x):
        pat=re.findall(r"%s"%p,str(x))   

        l=[re.findall(r'[%s].{%s,%s}?(%s)'%(kw,nmn,nmx,i),str(x))  for i in pat]
        l=str(l).strip('[').strip(']')
        
        
        return l
    
    def user_pattern_kw_nonclean(x):
        pat=re.findall(r"%s"%p,str(x))
        l=[re.findall(r'\b[%s].{%s,%s}?(%s)\b'%(kw,nmn,nmx,i),str(x))  for i in pat]
        l=str(l).strip('[').strip(']')
        return l

    def convert_string(x):
        try: 
            return str(x)
        except:
            return ""
        
    def validate_iban(Iban):
        if len(str(Iban))>26:
            IBAN=re.sub(r'[-\.\s]','',str(Iban))
            int_iban=IBAN[4:]+'18'+'27'+IBAN[2]+IBAN[3]
            int_iban=int(int_iban)
            if int_iban % 97 ==1:
                return 1
        else:
            int_iban=Iban[4:]+'18'+'27'+Iban[2]+Iban[3]
            int_iban=int(int_iban)
            if int_iban % 97 ==1:
                return 2
        
        return '' #Iban=str(Iban).replace(" ","")
    
    def validate_postal_code(S):
        P=S[:5]
        if '1' in P:
            return S
        return ''
    
    
    def iban(x):
        x=convert_string(x)
        ibans=''
        for iban in  re.findall(r'IR\d{2}[-\.\s]{0,1}0[1|2|5|6|9][0-9][01]{1}[-\.\s]{0,1}(?:\d{4}[-\.\s]{0,1}){4}\d{2}',x,re.MULTILINE):
            if validate_iban(iban)==2:
                ibans+=(iban+',')
            if validate_iban(iban)==1:
                iban=re.sub(r'[-\.\s]','',iban)
                ibans+=(iban+',')
                
        return ibans 
    
    
    def postal_code(x):
        s=''
        for pos in  re.findall(r'\b[13-9]{5}\d{5}\b',str(x),re.MULTILINE):
            if validate_postal_code(pos):
               s+=(pos+",")
        return s
        
    def mobile(x):
        s=''
        matches=re.finditer(r"(0|\+98|98|0098)?([ ]|-|[()]){0,2}9[0-49]([ ]|-|[()]){0,2}(?:[0-9]([ ]|-|[()]){0,2}){8}",str(x),re.MULTILINE)
        for m in matches:
            s+=m.group()+" , "
        return s
        
    def vehicle_plate(x):
        s=''
        for v in re.findall(r'\u06F0-\u06F9{2}[\u0621-\u0628\u062A-\u063A\u0641-\u0642\u0644-\u0648\u064E-\u0651\u0655\u067E\u0686\u0698\u06A9\u06AF\u06BE\u06CC]\u06F0-\u06F9{3}\u0627\u06CC\u0631\u0627\u0646\u06F0-\u06F9{2}',str(x),re.MULTILINE):
            s+=v+' , '
        return s
    
    def validate_nationcode(n):
        check = int(n[-1])
        B = sum([int(n[y]) * (len(n) - y) for y in range(len(n)-1)]) % 11
        if (B < 2 and  check== B) or (B >= 2 and check + B == 11):
            return n
        return None
        
    
    def nation_code(x):
        
        s=''
        x = re.sub(r'پست.*\d{10}', '', str(x),re.MULTILINE)
        for nc in re.findall(r'\b\d{8,10}\b', str(x),re.MULTILINE):
            if validate_nationcode(nc):
                s+=nc+" , "
        return s
    
    def vlidate_card_number(x):
        if len(str(x))>16:
            x=re.sub(r'[^\d]', '',x)
            if len(str(x))==16:
                
                odd_n=list(map(int,x[0::2]))
                odd_num=[]
                for i in odd_n:
                    if (i*2)<9:
                        m=i*2
                    else:
                        m=(i*2)-9
                    odd_num.append(m)
                even_num=list(map(int,x[1::2]))
                S=sum(even_num)+sum(odd_num)
                if S%10==0:
                    return str(x)
        elif len(str(x))==16:
            odd_n=list(map(int,x[0::2]))
            odd_num=[]
            for i in odd_n:
                if (i*2)<9:
                    m=i*2
                else:
                    m=(i*2)-9
                odd_num.append(m)
            even_num=list(map(int,x[1::2]))
            S=sum(even_num)+sum(odd_num)
            if S%10==0:
                return str(x)
            
            
                
                
        return None
    
    def card_number(card):
        cards=''
        matches=re.findall(r'\d{4}[\s\-\.]{0,1}?\d{4}[\s\-\.]?\d{4}[\s\-\.]?\d{4}',str(card),re.MULTILINE)
       # st.write(matches)
        #st.write(type(matches))
        for co in matches:
            if vlidate_card_number(co): 
                #st.write(co)
                cards+=co+","
            
        return cards
    
    def number_count(x):
        num=''
        for n in re.findall(r'\b\d{%s}\b'%c,str(x),re.MULTILINE):
            num+=n+" , "
        return num
            
    def number(x):
        num=''
        for n in re.findall(r'\d+',str(x),re.MULTILINE):
            num+=n+" , "
        return num
    
    def jalali_date(x):
        dates=''
        regex=r'(1){0,1}[34]{0,1}?[0-9]{2}(-|\/|\.)[01]{0,1}\d{1}(-|\/|\.)[0-3]{0,1}\d{1}'
        matches = re.finditer(regex, str(x), re.MULTILINE)
        for match in matches:
            dates+=match.group()+" , "
            
        return dates
    
    def miladi_date(x):
        dates=''
        regex=r'\d{1,2}(-|\/)\d{1,2}(-|\/)[12]{01}[09]{01}\d{2}'
        matches = re.finditer(regex, str(x), re.MULTILINE)
        for match in matches:
            dates+=match.group()+" , "
            
        return dates
    
    def samen(x):
        S=''
        x=re.sub(r'(ثامن|کدثامن|کد ثامن|کد پیگیری ثامن|کد رهگیری ثامن|کدپیگیری ثامن|کدرهگیری ثامن)[:\s]{0,1}\s{0,1}','~',str(x),re.MULTILINE)
        for s in re.findall(r'(?<=\~)[09][( )\-Oo()\.]{0,1}(?:[0-9][( )\-Oo()\.]{0,2}){6,8}',str(x),re.MULTILINE):
            S+=s+" , "
            
        return S
                
 
    
    if proccess=='استخراج از طریق الگو':
    
        if user_patern:
            try:
                data[n_col] = data[col].apply(user_pat_apply)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(user_pat_apply)
        if user_patern_kw_cl:
            try:
                data[n_col] = data[col].apply(user_pattern_kw_clean)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(user_pattern_kw_clean)
       
        if user_patern_kw_noncl:
            try:
                data[n_col] = data[col].apply(user_pattern_kw_nonclean)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(user_pattern_kw_nonclean)
        
        
        if ibcode:
            try:
                data[n_col] = data[col].apply(iban)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(iban)
        
        if poscode:
            try:
                data[n_col] = data[col].apply(postal_code)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(postal_code)
            
        if mobilecode:
            try:
                data[n_col] = data[col].apply(mobile)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(mobile)
             
        if vehiclecode:
            try:
                data[n_col] = data[col].apply(vehicle_plate)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(vehicle_plate)
                
        if nationcode:
            try:
                data[n_col] = data[col].apply(nation_code)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(nation_code)
         
        if cardcode:
            try:
                data[n_col] = data[col].apply(card_number)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(card_number)
        
        if numcount:
            try:
                data[n_col] = data[col].apply(number_count)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(number_count)
        
        
        if num:
            try:
                data[n_col] = data[col].apply(number)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(number)
                
                
        if sh_date:
            try:
                data[n_col] = data[col].apply(jalali_date)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(jalali_date)
                
        if m_date:
            try:
                data[n_col] = data[col].apply(miladi_date)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(miladi_date)
                
        if samen_code:
            try:
                data[n_col] = data[col].apply(samen)
            except AttributeError:
                data[col].replace( np.nan,'',inplace=True)
                data[n_col] = data[col].apply(samen)
                
                
                
        
    else:
        pass
    return data                    



def proccessing2(data,col1=None,col2=None,new_col=None,sim_type=""):
    data[col1] = D3[col1].apply(str) 
    data[col2] = D3[col2].apply(str) 
    data[new_col]=0
    if sim_type=="f_ratio" :
        data[new_col]=data.apply(lambda x : fuzz.ratio(x[col1], x[col2]),axis=1)
    elif sim_type=="f_partial_ratio" :
        data[new_col]=data.apply(lambda x : fuzz.partial_ratio(x[col1], x[col2]),axis=1)
    elif sim_type=="f_token_sort_ratio" :
        data[new_col]=data.apply(lambda x : fuzz.token_sort_ratio(x[col1], x[col2]),axis=1)
    
    elif sim_type=="f_token_set_ratio" :
        data[new_col]=data.apply(lambda x : fuzz.token_set_ratio(x[col1], x[col2]),axis=1)
  
    return data    

def explode_split(df,new_col):
    cols=list(df.columns)
    cols.remove(new_col)
    F=df.set_index(cols).apply(lambda x: x.str.split(',').explode()).reset_index() 
    return F

if authentication_status:
    st.write('Welcome *%s*' % (name))
    
    st.markdown('<div style="direction: rtl;font-size: 150%;direction: rtl;font-family: B Nazanin;">نوع داده را تعیین کنید   </div> ', unsafe_allow_html=True)

    D_Type=st.selectbox(" ",["CSV,TEXT","EXCEL","HTML","XML","JSON","SQL SERVER","MY SQL","SQLite"])
    st.markdown('<div style="direction: center; width:100% ; height:40px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)

    #if D_Type=="TEXT":
     #   st.markdown('<div style="color:#E8FFFF;direction: rtl;font-size: 200%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
      #  f_address=st.text_input("")
       # data=pd.read_csv(r'%s'%f_address)
        #data
        
     #   with open(File,encoding='utf-8') as F:
      #      data=F.read().replace('\n',' ')
      
    
    
    if D_Type=="CSV,TEXT":
       # st.markdown('<div style="color:#black;direction: rtl;font-size: 200%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
        file=st.sidebar.file_uploader('choose your file',type=['csv'])
       
        st.sidebar.subheader("   پارامتر ها   : " )
        delimiters={"comma":",","space":" ","tab":"\t","colon":":","semicolon":";"}
        delimiter=["comma","space","tab","colon","semicolon","سایر موارد"]
        Sep=st.sidebar.radio("separator",delimiter)
        if Sep=="سایر موارد":
            Sep_inp=st.sidebar.text_input("را وارد کنید separator")
        else:
            Sep_inp=delimiters[Sep]
            
        
        st.sidebar.markdown('<div style="direction: rtl;font-size: 200%;direction: rtl"></div> ', unsafe_allow_html=True)
        #UNC=st.sidebar.checkbox("encoding")
        #if UNC:
        encode=st.sidebar.text_input("enter encode")
        if encode:
            encoding=encode
        else:
            encoding=None
            
            
                
        Head= st.sidebar.checkbox("تغییر نام ستون‌ها و تعیین اولین سطر ")
        if Head:
            header=st.sidebar.radio("",["skiprows","header_names"])
            if header=="skiprows":
                number = st.sidebar.number_input('شماره سطر عنوان را وارد کنید',min_value=0, max_value=10,step=1)
                st.sidebar.warning("چنانچه عدد وارد شده غیر صفر باشد سطرهای پیش از عنوان خوانده نمیشوند")
    
                try:
                    data=pd.read_csv(file,sep=Sep_inp,skiprows=number,header=0,encoding=encoding)
                except pd.errors.ParserError:
                    data=pd.read_csv(file,sep=Sep_inp,error_bad_lines=False,encoding=encoding)
                    print('bad lines skipped')
            if header=="header_names":
                headers=st.sidebar.text_input("h1,h2,...عنوان ستون ها را وارد کنید     ")
                headers =headers.split(",")
                number = st.sidebar.number_input('شماره اولین سطر را وارد کنید',min_value=0, max_value=10,step=1)
    
                try:
                    data=pd.read_csv(file,sep=Sep_inp,header=None,names=headers,skiprows=number,encoding=encoding)
                except pd.errors.ParserError:
                    data=pd.read_csv(file,sep=Sep_inp,error_bad_lines=False,encoding=encoding)
                    print('bad lines skipped')
                    
        else:
            try:
                data=pd.read_csv(file,sep=Sep_inp,skiprows=0,encoding=encoding)
            except pd.errors.ParserError:
                data=pd.read_csv(file,sep=Sep_inp,error_bad_lines=False,encoding=encoding)
                print('bad lines skipped')
       # data
                
    
      
        #col1,col2=st.columns(2)
           
    
    elif D_Type=="EXCEL":
       # st.markdown('<div style="direction: rtl;font-size: 200%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
        file=st.sidebar.file_uploader('choose your file',type=['xlsx'])
        st.sidebar.subheader("   پارامتر ها   : " )
        #sh_n=st.sidebar.checkbox("sheet name")
        
        sheet=st.sidebar.radio("sheet name",["sheet_number","sheet_name"])
        if sheet=="sheet_name":
            sheet_name=st.sidebar.text_input("sheet_name",key="sh_name")
        if sheet=="sheet_number":
            sheet_name=st.sidebar.number_input("sheet_number",min_value=0,step=1,key="sh_num")
            #st.sidebar.write(type(sheet_name))
        sheet_name=sheet_name
        st.sidebar.write(" ")
        st.sidebar.write(" ")
        
        Head= st.sidebar.checkbox("تغییر نام ستون‌ها و تعیین اولین سطر")
        if Head:
            header=st.sidebar.radio("",["skiprows","headers_skiprows"])
            if header=="skiprows":
                number = st.sidebar.number_input('شماره سطر عنوان را وارد کنید',min_value=0,step=1)
                st.sidebar.warning("چنانچه عدد وارد شده غیر صفر باشد سطرهای پیش از عنوان خوانده نمیشوند")
                data=pd.read_excel(file,skiprows=number,header=0,sheet_name=sheet_name)
            if header=="headers_skiprows":
                headers=st.sidebar.text_input("h1,h2,...عنوان ستون ها را وارد کنید     ")
                headers =headers.split(",")
                number = st.sidebar.number_input('شماره اولین سطر را وارد کنید',min_value=0,step=1)   
                data=pd.read_excel(file,names=headers,skiprows=number,sheet_name=sheet_name)
        else:
            data=pd.read_excel(file,sheet_name=sheet_name)
            
       # st.dataframe(data)
    elif D_Type=="HTML":
        st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">  نحوه ی استخراج دیتا را انتخاب کنید </div> ', unsafe_allow_html=True)
        st.sidebar.write(" ")
        tag=st.sidebar.radio('',(" table استخراج دیتا بر اساس تگ ","استخراج دیتا بر اساس سایر تگ ها"))
        if tag=="استخراج دیتا بر اساس سایر تگ ها":
            st.sidebar.write(" ")
            st.sidebar.write(" ")
            st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5"> نوع فایل را انتخاب کنید </div> ', unsafe_allow_html=True)
            st.sidebar.write(" ")
            typ=st.sidebar.radio('',('html','txt','url'))
            if typ=='html':
                #st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
                #f_address=st.text_input("")
                f_address=st.sidebar.file_uploader('choose your file',type=['html'])
                number = st.sidebar.number_input('تعداد تگ را وارد کنید',min_value=0, max_value=20,step=1)
                l=[]
                if number>0:
                    
                    for i in range(number):
                        t1=st.text_input('نام تگ %d را وارد کنید'%(i+1),key=i)   
                        l.append(t1)
                
                data=H.create_table(html_file=f_address,n=number,t=l)
            elif typ=="txt":
                #st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
                #f_address=st.text_input("")
                f_address=st.sidebar.file_uploader('choose your file',type=['txt'])
                number = st.sidebar.number_input('تعداد تگ را وارد کنید',min_value=0, max_value=20,step=1)
                l=[]
                if number>0:
                    
                    for i in range(number):
                        t1=st.text_input('نام تگ %d را وارد کنید'%(i+1),key=i)   
                        l.append(t1)
                
                data=H.create_table(string=f_address,n=number,t=l)
                
            else:
                st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">  آدرس وبسایت را وارد کنید </div> ', unsafe_allow_html=True)
    
                f_address=st.text_input("")
                number = st.sidebar.number_input('تعداد تگ را وارد کنید',min_value=0, max_value=20,step=1)
                l=[]
                if number>0:
                    
                    for i in range(number):
                        t1=st.text_input('نام تگ %d را وارد کنید'%(i+1),key=i)   
                        l.append(t1)
                
                data=H.create_table(url=f_address,n=number,t=l)
                
                
        else:
            st.sidebar.write(" ")
            st.sidebar.write(" ")
            st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5"> نوع فایل را انتخاب کنید </div> ', unsafe_allow_html=True)
            st.sidebar.write(" ")
            typ=st.sidebar.radio('',('html','text','url'))
            if typ=='html':
                #st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
                #f_address=st.text_input("")
                f_address=st.sidebar.file_uploader('choose your file',type=['html'])
                data=H.read_html(html_file=f_address)
                
                #st.dataframe(data.data.head(5))
                
            elif typ=='text':
                #st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
                #f_address=st.text_input("")
                f_address=st.sidebar.file_uploader('choose your file',type=['txt'])
                data=H.read_text(file=f_address)
                
            else:
                st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;">آدرس وبسایت را وارد کنید    </div> ', unsafe_allow_html=True)
                f_address=st.text_input("")
                data=H.read_url(url=f_address)
                
        #data
    elif D_Type=="JSON":
       # file=st.sidebar.file_uploader('choose your file',type=['json,txt'])
        st.sidebar.markdown('<div style="color: black;background-color:#CDD4E0;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5"> نوع فایل را انتخاب کنید </div> ', unsafe_allow_html=True)
        #st.sidebar.write(" ")
        st.sidebar.write(" ")
        typ=st.sidebar.radio('',('json','text','url'))
        
        if typ=='json':
           # st.markdown('<div style="color:#000000;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #e8c2ca">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
            #f_address=st.text_input("")
            file=st.sidebar.file_uploader('choose your file',type=['json'])
            data=H.read_json(json_file=file)
        #data
        if typ=='text':
            #st.markdown('<div style="color:#000000;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #e8c2ca">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
           # f_address=st.text_input("")
            file=st.sidebar.file_uploader('choose your file',type=['txt'])
            data=H.read_json_text(text_file=file)
        #data
        if typ=='url':
            st.markdown('<div style="color: black;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #e8c2ca"> آدرس وبسایت را وارد کنید </div> ', unsafe_allow_html=True)
            f_address=st.text_input("")
            data=H.read_json_url(url=f_address)    
       # data
    elif D_Type=="XML":
        st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5"> نوع فایل را انتخاب کنید </div> ', unsafe_allow_html=True)
        st.sidebar.write(" ")
        typ=st.sidebar.radio('',('xml','text','url'))
        
        if typ=='xml':
            #st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #e8c2ca">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
            #f_address=st.text_input("")
            st.sidebar.write(" ")
            st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5">نحوه ی خواندن فایل را تعیین کنید </div> ', unsafe_allow_html=True)
            st.sidebar.write(" ")
            howto=st.sidebar.radio('',("xml_normalized","parse_xml"))
            if howto=="xml_normalized":
                file=st.sidebar.file_uploader('choose your file',type=['xml'])
                data=H.read_xml(xmlfile=file)  
            elif howto=="parse_xml":
                file=st.sidebar.file_uploader('choose your file',type=['xml'])
                data=H.parse_xml(xml_file=file)
                
            
        if typ=='text':
           # st.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 0px solid #e8c2ca">آدرس فایل را وارد کنید    </div> ', unsafe_allow_html=True)
            #f_address=st.text_input("")
            #st.sidebar.write(" ")
            st.sidebar.markdown('<div style="direction: rtl;font-size: 130%;direction: rtl;font-family: B Nazanin;border: 2px solid #6385C5">نحوه ی خواندن فایل را تعیین کنید </div> ', unsafe_allow_html=True)
            st.sidebar.write(" ")
            howto=st.sidebar.radio('',("xml_normalized","parse_xml"))
            if howto=="xml_normalized":
                file=st.sidebar.file_uploader('choose your file',type=['txt'])
                data=H.read_xml_text(text_file=file)
            elif howto=="parse_xml":
                file=st.sidebar.file_uploader('choose your file',type=['txt'])
                data=H.parse_xml(xml_file=file)
        
        if typ=='url':
            st.markdown('<div style="color:#black;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">آدرس وبسایت را وارد کنید</div> ', unsafe_allow_html=True)
            f_address=st.text_input("")
            st.sidebar.write(" ")
            st.sidebar.markdown('<div style="color:#black;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">نحوه ی خواندن فایل را تعیین کنید </div> ', unsafe_allow_html=True)
            st.sidebar.write(" ")
            howto=st.sidebar.radio('',("xml_normalized","parse_xml"))
            if howto=="xml_normalized":
                data=H.read_xml_url(url=f_address)
            elif howto=="parse_xml":
                data=H.parse_xml(xml_file=f_address)
       # data        
    elif D_Type=="SQL SERVER" :
        st.write("")
        st.sidebar.markdown('<div style="background-color:#CDD4E0;color:#black;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">مشخصات پایگاه داده را وارد کنید </div> ', unsafe_allow_html=True)    
        co_1, co_2= st.columns(2)
        #with co_1:
        database=st.sidebar.text_input("database",key=4)
        server=st.sidebar.text_input("server",key=5)
        username=st.sidebar.text_input("username",key=1)
        password=st.sidebar.text_input("password",key=2,type='password')
        table=st.sidebar.text_input("table",key=3)
        #with co_2:
        
        
        
        
        with st.expander("QUERY"):
            st.write("در صورت وارد نکردن کوئری بصورت کامل به جدول متصل میشوید  ")
            query=st.text_input("query",key="q")
            
        if query:
            data=connection_db(sql_server=True,server=server,database=database,table=table,username=username,password=password,Q=query)
        else:   
            data=connection_db(sql_server=True,server=server,database=database,table=table,username=username,password=password)
        
       # data
         
    elif D_Type=="MY SQL" :
        st.write("")
        st.sidebar.markdown('<div style="background-color:#CDD4E0;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">مشخصات پایگاه داده را وارد کنید </div> ', unsafe_allow_html=True)    
        co_1, co_2= st.columns(2)
        #with co_1:
        database=st.sidebar.text_input("database",key=4)
        host=st.sidebar.text_input("server",key=5)
        username=st.sidebar.text_input("username",key=1)
        password=st.sidebar.text_input("password",key=2,type='password')
        table=st.sidebar.text_input("table",key=3)
        #with co_2:
            
        with st.expander("QUERY"):
            st.write("در صورت وارد نکردن کوئری بصورت کامل به جدول متصل میشود  ")
            query=st.text_input("query",key="q")
            
        if query:
            data=connection_db(my_sql=True,server=host,database=database,table=table,username=username,password=password,Q=query)
        else:   
            data=connection_db(my_sql=True,server=host,database=database,table=table,username=username,password=password)
        
     #   data
        
        
    elif D_Type=="SQLite" :
        st.write("")
        st.sidebar.markdown('<div style="background-color:#CDD4E0;color:#black;direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">مشخصات پایگاه داده را وارد کنید </div> ', unsafe_allow_html=True)    
        co_1, co_2= st.columns(2)
        #with co_1:
        database=st.sidebar.text_input("database",key=4)
        #with co_2:
        table=st.sidebar.text_input("table",key=3)
        with st.expander("QUERY"):
            st.write("در صورت وارد نکردن کوئری بصورت کامل به جدول متصل میشود  ")
            query=st.text_input("query",key="q")
            
        if query:
            data=connection_db(sqllit=True,database=database,table=table,Q=query)
        else:   
            data=connection_db(sqllit=True,database=database,table=table)
        
       # data   
    data_head=data.head(10)    
    st.dataframe(data_head)        
     
    st.write("") 
    st.write("")
        
    
    csv = convert_df(data)
    #col1,col2= st.columns(2)
    
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='Data.csv',
        mime='text/csv',  
        key='Down1'
    )
    
     
    st.write("")
    
        #st.markdown(download_link_csv(D,"data.csv"), unsafe_allow_html=True)            
    with st.expander("Other Link"):    
        st.markdown(download_link_excel(data,"data.xlsx"), unsafe_allow_html=True)
       
            
        
    
    st.markdown('<div style="direction: center; width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    #st.markdown('<div style="font-size: 250%;font-family:  B Nazanin ;text_align:center;direction: center; width:100% ; height:100px;border: 10px solid #2c7da0;margin-left: auto;margin-right: auto">سامانه متن کاوی</div> ', unsafe_allow_html=True)


        
        
    st.markdown('<div style="font-size: 250%;font-family:  B Nazanin ;text_align:center;direction: center;width:100% ; height:100px;border: 10px solid #2c7da0;margin-left: auto;margin-right: auto">پیش پردازش داده ها</div> ', unsafe_allow_html=True)   
    st.markdown('<div style="direction: center;width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    
    
    st.write('')
    st.sidebar.write('')
    st.sidebar.write('')
    
    col_name=list(data.columns)
    cn=st.container()
    
    st.markdown('<div style="direction: rtl;font-size: 150%;direction: rtl;font-family: B Nazanin; border: 0px solid #6385C5"> ستون های مورد نظر جهت پیش پردازش داده ها را انتخاب کنید </div> ', unsafe_allow_html=True)
    
    fields=st.multiselect("columns_name",col_name)
    
    fields_len=len(fields)
    preprocess=[]
    nfields=[]
    if fields_len!=0:
        for i in range(fields_len):
            col1=st.container()
            with col1:
                st.subheader(' %s :'%fields[i])
                st.markdown('<div style="direction: rtl;font-size: 160%;direction: rtl;font-family: B Nazanin;"> نام ستون جدید را وارد کنید</div> ', unsafe_allow_html=True)    
                new_fields=st.text_input('',key='prep_nfields%i'%i)
                with st.expander("warning"):
                    st.warning("چنانچه ستون جدیدی تعیین نگردد پردازش بر روی ستون انتخاب شده اولیه اعمال میشود")
                st.markdown('<div style="direction: center;width:100% ; height:30px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    
                nfields.append(new_fields)
                st.markdown('<div style="direction: rtl;font-size: 160%;direction: rtl;font-family: B Nazanin;"> گزینه های مورد نظر جهت پیش پردازش داده ها را انتخاب کنید </div> ', unsafe_allow_html=True)
    
                p=st.multiselect('پیش پردازش',['normalizing','tokenizing','lemmatizing','stemming','remove_stopwords','remove punctuations'],key="%i"%i)
                preprocess.append(p)
                #st.markdown('<div style="direction: center ;width:100% ; height:0px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    
                
               
                            
    #st.write(preprocess)
    
    
    
    #st.markdown('<div style="direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;"> نام فیلد مورد نظر جهت پیش پردازش را وارد کنید</div> ', unsafe_allow_html=True)    
    #fields=st.text_input('   ') 
    #
    #nfields=st.text_input('   ',key='prep_nfields')
    
              
     
    st.markdown('<div style="direction: center ;width:100% ; height:30px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    D=preproccessing(data,fields,nfields,preprocess)
    
    new_data=pd.DataFrame(D)
    data_head_pre=D.head(10)    
    st.dataframe(data_head_pre)  
    
    
    
    #3####################################################################################3
    
     
    st.write("") 
    st.write("")
        
    
    csv = convert_df(D)
    #col1,col2= st.columns(2)
    
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='Data.csv',
        mime='text/csv',  
        key='Down2'
    )
    
     
    st.write("")
    
        #st.markdown(download_link_csv(D,"data.csv"), unsafe_allow_html=True)            
    with st.expander("Other Link"):    
        st.markdown(download_link_excel(D,"data.xlsx"), unsafe_allow_html=True)
       
            
       
    
    
    
    
    
    #st.write(D.columns)
    #st.write(type(D.loc[0][prep_nfields]))           ##############
    st.markdown('<div style="direction: center ;width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    #st.markdown('<div style="font-size: 250%;font-family:  B Nazanin ;text_align:center;direction: center; width:80% ; height:100px;border: 10px solid #2c7da0;margin-left: auto;margin-right: auto">پیش پردازش داده ها</div> ', unsafe_allow_html=True)   
    
    st.markdown('<div style="font-size: 250%;font-family:  B Nazanin ;text_align:center;direction: center; width:100% ; height:100px;border: 10px solid #2c7da0;margin-left: auto;margin-right: auto"> پردازش داده ها</div> ', unsafe_allow_html=True)   
    st.markdown('<div style="direction: center;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)
    
    
    
    proccess=['استخراج داده','شباهت‌سنجی']
    process= st.container()
    col1= st.container()
    
    
    
    with process:
        st.write("")
        st.write("")
        st.write("")
    
        st.markdown('<div style="direction: rtl;float:right;width:100% ; height=50px;font-size: 150%;direction: rtl;font-family: B Nazanin;border: 0px solid #6385C5"> گزینه مناسب جهت پردازش داده را انتخاب کنید</div> ', unsafe_allow_html=True)
        st.write("")
        #st.write("گزینه مناسب جهت پردازش داده را انتخاب کنید")
        pattern=st.radio("",proccess)
        #st.write(type(pattern))
    
    
    
    
    
    st.markdown('<div style="direction: center;width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
    
    button1=['شماره شبا','شماره موبایل',"کد ملی",'کد پستی',"شماره عابر بانک","شماره پلاک خودرو"," عدد","رقم n عدد با"]
    b=["","تاریخ شمسی","تاریخ میلادی","شماره شبا","کدملی","عدد با nرقم","کد پستی","شماره پلاک خودرو","شماره موبایل","عدد","شماره عابر بانک","کد ثامن"]
    
    #P=st.selectbox('select',button1)
    col_name=list(new_data.columns)
    
    
    
    if pattern=='استخراج داده':
        
        
        st.markdown('<div style="direction: rtl;font-size: 150%;direction: rtl;font-family: B Nazanin;"> ستون های مورد نظر جهت  پردازش داده ها را انتخاب کنید</div> ', unsafe_allow_html=True)    
        fields=st.multiselect("columns_name",col_name,key="p_field")
        fields_len=(len(fields))
        nfields=[]
        #T_pat=[]
        #proccess=[]
        if fields_len!=0:
            for i in range(fields_len):
                col1=st.container()
                with col1:
                    st.subheader(' %s :'%fields[i])
                
                    st.markdown('<div style="direction: rtl;font-size: 140%;direction: rtl;font-family: B Nazanin;"> نام ستون جدید را وارد کنید</div> ', unsafe_allow_html=True)    
                    new_fields=st.text_input('   ',key='n_col %i'%i)    
                    
                    nfields.append(new_fields)
                    #st.markdown('<div style="direction: center;background-color:#1E3C5A ;width:100% ; height:70px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
            
                    pat_selection=st.radio("",["استفاده از الگوهای موجود","وارد کردن الگو","وارد کردن الگو به همراه کلیدواژه"],key="pat%i"%i)
    #def proccessing(data,col=[],n_col=[],proccess=[],pat=[],ibcode=False,poscode=False,mobilecode=False,nationcode=False,cardcode=False,vehiclecode=False,numcount=False,num=False,user_patern=False,count=0):
            
        
                    if pat_selection=="وارد کردن الگو":
                        T=st.text_input("الگو را وارد کنید",key='Tpat %i'%i)
                       
                        
                        st.markdown('<div style="direction: center;width:100% ; height:50px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
                
                        D=proccessing(new_data,proccess='استخراج از طریق الگو',p=T,user_patern=True,col=fields[i],n_col=new_fields)
                    
                    elif pat_selection=="وارد کردن الگو به همراه کلیدواژه":
                        T=st.text_input("الگو را وارد کنید",key='Tpat %i'%i)
                        st.markdown('<div style="direction: center;background-color:#F0F4F0 ;width:100% ; height:50px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
    
                        att=st.warning("در صورت استفاده از چندین کلید‌‌واژه آن‌ها را در باکس زیر وارد کنید و و بین آن‌ها از علامت( , )استفاده کنید")
                        kw=st.text_input("کلیدواژه را وارد کنید",key='Tpatk %i'%i)
                        num_min=st.number_input("حداقل تعداد کاراکترهای بین کلیدواژه و الگو",min_value=0 ,max_value=30,step=1,key='npat %i'%i)
                        num_max=st.number_input("حداکثر تعداد کاراکترهای بین کلیدواژه و الگو",min_value=1 ,max_value=50,step=1,key='2pat %i'%i)
        
                        clean=st.checkbox('داده‌ها پالایش شده می‌باشند',key='clean %i'%i)
                        if clean==False:
                            
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',kw=kw,nmx=num_max,nmn=num_min,p=T,cl=False,user_patern_kw_noncl=True,col=fields[i],n_col=new_fields)
                        elif clean==True:
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',kw=kw,nmx=num_max,nmn=num_min,p=T,cl=True,user_patern_kw_cl=True,col=fields[i],n_col=new_fields)
                        
                        st.markdown('<div style="direction: center ;width:100% ; height:50px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
                        
                    
                    
                    
                    elif  pat_selection=="استفاده از الگوهای موجود":
                          
                        
                        st.markdown('<div style="direction: rtl;font-size: 140%;direction: rtl;font-family: B Nazanin;">    گزینه مناسب را انتخاب کنید</div> ', unsafe_allow_html=True)    
                    
                        
                        P=st.selectbox('',b,key='P%i'%i)
                        st.markdown('<div style="direction: center; ;width:100% ; height:90px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)                    
                
                        if P=="":
                            pass
                        
                        if P=='تاریخ شمسی':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',sh_date=True,col=fields[i],n_col=new_fields)
                            
                        if P=='تاریخ میلادی':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',m_date=True,col=fields[i],n_col=new_fields)
                        
                        
                        
                        if P=='شماره شبا':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',ibcode=True,col=fields[i],n_col=new_fields)
                            
                        if P=='کدملی':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',nationcode=True,col=fields[i],n_col=new_fields)
                            
                            
                        if P=='کد پستی':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',poscode=True,col=fields[i],n_col=new_fields)
                            
                         
                        if P=='شماره پلاک خودرو':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',vehiclecode=True,col=fields[i],n_col=new_fields)
                            
                        
                        if P=='شماره موبایل':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',mobilecode=True,col=fields[i],n_col=new_fields)
                            
                        
                        if P=='شماره عابر بانک':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',cardcode=True,col=fields[i],n_col=new_fields)
                            
                        
                        if P=='عدد':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',num=True,col=fields[i],n_col=new_fields)
                            
                        if P=='کد ثامن':
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',samen_code=True,col=fields[i],n_col=new_fields)
                            
                        
                        if P=='عدد با nرقم' :
                            digit=st.number_input("تعداد ارقام را تعیین کنید",1,16,key="num%i"%i)
                        
                            D=proccessing(new_data,proccess='استخراج از طریق الگو',numcount=True,col=fields[i],n_col=new_fields,count=str(digit))
                            
        #explode_data=new_fields
        
        st.markdown('<div style="direction: center; width:100% ; height:50px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)

        if st.checkbox('تفکیک مقادیر استخراج شده در سطر های متمایز',key='explode') :
            st.markdown('<div style="direction: center; width:100% ; height:30px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)

            explode_data=st.multiselect("ستون های مورد نظر را انتخاب کنید",D.columns,key="explode")
            #st.write(type(explode_data))
            for i in explode_data:
                
                D=explode_split(D,new_col=i)
            
                    
            
        
        st.markdown('<div style="direction: center; width:100% ; height:40px;margin-left: auto;margin-right: auto"></div> ', unsafe_allow_html=True)

        #st.dataframe(D)                
        data_head_pre=D.head(10)    
        st.dataframe(data_head_pre)
        st.write("row number",len(D))                 
        
           
        
            
        
    if pattern=="شباهت‌سنجی":
        st.markdown('<div style="direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">  فیلد اول  را انتخاب کنید</div> ', unsafe_allow_html=True)    
        fields1=st.selectbox('   ',col_name,key='col1') 
        st.markdown('<div style="direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">  فیلد دوم  را انتخاب کنید</div> ', unsafe_allow_html=True)    
        fields2=st.selectbox('   ',col_name,key='col2') 
        st.markdown('<div style="direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;"> نام فیلد جدید را وارد کنید</div> ', unsafe_allow_html=True)    
        nfields=st.text_input('   ',key='n_col')    
        S_type=[" ","f_ratio","f_partial_ratio","f_token_sort_ratio","f_token_set_ratio"]
        st.markdown('<div style="direction: rtl;font-size: 120%;direction: rtl;font-family: B Nazanin;">    گزینه مناسب را انتخاب کنید</div> ', unsafe_allow_html=True)    
    
        S=st.selectbox('',S_type)
        
        if S==" ":
            pass
        else:
            D=proccessing2(new_data,col1=fields1,col2=fields2,new_col=nfields,sim_type=S)
            st.write("")
            st.write("")
    
            data_head_pre=D.head(10)    
            st.dataframe(data_head_pre)
     
    st.write("") 
    st.write("")
        
    
    csv = convert_df(D)
    #col1,col2= st.columns(2)
    
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='Data.csv',
        mime='text/csv',  
        key='Down3'
    )
    
     
    st.write("")
    
        #st.markdown(download_link_csv(D,"data.csv"), unsafe_allow_html=True)            
    with st.expander("Other Link"):    
        st.markdown(download_link_excel(D,"data.xlsx"), unsafe_allow_html=True)
       
 
        
            
     
        
        
        
        
        
    #co1, co2= st.columns(2)
    #with co1:    
    #with co2:
        
    
    
        
    
    
    st.write(""" 
             
    
    
    
    
    """)
    
   
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
    
        
        
        
