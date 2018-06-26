class Config:
    def parse(file_loc):
        main_data = {}
        with open(file_loc, 'r') as main_file:
            for line in main_file.readlines():
                clean_line = line.replace(" ", "").rstrip()
                if clean_line.startswith('#') or len(clean_line) == 0:
                    continue
                if clean_line.find('=') == -1:
                    raise SyntaxError("Config missing = on a line.")  # Todo: make more informative.
                splitted = clean_line.split("=")
                value = splitted[1]
                if ("'" or '"') in value:
                    value = value[1:len(value - 2)]  # Starting from 2nd charcter->2nd to last
                elif value in ('True', 'False'):
                    if value == 'True':
                        value = True
                    else:
                        value = False
                else:
                    value = int(value[1:])  # removes the space after the =
                main_data[splitted[0]] = value  # Todo: make more robust.
        return main_data
