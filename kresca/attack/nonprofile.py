import scared as _scared
import pandas as _pd
import numpy as _np
import matplotlib.pyplot as _plt
from ipywidgets import Button as _Button
from ipywidgets import HBox as _HBox
from ipywidgets import Output as _Output
from ipywidgets import Layout as _Layout
from IPython.display import clear_output as _clear_output

CPAAttack = _scared.CPAAttack
DPAAttack = _scared.DPAAttack
ANNOVAAttack = _scared.ANOVAAttack
MIAAttack = _scared.MIAAttack
SNRAttack = _scared.SNRAttack
NICVAttack = _scared.NICVAttack

HammingWeight = _scared.HammingWeight
Monobit = _scared.Monobit
Value = _scared.Value

maxabs = _scared.maxabs
nanmax = _scared.nanmax

class NonProfileAttack:

    def __init__(self, 
                 ths,
                 selection_functions,
                 distinguisher=CPAAttack,
                 model=HammingWeight(),
                 discriminant=maxabs,
                 frame=None,
                 preprocesses=[],
                 **kwargs,
                 ):
        
        self._ths = ths
        self._selection_functions = selection_functions
        self._distinguisher = distinguisher
        self._model = model
        self._discriminant = discriminant
        self._frame = frame
        self._preprocesses = preprocesses
        
        self._result = dict()
        self._convstep = int(len(ths)/10)
        
    def run(self):
        
        for name, sf in self._selection_functions.items():
            print(f"selection_function: {name}")
            self._result[name] = dict()
            container = _scared.Container(self._ths, self._frame, self._preprocesses)
            attack = self._distinguisher(
                selection_function=sf,
                model=self._model,
                discriminant=self._discriminant,
                convergence_step=self._convstep,
            )
            attack.run(container)
            self._result[name][''] = attack
        
    def report(self):
        
        for name, area in self._result.items():
            for name_2, attack in area.items():
                
                try:
                    expected_key = attack.selection_function.expected_key_function(self._ths.metadatas[attack.selection_function.key_tag][0])
                except:
                    if(attack.selection_function.expected_key_function is not None):
                        expected_key = attack.selection_function.expected_key_function(self._ths.metadatas['key'][0])
                    else:
                        expected_key = None
                found_bytes = attack.scores.argmax(axis=0)
                len_bytes = len(found_bytes)
                len_guesses = len(attack.scores)
                rank = list()

                if expected_key is not None:
                    df = _pd.DataFrame(columns=[i for i in range(len_bytes)], index=['Scores','Found Bytes','Expected', 'Rank'])
                    
                    for i in range(len_bytes):
                        rank.append(int(len_guesses-1-_np.where(_np.argsort(attack.scores[:, i]) == expected_key[i])[0][0]))
                else:
                    df = _pd.DataFrame(columns=[i for i in range(len_bytes)], index=['Scores','Found Bytes'])

                df.loc['Scores'] = _np.round(_np.max(attack.scores, axis=0), 3)
                df.loc['Found Bytes'] = [hex(n) for n in found_bytes]

                if expected_key is not None:
                    df.loc['Expected'] = [hex(n) for n in expected_key]
                    df.loc['Rank'] = rank
                
                    idx = _pd.IndexSlice
                    found_list = idx[idx['Found Bytes':'Found Bytes',
                                        [n for n in range(len_bytes) if df.loc['Found Bytes'][n] == df.loc['Expected'][n]]]]
                    unfound_list = idx['Found Bytes':'Found Bytes', 
                                      [n for n in range(len_bytes) if df.loc['Found Bytes'][n] != df.loc['Expected'][n]]]

                df = df.style.set_table_attributes("style='display:inline'")
                df = df.format(lambda val: f"{val:.3f}" if isinstance(val, (float)) else val)
                df = df.set_table_attributes('style="font-size: 15px"')
                df = df.set_caption(f"{name} {name_2}")
                df = df.set_table_styles([{
                    'selector': 'caption',
                    'props': [('text-align', 'center')]
                }])
                if expected_key is not None:
                    df = df.map(lambda val: 'color: %s' % 'green', subset=found_list)
                    df = df.map(lambda val: 'color: %s' % 'red', subset=unfound_list)
                
                display(df)
    
    def _show_result(self, attack):
        _plt.rcParams['figure.figsize']=(22, 7)

        try:
            expected_key = attack.selection_function.expected_key_function(self._ths.metadatas[attack.selection_function.key_tag][0])
        except:
            if(attack.selection_function.expected_key_function is not None):
                expected_key = attack.selection_function.expected_key_function(self._ths.metadatas['key'][0])
            else:
                expected_key = None
                
        found_bytes = attack.scores.argmax(axis=0)
        len_bytes = len(found_bytes)
        len_guesses = len(attack.scores)

        switch = [_Button(description=str(name)) for name in range(len_bytes)]
        combined = _HBox([items for items in switch])
        out = _Output(layout = _Layout(height='400px'))
        len_conv = attack.convergence_traces[:, 0,:].shape[-1]
        x_step = _np.arange(self._convstep, (self._convstep*(len_conv+1)), self._convstep)

        def upon_clicked(btn):
            byte_selected = int(btn.description)

            with out:
                _clear_output()
                _plt.subplot(121)
                _plt.title('Attack Result - Byte ' + str(byte_selected), fontsize=20)
                _plt.xlabel('Sample Point', fontsize=14)
                _plt.ylabel('Correlation Scores', fontsize=14)

                _plt.plot(attack.results[1, byte_selected, :], 'lightgrey', label='Wrong Guesses')
                _plt.plot(attack.results[1:, byte_selected, :].T, 'lightgrey')

                if expected_key is not None:
                    if(found_bytes[byte_selected] == expected_key[byte_selected]):
                        _plt.plot(attack.results[:, byte_selected, :][expected_key[byte_selected]], 'green', label='Expected Key')
                    else:
                        _plt.plot(attack.results[:, byte_selected, :][found_bytes[byte_selected]], 'red', label='Found Key')
                        _plt.plot(attack.results[:, byte_selected, :][expected_key[byte_selected]], 'blue', label='Expected Key')
                else:
                    _plt.plot(attack.results[:, byte_selected, :][found_bytes[byte_selected]], 'blue', label='Found Key')
                    
                _plt.legend(loc=3, fontsize=12);

                # Plotting the convergence scores for byte 15

                _plt.subplot(122)
                _plt.title('Convergence Scores - Byte ' + str(byte_selected), fontsize=20)
                _plt.xlabel('Number of traces/Convergence Step', fontsize=14)
                _plt.ylabel('Correlation Scores', fontsize=14)
                if (attack.convergence_traces.all() != None):

                    _plt.plot(x_step, attack.convergence_traces[1, byte_selected,:], 'lightgrey', label='Wrong Guesses')
                    _plt.plot(x_step, attack.convergence_traces[1:, byte_selected,:].T, 'lightgrey')

                    if expected_key is not None:
                        
                        if(found_bytes[byte_selected] == expected_key[byte_selected]):
                            _plt.plot(x_step, attack.convergence_traces[:, byte_selected,:][expected_key[byte_selected]], 'green', label='Expected Key')
                        else:
                            _plt.plot(x_step, attack.convergence_traces[:, byte_selected,:][found_bytes[byte_selected]], 'red', label='Found Key')
                            _plt.plot(x_step, attack.convergence_traces[:, byte_selected,:][expected_key[byte_selected]], 'blue', label='Expected Key')
                    else:
                        _plt.plot(x_step, attack.convergence_traces[:, byte_selected,:][found_bytes[byte_selected]], 'blue', label='Found Key')

                _plt.legend(loc=3, fontsize=12);
                _plt.show()

            for n in range(len_bytes):
                switch[n].style.button_color = '#F4F6F6'
            btn.style.button_color = '#5DADE2'

        for n in range(len_bytes):
            switch[n].on_click(upon_clicked)

        display(combined)
        display(out)
        
    def show_result(self):
        
        for name, area in self._result.items():
            for name_2, attack in area.items():
                print(f" {name} {name_2} ".center(100, "="))
                self._show_result(attack)
    
    def get_result(self):
        return self._result
        