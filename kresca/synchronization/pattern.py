import scared as _scared
import numpy as _np
import matplotlib.pyplot as _plt

distance = _scared.signal_processing.distance
correlation = _scared.signal_processing.correlation
bcdc = _scared.signal_processing.bcdc

class PatternSynchronization:

    def __init__(self, 
                 ths,
                 patterns = None,
                 pattern_function = distance,
                 patterns_area = None,
                 patterns_len = None,
                 score_limit = 0,
                 frames = None,
                 preprocesses = [],
                 filtered_output = False,
                 **kwargs,
                 ):
        
        self._ths = ths
        self._patterns = patterns
        self._pattern_function = pattern_function
        self._patterns_area = patterns_area
        self._score_limit = score_limit
        self._preprocesses = preprocesses
        self._filtered_output = filtered_output
        
        if frames == None:
            self._frames = [range(0, len(ths.samples[0]))]
        else:
            self._frames = frames
            
        if patterns_len == None:
            self._patterns_len = list()
            for pattern in patterns:
                self._patterns_len.append((0, len(pattern)))
        else:
            self._patterns_len = patterns_len
                    
        self._result = dict()
    
    def _sync_function(self, trace_object, debug = False):
        
        data_output = _np.zeros((0,))
        
        for index, frame in enumerate(self._frames):
        
            reference_area = trace_object.samples[frame[0]:frame[-1]]
            reference_preprocess = reference_area.copy()

            # apply any preprocess 
            for preprocess in self._preprocesses:
                #  if preprocess filtered output True, use filter for output
                if(preprocess == _scared.signal_processing.butterworth and self._filtered_output == True):
                    reference_area = preprocess(reference_preprocess)
                    reference_preprocess = reference_area.copy()
                else:
                    reference_preprocess = preprocess(reference_preprocess)
            
            pattern = self._patterns[index]
            scores = self._pattern_function(reference_preprocess, pattern)

            if(self._pattern_function == _scared.signal_processing.correlation):
                scores = _np.negative(scores)

            t0 = _np.argmin(scores)

            if(debug == True):
                _plt.figure(figsize=(15, 2))
                _plt.plot(range(len(scores)), scores)
                _plt.scatter(t0, scores[t0], c='red', marker='+', s=100)
                _plt.title(f'Pattern Detection Correlation - Minimum Score {round(scores[t0], 3)}')
                _plt.show()

            if(scores[t0] > self._score_limit):
                raise Exception(f'Minimum score:{round(scores[t0], 3)} greater than Score Limit:{self._score_limit}')

            if(self._patterns_area):
                pattern_area = self._patterns_area[index]
                if(t0 < pattern_area[0] or t0 > pattern_area[-1]):
                    raise Exception(f'Pattern out of area:{t0}')
            
            data_output = _np.append(data_output, reference_area[t0+self._patterns_len[index][0]:t0+self._patterns_len[index][-1]])
            
        return data_output
    
    def check(self, total=5, debug=True):
        synchronization = _scared.synchronization.Synchronizer(
            input_ths = self._ths,
            output = "",
            function = self._sync_function,
            overwrite = True,
            debug = debug,
        )
        data_output = _np.array(synchronization.check(total))
        
        _plt.figure(figsize=(16, 6))
        _plt.plot(data_output.T)
        _plt.title('Synchronization Result')
        _plt.show()
        
    def run(self, path, total=None):
        if(total == None):
            total = len(self._ths)
            
        synchronization = _scared.synchronization.Synchronizer(
            input_ths = self._ths[:total],
            output = path,
            function = self._sync_function,
            overwrite = True,
            debug = False,
        )
        
        synchronization.run()
        print(str(synchronization))
        
    