#import MACD as macd
#import matplotlib.pyplot as plt
import MACD as macd
from Trade_Module import Trades
from cassandra.cluster import Cluster
import datetime as dt
from datetime import datetime
import csv
import sys
import ast
"""
                     ---Trade Using MACD signal ---
1. Definations
 1.1 Execution
 1.2 Market
 1.3 pl
 1.4 draw
                        ---Flow of Code---
2.1 Highest Run Number is feched from the Trades Table from the defined keyspace
2.2 Run Number is incremented by 1 to identify unique code runs
2.3 Give dates between which you want to run the code
2.4 After all the configeration and input is given MAcalculation function from the MACD Class is called
2.5 It returns the calculated values like ma1,ma2,ema etc for each candle of defined size
2.6 This Info is then passed on to the Market function to generate trades
2.7 As soon as the function detects trade signal it passes the trade info to execution function which handles execution of trade as well uploading the trade
    information into cassandra

2.8 LOGIC : MARKET Function 

	2.8.1 : As the initial values of MACD and SIgnal are null, we start Trade generation only after we have those values
	2.8.2 : if current MACD is greater than current signal value and previous MACD is less than previous SIGNAL then Buy is generated
	2.8.2 : Visa Versa for the SELL signal generation
	 
"""
s_t=datetime.now();

#------------------------------Trade Execution----------------------------------------
def execution(date,time,product,size,price,side,order_type,ratio,new_day_indicator):   
    Trade_generated=Trades(date,time,product,size,price,side,order_type,ratio,keyspace_name,session)
    time2=''
    
    if Trade_generated[0]!='Not Found':
        if new_day_indicator>1:  
            previous_trade_time=str(trades[-1][1])[:8]
            current_trade_time=str(time)[:8]

            #Last Trade which happens at or after 18:00:00 HRS
            if datetime.strptime(current_trade_time,"%H:%M:%S")>=datetime.strptime('18:00:00',"%H:%M:%S"):
                session.execute(upload_query,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],date,trades[-1][1],'MACD',order_type))                
                trades.extend(Trade_generated)
                return None
            
            #Upload trade to cassandra only if previous Trade's execution time is before current trade
            if datetime.strptime(current_trade_time,"%H:%M:%S")>=datetime.strptime(previous_trade_time,"%H:%M:%S"):
                session.execute(upload_query,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],date,trades[-1][1],'MACD',order_type))
                trades.extend(Trade_generated)
                return None
            else:
                return 9
        else:
            trades.extend(Trade_generated)
    else:
        print "Not Found"     
        return 9
#-----------------------------------------Trade Generation-----------------------
def market(MACD_data_objects,order_type,size,price,ratio):
    previous_macd=0.0
    previous_signal=0.0
    position=0
    size2=size+1
    new_day_indicator=0
    indicator=0

    for current_item in MACD_data_objects:
        
        if current_item.sp!=0 and current_item.esp!=0:
            time1=str(current_item.period.time_end)[:8]
            
            if datetime.strptime(time1,"%H:%M:%S")<datetime.strptime('18:00:00',"%H:%M:%S"):

                #Generation Of BUY orders
                if current_item.macd1>=current_item.sp and previous_macd<previous_signal :
        
                    if position==0:
                        new_day_indicator+=1
                        indicator=execution(current_item.period.date1,current_item.period.time_end,product,size,price,'buy',order_type,ratio,new_day_indicator)
                        if indicator==9:
                            position=0
                        else:
                            position=1
                            
                    elif position==-1:
                        new_day_indicator+=1
                        indicator=execution(current_item.period.date1,current_item.period.time_end,product,size2,price,'buy',order_type,ratio,new_day_indicator)
                        if indicator==9:
                            position=-1
                        else:
                            position=1

                #Generation Of SELL orders   
                elif previous_macd>previous_signal and current_item.macd1<=current_item.sp :                    
                    if position==1:
                        new_day_indicator+=1
                        indicator=execution(current_item.period.date1,current_item.period.time_end,product,size2,price,'sell',order_type,ratio,new_day_indicator)
                        if indicator==9:
                            position=1
                        else:
                            position=-1
                            
                    elif position==0:
                        new_day_indicator+=1
                        indicator=execution(current_item.period.date1,current_item.period.time_end,product,size,price,'sell',order_type,ratio,new_day_indicator)
                        if indicator==9:
                            position=0
                        else:
                            position=-1
                    
            # After 18:00:00 HRS Trade Execution    
            else:
                if position==1:
                    new_day_indicator+=1
                    execution(current_item.period.date1,current_item.period.time_end,product,1,price,'sell','Market',ratio,new_day_indicator)
                    
                if position==-1:
                    new_day_indicator+=1
                    execution(current_item.period.date1,current_item.period.time_end,product,1,price,'buy','Market',ratio,new_day_indicator)
                if position==0:
                    session.execute(upload_query,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],trades[-1][4],trades[-1][1],'MACD','Market'))
                    #print run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],trades[-1][4],trades[-1][1],'MACD','Market'
                position=0
                new_day_indicator=0
                
                pass
            
            previous_macd=current_item.macd1
            previous_signal=current_item.sp
            #Uncomment For Graph generation !!
            """
            time_reference.append(str(current_item.period.time_end))
            macd_values_for_graph.append(current_item.macd1)
            signal_values_for_graph.append(current_item.sp)
    	    """
            
def pl(trades):
    # Does not work Properly !!!!!
    prev=0.0
    sum1=[]
    for current_item in range(len(trades)-1):
        position=trades[current_item+1][3]-trades[current_item][3]+prev
        if trades[current_item][0]=='buy':
            sum1.append((trades[current_item+1][2]-trades[current_item][2])*1000*(position))  
        else:
            sum1.append((trades[current_item][2]-trades[current_item+1][2])*1000*(position))
        prev=position
    print sum1,sum(sum1)
    
def draw():
    plt.plot(time_reference,macd_values_for_graph,color='red',label='MACD')
    plt.plot(time_reference,signal_values_for_graph,color='yellow',label='signal')
    
    
    #plt.plot(time_reference,exponential_macd,color='blue',label='EMACD')
    #plt.plot(time_reference,exponential_signal,color='black',label='Esignal')

    plt.xlabel('')
    plt.ylabel('SIGNAL & MACD')
    plt.legend()
    plt.gcf().autofmt_xdate()

    plt.show()
    
#----------------------------------------------CODE starts HERE--------------------------------------------
#keyspace_name='try1'
name_of_file=sys.argv[1]
config_data_main={}
config_data={}

myfile=open(name_of_file)

for line in myfile:
    name,var=line.partition('@')[::2]
    config_data_main[name.strip()]=str(var)[:-1]
    
temp=(config_data_main['Trade_main_config'])
config_data=ast.literal_eval(temp)
print config_data    
keyspace_name=config_data['keyspace_name']
date_start=config_data['start_date']
date_end=config_data['end_date']
product=config_data['xric']
candle_type=config_data['candle_type']

candle_size=int(config_data['candle_size'])
slow_time_period=int(config_data['slow_time_period'])
fast_time_period=int(config_data['fast_time_period'])
signal_time_period=int(config_data['signal_time_period'])

ip_address=[]
ip_address.append(config_data['ip_address'])


cluster = Cluster(ip_address)
session = cluster.connect(keyspace_name)

query_for_trade_upload="insert into trades(run_no,product,side,price,size,date1,time1,strategy,type) values (?,?,?,?,?,?,?,?,?)"
query_for_run_no="select max(run_no) from trades allow filtering"

upload_query = session.prepare(query_for_trade_upload)
prepared2 = session.prepare(query_for_run_no)

run_no=session.execute(prepared2)
run_no=0 if run_no[0][0]==None else run_no[0][0]
run_no=int(run_no)+1

#date_start='2018-02-01'
#date_end='2018-03-01'

#------------------------------------------- Configerations-----------------------------------------------

# [candle size(minute/volume),size for 1st SMA/EMA,size for 2nd SMA/EMA,size for Signal candle calculation]
Config=[candle_size,slow_time_period,fast_time_period,signal_time_period]

MACD_Class_Object=macd.MACD()
MACD_Values=MACD_Class_Object.MAcalculation(Config,candle_type,date_start,date_end,product,keyspace_name,session)

#------------------------------------------Initializations----------------------------
macd_values_for_graph=[]
signal_values_for_graph=[]
time_reference=[]

exponential_macd=[]
exponential_signal=[]
previous_macd=0.0
previous_signal=0.0

buy=[]
sell=[]
trades=[]

#price=0.0
#product='FGBLH8'

#----------------------------------------Inputs---------------------------------------
user_input=raw_input("Market or Limit Order?\n")
lots=int(raw_input("How many Lots??\n"))
ratio=float(raw_input("Input the Ratio\n"))
price=float(raw_input("Price..[0.0 for auto price function]\n"))

market(MACD_Values,user_input,lots,price,ratio)

print trades
#session.execute(upload_query,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],date_end,trades[-1][1],'MACD',user_input))

#pl(trades)
#draw()
print (datetime.now()-s_t)   
