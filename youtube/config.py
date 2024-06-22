import tomllib

class Config:
    def __init__(self, filepath):
        with open(filepath, 'rb') as f:
            data = tomllib.load(f)
        self.channels = data['channels']['folder_filepath']
        self.cycle = _Cycle(data['cycle'])
        self.ytarchive = data['ytarchive']['filepath']
        self.output = _Output(data['ytarchive'], data['output'])
        self.webhook = data['discord']['webhook']
        self.logging = data['logging']['directory'] if data['logging']['enabled'] else False

    def __str__(self) -> str:
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        return str(self.__dict__)

class _Cycle:
    def __init__(self, data: dict):
        self.mod = data['mod_factor']
        self.interval = data['interval']
        self.format = data['time_format']
        self.log_day = data['log_day_change']

class _Output:
    def __init__(self, yt: dict, out: dict) -> None:
        self.path = out['directory']
        self.directory = out['directory'] + out['format']['style']
        self.quality = out['format']['quality']

        args = []
        if yt['merge']: args.append('--merge')
        if out['format']['mkv']: args.append('--mkv')
        args.extend([f'--{yt["debug_level"]}', '-r', str(yt['retry_stream']), '--retry-frags', str(yt['retry_frag'])])
        
        tb = out['thumbnail']
        if tb['embed']: args.append('--thumbnail')
        if tb['separate']: args.append('--write-thumbnail')
        
        md = out['metadata']
        if md['embed']: args.append('--add-metadata')
        if md['separate']: args.append('--write-description')
        
        args.extend(['-o', self.directory])
        self.args = args

    def __str__(self) -> str:
        return str(self.__dict__)
    
    def __repr__(self) -> str:
        return str(self.__dict__)