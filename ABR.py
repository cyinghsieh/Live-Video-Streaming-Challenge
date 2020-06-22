import numpy as np

#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings
TARGET_BUFFER = [0.5 , 1.0]
BIT_RATE = [500.0,850.0,1200.0,1850.0]

# BITRATE_CONTROL, PLAYBACK_CONTROL, FRAME_DROP
optimization = (False, False, False) 

class Algorithm:
    def __init__(self):
    # fill your self params
        self.last_predict = []
        self.last_bitrate = [3]
        self.last_actual = []
        self.bitrate_diff = 1
        self.cdn_latest = 0
        self.cdn_last_id = -1

    # Intial
    def Initial(self):
    # Initail your session or something
        return self.get_params()

    def reset(self):
        self.last_predict = []
        self.last_bitrate = [3]
        self.last_actual = []
        self.bitrate_diff = 1
        self.cdn_latest = 0
        self.cdn_last_id = -1
    
    def predict_bitrate(self, last_actual, current_bitrate):
        previous_bitrate = last_actual * BIT_RATE[current_bitrate] / BIT_RATE[self.last_bitrate[-1]]
        self.last_actual.append(previous_bitrate)

        sample_num = 15
        # count_max = self.last_bitrate.count(0)
        # count_min = self.last_bitrate.count(3)
        count_max = 25
        count_min = 4

        SC_slow = 2 / (count_max + 1)
        SC_fast = 2 / (count_min + 1)

        if(len(self.last_actual) <= sample_num):
            predict = np.average(self.last_actual)
        else:
            self.bitrate_diff = 1
            for idx in range(-1, -11, -1):
                self.bitrate_diff += abs(self.last_actual[idx] - self.last_actual[idx-1])
            ER = abs(self.last_actual[-1] - self.last_actual[-1 * sample_num]) / self.bitrate_diff
            SC = (ER * (SC_fast - SC_slow) + SC_slow) ** 2
            
            predict = (1 - SC) * self.last_predict[-1] + SC * previous_bitrate
            
        #print(predict)
                
        self.last_predict.append(predict)

        return predict

    def playback(self, buffer_occupy):
        # after rounding 0.5 / 2 = 0.2
        b0_min = round(TARGET_BUFFER[0]/2, 1)
        b0_max = TARGET_BUFFER[0]*2
        b1_min = round(TARGET_BUFFER[1]/2, 1)
        b1_max = TARGET_BUFFER[1]*2

        # calculate target buffer
        if(buffer_occupy >= b0_min and buffer_occupy < b0_max):
            t_buffer = 1
        else:
            t_buffer = 0

        # calculate the corresponding playback rate
        if(buffer_occupy < b1_min):
            play_rate = 0.95
        elif(buffer_occupy >=  b0_max):
            play_rate = 1.05
        else:
            play_rate = 1
        
        return t_buffer, play_rate

    def frame_drop(self, bit_rate, frame_length, total_delay):
        avg_latency = 5
        skip_weight = 0.005 if total_delay <= 1.0 else 0.01

        th_drop = (BIT_RATE[bit_rate] + BIT_RATE[0]) * frame_length / (avg_latency * skip_weight * 1000)
        return th_drop

    #Define your al
    def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
        # If you choose BBA

        BITRATE_CONTROL, PLAYBACK_CONTROL, FRAME_DROP = optimization        
        # playback control
        target_buffer, play_rate = self.playback(S_buffer_size[-1])

        # negative number of frames in GOP
        frame_num = self.cdn_last_id - download_id        
        bit_rate = 0

        if PLAYBACK_CONTROL:
            target_buffer, play_rate = self.playback(S_buffer_size[-1])
        else:
            target_buffer, play_rate = 0, 1

        bit_rate = 0
        if BITRATE_CONTROL:
            # negative number of frames in GOP
            frame_num = self.cdn_last_id - download_id
            
            if(end_of_video):
                self.reset()
            else:
                throughput = np.sum(S_send_data_size[-1]) / np.sum(S_time_interval[-1])
                #throughput = np.sum(S_send_data_size[frame_num:]) / np.sum(S_time_interval[frame_num:])

                encode = np.sum(S_send_data_size[frame_num:]) / np.sum(S_chunk_len[frame_num:]) 
                #encode = np.sum(S_send_data_size[-1]) / np.sum(S_chunk_len[-1])                 
   
        
                for i in range(3, -1, -1):
                    #actual_bitrate = self.predict_bitrate(encode, i)
                    period = BIT_RATE[i] * 1000 * np.sum(S_chunk_len[frame_num:]) / throughput
                    buffer_occupancy = S_buffer_size[-1] + np.sum(S_chunk_len[frame_num:]) - play_rate * period

                    cdn_cumualte = (cdn_newest_id - self.cdn_latest)*S_chunk_len[-1]/np.sum(S_time_interval[frame_num:])
                    factor = 1
                    cdn_latency = (cdn_newest_id - download_id)*S_chunk_len[-1] + factor*cdn_cumualte*period - np.sum(S_chunk_len[frame_num:])
                    
                    # print(buffer_occupancy, cdn_latency)
                    if(buffer_occupancy >= 0.6 or cdn_cumualte >= 2.5):
                        bit_rate = i
                        break        

        if FRAME_DROP:
            latency_limit = self.frame_drop(bit_rate, S_chunk_len[-1], S_end_delay[-1])
        else:
            latency_limit = 3
        #print(latency_limit)

        self.last_bitrate.append(bit_rate)
        self.cdn_latest = cdn_newest_id
        self.cdn_last_id = download_id

        return bit_rate, target_buffer, latency_limit

    def get_params(self):
    # get your params
        your_params = [self.last_bitrate]
        return your_params
