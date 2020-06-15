import numpy as np

#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings
TARGET_BUFFER = [0.5 , 1.0]
BIT_RATE = [500.0,850.0,1200.0,1850.0]
class Algorithm:
    def __init__(self):
    # fill your self params
        self.buffer_size = 0
        self.last_bitrate = 0
        self.cdn_latest = 0
        self.cdn_last_id = -1

    # Intial
    def Initial(self):
    # Initail your session or something
        return self.get_params()

    def reset(self):
        self.last_bitrate = 0
        self.cdn_latest = 0
        self.cdn_last_id = -1

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
        target_buffer, play_rate = self.playback(S_buffer_size[-1])

        # negative number of frames in GOP
        frame_num = self.cdn_last_id - download_id
        bit_rate = 0

        if(end_of_video):
            self.reset()
        else:
            throughput = np.sum(S_send_data_size[-1]) / np.sum(S_time_interval[-1])
            # print(throughput)
            #throughput = np.average(S_send_data_size[frame_num:]) / np.average(S_time_interval[frame_num:])
            # print(throughput)
            for i in range(2, -1, -1):
                if(S_buffer_size[-1] > BIT_RATE[i] * 1000 / throughput):
                    bit_rate = i+1
                    break

            # print(S_chunk_len[frame_num:])
            #print(download_id)
            
            # if(download_id > 1000):
            #     print(k)

            # for i in range(1, 4):
            #     period = BIT_RATE[i] * 1000 * np.sum(S_chunk_len[frame_num:]) / throughput
            #     buffer_occupancy = S_buffer_size[-1] + np.sum(S_chunk_len[frame_num:]) - play_rate * period
            #     buffer_occupancy = max( buffer_occupancy, 0)

            #     # unit transformation byte -> secs
            #     frame_len = np.sum(cdn_has_frame[i])/ (BIT_RATE[i] * 1000)
            #     frame_len /= (cdn_newest_id - download_id + 1)
            #     cdn_cumualte = (cdn_newest_id - self.cdn_latest)*frame_len/period
            #     cdn_latency = (cdn_newest_id - download_id)*frame_len + cdn_cumualte*period - np.sum(S_chunk_len[frame_num:])
            #     cdn_latency = max(cdn_latency, 0)
            #     if(buffer_occupancy + cdn_latency == 0):
            #         bit_rate = i
            #         break        
        latency_limit = self.frame_drop(bit_rate, S_chunk_len[-1], S_end_delay[-1])
        #print(latency_limit)

        #print(bit_rate)
        self.last_bitrate = bit_rate
        self.cdn_latest = cdn_newest_id
        self.cdn_last_id = download_id
        # latency_limit = 3

        return bit_rate, target_buffer, latency_limit

    def get_params(self):
    # get your params
        your_params = [self.last_bitrate]
        return your_params
