# coding=cp936
import csv
import numpy as np
from base import data_path, work_path
from odbAccess import openOdb


def get_urf_data(odb, csv_path='', pad0_name='PADL', pad1_name='PADR', beam_name='BEAM1'):
    rf0 = None
    rf1 = None
    u3 = None
    for step in odb.steps.values():
        for hr in step.historyRegions.keys():
            data = step.historyRegions[hr].historyOutputs.values()[0].data
            data = np.array(data)
            if pad0_name in hr:
                if rf0 is not None:
                    rf0 = np.concatenate((rf0, data))
                else:
                    rf0 = data
            if pad1_name in hr:
                if rf1 is not None:
                    rf1 = np.concatenate((rf1, data))
                else:
                    rf1 = data
            if beam_name in hr:
                if u3 is not None:
                    u3 = np.concatenate((u3, data))
                else:
                    u3 = data
    rf = rf0 + rf1
    if csv_path != '':
        with open(csv_path, mode='w') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow(['U', 'RF'])
            u3 = -u3[:, 1]
            rf = rf[:, 1]
            writer.writerows(np.column_stack([u3, rf]))

    return u3, rf


if __name__ == '__main__':
    path0 = work_path + '/' + 'Job-SimplyBeam0.odb'
    path1 = work_path + '/' + 'Job-SimplyBeam1.odb'
    path2 = work_path + '/' + 'Job-SimplyBeam2.odb'

    odb0 = openOdb(path0)
    odb1 = openOdb(path1)
    odb2 = openOdb(path2)
    get_urf_data(odb0, csv_path=data_path + '/' + 'SimplyBeam0_URF.csv')
    get_urf_data(odb1, csv_path=data_path + '/' + 'SimplyBeam1_URF.csv')
    get_urf_data(odb2, csv_path=data_path + '/' + 'SimplyBeam2_URF.csv')
    odb0.close()
    odb1.close()
    odb2.close()
