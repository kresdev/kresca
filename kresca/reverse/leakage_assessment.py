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
                 model=HammingWeight,
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
                model=self._model(),
            )
            reverse.run(container)
            self._result[name] = reverse

    def show_result(self):
        for name, _ in self._selection_functions.items():
            fig, ax = _plt.subplots(figsize=(15, 6))
            ths = self._ths
            ax.plot(self._ths.samples[:int(len(self._ths)/10)].mean(axis=0), color='lightgrey', label='Mean Traces')

            ax_ = ax.twinx() 
            for idx, res in enumerate(self._result[name].results):
                ax_.plot(res, label=f'byte {idx}')
                    
            col_size = self._result[name].results.shape[0] 
            col_size = col_size if col_size < 8 else int(col_size/2)
            
            ax.set_xlabel('Sample Point', fontsize=14)
            ax.set_ylabel('Trace Magnitude', fontsize=14)
            ax_.set_ylabel('Correlation', fontsize=14)

            ax.legend(loc='upper left')
            ax_.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=col_size)
            ax.set_title(f'Leakage Assessment of {name}', fontsize=18)
            _plt.show()