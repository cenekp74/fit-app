print('Starting the app...')

import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from fit_from_string import fit_from_str
import json

matplotlib.use('TkAgg')

class App:
    def __init__(self) -> None:
        sg.theme('BlueMono')
        self.load_settings()
        try:
            self.load_data()
        except Exception as e:
            print(f"Failed to load data - {e}")
            sg.Popup(f"Failed to load data - {e}\n The data should be in a csv, where first column in x data and second is the corresponding y data. The data has to be separated by ; and there can't be any headers")
        self.layout = [
                    [sg.Text('Data path:'), sg.Input(default_text=self.settings["data_path"], size=(
                        50, 1), enable_events=True, key='-DATA_PATH-'), sg.FileBrowse()],
                    [sg.HorizontalSeparator()],
                    [sg.Text("Enter Equation:")],
                    [sg.InputText(key='-EQUATION-'), sg.Button('Add equation', key='-ADD_EQUATION-')],
                    [sg.HorizontalSeparator()],
                    [sg.Listbox(self.settings["equations"], key='-EQUATION_SELECT-', size=(30, 10)), sg.Button('Calculate parameters', key='-CALCULATE-'), sg.Button('Plot', key='-PLOT-'), sg.Button('Remove', key='-REMOVE-')],
                    [sg.Text('Plot scale:'), sg.Combo(['log', 'linear', 'symlog', 'logit'], readonly=True, key='-SCALE-', enable_events=True, default_value=self.settings["scale"])]
                ]
        self.window = sg.Window('Aproximace spektra kapek',
                                self.layout,
                                size=(self.settings["window_size_x"],
                                      self.settings["window_size_y"]),
                                finalize=True,
                                resizable=True
                                )
    def dump_settings(self):
        json.dump(self.settings, open('settings.json', 'w'), indent=4)
    def load_settings(self):
        try:
            self.settings = json.load(open('settings.json', 'r'))
        except Exception as e:
            print('settings.json not found - creating new')
            self.settings = {
                "window_size_x":600,
                "window_size_y":400,
                "data_path":"data.csv",
                "equations":["a*x**b*exp(-c*x)", "a*x**b*exp(-c*x)|m*exp(-k*x)", "a*x**b*exp(-c*x)|m*exp(-k*x)|0.6;3.6"],
                "scale":"log"
            }
            self.dump_settings()
        return self.settings
    
    def load_data(self):
        def load():
            self.x_data = []
            self.y_data = []
            with open(self.settings["data_path"], 'r') as f:
                for line in f.readlines():
                    self.x_data.append(float(line.split(';')[0]))
                    self.y_data.append(float(line.split(';')[1]))
            self.x_data = np.array(self.x_data)
            self.y_data = np.array(self.y_data)
        try:
            load()
            print("Data loaded succesfully")
        except Exception as e:
            print(f"Failed to load data - {e}")
            sg.Popup(f"Failed to load data - {e}\n The data should be in a csv, where first column in x data and second is the corresponding y data. The data has to be separated by ; and there can't be any headers. X data and y data have to be of the same length. ")
        

    def run(self) -> None:
        self.window.bind('<Configure>', "Configure")
        while True:
            self.event, self.values = self.window.read(timeout=200)
            if self.event == sg.WIN_CLOSED or self.event == 'Exit':
                break

            elif self.event == 'Configure':
                self.settings["window_size_x"] = self.window.size[0]
                self.settings["window_size_y"] = self.window.size[1]
                self.dump_settings()

            elif self.event == '-DATA_PATH-':
                self.settings['data_path'] = self.values['-DATA_PATH-']
                self.dump_settings()
                self.load_data()

            elif self.event == '-SCALE-':
                self.settings['scale'] = self.values['-SCALE-']
                self.dump_settings()

            elif self.event == '-ADD_EQUATION-':
                equation = self.values['-EQUATION-'].replace('^', '**')
                try:
                    fit_from_str(equation, self.x_data, self.y_data)
                except Exception as e:
                    sg.Popup(f"Invalid equation - {e}")
                    continue
                self.settings["equations"].append(equation)
                self.dump_settings()
                self.window['-EQUATION_SELECT-'].update(self.settings["equations"])
                sg.Popup(f"Equation added succesfully")

            elif self.event == '-CALCULATE-':
                if len(self.values['-EQUATION_SELECT-']) == 0: continue
                selected_equation = self.values['-EQUATION_SELECT-'][0]
                fit = fit_from_str(selected_equation, self.x_data, self.y_data)
                fit_result = fit.execute()
                sg.popup_non_blocking(fit_result, title='Fit result')

            elif self.event == '-PLOT-':
                if len(self.values['-EQUATION_SELECT-']) == 0: continue
                selected_equation = self.values['-EQUATION_SELECT-'][0]
                fit = fit_from_str(selected_equation, self.x_data, self.y_data)
                fit_result = fit.execute()
                sg.popup_non_blocking(fit_result, title='Fit result')
                plt.scatter(self.x_data, self.y_data)
                plt.plot(self.x_data, fit.model(x=self.x_data, **fit_result.params).y)
                plt.yscale(self.settings["scale"])
                plt.show()
            
            elif self.event == '-REMOVE-':
                if len(self.values['-EQUATION_SELECT-']) == 0: continue
                selected_equation = self.values['-EQUATION_SELECT-'][0]
                self.settings["equations"].remove(selected_equation)
                self.dump_settings()
                self.window['-EQUATION_SELECT-'].update(self.settings["equations"])
                sg.Popup(f"Equation removed succesfully")
                
def main():
    app = App()
    app.run()

if __name__ == '__main__':
    main()


# x_data = np.arange(0.1, 3.9, 0.2)
# y_data = [15.18, 262.94, 337.03, 319.32, 211.86, 100.82, 39.35, 15.52, 7.70, 3.38, 1.83, 0.95, 0.52, 0.23, 0.12, 0.07, 0.04, 0.02, 0.01]

# while True:
#     event, values = window.read()

#     if event == sg.WIN_CLOSED:
#         break
#     elif event == 'Create Function':
#         equation = values['-EQUATION-']
#         result_elem = window['-RESULT-']

#         try:
#             fit = fit_from_str(equation, x_data, y_data)
#         except Exception as e:
#             result_elem.update(value=f"Invalid equation - {e}")
#             continue
        

# window.close()