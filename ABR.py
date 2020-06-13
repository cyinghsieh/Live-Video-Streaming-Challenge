# import tensorflow as tf

#NN_MODEL = "./submit/results/nn_model_ep_18200.ckpt" # model path settings
TARGET_BUFFER = [0.5 , 1.0]
BIT_RATE = [500.0,850.0,1200.0,1850.0]
class Algorithm:
    def __init__(self):
    # fill your self params
        self.buffer_size = 0

    # Intial
    def Initial(self):
    # Initail your session or something

    # restore neural net parameters
        self.buffer_size = 0


    #Define your al
    def run(self, time, S_time_interval, S_send_data_size, S_chunk_len, S_rebuf, S_buffer_size, S_play_time_len,S_end_delay, S_decision_flag, S_buffer_flag,S_cdn_flag,S_skip_time, end_of_video, cdn_newest_id,download_id,cdn_has_frame,IntialVars):
        # If you choose BBA
        if(S_time_interval[-1] != 0):
            throughput = S_send_data_size[-1] / S_time_interval[-1]
            for i in range(3, -1, -1):
                if(S_buffer_size[-1] > BIT_RATE[i] / throughput):
                    bit_rate = i
        else:
            bit_rate = 0

        target_buffer = 0
        latency_limit = 5

        return bit_rate, target_buffer, latency_limit

    def get_params(self):
    # get your params
        your_params = []
        return your_params
