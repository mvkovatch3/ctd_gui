from pathlib import Path
import pandas as pd


def load_ct1(dir=None, ssscc_list=None):

    # load continuous CTD data and make into a dict
    file_list = sorted(Path(dir).glob("*_ct1*"))
    if ssscc_list:
        breakpoint()
    ctd_data = []
    for f in file_list:
        df = pd.read_csv(f, header=12, skiprows=[13], skipfooter=1, engine="python")
        df["SSSCC"] = f.stem[:5]
        ctd_data.append(df)
    ctd_data = pd.concat(ctd_data, axis=0, sort=False)

    return ctd_data


def load_pkl(dir=None, ssscc_list=None):

    file_list = sorted(Path(dir).glob("*.pkl"))
    if ssscc_list:
        breakpoint()
    upcast_data = []
    for f in file_list:
        df = pd.read_pickle(f)
        df["SSSCC"] = f.stem[:5]
        # change to secondary if that is what's used
        upcast_data.append(df[["SSSCC", "CTDCOND1", "CTDTMP1", "CTDPRS"]])
    upcast_data = pd.concat(upcast_data, axis=0, sort=False)

    return upcast_data


def load_salt(dir=None, ssscc_list=None):

    file_list = sorted(Path(dir).glob("*.csv"))
    if ssscc_list:
        breakpoint()
    salt_data = []
    for f in file_list:
        df = pd.read_csv(f, usecols=["STNNBR", "CASTNO", "SAMPNO", "SALNTY"])
        df["SSSCC"] = f.stem[:5]
        salt_data.append(df)
    salt_data = pd.concat(salt_data, axis=0, sort=False)

    return salt_data
