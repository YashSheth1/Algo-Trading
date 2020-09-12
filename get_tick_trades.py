"""
                      ---For Bolinger Trade Strategy---
                      
1. Goes to Tick Data in cassandra and check if we will get a fill on Mid level value or Not
2. If Yes then returns TRUE else returns FALSE
"""
def check_data(product,time_start,time_end,date1,session,mid_price,side):
    query_fetch_tick_data="select type,price,is_block from data where xric=? and date1=? and time1>=? and time1<=? allow filtering"
    p = session.prepare(query_fetch_tick_data)
    tick_data = session.execute(p,(product,date1,time_start,time_end))
    for item in tick_data:
        if item[1]!=None and item[2]!=True:
            if item[0]=='Trade':
                if side=='buy':
                    if item[1]<=mid_price:
                        return True
                    else:
                        return False
                else:
                    if item[1]>=mid_price:
                        return True
                    else:
                        return False
    return False    
    
