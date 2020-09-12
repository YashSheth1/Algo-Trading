from get_agg import get_agg
import csv
"""
                                        --- Generating States---
1. Definations:
   1.1 Class State
   1.2 state_main
   1.3 showdata
                                           ---Flow of CODE---
2.1 whichever script wants to use state data has to call the state_main function 
2.2 get_agg is the function of get_agg script which returns the aggregated candle data for like 10 min,500 volume etc
2.3 the period_data received is then every 2nd period data is compared with the previous and
    state of the candle is found out

"""
class State():
    
    def __init__(self,period=None,temp_high=None,temp_low=None,local_high=None,local_low=None,state=None):
        
        self.period=period
        self.temp_high=temp_high
        self.temp_low=temp_low
        self.local_high=local_high
        self.local_low=local_low    
        self.state=state
        
    def showdata(self):
        
        stri=str(self.period.open1)+' ; '+str(self.period.high)+' ; '+str(self.period.low)+' ; '+str(self.period.close)+' ; '+str(self.local_high)+' ; '+str(self.local_low)+' ; '+str(self.state)
        print stri
    
    def state_main(self,data,datatype,date1,date2,pro,Keyspace_name,session):
        
        period_data=get_agg(data,datatype,date1,date2,pro,Keyspace_name,session)
        temp_low=0.0        
        temp_high=0.0
        local_low=0.0
        local_high=0.0
        previous_high=0.0
        previous_low=0.0
        state=0
        i=1
        State_object_list=[]
        

        for current_item in period_data:
            #print current_item.close
            if i==1:
                temp_high=current_item.high
                temp_low=current_item.low
                local_high=temp_high
                local_low=temp_low
                previous_high=temp_high
                previous_low=temp_low
                i=2
            else:
                if previous_high<current_item.high:
                    temp_high=current_item.high
                    
                if previous_low>current_item.low:
                    temp_low=current_item.low
                    
                if previous_high<current_item.high:
                    local_low=temp_low
                
                if previous_low>current_item.low:
                    local_high=temp_high

            
            previous_high=current_item.high
            previous_low=current_item.low
            #x acts as a seperator
            x=(local_high-local_low)/3
            
            close=current_item.close
            if close>=local_high:
                state=5
            if close<local_high and close>=(local_high-x):
                state=4
            if close<(local_high-x) and close>=(local_high-(2*x)):
                state=3
            if close<(local_high-(2*x)) and close>(local_high-(3*x)):
                state=2
            if close<=local_low:
                state=1
                
            State_class_object=State(current_item,temp_high,temp_low,local_high,local_low,state)
            State_object_list.append(State_class_object)
        return State_object_list    
        
        
    
        
