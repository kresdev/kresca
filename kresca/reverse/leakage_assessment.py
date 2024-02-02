import scared as _scared
import matplotlib.pyplot as _plt

CPAReverse = _scared.CPAReverse
DPAReverse = _scared.DPAReverse
ANNOVAReverse = _scared.ANOVAReverse
MIAReverse = _scared.MIAReverse
SNRReverse = _scared.SNRReverse
NICVReverse = _scared.NICVReverse

HammingWeight = _scared.HammingWeight
Monobit = _scared.Monobit
Value = _scared.Value

class LeakageAssessment:

    def __init__(self, 
                 ths,
                 selection_functions,
                 distinguisher=CPAReverse,
                 model=HammingWeight(),
                 frame=None,
                 preprocesses=[],
                 **kwargs,
                 ):
        
        self._ths = ths
        self._selection_functions = selection_functions
        self._distinguisher = distinguisher
        self._model = model
        self._frame = frame
        self._preprocesses = preprocesses
        
        self._result = dict()

    def run(self):

        for name, sf in self._selection_functions.items():
            print(f"selection_function: {name}")
            self._result[name] = dict()
            container = _scared.Container(self._ths, self._frame, self._preprocesses)
            reverse = self._distinguisher(
                selection_function=sf,
                model=self._model,
            )
            reverse.run(container)
            self._result[name] = reverse

    def show_result(self):
        for name, _ in self._selection_functions.items():
            fig = _plt.figure(figsize=(15, 8))
            gs = fig.add_gridspec(2, hspace=0)
            ax = gs.subplots(sharex=True)
            fig.suptitle(f'Leakage Assessment of {name}', fontsize=18).set_position([0.5, 0.92])

            if(self._frame != None):
                ax[1].plot(self._ths.samples[:int(len(self._ths)/10), self._frame[0]:self._frame[-1]].mean(axis=0), color='lightgrey', label='Mean of Traces')
            else:
                ax[1].plot(self._ths.samples[:int(len(self._ths)/10)].mean(axis=0), color='lightgrey', label='Mean of Traces')

            for idx, res in enumerate(self._result[name].results):
                ax[0].plot(res, label=f'byte {idx}')

            ax[1].set_xlabel('Sample Point', fontsize=14)
            ax[1].set_ylabel('Magnitude', fontsize=14)
            ax[0].set_ylabel('Scores', fontsize=14)

            col_size = self._result[name].results.shape[0] 
            col_size = col_size if col_size < 8 else int(col_size/2)

            ax[1].legend(loc='upper left')
            ax[0].legend(loc='upper center', bbox_to_anchor=(0.5, -1.25), ncol=col_size)

            _plt.show()

    def get_result(self):
        return self._result