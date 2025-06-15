import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# Načítanie dát
data = pd.read_csv('predpoved_pocasia.csv', sep=';')

# Úprava typov a čistenie dát
data['hodina'] = data['hodina'].astype(int)
data['mesiac'] = data['mesiac'].astype(int)
data['teplota'] = data['teplota'].astype(int)
data['cas'] = data['cas'].astype(str)
cols_float = ['smer', 'rychlost', 'tlak', 'zrazky', 'oblacnost', 'vlhkost']
for col in cols_float:
    data[col] = pd.to_numeric(data[col], errors='coerce')
data = data.drop(columns=[col for col in data.columns if 'Unnamed' in col])

# Príprava dát pre predikciu zrážok o 13:00 na základe údajov z 8:00
data_8 = data[data['hodina'] == 8].copy().add_suffix('_8')
data_13 = data[data['hodina'] == 13].copy().add_suffix('_13')
merged = pd.merge(
    data_8,
    data_13[['cas_13', 'zrazky_13']],
    left_on='cas_8',
    right_on='cas_13',
    how='inner'
)

features = ['mesiac_8', 'teplota_8', 'smer_8', 'rychlost_8', 'tlak_8', 'oblacnost_8', 'vlhkost_8']
X = merged[features].fillna(0)
y = merged['zrazky_13']

# Škálovanie vstupných dát
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Rozdelenie na trénovaciu a testovaciu množinu
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=212)

# Tréning modelu
model = LinearRegression()
model.fit(X_train, y_train)


def model_predict(vstup):
    # vstup je zoznam: [mesiac, teplota, smer, rychlost, tlak, oblacnost, vlhkost]
    vstup_np = np.array(vstup).reshape(1, -1)
    vstup_scaled = scaler.transform(vstup_np)
    predikovane_zrazky = model.predict(vstup_scaled)[0]
    if predikovane_zrazky < 0:
        predikovane_zrazky = 0.0
    return predikovane_zrazky


if __name__ == "__main__":
    mesiac = int(input("Zadaj mesiac (1-12): "))
    teplota = float(input("Zadaj teplotu o 8:00 [°C]: "))
    smer = float(input("Zadaj smer vetra o 8:00 [stupne]: "))
    rychlost = float(input("Zadaj rýchlosť vetra o 8:00 [m/s]: "))
    tlak = float(input("Zadaj tlak o 8:00 [hPa]: "))
    oblacnost = float(input("Zadaj oblačnosť o 8:00 [%]: "))
    vlhkost = float(input("Zadaj vlhkosť o 8:00 [%]: "))
    vstup = [mesiac, teplota, smer, rychlost, tlak, oblacnost, vlhkost]
    predikovane_zrazky = model_predict(vstup)
    print(f"\nPredikované zrážky o 13:00: {predikovane_zrazky:.2f} mm")
    # Výpočet presnosti na testovacej množine
    # y_pred = model.predict(X_test)
    # mse = mean_squared_error(y_test, y_pred)
    # mae = mean_absolute_error(y_test, y_pred)
    # print(f"Presnosť modelu na testovacej množine: MSE={mse:.3f}, MAE={mae:.3f}")