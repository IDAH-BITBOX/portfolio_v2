from components.libs.basic import *
import requests


def dispatchDeleteRoundComponent(routeId, driverId, date, deleteRound, status, reason, managerId, deployCheck):
    deleteRound = deleteRound - 1
    dispatchCond = {
        "route_id": str(routeId),
        "date": "'"+str(date)+"'"
    }
    example = load_db(deployCheck, 'dispatch', dispatchCond)
    example.index = np.arange(len(example))
    try:
        max_round = np.max(example['bus_round'].values)
        max_order = np.max(example['start_order'].values)
    except:
        #raise HTTPException(status_code=404, detail="배차일보가 존재하지 않습니다.")
        return 404
    try:
        delete_order = example.loc[example['driver_id']==driverId, 'start_order'].values.tolist()[0]
        print(delete_order)
    except:
        print("driver not found")
        ##raise HTTPException(status_code=406, detail="해당 승무원을 배차일보에서 찾을 수 없습니다.")
        return 406

    residue_driver_list = [int(driver_id_) for driver_id_ in example['driver_id'].unique() if int(driver_id_) != driverId]
    temp_table = pd.DataFrame(example)
    temp_table.index = np.arange(len(temp_table))
    temp_table['start_time'] = temp_table['start_time'].dt.strftime("%H:%M")

    '''formCond = {
        "route_id": str(routeId),
        "bus_count": str(len(residue_driver_list))
    }
    form_df = load_db(deployCheck, 'dispatch_form', formCond)
    form_df.index = np.arange(len(form_df))
    form_day_types = form_df['day_type'].unique().tolist()
    form_day_type = "WEEKDAY"
    for day_type_ in form_day_types:
        form_df_buf = form_df[form_df['day_type']==day_type_]
        if np.max(form_df_buf['bus_round'].values) == max_round + 1:
            form_day_type = day_type_
    if form_day_type == "HOLIDAY":
        form_day_type = "WEEKDAY"
    form_df = form_df[form_df['day_type']==form_day_type]
    form_df.index = np.arange(len(form_df))'''

    '''## form data를 dictionay에 저장 -> 레퍼런스 용도의 변수 ##
    form_dict = dict()
    for idx in range(len(form_df)):
        order_ = form_df.loc[idx, 'start_order']-1
        round_ = form_df.loc[idx, 'bus_round']-1
        hm = int("".join(form_df.loc[idx, 'time'].split(":")))
        start_time_ = date + " " + form_df.loc[idx, 'time'] + ":00"
        if hm < 300:
            start_time_ = datetime.datetime.strptime(start_time_, "%Y-%m-%d %H:%M:%S")
            start_time_ = start_time_ + datetime.timedelta(days=1)
        else:
            start_time_ = datetime.datetime.strptime(start_time_, "%Y-%m-%d %H:%M:%S")
        
        if order_ in form_dict:
            form_dict[order_][round_] = start_time_
        else:
            form_dict[order_] = dict()
            form_dict[order_][round_] = start_time_'''

    #print(form_dict)
    ## update 하려는 start_time을 temporary table에 임시 저장 ##
    idx_list = []
    patch_start_time = dict()
    patch_start_order = dict()
    for idx in range(len(temp_table)):
        order_ = temp_table.loc[idx, 'start_order']
        round_ = temp_table.loc[idx, 'bus_round']
        raw_start_time_ = temp_table.loc[idx, 'start_time']
        driver_id_ = temp_table.loc[idx, 'driver_id']

        if round_ >= deleteRound and round_ < max_round+1:
            if driver_id_ in residue_driver_list:
                ## deleteRound 이후 남아있는 승무원들의 경우 ##
                ## order_가 삭제하려고하는 순번보다 큰 경우 ##
                if order_ > delete_order:
                    #patch_start_time[idx] = form_dict[order_ - 1][round_]
                    patch_start_time[idx] = raw_start_time_
                    if deleteRound == -1 or deleteRound == 0:
                        patch_start_order[idx] = order_ - 1
                    else:
                        patch_start_order[idx] = order_
                else:
                    ## order_가 삭제하려고하는 순번보다 작은 경우 && round_가 삭제시작된 deleteRound보다 큰 경큰 ##
                    if order_ < delete_order and round_ > deleteRound:
                        #patch_start_time[idx] = form_dict[order_][round_]
                        patch_start_time[idx] = raw_start_time_
                        patch_start_order[idx] = order_
                    else:
                        patch_start_time[idx] = raw_start_time_
                        patch_start_order[idx] = order_
                idx_list.append(idx)
            else:
                ## deleteRound 이후 사라지는 승무원의 경우 ##
                continue
        else:
            ## deleteRound 이전의 경우는 그대로 유지 ##
            patch_start_time[idx] = raw_start_time_
            patch_start_order[idx] = order_
            idx_list.append(idx)
                
    temp_table.loc[idx_list, 'start_time'] = list(map(lambda x:patch_start_time[x], idx_list))
    temp_table.loc[idx_list, 'start_order'] = list(map(lambda x:patch_start_order[x], idx_list))
    temp_table = pd.DataFrame(temp_table.loc[idx_list])
    temp_table['updated_at'] = [datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S") for _ in range(len(temp_table))]
    temp_table['manager_id'] = [managerId for _ in range(len(temp_table))]
    print(temp_table)

    ## 해당 배차일보가 조커인지 아닌지 판별 ##
    ## 승무원 제외인 경우
    formCond = {
        "route_id": str(routeId),
    }
    form_df_raw = load_db(deployCheck, 'dispatch_form', formCond)
    if len(form_df_raw)==0:
        raise HTTPException(status_code=404, detail=str(date)+" 일자에 "+str(max_order+1)+"대 배차일보 양식이 존재하지 않습니다.")
    day_types = ['WEEKDAY', 'SATURDAY', 'HOLIDAY']
    current_day_type = day_types[0]
    current_form_max_round = 0
    current_form_df = dict()
    current_sim_lst = []
    start_time_lst = temp_table['start_time'].values.tolist()
    print(start_time_lst)
    for day_type_ in day_types:
        form_df = form_df_raw.loc[form_df_raw['day_type']==day_type_]
        form_times_ = form_df['time'].values.tolist()
        form_df = form_df[form_df['bus_count']==max_order+1]
        form_max_round_ = form_df['bus_round'].max()
        form_df = form_df.loc[form_df['bus_round']==form_max_round_]
        form_df.index = np.arange(len(form_df))

        similarity_ = 0.0
        if len(form_times_)==0:
            continue
        for start_time_ in start_time_lst:
            if start_time_ in form_times_:
                similarity_ += 1.0
        similarity_ = similarity_ / len(start_time_lst)
        current_form_df[day_type_] = form_df
        current_sim_lst.append(similarity_)

    print(day_types, current_sim_lst)
    max_sim_type = day_types[current_sim_lst.index(max(current_sim_lst))]
    print(max_sim_type)
    form_df = current_form_df[max_sim_type]
    current_form_max_round = form_df['bus_round'].max()
    current_day_type = max_sim_type

    currentCreateCheck = False
    if "2:30" in form_df['time'].values or "02:30" in form_df['time'].values:
        currentCreateCheck = True
    if len(form_df) != max_order + 1:
        currentJokerCheck = True
        joker_order_current = form_df['start_order'].unique().tolist()
    else:
        currentJokerCheck = False
        joker_order_current = []

    createCheck = False
    if deleteRound == -1 or deleteRound == 0:
        form_df = form_df_raw[form_df_raw['bus_count']==max_order]
        form_df = form_df[form_df['day_type']==current_day_type]
        if len(form_df)==0:
            raise HTTPException(status_code=404, detail=str(date)+" 일자에 "+str(max_order)+"대 배차일보 양식이 존재하지 않습니다.")
        form_max_round = form_df['bus_round'].max()
        form_df = form_df.loc[form_df['bus_round']==form_max_round]
        form_df.index = np.arange(len(form_df))
        if "2:30" in form_df['time'].values or "02:30" in form_df['time'].values:
            createCheck = True
        if len(form_df) != max_order:
            jokerCheck = True
            joker_order = form_df['start_order'].unique().tolist()
        else:
            jokerCheck = False
            joker_order = []
    ## 중도귀가인 경우 ##
    else:
        form_df = form_df_raw[form_df_raw['bus_count']==max_order+1]
        form_df = form_df[form_df['day_type']==current_day_type]
        if len(form_df)==0:
            raise HTTPException(status_code=404, detail=str(date)+" 일자에 "+str(max_order+1)+"대 배차일보 양식이 존재하지 않습니다.") 
        form_max_round = form_df['bus_round'].max()
        form_df = form_df.loc[form_df['bus_round']==form_max_round]
        form_df.index = np.arange(len(form_df))
        if "2:30" in form_df['time'].values or "02:30" in form_df['time'].values:
            createCheck = True
        if len(form_df) != max_order+1:
            jokerCheck = True
            joker_order = form_df['start_order'].unique().tolist()
        else:
            jokerCheck = False
            joker_order = []
    
    print(currentJokerCheck, jokerCheck, len(form_df), temp_table.loc[temp_table['bus_round']==max_round, 'start_order'].max()+1, max_order+1)
    print("form max round:", form_max_round)

    ## 기준 round_list 목록을 참고하여 중도귀가인지 판단하기 ##
    round_list = [r for r in range(form_max_round)]
    start_delete_round = np.max(round_list) + 1
    start_delete_order = 0
    ## 중도귀가 처리하고 남은 start_order, bus_round ##
    exist_order = dict()
    exist_round = dict()
    table_pos = []
    table_pos_dict = dict()
    exist_table_pos = []
    leave_early_pos = []

    for order_ in range(max_order+1):
        row_ = temp_table[temp_table['start_order']==order_]
        rounds_ = row_['bus_round'].values.tolist()
        
        ## 중도귀가를 한 rounds: no_exist_rounds ##
        no_exist_rounds = [np.max(round_list)+1]
        for r in round_list[::-1]:
            if r in rounds_:
                continue
            else:
                if r+1 in no_exist_rounds:
                    no_exist_rounds.append(r)
        no_exist_rounds = no_exist_rounds[1:]
        if currentCreateCheck:
            no_exist_rounds = []
        elif order_-1 not in joker_order_current and len(no_exist_rounds) == 1:
            no_exist_rounds = [r_ for r_ in no_exist_rounds if r_+1 < form_max_round - 1]
        elif order_-1 not in joker_order and len(no_exist_rounds) == 1:
            no_exist_rounds = [r_ for r_ in no_exist_rounds if r_+1 < form_max_round - 1]
        elif jokerCheck and len(no_exist_rounds) == 1:
            no_exist_rounds = [r_ for r_ in no_exist_rounds if r_+1 < form_max_round]
        
        print(order_+1, joker_order_current, joker_order, no_exist_rounds)
        if len(no_exist_rounds) > 0:
            if start_delete_round > np.min(no_exist_rounds):
                start_delete_round = np.min(no_exist_rounds)
                start_delete_order = order_
                print(start_delete_round, start_delete_order)

        exist_rounds_ = [r for r in round_list if r not in no_exist_rounds]
        exist_round[order_] = exist_rounds_
        table_pos.extend([(order_, r) for r in round_list])
        for r_ in round_list:
            if r_ in table_pos_dict:
                table_pos_dict[r_].append(order_)
            else:
                table_pos_dict[r_] = [order_]

        exist_table_pos.extend([(order_, r) for r in exist_rounds_])
        if len(no_exist_rounds) > 0:
            leave_early_pos.extend([(order_, r) for r in no_exist_rounds])

    print(209, start_delete_round, start_delete_order)

    leave_early_order = dict()
    for order_, round_ in leave_early_pos:
        if round_ in leave_early_order:
            leave_early_order[round_].append(order_)
        else:
            leave_early_order[round_] = [order_]

    re_map_order = dict()
    for round_ in table_pos_dict:
        sub_order_ = 0
        re_map_order[round_] = dict()
        for order_ in table_pos_dict[round_]:            
            if round_ in leave_early_order and order_ in leave_early_order[round_]:
                sub_order_ += 1
            re_map_order[round_][order_] = - sub_order_

    print(re_map_order)

    for order_ in exist_round:
        for round_ in exist_round[order_]:
            if round_ in exist_order:
                exist_order[round_].append(order_)
            else:
                exist_order[round_] = [order_]

    print(exist_order)
    bus_cnt_list = []
    for r in exist_order:
        bus_cnt_ = len(exist_order[r])
        bus_cnt_list.append(bus_cnt_)
    print(241,bus_cnt_list, len(joker_order), len(joker_order_current))
    unique_bus_cnt_list = np.unique(bus_cnt_list)
    form_df_refer = dict()
    max_round_lst = []
    for bus_cnt_ in unique_bus_cnt_list:
        print(bus_cnt_, len(joker_order), jokerCheck)
        if jokerCheck and bus_cnt_list.index(bus_cnt_) == len(bus_cnt_list)-1:
            continue
        form_df = form_df_raw[form_df_raw['bus_count']==bus_cnt_]
        form_df = form_df[form_df['day_type']==current_day_type]
        form_df.index = np.arange(len(form_df))
        print(219, len(form_df))
        if len(form_df) == 0:
            raise HTTPException(status_code=404, detail=str(date)+" 일자에 "+str(bus_cnt_)+"대 배차일보 양식이 존재하지 않습니다.")
        form_df_refer[bus_cnt_] = form_df
        max_round_lst.append(form_df['bus_round'].max())

    if deleteRound==0 or deleteRound==-1:
        form_df = form_df_raw[form_df_raw['bus_count']==min(unique_bus_cnt_list)+1]
        form_df = form_df[form_df['day_type']==current_day_type]
        form_df.index = np.arange(len(form_df))
    else:
        form_df = form_df_raw[form_df_raw['bus_count']==min(unique_bus_cnt_list)]
        form_df = form_df[form_df['day_type']==current_day_type]
        form_df.index = np.arange(len(form_df))
    last_form_max_round = form_df['bus_round'].max()
    print(form_max_round, last_form_max_round, "ENG")
        
    print(form_df_refer)
    print('start_delete_round: ', start_delete_round, start_delete_order)
    print(leave_early_pos)
    new_form_dict = dict()
    for order_, round_ in table_pos:
        sub_order_ = re_map_order[round_][order_]
        if (order_, round_) in exist_table_pos:
            print(order_, round_, joker_order, form_max_round)
            if form_max_round > last_form_max_round and round_==last_form_max_round and len(exist_order[round_]) in form_df_refer:
                form_df_buf_ = form_df_refer[len(exist_order[round_])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_ + sub_order_ + 1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==form_max_round]
                print(form_df_buf_, "ENGENGENG")
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00" 
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    raw_start_time_ = None
            elif jokerCheck and round_ + 1 == form_max_round:
                print("OHYEAH")
                sub_order_ = 0 
                form_df_buf_ = form_df_refer[len(exist_order[0])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_+sub_order_+1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==round_+1]
                print(order_, round_, len(exist_order[0]))
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00" 
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    raw_start_time_ = None
                    print("None time", order_, round_)
            elif currentJokerCheck and round_ + 1 == form_max_round:
                print("OHYEAH 2")
                sub_order_ = 0 
                form_df_buf_ = form_df_refer[len(exist_order[0])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_+sub_order_+1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==round_+1]
                print(order_, round_, len(exist_order[0]))
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00" 
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    temp_table_buf = temp_table[temp_table['start_order']==order_]
                    temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                    raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                    raw_start_time_ = date + " " + raw_start_time_ + ":00"
                    print("TEST")
                    
            elif round_ > start_delete_round and len(exist_order[round_]) in form_df_refer:
                form_df_buf_ = form_df_refer[len(exist_order[round_])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_ + sub_order_ + 1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==round_+1]
                print(order_, round_, len(exist_order[round_]))
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    temp_table_buf = temp_table[temp_table['start_order']==order_]
                    temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                    raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                    raw_start_time_ = date + " " + raw_start_time_ + ":00"
            elif round_ == start_delete_round and order_ > start_delete_order and deleteRound > 0 and len(exist_order[round_]) in form_df_refer:
                form_df_buf_ = form_df_refer[len(exist_order[round_])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_ + sub_order_ + 1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==round_+1]
                print(order_, round_, len(exist_order[round_]))
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00" 
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    temp_table_buf = temp_table[temp_table['start_order']==order_]
                    temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                    raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                    raw_start_time_ = date + " " + raw_start_time_ + ":00"
                '''elif round_ == start_delete_round and order_ < start_delete_order:
                temp_table_buf = temp_table[temp_table['start_order']==order_]
                temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                raw_start_time_ = date + " " + raw_start_time_ + ":00"
                raw_start_time_ = datetime.datetime.strptime(raw_start_time_, "%Y-%m-%d %H:%M:%S")
                '''

            elif round_ == start_delete_round and deleteRound <= 0 and len(exist_order[round_]) in form_df_refer:
                form_df_buf_ = form_df_refer[len(exist_order[round_])]
                form_df_buf_ = form_df_buf_[form_df_buf_['start_order']==order_ + sub_order_ + 1]
                form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==round_+1]
                print(order_, round_, len(exist_order[round_]))
                if len(form_df_buf_) > 0:
                    raw_start_time_ = form_df_buf_['time'].values.tolist()[0]
                    if int("".join(raw_start_time_.strip().split(":"))) == 230:
                        try:
                            temp_table_buf = temp_table[temp_table['start_order']==order_]
                            temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                            raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                            raw_start_time_ = date + " " + raw_start_time_ + ":00"
                        except:
                            raw_start_time_ = date + " " + raw_start_time_ + ":00" 
                    else:
                        raw_start_time_ = date + " " + raw_start_time_ + ":00"
                else:
                    temp_table_buf = temp_table[temp_table['start_order']==order_]
                    temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                    raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                    raw_start_time_ = date + " " + raw_start_time_ + ":00"
            else:
                print("debug", order_, round_)
                try:
                    temp_table_buf = temp_table[temp_table['start_order']==order_]
                    temp_table_buf = temp_table_buf[temp_table_buf['bus_round']==round_]
                    raw_start_time_ = temp_table_buf['start_time'].values.tolist()[0]
                    raw_start_time_ = date + " " + raw_start_time_ + ":00"
                except:
                    continue

            if order_ in new_form_dict:
                new_form_dict[order_][round_] = raw_start_time_
            else:
                new_form_dict[order_] = dict()
                new_form_dict[order_][round_] = raw_start_time_

    print(new_form_dict)
    refined_idx = []
    refined_start_time = []
    temp_table.index = np.arange(len(temp_table))

    for idx in range(len(temp_table)):
        order_ = temp_table.loc[idx, 'start_order']
        round_ = temp_table.loc[idx, 'bus_round']
        if order_ in new_form_dict:
            if round_ in new_form_dict[order_] and new_form_dict[order_][round_]:
                if (deleteRound == 0 or deleteRound == -1) and round_ <= form_max_round-1:
                    refined_start_time.append(new_form_dict[order_][round_])
                    refined_idx.append(idx)
                elif deleteRound != 0 and deleteRound != -1:
                    refined_start_time.append(new_form_dict[order_][round_])
                    refined_idx.append(idx)

    temp_table.loc[refined_idx, 'start_time'] = refined_start_time
    temp_table = temp_table.loc[refined_idx]
    temp_table.index = np.arange(len(temp_table))
    if (not createCheck and not currentCreateCheck and (jokerCheck or currentJokerCheck) and (deleteRound == 0 or deleteRound == -1)) or form_max_round > last_form_max_round:
        print(exist_order[form_max_round-2], max_round, form_max_round - 1)
        form_df_buf_ = form_df_refer[len(exist_order[form_max_round-2])]
        form_df_buf_ = form_df_buf_[form_df_buf_['bus_round']==form_max_round]
        print(form_df_buf_.head())
        for order_ in new_form_dict:
            if form_max_round-1 in new_form_dict[order_] and new_form_dict[order_][form_max_round-1] and len(form_df_buf_) > 0:
                sub_order_ = re_map_order[form_max_round-2][order_]
                print('sub_order:', sub_order_)
                temp_joker_table = temp_table.loc[temp_table['start_order']==order_]
                temp_joker_table.index = np.arange(len(temp_joker_table))
                temp_joker_table = pd.DataFrame(temp_joker_table.loc[temp_joker_table['bus_round']==form_max_round-2])
                temp_joker_table['id'] = [None]
                temp_joker_table['start_order'] = [order_]
                temp_joker_table['bus_round'] = [form_max_round - 1]
                raw_start_time_ = new_form_dict[order_][form_max_round-1]
                temp_joker_table['start_time'] = [raw_start_time_]
                temp_table = pd.concat([temp_table, temp_joker_table])

    temp_table.index = np.arange(len(temp_table))
    temp_table = temp_table.sort_values(by=['start_order'], ascending=True)
    temp_table = temp_table.sort_values(by=['bus_round'], ascending=True)
    temp_table.index = np.arange(len(temp_table))
    temp_table = temp_table.drop_duplicates(subset=['start_order', 'bus_round'], keep='first').reset_index(drop=True)
    temp_table.index = np.arange(len(temp_table))
    print(temp_table.head())

    temp_table = temp_table.sort_values(by=['start_order'], ascending=True)
    temp_table = temp_table.sort_values(by=['bus_round'], ascending=True)    
    temp_table.index = np.arange(len(temp_table))
    temp_table['int_start_time'] = temp_table['start_time'].str.replace(pat=r'[^\w]', repl=r'', regex=True).str.replace(' ', '').astype(int)
    temp_max_round = temp_table['bus_round'].max()
    start_time_check_1 = temp_table.loc[temp_table['bus_round']==temp_max_round-1, 'int_start_time'].max()
    start_time_check_2 = temp_table.loc[temp_table['bus_round']==temp_max_round, 'int_start_time'].min()
    if start_time_check_1 > start_time_check_2 and not createCheck and not currentCreateCheck:
        print("Revise Check")
        temp_table = temp_table[temp_table['bus_round']<temp_max_round]
    temp_table = temp_table.drop(columns=['int_start_time'])
    temp_table.index = np.arange(len(temp_table))
 
    delete_bulk_db(deployCheck, "dispatch", [dispatchCond])
    insert_df_to_db(deployCheck, 'dispatch', temp_table)

    #if deleteRound==-1:

    '''try:
        if deployCheck:
            workCheckUrl = ""+str(driverId)+"/"+str(date)
            workChangeUrl = ""+str(driverId)+"/"+str(date)+"/work"
        else:
            workCheckUrl = ""+str(driverId)+"/"+str(date)
            workChangeUrl = ""+str(driverId)+"/"+str(date)+"/work"
        resWorkCheck = requests.get(workCheckUrl)
        resWorkCheck = resWorkCheck.json()['object']
        print(resWorkCheck)
        workStatus = resWorkCheck['status']
        if workStatus=="WORK_SUPPORT":
            routeId = resWorkCheck['routeId']
            resWorkChange = requests.patch(workChangeUrl, json={"reason":"null"}, headers={'content-type': 'application/json', 'Authorization': token})
            print(resWorkChange.json())
    except:
        pass'''

    workCond = {
        "route_id": str(routeId),
        "date": "'"+str(date)+"'",
        "driver_id": str(driverId)
    }
    if reason and reason != "null" and reason != "undefined" and reason != "":
        workPatchObj = {
            "status": "'"+status+"'",
            "reason": "'"+reason+"'" 
        }
    else:
        workPatchObj = {
            "status": "'"+status+"'",
            "reason": "null" 
        }
    getWorkDf = load_db(deployCheck, 'work', workCond)
    work_id = getWorkDf['id'].values.tolist()[0]
    past_status = getWorkDf['status'].values.tolist()[0]
    workHistory = pd.DataFrame()
    workHistory['work_id'] = [work_id]
    workHistory['driver_id'] = [driverId]
    workHistory['date'] = [date]
    workHistory['past_status'] = [past_status]
    workHistory['curr_status'] = [status]
    workHistory['reason'] = [None]
    workHistory['created_at'] = [datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")]
    workHistory['updated_at'] = [datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")]
    workHistory['manager_id'] = [managerId]

    insert_df_to_db(deployCheck, 'work_history', workHistory)
    patch_db(deployCheck, 'work', workPatchObj, workCond)
    '''else:
        workCond = {
            "route_id": str(routeId),
            "date": "'"+str(date)+"'",
            "driver_id": str(driverId)
        }
        workPatchObj = {
            "status": "'LEAVE_EARLY'",
            "reason": "null" 
        }
        patch_db(deployCheck, 'work', workPatchObj, workCond)
        insert_df_to_db(deployCheck, 'work_history', workHistory)'''

    changed_drivers = []
    for idx in range(len(temp_table)):
        driver_id_ = temp_table.loc[idx, 'driver_id']
        start_order_ = temp_table.loc[idx, 'start_order']
        bus_round_ = temp_table.loc[idx, 'bus_round']
        start_time_ = temp_table.loc[idx, 'start_time']

        example_buf_ = example[example['driver_id']==driver_id_]
        example_buf_ = example[example['start_order']==start_order_]
        example_buf_ = example[example['bus_round']==bus_round_]
        example_buf_ = example[example['start_time']==start_time_]
        if len(example_buf_.values.tolist()) == 0 and driver_id_ not in changed_drivers:
            changed_drivers.append(int(driver_id_))

    changed_drivers.append(driverId)
    changed_drivers = list(set(changed_drivers))
    print(changed_drivers)
    fcm_data = {'date':date, 'driverIdList':changed_drivers}
    if deployCheck:
        fcm_url = ""
    else:
        fcm_url = ""
        
    try:
        res = requests.post(fcm_url, json=fcm_data)
        print(res)
    except:
        print("FCM ERROR")

    return {"status":200, "message":"success","object":{}}