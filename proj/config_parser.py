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
                main_data[splitted[0]] = splitted[1]  # Todo: make more robust.
        return main_data
