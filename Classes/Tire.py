class Tire:
    def __init__(self, 
                 wearL=[], pressure=[], tempM=[], tempL=[], tiresUsed=[], 
                 tempCL=[], brakeLinePress=[], shockDefl=[], tempCR=[], tempCM=[], 
                 tempR=[], coldPressure=[], rideHeight=[], shockVel=[], speed=[], 
                 wearM=[], wearR=[], rumblePitch=[]):
        self.wearL = wearL
        self.pressure = pressure
        self.tempM = tempM
        self.tempL = tempL
        self.tiresUsed = tiresUsed
        self.tempCL = tempCL
        self.brakeLinePress = brakeLinePress
        self.shockDefl = shockDefl
        self.tempCR = tempCR
        self.tempCM = tempCM
        self.tempR = tempR
        self.coldPressure = coldPressure
        self.rideHeight = rideHeight
        self.shockVel = shockVel
        self.speed = speed
        self.wearM = wearM
        self.wearR = wearR
        self.rumblePitch = rumblePitch

    def get_value_at(self, index, default=0):
        return {
            'wearL': self.wearL[index] if index < len(self.wearL) else default,
            'pressure': self.pressure[index] if index < len(self.pressure) else default,
            'tempM': self.tempM[index] if index < len(self.tempM) else default,
            'tempL': self.tempL[index] if index < len(self.tempL) else default,
            'tiresUsed': self.tiresUsed[index] if index < len(self.tiresUsed) else default,
            'tempCL': self.tempCL[index] if index < len(self.tempCL) else default,
            'brakeLinePress': self.brakeLinePress[index] if index < len(self.brakeLinePress) else default,
            'shockDefl': self.shockDefl[index] if index < len(self.shockDefl) else default,
            'tempCR': self.tempCR[index] if index < len(self.tempCR) else default,
            'tempCM': self.tempCM[index] if index < len(self.tempCM) else default,
            'tempR': self.tempR[index] if index < len(self.tempR) else default,
            'coldPressure': self.coldPressure[index] if index < len(self.coldPressure) else default,
            'rideHeight': self.rideHeight[index] if index < len(self.rideHeight) else default,
            'shockVel': self.shockVel[index] if index < len(self.shockVel) else default,
            'speed': self.speed[index] if index < len(self.speed) else default,
            'wearM': self.wearM[index] if index < len(self.wearM) else default,
            'wearR': self.wearR[index] if index < len(self.wearR) else default,
            'rumblePitch': self.rumblePitch[index] if index < len(self.rumblePitch) else default
        }
    
    def assign_df(self, df, headerlist):
        self.wearL = df[headerlist[0]].astype(float).values.tolist()
        self.pressure = df[headerlist[1]].values.tolist()
        self.tempM = df[headerlist[2]].values.tolist()
        self.tempL = df[headerlist[3]].values.tolist()
        self.tiresUsed = df[headerlist[4]].values.tolist()
        self.tempCL = df[headerlist[5]].values.tolist()
        self.brakeLinePress = df[headerlist[6]].values.tolist()
        self.shockDefl = df[headerlist[7]].values.tolist()
        self.tempCR = df[headerlist[8]].values.tolist()
        self.tempCM = df[headerlist[9]].values.tolist()
        self.tempR = df[headerlist[10]].values.tolist()
        self.coldPressure = df[headerlist[11]].values.tolist()
        self.rideHeight = df[headerlist[12]].values.tolist()
        self.shockVel = df[headerlist[13]].values.tolist()
        self.speed = df[headerlist[14]].values.tolist()
        self.wearM = df[headerlist[15]].astype(float).values.tolist()
        self.wearR = df[headerlist[16]].astype(float).values.tolist()
        self.rumblePitch = df[headerlist[17]].values.tolist()

    def get_wear(self, index):
        return {
            'wearL': self.wearL[index] if index < len(self.wearL) else 0.0,
            'wearM': self.wearM[index] if index < len(self.wearM) else 0.0,
            'wearR': self.wearR[index] if index < len(self.wearR) else 0.0
        }

    def print_values_at_index(self, index):
        values = self.get_value_at(index)
        print(f"Values at index {index}:")
        for key, value in values.items():
            print(f"{key}: {value}")

    def __repr__(self):
        return (f"Tire(wearL={self.wearL}, pressure={self.pressure}, tempM={self.tempM}, "
                f"tempL={self.tempL}, tiresUsed={self.tiresUsed}, tempCL={self.tempCL}, "
                f"brakeLinePress={self.brakeLinePress}, shockDefl={self.shockDefl}, "
                f"tempCR={self.tempCR}, tempCM={self.tempCM}, tempR={self.tempR}, "
                f"coldPressure={self.coldPressure}, rideHeight={self.rideHeight}, "
                f"shockVel={self.shockVel}, speed={self.speed}, wearM={self.wearM}, "
                f"wearR={self.wearR}, rumblePitch={self.rumblePitch})")