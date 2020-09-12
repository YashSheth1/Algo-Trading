import datetime as dt
from datetime import datetime
import sys
"""
                             ---Trade Module--
1. Query the Tick data from cassandra  
2. Check Order type

3. LOGIC : Market Order
     3.1 : Check if the row is a block or not not
     3.2 : Find the current ask and bid price
     3.3 : Buy or Sell at the current price

4. LOGIC : Limit Order
     4.1 : Check if the row is a block or not not
     4.2 : If ratio is 0.0 then price is automatically calculate on basis of bid and ask price
     4.3 : If ratio is given is non zero,price is calculated on only if the ratio gets satisfied  
     4.4 : If the order is not fullfilled in one hour then we get return value as NOT FOUND

5. LOGIC : Stop Order
     5.1 : Place order at the given Price and wait
     5.2 : If order is not fulfilled in 1 hour then return Not Found
     
"""
def Trades(date1,time1,product,size,price,side,Order_type,ratio,keyspace_name,session):
    
    """_______________________0_____1_____2_____3_____4_____5______6_______7_______8________9______10______11___"""
    tick_data_query="select xric,date1,time1,number,type,price,volume,bidprice,bidsize,askprice,asksize,is_block from data where date1=? and time1>=? allow filtering"
    prepared_tick_data_query=session.prepare(tick_data_query)
    tick_data=session.execute(prepared_tick_data_query,(date1,time1))
    execute_trade_list=[]
    bidprice=0.0
    bidsize=0
    askprice=0.0
    asksize=0
    not_found='Not Found'
    
    if Order_type=='Market':
        for item in tick_data:
            if item[11]=='True':
                pass
            else:                
                bidprice=bidprice if item[7]==None else round(float(item[7]),2)
                bidsize=bidsize if item[8]==None else int(item[8])
                askprice=askprice if item[9]==None else round(float(item[9]),2)
                asksize=asksize if item[10]==None else int(item[10])
            
                if side=='buy' and askprice!=None and askprice!=0.0 :
                    print "Buy"
                    k=side,item[2],askprice,size,date1
                    #print k[1]
                    execute_trade_list.append(k)
                    return execute_trade_list

                if side=='sell' and bidprice!=None and bidprice!=0.0:
                    print "Sell"
                    #print size
                    k=side,item[2],bidprice,size,date1
                    #print k[1]
                    execute_trade_list.append(k)
                    return execute_trade_list
    
    if Order_type=='Limit':
        i=0
        j=0
        
        f=str(time1)[:8]
        time2=datetime.strptime(f,"%H:%M:%S")+dt.timedelta(hours=1)
        
        #print str(time2)
        for item in tick_data:
            if item[11]=='True':
                pass
            else:
                f3=str(item[2])[:8]
                f2=datetime.strptime(f3,"%H:%M:%S")
                #print time2
                if f2<=time2:
                    #print side
                    bidprice=bidprice if item[7]==None else round(float(item[7]),2)
                    bidsize=bidsize if item[8]==None else int(item[8])
                    askprice=askprice if item[9]==None else round(float(item[9]),2)
                    asksize=asksize if item[10]==None else int(item[10])
                
                    # for calculating automated price 
                    if bidprice!=0.0 and side=='buy' and askprice!=0.0:
                        i+=1
                    if askprice!=0.0 and side=='sell' and bidprice!=0.0:
                        j+=1
                    if ratio!=0.0:
                        if i==1 and side=='buy':
                            
                            if ((asksize*1.0)/bidsize)<ratio:
                                price=askprice
                            else:
                                price=bidprice                            

                        if j==1 and side=='sell':
                            
                            if ((bidsize*1.0)/asksize)<ratio:
                                price=bidprice
                            else:
                                price=askprice
                            
                    else:
                        if i==1 and side=='buy':
                            price=bidprice
                        if j==1 and side=='sell':
                            price=askprice
                        
                    if side=='buy' and asksize!=None and price==askprice and askprice!=0.0:
                        print "Buy"
                        k=side,item[2],askprice,size,date1
                        #print k
                        execute_trade_list.append(k)
                        return execute_trade_list
                
                    if side=='sell' and bidsize!=None and price==bidprice and bidprice!=0.0:
                        print "Sell"
                        k=side,item[2],bidprice,size,date1
                        #print k
                        execute_trade_list.append(k)
                        return execute_trade_list
                else:
                    break
        execute_trade_list.append(not_found)        
        return execute_trade_list
    
    if Order_type=='Stop_Buy':

        f=str(time1)[:8]
        time2=datetime.strptime(f,"%H:%M:%S")+dt.timedelta(hours=1)
        
        for item in tick_data:
            if item[11]=='True':
                pass
            else:
                f3=str(item[2])[:8]
                f2=datetime.strptime(f3,"%H:%M:%S")
                if f2<=time2:
                    bidprice=bidprice if item[7]==None else round(float(item[7]),2)
                    bidsize=bidsize if item[8]==None else int(item[8])
                    askprice=askprice if item[9]==None else round(float(item[9]),2)
                    asksize=asksize if item[10]==None else int(item[10])

                    if side=='buy' and asksize!=None and price==askprice:
                        k=item[2],askprice,size,date1
                        execute_trade_list.append(k)
                        return execute_trade_list
                else:
                    break
        execute_trade_list.append(not_found)
        return execute_trade_list
    
    if Order_type=='Stop_Sell':
        f=str(time1)[:8]
        time2=datetime.strptime(f,"%H:%M:%S")+dt.timedelta(hours=1)
        
        for item in tick_data:
            if item[11]=='True':
                pass            
            else:
                f3=str(item[2])[:8]
                f2=datetime.strptime(f3,"%H:%M:%S")
                if f2<=time2: 
                    bidprice=bidprice if item[7]==None else round(float(item[7]),2)
                    bidsize=bidsize if item[8]==None else int(item[8])
                    askprice=askprice if item[9]==None else round(float(item[9]),2)
                    asksize=asksize if item[10]==None else int(item[10])

                    if side=='sell' and bidsize!=None and price==bidprice:
                        k=item[2],bidprice,size,date1
                        execute_trade_list.append(k)
                        return execute_trade_list
                else:
                    break                
        execute_trade_list.append(not_found)        
        return execute_trade_list
