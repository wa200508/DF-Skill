# SPDX-License-Identifier: Apache-2.0
"""Skill-owned display description. Bindings refer only to received-I/Q results.

The dashboard renders these primitives; it never imports this module or decides
which algorithm/metrics a skill should present. No executable UI code is sent.
"""


def describe_display(arrays):
    sites=arrays['sites']
    names=[site['id'] for site in sites]
    selectors=[{'id':'receiver','label':'Receiver I/Q stream','options':[
        {'value':str(i),'label':name+' · element 0','available':{'path':f'/receiver_spectra/{i}/psd/frequency_khz'}}
        for i,name in enumerate(names)]}]
    panels=[
        {'id':'psd','type':'line','title':'Receiver I/Q spectrum',
         'x':{'data':{'path':'/receiver_spectra/{receiver}/psd/frequency_khz'},'label':'Frequency offset','unit':'kHz'},
         'y':{'label':'PSD','unit':'dB re 1 V²/Hz','range':[-180,-105]},
         'series':{'path':'/receiver_spectra/{receiver}/psd/density_db_v2_hz'},
         'caption':'Selected receiver, element 0; measured post-ADC complex volts.'},
        {'id':'waterfall','type':'waterfall','title':'Receiver I/Q waterfall',
         'x':{'data':{'path':'/receiver_spectra/{receiver}/psd/frequency_khz'},'label':'Frequency offset','unit':'kHz'},
         'y':{'label':'Acquisition windows · newest at top'},
         'rows':{'path':'/waterfall','each':'/site_psd_db/{receiver}'},
         'color':{'label':'PSD','unit':'dB re 1 V²/Hz','range':[-178,-113]},
         'caption':'Received windows only; no interpolation across missing data.'},
        {'id':'bearings','type':'metrics','title':'Direction-finding candidates','items':[
            item for i,name in enumerate(names) for item in (
                {'label':name+' bearing','value':{'path':f'/bearings/{i}/angle_deg'},'unit':'°','precision':1,
                 'valid_when':{'path':f'/bearings/{i}/detected'},'empty':'No stable MUSIC peak'},
                {'label':name+' received power','value':{'path':f'/bearings/{i}/received_power_dbm'},'unit':'dBm','precision':1})],
         'caption':'A candidate is not proof of an unambiguous emitter bearing. A linear array retains front/back and elevation ambiguity.'},
        {'id':'spatial','type':'polar','title':'MUSIC spatial search',
         'x':{'data':{'path':'/angle_grid_deg'},'label':'Azimuth from array broadside','unit':'°','period':360},
         'y':{'label':'Pseudospectrum','unit':'dB','range':[-65,0],'ticks':[-40,-20,0]},
         'series':{'path':'/music_db'},'legend':names,
         'caption':'Full-circle display; 0° is array broadside. Multipath peaks can be echoes.'},
        {'id':'eigen','type':'line','title':'Covariance eigenvalues',
         'x':{'index_start':1,'label':'Eigenvalue rank'},'y':{'label':'Relative power','unit':'dB','range':[-60,0]},
         'series':{'path':'/eigenvalues_db'},'legend':names,'points':True},
        {'id':'phase','type':'line','title':names[0]+' relative element phase',
         'x':{'index_start':0,'label':'Element index'},'y':{'label':'Phase','unit':'rad','range':[-9,9]},
         'series':{'path':'/phase_rad'},'points':True,
         'caption':'Ideal clock and array phase calibration; up to 24,000 simultaneous ADC samples per analysis.'}]
    return {'schema_version':1,'id':'direction-finding-rf-skill','revision':'1',
            'title':'Direction Finding RF Skill','selectors':selectors,'panels':panels,'histories':[{
                'key':'waterfall','limit':60,'row':{'timestamp_ns':{'path':'/timestamp_ns'},
                'psd_db':{'path':'/psd/density_db_v2_hz'},
                'site_psd_db':{'path':'/receiver_spectra','each':'/psd/density_db_v2_hz'}}}]}
