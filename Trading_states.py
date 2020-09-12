import State as st
import csv
import sys
from cassandra.cluster import Cluster
import datetime as dt
from datetime import datetime
from Trade_Module import Trades
#import matplotlib.pyplot as plt
import ast

s_t=datetime.now();
"""
                  ---Trading using State Indicator---
1. Definations
 1.1 execution
 1.2 state_trade
                        ---Flow of Code---
2.1 Highest Run Number is feched from the Trades Table from the defined keyspace
2.2 Run Number is incremented by 1 to identify unique code runs
2.3 Give dates between which you want to run the code
2.4 After all the configeration and input is given State_main function from the State Class is called
2.5 It returns the calculated States as well as the Open,High,Low,Close values for each candle of defined size
2.6 This Info is then passed on to the state_trade function to generate trades
2.7 As soon as the function detects trade signal it passes the trade info to execution function which handles execution of trade as well uploading the trade
    information into cassandra

2.8 LOGIC : state_trade Generation

    2.8.1 : State changes to 5 while previous state was not 5 then BUY Signal is generated
    2.8.2 : If the state has changed from 5 i.e previous state was 5 and current state is something else then SELL
    2.8.3 : If the state changes to 1 while previous state was not 1 then SELL
    2.8.4 : if the previous state was 1 and now it has change to something else then BUY

2.9 LOGIC : Execution
    
    2.9.1 : 1st Trade of the day is inserted into the trades List without any condition checking
    2.9.2 : Now, the Current trade Time is checked if It's Time of Execution is before than that of the previous Trade then
            the previous Trade is accepted
    2.9.3 : Similar checking is done for every trade till its 18:00:00 and then the last trade is Accepted as it is 
    2.9.4 : 9 is returned in the case when 1. Trade is NOT FILLED 2. when last trades's execution time is greater than that of the current Trade 

"""
def execution(date,time,product,size,price,side,order_type,ratio,day_start_indicator):
    generated_trade=Trades(date,time,product,size,price,side,order_type,ratio,keyspace_name,session)
    time2=''
    
    if generated_trade[0]!='Not Found':
        if day_start_indicator>1:
            #Format the previous trade time so as to compare it with current order time
            last_trade_time=str(trades[-1][1])[:8]
            curr_time=str(time)[:8]
            
            #if order is of after closing time then it is accepted here
            if datetime.strptime(curr_time,"%H:%M:%S")>=datetime.strptime('18:00:00',"%H:%M:%S"):
                session.execute(prepared,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],date,trades[-1][1],'States',order_type))                
                trades.extend(generated_trade)
                return None
            
            #If last traded time is smaller then current order time then only accept order into database     
            if datetime.strptime(curr_time,"%H:%M:%S")>=datetime.strptime(last_trade_time,"%H:%M:%S"):
                session.execute(prepared,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],date,trades[-1][1],'States',order_type))                
                trades.extend(generated_trade)
                return None
            else:
                #when order is filled but has time higher than the new trade time
                #ignore the order and reset the positions to previous value
                return 9
        else:
            #Accepting First trade of the day
            trades.extend(generated_trade)
    else:
        #order Not Filled so change indicator to 9 hence not changing the position of our ALGO
        print "Not Found "
        return 9
    
        
#Generating Trades  
def state_trade(l,order_type,size,price,ratio):
    
    #Indicates the current position of of our Account
    position=0
    #Resets after each Day indicating day end
    day_start_indicator=0
    #Modify only if you want to change the buying and selling quantities
    size2=size
    #Indicator=9 Tells us if the Order is not Filled
    indicator=0
    #previous value of the State
    previou_state=1

    #Looping through each state value received to find buy/sell signals
    for Current_item in l:

        #python Datetime does not suppor time till nano second percision
        #strip time till seconds and compare if its less than market closing time i.e 6:00 pm or 18:00:00

        candle_time_end=str(Current_item.period.time_end)[:8]
        candle_time_start=str(Current_item.period.time_start)[:8]
        if datetime.strptime(candle_time_end,"%H:%M:%S")<datetime.strptime('18:00:00',"%H:%M:%S") and datetime.strptime('07:00:00',"%H:%M:%S")<=datetime.strptime(candle_time_start,"%H:%M:%S")<=datetime.strptime('19:00:00',"%H:%M:%S"):
            
            #Generation Of BUY orders
            if Current_item.state==5 and previou_state!=5:

                if position==0:
                    
                    day_start_indicator+=1
                    indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size,price,'buy',order_type,ratio,day_start_indicator)
                    
                    if indicator == 9:
                        position=0
                    else:
                        position=1
                elif position==-1:  
                    day_start_indicator+=1
                    indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size2,price,'buy',order_type,ratio,day_start_indicator)

                    if indicator==9:
                        position=-1
                    else:
                        position=0
            #SELL when state changes from 5 to something else    
            elif position==1 and Current_item.state!=5 and previou_state==5:
                   
                day_start_indicator+=1
                indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size2,price,'sell',order_type,ratio,day_start_indicator)

                if indicator==9:
                    position=1
                else:
                    position=0
            
            #Generation Of SELL orders     
            elif Current_item.state==1 and previou_state!=1:
                
                if position==1:
                    day_start_indicator+=1
                    indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size2,price,'sell',order_type,ratio,day_start_indicator)

                    if indicator==9:
                        position=1
                    else:
                        position=0
                    
                elif position==0:
                    
                    day_start_indicator+=1
                    indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size,price,'sell',order_type,ratio,day_start_indicator)     

                    if indicator==9:
                        position=0
                    else:
                        position=-1
            #BUY when state changes from 1 to something else    
            elif position==-1 and Current_item.state!=1 and previou_state==1:   
                day_start_indicator+=1
                indicator=execution(Current_item.period.date1,Current_item.period.time_end,product,size2,price,'buy',order_type,ratio,day_start_indicator)

                if indicator==9:
                    position=-1
                else:
                    position=0
        # After 18:00:00 HRS Trade Execution         
        else:
            #print position
            if position==1:
                day_start_indicator+=1
                execution(Current_item.period.date1,Current_item.period.time_end,product,1,price,'sell','Market',ratio,day_start_indicator)
                session.execute(prepared,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],trades[-1][4],trades[-1][1],'States',order_type))
                    
            if position==-1:
                day_start_indicator+=1
                execution(Current_item.period.date1,Current_item.period.time_end,product,1,price,'buy','Market',ratio,day_start_indicator)
                session.execute(prepared,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],trades[-1][4],trades[-1][1],'States',order_type))

            if position==0:
                session.execute(prepared,(run_no,product,trades[-1][0],trades[-1][2],trades[-1][3],trades[-1][4],trades[-1][1],'States','Market'))
    
            position=0
            pass
        day_start_indicator=0
        previou_state=Current_item.state
        time_series_for_graph.append(str(Current_item.period.time_end))
        states_list_for_graph.append(Current_item.state)
#-----------------------------------------------------Code START---------------------------------------------------
#name='try1'
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
size_of_candle=int(config_data['candle_size'])
candle_type=config_data['candle_type']

ip_address=[]
ip_address.append(config_data['ip_address'])


cluster = Cluster(ip_address)
session = cluster.connect(keyspace_name)

query="insert into trades(run_no,product,side,price,size,date1,time1,strategy,type) values (?,?,?,?,?,?,?,?,?)"
query2="select max(run_no) from trades allow filtering"

prepared = session.prepare(query)
prepared2 = session.prepare(query2)

run_no=session.execute(prepared2)
run_no=0 if run_no[0][0]==None else run_no[0][0]
run_no=int(run_no)+1

#Various List Initializations
trades=[]
time_series_for_graph=[]
states_list_for_graph=[]

#State Class Object
h=st.State()

#data received from State Class
state_data=h.state_main(size_of_candle,candle_type,date_start,date_end,product,keyspace_name,session)

#Inputs
order_type=raw_input("Market Orders or Limit Orders?\n")
number_of_lots=int(raw_input("How many Lots??\n"))

#Keep 0.0 for ordering without ratio using 
ratio=float(raw_input("Input the Ratio\n"))

#Keep price whatever you want for market order -- 0.0 for Auto Pricing
price=float(raw_input("Enter Price..[0.0 for Auto Pricing feature]\n"))

#Trade Generation 
state_trade(state_data,order_type,number_of_lots,price,ratio)

#Final Trades
for i in trades:
    print i[0],i[1],i[4]

# Uncomment for Generating Graph (Import Matplotlib Library!!)
"""
plt.plot(ti,s,color='red',label='States')
#plt.plot(ti,sp,color='yellow',label='signal')

plt.xlabel('')
plt.ylabel('States')
plt.legend()
plt.gcf().autofmt_xdate()
plt.show()
"""
print (datetime.now()-s_t)
