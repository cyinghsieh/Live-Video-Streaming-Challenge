import numpy as np
import math

#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings
TARGET_BUFFER = [0.5 , 1.0]
BIT_RATE = [500.0,850.0,1200.0,1850.0]
class Algorithm:
    def __init__(self):
    # fill your self params
        self.buffer_size = 0
        self.last_bitrate = 0
        self.cdn_latest = 0

    # Intial
    def Initial(self):
    # Initail your session or something
        return self.get_params()

    def reset(self):
        self.last_bitrate = 0
        self.cdn_latest = 0

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

    #Define your al
    def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
        # If you choose BBA
        bit_rate = 0
        target_buffer, play_rate = self.playback(S_buffer_size[-1])

        if(end_of_video):
            self.reset()
        else:
            throughput = S_send_data_size[-1] / S_time_interval[-1]
            # for i in range(3, -1, -1):
            #     if(S_buffer_size[-1] > BIT_RATE[i] * 1000 / throughput):
            #         bit_rate = i
            #         break

            # if(S_buffer_size[-1] > self.last_bitrate * 1000 / throughput):
            #     bit_rate = self.last_bitrate
            # else:
            print(S_buffer_size[-50:])
            print(download_id)
            
            if(download_id > 100):
                print(k)

            for i in range(0, 4):
                period = BIT_RATE[i] * 1000 * S_chunk_len[-1] / throughput
                future_buffer = max( S_buffer_size[-1] + S_chunk_len[-1] - period ,0)

                # print(cdn_newest_id, download_id)
                # unit transformation byte -> secs
                frame_len = sum(cdn_has_frame[i])/ (BIT_RATE[i] * 1000)
                frame_len /= (cdn_newest_id - download_id + 1)
                cdn_cumualte = (cdn_newest_id - self.cdn_latest)*frame_len/period
                future_cdn = max((cdn_newest_id - download_id)*frame_len + cdn_cumualte*period - S_chunk_len[-1],0)
                if(future_buffer + future_cdn == 0):
                    bit_rate = i
                    break

        #print(bit_rate)
        self.last_bitrate = bit_rate
        self.cdn_latest = cdn_newest_id
        latency_limit = 3

        return bit_rate, target_buffer, latency_limit

    def get_params(self):
    # get your params
        your_params = [self.last_bitrate]
        return your_params
