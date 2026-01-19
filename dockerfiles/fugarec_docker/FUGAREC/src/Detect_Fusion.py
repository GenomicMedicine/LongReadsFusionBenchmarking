#!/usr/bin/env python
# coding: utf-8
import sys
root = sys.argv[1]
TARGET=sys.argv[2] #TARGET="MCF7"
reference_data_path=sys.argv[3]
genome_name=sys.argv[4] #"hg38"
gtf_name=sys.argv[5] #"genCode44"

# root = "/data2/chimericRNA_detection/datasets/real_data/K562"
# TARGET="MCF7" #TARGET="MCF7"
# reference_data_path="/data2/chimericRNA_detection/code/Reference_data"
# genome_name="hg38" #"hg38"
# gtf_name="genCode44" #"genCode44"

mapping_rate_criteria_trans=0.99
buffer=15
Nth_hit_buffer=50
unpaired_mapping_rate=0.95
mapping_gap_rate=0.5
mapping_gap_len_criteria=10000
clst_percent_cutoff=0.5
clst_bp=1000

realign_gap_len_criteria=15
gap_len_cutoff=15

gap_mapping_rate_cutoff=0.5
gap_evalue_cutoff=0.05
buffer=15


# ## 関数のインポート

# In[2]:


import pandas as pd
import numpy as np
import math
from tqdm import tqdm_notebook as tqdm
import re
import os
from tqdm import tqdm
tqdm.pandas()
from pathlib import Path
import itertools
from collections import Counter
from glob import glob 
#import matplotlib.pyplot as plt
#import collections
#mport pandas_bj
#sns.set_context('notebook')
#!jupyter nbextension enable --py --sys-prefix widgetsnbextension

import warnings
warnings.simplefilter('ignore')
# pd.set_option('display.max_columns', 50)


# In[3]:


def my_round_int(x): return int((x * 2 + 1) // 2)

def rm_cross_over(df_fusioncand,buffer=buffer):
    df_A = df_fusioncand[df_fusioncand["chr1"] !=df_fusioncand["chr2"]]  # 同じ染色体ではないのでクロスオーバーの対象外
    tmp = df_fusioncand[df_fusioncand["chr1"] == df_fusioncand["chr2"]]
    drop1 = tmp.query('start1<start2 and end1>end2')
    drop2 = tmp.query('start1>start2 and end1<end2')
    drop_rid=list(drop1['hit_rid'])+list(drop1['hit_rid'])

    df_B_a = tmp[(tmp["end1"] - tmp["start2"] - buffer) *
                 (tmp["end2"] - tmp["start1"] - buffer) < 0]
    df_B_b = tmp[(tmp["end1"] - tmp["start2"] - buffer) *
                 (tmp["end2"] - tmp["start1"] - buffer) < 0]

    df_fusioncand_rmcross = pd.concat([df_A, df_B_a, df_B_b])
    df_fusioncand_rmcross = df_fusioncand_rmcross.drop_duplicates()
    df_fusioncand_rmcross.query('hit_rid not in @drop_rid')
    #print('クロスオーバーで除く本数は{}本'.format(df_fusioncand.shape[0] - df_fusioncand_rmcross.shape[0]))
    return df_fusioncand_rmcross,drop_rid

def judge_cross_over_v3(mmap2_paired,buffer,s,e):
    ##print('クエリ側のクロスオーバーの判定')
    rids=[]
    if mmap2_paired['Nth_hit'].value_counts()[1] != mmap2_paired['Nth_hit'].value_counts()[2]:
        drop_rid_nopaired = pd.DataFrame(mmap2_paired.groupby('Qname')['Nth_hit'].nunique() == 1).query('Nth_hit==True').index
        mmap2_paired = mmap2_paired.query('Qname not in @drop_rid_nopaired')
    for x,rid in enumerate(tqdm(mmap2_paired.Qname.unique())): #read_idごと
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        N=mmap2_paired_sub.Nth_hit.min()
        first_end_pos = int(mmap2_paired_sub.query('Nth_hit==@N')[e].max())
        try:
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit==@N+1')[s].min())
        except:
            assert mmap2_paired_sub['Nth_hit'].nunique()==2 ,'Nth_hitが3以上です'
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit!=@N')[s].min())
        if first_end_pos - buffer > second_start_pos:
            rids.append(rid)
    return rids
    


def cul_mapping_rate_all(df):
    df_tmp = df.copy()
    df_tmp['map_len'] = df_tmp.apply(lambda x: x['Qend']-x['Qstart'], axis=1)
    df_tmp=df_tmp.drop_duplicates(['Qname','Nth_hit'])
    mapping_rate_all = df_tmp.groupby(['Qname']).agg({'map_len': 'sum', 'Qlen': 'max'}).apply(lambda x: x['map_len']/x['Qlen'], axis=1)
    add_df = pd.DataFrame(mapping_rate_all, columns=['mapping_rate_all']).reset_index()
    df_out = pd.merge(df, add_df)
    return df_out

def cul_mapping_GAP(df):
    df_tmp = df.copy()
    df_tmp['map_len'] = df_tmp.apply(lambda x: x['Qend']-x['Qstart'], axis=1)
    df_tmp=df_tmp.drop_duplicates(['Qname','Nth_hit'])
    mapping_gap = df_tmp.groupby(['Qname']).agg({'Qend': 'min', 'Qstart': 'max'}).apply(lambda x: x['Qstart']-x['Qend'], axis=1)
    add_df = pd.DataFrame(mapping_gap, columns=['mapping_gap']).reset_index()
    df_out = pd.merge(df, add_df)
    return df_out


def get_gene_name_start_end(gtf,chr,s,e,buffer=15):
    gtf['len']=gtf['end']-gtf['start']
    multi_hit_flg=0
    gtf_sub1=gtf.query('chr==@chr & start-@buffer <= @s <= end + @buffer and chr==@chr & start-@buffer <= @e <= end+@buffer') #gtfの中にstart,endともに張り付いている
    if len(gtf_sub1) >= 1:
        gtf_sub1= gtf_sub1.sort_values('len',ascending=False)
        g_tmp = gtf_sub1['gene'].unique()
        g_multi="||".join(g_tmp)
        #g=g_tmp[0]
        if len(g_tmp) > 1:
            multi_hit_flg=1
            g_multi="||".join(g_tmp)
    else:
        gtf_sub2=gtf.query('chr==@chr & start-@buffer <= @s <= end+@buffer') #gtfの中にstartのみ張り付いている
        gtf_sub3=gtf.query('chr==@chr & start-@buffer <= @e <= end+@buffer') #gtfの中にendのみ張り付いている
        if len(gtf_sub2)>=1: 
            gtf_sub2= gtf_sub2.sort_values('len',ascending=False)
            g_tmp = gtf_sub2['gene'].unique()
            g_multi="||".join(g_tmp)
            #g=g_tmp[0]
            if len(g_tmp) > 1:
                multi_hit_flg=1
        elif len(gtf_sub3)>=1: 
            gtf_sub3= gtf_sub3.sort_values('len',ascending=False)
            g_tmp = gtf_sub3['gene'].unique()
            g_multi="||".join(g_tmp)
            #g=g_tmp[0]
            if len(g_tmp)>1:
                multi_hit_flg=1
        else:
            #g='no_hit'
            g_multi='intron'
        
    return pd.Series(g_multi)

def prep_gtf(gtf):
    gtf['gene_3char'] = gtf['name2'].str[0:3]
    gtf = gtf.rename(columns={"name2": "gene", 'chrom': 'chr','txStart': 'start', 'txEnd': 'end'}).sort_values(['chr', 'start'])
    return gtf

def add_Nth_hit(mmap2_paired_in,X=Nth_hit_buffer): #30から変更
    ##print('Nth hitの判定')
    mmap2_paired = mmap2_paired_in.sort_values(['Qname','Qstart','Qend','mapQ','match_rate'],ascending=[True,True,True,False,False])
    res=[]
    for x,rid in tqdm(enumerate(mmap2_paired.Qname.unique())): #read_idごと
        counter=1 #Nth
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        for n,(_,r) in enumerate(mmap2_paired_sub.iterrows()): #同じread_idでの複数ヒット
            if n==0:
                res.append(1)
            else:
                if (mmap2_paired_sub.iloc[n-1]["Qstart"] >= mmap2_paired_sub.iloc[n]['Qstart'] - X):
                    counter+=0
                    res.append(counter)
                elif (mmap2_paired_sub.iloc[n-1]["Qend"] >= mmap2_paired_sub.iloc[n]['Qend'] -X ): 
                    counter+=0
                    res.append(counter)
                else:
                    counter+=1
                    res.append(counter)
    mmap2_paired["Nth_hit"] = res
    return mmap2_paired

def filter_out_Nth_hit_ov2(df):
    cond = df.groupby("Qname").Nth_hit.max() == 2
    filterd_qid = cond[cond].index
    df_out=df.query('Qname in @filterd_qid')
    return df_out


def filter_out_mismatch_clst_gname(clst,g1,g2):
    clst_1=clst.split("--")[0]
    clst_2=clst.split("--")[1]
    if (clst_1 in g1 or clst_2 in g1) and (clst_1 in g2 or clst_2 in g2):
        ##print(clst,g1,g2,"_clst_geme_mismatch")
        return 0
    else:
        return 1


def cul_fusioncand_v4_4refseq(mmap2_paired):
    ##print('---------------融合点の計算----------------')
    col = ["Qname","Qstart","Qend","dir", "Tname", "Tstart", "Tend", "mapQ","match_rate", "mapping_rate","gene"]
    out_col = ["hit_rid", "Qstart1","Qend1","dir1", "chr1", "start1", "end1", "mapQ1", "match_rate1", "mapping_rate1","g1","Qstart2","Qend2","dir2", "chr2",
               "start2", "end2", "mapQ2", "match_rate2", 'mapping_rate2', "g2","gap_len",'gap_rate']
    arr=[]
    for rid in tqdm(mmap2_paired.Qname.unique()):
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        if mmap2_paired_sub.Nth_hit.nunique()==2:
            mmap2_paired_sub_Nth1= mmap2_paired_sub.query('Nth_hit==1')
            mmap2_paired_sub_Nth2= mmap2_paired_sub.query('Nth_hit==2')
            for i in range(len(mmap2_paired_sub_Nth1)):
                for j in range(len(mmap2_paired_sub_Nth2)):
                    flont_fp = list(mmap2_paired_sub_Nth1.iloc[i][col]) 
                    rear_fp = list(mmap2_paired_sub_Nth2.iloc[j][col])[1:]
                    gap_len =  mmap2_paired_sub_Nth2.iloc[j]['Qstart']- mmap2_paired_sub_Nth1.iloc[i]['Qend']
                    gap_rate =  gap_len / mmap2_paired_sub_Nth1.iloc[i]['Qlen']
                    res = flont_fp + rear_fp + [gap_len] + [gap_rate] 
                    arr.append(res)
                    
        else:
            pass
    df_fusioncand=pd.DataFrame(arr)
    df_fusioncand.columns=out_col
    df_fusioncand = df_fusioncand.drop_duplicates()
    return df_fusioncand

def cul_fusioncand_v4_quick(mmap2_paired):
    ##print('---------------融合点の計算----------------')
    col = ["Qname","Qstart","Qend","dir", "Tname", "Tstart", "Tend", "mapQ","match_rate", "mapping_rate"]
    out_col = ["hit_rid", "Qstart1","Qend1","dir1", "chr1", "start1", "end1", "mapQ1", "match_rate1", "mapping_rate1","Qstart2","Qend2","dir2", "chr2",
               "start2", "end2", "mapQ2", "match_rate2", 'mapping_rate2', "gap_len",'gap_rate']
    arr=[]
    for rid in tqdm(mmap2_paired.Qname.unique()):
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        if mmap2_paired_sub.Nth_hit.nunique()==2:
            mmap2_paired_sub_Nth1= mmap2_paired_sub.query('Nth_hit==1')
            mmap2_paired_sub_Nth2= mmap2_paired_sub.query('Nth_hit==2')
            for i in range(len(mmap2_paired_sub_Nth1)):
                for j in range(len(mmap2_paired_sub_Nth2)):
                    flont_fp = list(mmap2_paired_sub_Nth1.iloc[i][col]) 
                    rear_fp = list(mmap2_paired_sub_Nth2.iloc[j][col])[1:]
                    gap_len =  mmap2_paired_sub_Nth2.iloc[j]['Qstart']- mmap2_paired_sub_Nth1.iloc[i]['Qend']
                    gap_rate =  gap_len / mmap2_paired_sub_Nth1.iloc[i]['Qlen']
                    res = flont_fp + rear_fp + [gap_len] + [gap_rate] 
                    arr.append(res)
                    
        else:
            pass
            ### 3箇所以上にマッピングされるものは候補から除外
        df_fusioncand=pd.DataFrame(arr)
        df_fusioncand.columns=out_col
        df_fusioncand = df_fusioncand.drop_duplicates()
    return df_fusioncand


def prep_paf_edge_4gaponly(path):
    paf_col=["Qname", "Qlen", "Qstart", "Qend", "dir", "Tname", "Tlen", "Tstart", "Tend", "match", "block", "mapQ"]
    df = pd.read_table(path, index_col=False, header=None, names=paf_col, usecols=range(0, 12)).drop('Tlen',axis=1)
    if len(df)>0:
        #df["Nth_hit"]=df['Qname'].str.rsplit("_",2).str[1].str[0].astype(int)
        df["pat"]=df['Qname'].str.rsplit("_",1).str[-1].str[0]
        df['Qname'] = df['Qname'].str.split(',').str[0].str.rsplit("_",4).str[0]
        #df['gene'] = df.apply(lambda x: get_gene_name_from_rid(x['Qname']), axis=1)
        df['match_rate'] = (df['match'])/(df['Qend']-df['Qstart']+1)
        df['mapping_rate'] = (df['Qend']-df['Qstart']+1)/df['Qlen']
        df.sort_values(['Qname','Qstart'],ascending=[True,True],inplace=True)
        return df

def prep_subseq_read_gaponly(df_in):
    res_df=pd.DataFrame()
    ##print('----start prep_subseq_read gap only -------')
    df = df_in[['Qname','Qlen' ,'Qstart', 'Qend','Nth_hit']].drop_duplicates()
    out_col=['Qname', 'Qstart', 'Qend']
    for rid in tqdm(df.Qname.unique()):
        df_sub = df.query('Qname in @rid')
        Nths = df_sub.Nth_hit.nunique()
        if Nths==2: 
            df_sub1=df_sub.query('Nth_hit == 1')
            df_sub2=df_sub.query('Nth_hit == 2')
            N=0
            for (_,r1) in df_sub1.iterrows():
                for (_,r2) in df_sub2.iterrows():
                    res = pd.Series([rid, int(r1['Qend']),int(r2['Qstart'])],index=out_col)
                    res_df = res_df.append(res,ignore_index=True)
                    N=N+1

    res_df = res_df.astype({'Qend':int,'Qstart':int}).sort_values(['Qname','Qstart','Qend'])[out_col].drop_duplicates(subset=['Qname','Qstart','Qend'])
    assert res_df.Qname.nunique()==df.Qname.nunique()
    return res_df

def filter_only_2pairofgene(df_fusioncand_in,g1_col,g2_col):
    df_fusioncand = df_fusioncand_in.copy()
    cond1=df_fusioncand.groupby('hit_rid')[g1_col].nunique()==1
    g1_uniq_rid=cond1[cond1].index
    cond2=df_fusioncand.groupby('hit_rid')[g2_col].nunique()==1
    g2_uniq_rid=cond2[cond2].index
    g1_g2_uniq_rid=set(g1_uniq_rid)&set(g2_uniq_rid)
    df_fusioncand = df_fusioncand.query('hit_rid in @g1_g2_uniq_rid')
    return df_fusioncand


def reclst_stop(df_in,dont_reclust_cutoff):
    df_fusioncand=df_in.copy()
    df_fusioncand.loc[(df_fusioncand['clst_count_1st']>=dont_reclust_cutoff) & (df_fusioncand["clst_final"]!=df_fusioncand['clst_1st']),'g1_clst']=df_fusioncand['g1_clst_1st']
    df_fusioncand.loc[(df_fusioncand['clst_count_1st']>=dont_reclust_cutoff) & (df_fusioncand["clst_final"]!=df_fusioncand['clst_1st']),'g2_clst']=df_fusioncand['g2_clst_1st']
    df_fusioncand.loc[(df_fusioncand['clst_count_1st']>=dont_reclust_cutoff) & (df_fusioncand["clst_final"]!=df_fusioncand['clst_1st']),'clst_final']=df_fusioncand['clst_1st']
    df_fusioncand.loc[(df_fusioncand['clst_count_1st']>=dont_reclust_cutoff) & (df_fusioncand["clst_final"]!=df_fusioncand['clst_1st']),'clst_count']=df_fusioncand['clst_count_1st']
    df_fusioncand.loc[(df_fusioncand['clst_count_1st']>=dont_reclust_cutoff) & (df_fusioncand["clst_final"]!=df_fusioncand['clst_1st']),'support_read']=df_fusioncand['support_read_1st']
    return df_fusioncand


def drop_different_genepair_reseq(g1,g2,g1_r,g2_r):
    if (g1 in g1_r or g1 in g2_r) and (g2 in g1_r or g2 in g2_r):
        res=0
    elif (g1_r in g1 or g1_r in g2) and (g2_r in g1 or g2_r in g2):
        res=0
    else:
        res=1
    return res



def filter_out_Nth_hit(df,N):
    cond = df.groupby("Qname").Nth_hit.max() == N
    filterd_qid = cond[cond].index
    df_out=df.query('Qname not in @filterd_qid')
    return df_out


def filter_refseq_paf(local_file_path_refseq,gtf_path,N=1):
    gtf = pd.read_csv(gtf_path, usecols=[0,5],names=['Tname','gene'],header=0,index_col=False)
    paf_col = ["Qname", "Qlen", "Qstart", "Qend", "dir", "Tname","Tlen", "Tstart", "Tend", "match", "block", "mapQ"]
    mmap2_refseq = pd.read_table(local_file_path_refseq, index_col=False, header=None,names=paf_col, usecols=range(0, 12)).drop('Tlen', axis=1)
    # mmap2_refseq['Tname'] = mmap2_refseq['Tname'].str.split("_").str[2]
    mmap2_refseq['Tname'] = mmap2_refseq['Tname'].str.split("|").str[0]
    mmap2_refseq = pd.merge(mmap2_refseq, gtf,how='left')
    
    #1geneにしか当たらないリードをdrop
    cond1=mmap2_refseq.groupby('Qname')['gene'].nunique()!=N
    filterd_qid1=cond1[cond1].index
    mmap2_refseq_cand1=mmap2_refseq.query('Qname in @filterd_qid1')
    
    #startとendが一致しているものは落とす
    cond2 = (mmap2_refseq_cand1.groupby('Qname')['Qstart'].nunique() != 1) & (mmap2_refseq_cand1.groupby('Qname')['Qend'].nunique() != 1)
    filterd_qid2=cond2[cond2].index
    mmap2_refseq_cand2=mmap2_refseq_cand1.query('Qname in @filterd_qid2')
    mmap2_refseq_cand2['match_rate'] = (mmap2_refseq_cand2['match']) / (mmap2_refseq_cand2['Qend']-mmap2_refseq_cand2['Qstart']+1)
    mmap2_refseq_cand2['mapping_rate'] = (mmap2_refseq_cand2['Qend']-mmap2_refseq_cand2['Qstart']+1)/mmap2_refseq_cand2['Qlen']
    cond2 = (mmap2_refseq_cand2.groupby('Qname')['Qstart'].nunique() != 1) & (mmap2_refseq_cand2.groupby('Qname')['Qend'].nunique() != 1)
    filterd_qid2=cond2[cond2].index
    mmap2_refseq_cand2=mmap2_refseq_cand2.query('Qname in @filterd_qid2').sort_values('Qname')
    multi_gene_id=mmap2_refseq_cand2.Qname.unique()
    
    return multi_gene_id,mmap2_refseq, mmap2_refseq_cand2

def prep_paf_file_v3(paffile_path, filterd_qid, Nth_hit_flg=1):
    paf_col = ["Qname", "Qlen", "Qstart", "Qend", "dir", "Tname","Tlen", "Tstart", "Tend", "match", "block", "mapQ"]
    mmap2 = pd.read_table(paffile_path, index_col=False, header=None,names=paf_col, usecols=range(0, 12)).drop('Tlen', axis=1)
    if len(filterd_qid)!=0: 
        mmap2_cand1=mmap2.query('Qname in @filterd_qid')
    else:
        mmap2_cand1=mmap2.copy()
    cond3 = (mmap2_cand1.groupby('Qname')['Qstart'].nunique() != 1) & (mmap2_cand1.groupby('Qname')['Qend'].nunique() != 1)
    filterd_qid3 = cond3[cond3].index
    mmap2_cand2 = mmap2_cand1.query('Qname in @filterd_qid3')
    mmap2_cand2['Qhit']=mmap2_cand2['Qend']-mmap2_cand2['Qstart']+1
    mmap2_cand2['match_rate'] = (mmap2_cand2['match']) / (mmap2_cand2['Qend']-mmap2_cand2['Qstart']+1)
    mmap2_cand2['mapping_rate'] = (mmap2_cand2['Qend']-mmap2_cand2['Qstart']+1)/mmap2_cand2['Qlen']
    if Nth_hit_flg==1:
        mmap2['Tname'] = mmap2['Tname'].str.split("_").str[2]
        mmap2_cand2 = add_Nth_hit(mmap2_cand2)
    return mmap2,mmap2_cand2

def flging_gap_use_read(df):
    Qnames=df.query('gene==gene_gap').Qname.unique()
    df.loc[df['Qname'].isin(Qnames),'gap_use']=1
    return df
        
def filterout_multigene_hit(df,col):
    cond=df.groupby('Qname')[col].nunique()==1
    uniq_hit_rid=cond[cond].index
    df_filtered=df.query('Qname in @uniq_hit_rid')
    return df_filtered

def cul_fusioncand_v4(mmap2_paired):
    ##print('---------------融合点の計算----------------')
    col = ["Qname","Qstart","Qend","dir", "Tname", "Tstart","Tend","mapQ","gene"]
    #out_col = ["hit_rid", "Qstart1","Qend1","dir1", "chr1", "start1", "end1", "mapQ1", "match_rate1", "mapping_rate1","Qstart2","Qend2","dir2", "chr2",
    #          "start2", "end2", "mapQ2", "match_rate2", 'mapping_rate2', "gap_len",'gap_rate']
    out_col = ["hit_rid", "Qstart1","Qend1","dir1", "chr1", "start1", "end1", "mapQ1","gene1","Qstart2","Qend2","dir2", "chr2",
               "start2", "end2", "mapQ2", "gene2","gap_len",'gap_rate']
    arr=[]
    for rid in tqdm(mmap2_paired.Qname.unique()):
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        if mmap2_paired_sub.Nth_hit.nunique()==2:
            mmap2_paired_sub_Nth1= mmap2_paired_sub.query('Nth_hit==1')
            mmap2_paired_sub_Nth2= mmap2_paired_sub.query('Nth_hit==2')
            for i in range(len(mmap2_paired_sub_Nth1)):
                for j in range(len(mmap2_paired_sub_Nth2)):
                    flont_fp = list(mmap2_paired_sub_Nth1.iloc[i][col]) 
                    rear_fp = list(mmap2_paired_sub_Nth2.iloc[j][col])[1:]
                    gap_len =  mmap2_paired_sub_Nth2.iloc[j]['Qstart']- mmap2_paired_sub_Nth1.iloc[i]['Qend']
                    gap_rate =  gap_len / mmap2_paired_sub_Nth1.iloc[i]['Qlen']
                    res = flont_fp + rear_fp + [gap_len] + [gap_rate] 
                    arr.append(res)
                    
        else:
            pass
            ### 3箇所以上にマッピングされるものは候補から除外
        df_fusioncand=pd.DataFrame(arr)
        df_fusioncand.columns=out_col
        df_fusioncand = df_fusioncand.drop_duplicates()
    return df_fusioncand

def change_order_g1g2_v3(df_fusioncand_in,type):
    df_fusioncand = df_fusioncand_in.copy()
    if type=="refseq":
        g1_col = ['dir1', 'chr1', 'start1', 'end1','mapQ1','g1']
        g2_col = ['dir2', 'chr2', 'start2', 'end2','mapQ2','g2']
        condition=(df_fusioncand['g1'] > df_fusioncand['g2']) | ((df_fusioncand['g1'] == df_fusioncand['g2']) & (df_fusioncand['start1'] > df_fusioncand['start2']))
    else:
        g1_col = ['dir1', 'chr1', 'start1', 'end1','mapQ1' ]
        g2_col = ['dir2', 'chr2', 'start2', 'end2','mapQ2']
        condition=(df_fusioncand['chr1'] > df_fusioncand['chr2']) | ((df_fusioncand['chr1'] == df_fusioncand['chr2']) & (df_fusioncand['start1'] > df_fusioncand['start2']))
    df_cand = df_fusioncand[condition]
    new2_df = df_cand[g1_col]
    new1_df = df_cand[g2_col]
    new1_df.columns=g1_col
    new2_df.columns=g2_col
    df_fusioncand.loc[condition, g1_col +g2_col] = pd.concat([new1_df, new2_df], axis=1)

    return df_fusioncand

def get_major_clst(clst1,count1,clst2,count2):
    if count1 >= count2:
        return clst1
    else:
        return clst2

def make_descendants_table(df,df_count):
    import networkx as nx
    x=df
    G = nx.DiGraph()
    G.add_weighted_edges_from([tuple(x) for x in x.values])
    nx.info(G)
    df_descendants=pd.DataFrame(columns=['clst_1st','clst_final'])
    for node in G.nodes():
        descendant=nx.descendants(G, node)
        if len(descendant)==0:
            descendant_=node
        else:
            descendant_=(list(descendant)[0])
        var_ser=pd.Series([node,descendant_],index=df_descendants.columns)
        df_descendants=df_descendants.append( var_ser, ignore_index=True )
    df_descendants=df_descendants.query('clst_1st!=clst_final')
    df_descendants=pd.merge(df_descendants,df_count.drop_duplicates(),on='clst_1st',how='left')
    return df_descendants

def re_clst_miner2major_v3(df_in,clst_col,clst_count_col,g1_r,g2_r,dont_reclust_cutoff):
    df=df_in.copy()
    df_clst_count=df[[clst_col,clst_count_col,g1_r,g2_r]].drop_duplicates()
    df_4reclst = df[[clst_col,clst_count_col,g1_r,g2_r]]
    df_case1=pd.merge(df_4reclst,df_clst_count,on=g1_r,suffixes=['', '_upd1']).query('clst_count<clst_count_upd1')[[clst_col,'clst_1st_upd1',clst_count_col,'clst_count_upd1']].drop_duplicates()
    df_case1.columns=df_case1.columns.str.replace('upd1','upd')
    df_case2=pd.merge(df_4reclst,df_clst_count,on=g2_r,suffixes=['', '_upd2']).query('clst_count<clst_count_upd2')[[clst_col,'clst_1st_upd2',clst_count_col,'clst_count_upd2']].drop_duplicates()
    df_case2.columns=df_case2.columns.str.replace('upd2','upd')

    df_clst_f2=pd.concat([df_case1,df_case2]).sort_values('clst_count_upd',ascending=False)\
        .drop_duplicates(clst_col)\
        .query('clst_count<=@dont_reclust_cutoff')\
        .drop("clst_count_upd",axis=1).rename(columns={'clst_1st_upd':'clst_final'})
        
    
    df_clst_count_in=df_clst_count[[clst_col,clst_count_col]].drop_duplicates()
    df_clst_f2_upd = make_descendants_table(df_clst_f2,df_clst_count_in) ##ネットワーク使ってアップデート
    df_clst_f2_upd2 = make_descendants_table(df_clst_f2_upd,df_clst_count_in)
    df_clst_f2_upd3 = make_descendants_table(df_clst_f2_upd2,df_clst_count_in)
    assert df_clst_f2_upd3.equals(df_clst_f2_upd2)
     
    df_out = pd.merge(df,df_clst_f2_upd3,on=[clst_col,clst_count_col],how='left')
    df_out.loc[df_out.clst_final.isna(),'clst_final']=df_out[clst_col]
    return df_out

def get_cytoband_start_end(cytoband,chr,s,e,buffer=15):
    cytoband['len']=cytoband['end']-cytoband['start']
    cytoband_col="chr_pq"
    multi_hit_flg=0
    gtf_sub1=cytoband.query('chr==@chr & start-@buffer <= @s <= end + @buffer and chr==@chr & start-@buffer <= @e <= end+@buffer') #gtfの中にstart,endともに張り付いている
    if len(gtf_sub1) >= 1:
        gtf_sub1= gtf_sub1.sort_values('len',ascending=False)
        g_tmp = gtf_sub1[cytoband_col].unique()
        g_multi="||".join(g_tmp)
        #g=g_tmp[0]
        if len(g_tmp) > 1:
            multi_hit_flg=1
            g_multi="||".join(g_tmp)
    else:
        cytoband2=cytoband.query('chr==@chr & start-@buffer <= @s <= end+@buffer') #gtfの中にstartのみ張り付いている
        cytoband3=cytoband.query('chr==@chr & start-@buffer <= @e <= end+@buffer') #gtfの中にendのみ張り付いている
        if len(cytoband2)>=1: 
            cytoband2= cytoband2.sort_values('len',ascending=False)
            g_tmp = cytoband2[cytoband_col].unique()
            g_multi="||".join(g_tmp)
            #g=g_tmp[0]
            if len(g_tmp) > 1:
                multi_hit_flg=1
        elif len(cytoband3)>=1: 
            cytoband3= cytoband3.sort_values('len',ascending=False)
            g_tmp = cytoband3[cytoband_col].unique()
            g_multi="||".join(g_tmp)
            #g=g_tmp[0]
            if len(g_tmp)>1:
                multi_hit_flg=1
        
    return pd.Series(g_multi)

def add_TF_columns_genename_v2(true_gA,true_gB, g1, g2):
    res=0;index=9999
    # if pd.isna(g1) or pd.isna(g2):
    #     return pd.Series([res,index])
    for row_g1,true_gA_sub in enumerate(true_gA):
        if true_gA_sub in g1 or true_gA_sub in g2:
            for row_g2,true_gB_sub in enumerate(true_gB):
                if (true_gB_sub in g1 or true_gB_sub in g2) and (row_g1==row_g2):
                    res=1
                    index=row_g1
    return pd.Series([res,index])


def make_breakpoint_divX(X,by=10000):
    bp=X
    chr1=bp.split("___")[0].split("__")[0]
    pos1=bp.split("___")[0].split("__")[1]
    chr2=bp.split("___")[1].split("__")[0]
    pos2=bp.split("___")[1].split("__")[1]
    pos1_div=str(my_round_int(int(pos1) / by))
    pos2_div=str(my_round_int(int(pos2) / by))
    res=chr1+ "__" + pos1_div + "___" +chr2+ "__" + pos2_div
    return res

def prep_blat_edge_4gaponly(path,topscore=1):
    df=pd.read_table(path,names=["Qname","Tname","identity","alignment_length","mismatches","gap_openings","Qstart","Qend","Tstart","Tend","evalue","bitscore"])
    if topscore==1:
        df=df.sort_values(['Qname','evalue','bitscore'],ascending=[True,True,False])
        df=(df.groupby(['Qname'],as_index=False).apply(select,col='evalue',kind='min'))

    else:
        pass
    df.sort_values(['Qname','Qstart'],ascending=[True,True],inplace=True)
    #df=df.query('evalue<=@cutoff')
    return df

def select(df, **kwargs):  # colに列名,kindに最大もしくは最小

    if kwargs['kind'] == 'min':
        val_r = df[df[kwargs['col']] == min(df[kwargs['col']])]
    elif kwargs['kind'] == 'max':
        val_r = df[df[kwargs['col']] == max(df[kwargs['col']])]
    else:
        raise Exception("パラメータ不正")

    # 全く同じ行があった場合は削除
    val_r = val_r.drop_duplicates()

    return val_r

def add_exon_s_e(df,gtf_exon_path):
    df=df.assign(gene2=df['gene'].str.split("\|\|")).explode('gene2')
    df_exon=pd.read_csv(gtf_exon_path)
    df_merged=pd.merge(df,df_exon[['gene','exstart','exend']],left_on='gene2',right_on="gene")
    df_merged['diff_s']=abs(df_merged['Tstart']-df_merged['exstart'])
    df_merged['diff_e']=abs(df_merged['exend']-df_merged['Tend'])

    tmp1=df_merged.groupby(['Qname','Nth_hit'],as_index=False).diff_s.min()
    tmp2=df_merged.groupby(['Qname','Nth_hit'],as_index=False).diff_e.min()
    df_merged_t=pd.merge(df_merged,tmp1,how='inner')
    df_start=df_merged_t[['Qname','Nth_hit','exstart','diff_s']].drop_duplicates()
    df_merged_t=pd.merge(df_merged,tmp2,how='inner')
    df_end=df_merged_t[['Qname','Nth_hit','exend','diff_e']].drop_duplicates()
    df_s_e=pd.merge(df_start,df_end)
    df_out=pd.merge(df,df_s_e).sort_values(['Qname','Nth_hit'])
    df_out['diff_s']=df_out['Tstart']-df_out['exstart']
    df_out['diff_e']=df_out['exend']-df_out['Tend']
    return df_out

def fix_start_end(df_in):
    df=df_in.copy()
    df[['Qstart_fix','Qend_fix','Tstart_fix','Tend_fix']]=df[['Qstart','Qend','Tstart','Tend']].copy()
    #Nth1 dir +
    df.loc[(df['Nth_hit']==1) & (df['dir']=="+"),"Tend_fix"]=df['exend']
    df.loc[(df['Nth_hit']==1) & (df['dir']=="+"),'Qend_fix']=df['Qend']+df['diff_e']
    #Nth1 dir -
    df.loc[(df['Nth_hit']==1) & (df['dir']=="-"),"Tstart_fix"]=df['exstart']
    df.loc[(df['Nth_hit']==1) & (df['dir']=="-"),'Qend_fix']=df['Qend']+df['diff_s']
    #df.loc[(df['Nth_hit']==1) & (df['dir']=="-")]

    #Nth2 dir +
    df.loc[(df['Nth_hit']==2) & (df['dir']=="+"),"Tstart_fix"]=df['exstart']
    df.loc[(df['Nth_hit']==2) & (df['dir']=="+"),'Qstart_fix']=df['Qstart']-df['diff_s']
    #Nth1 dir -
    df.loc[(df['Nth_hit']==2) & (df['dir']=="-"),"Tend_fix"]=df['exend']
    df.loc[(df['Nth_hit']==2) & (df['dir']=="-"),'Qstart_fix']=df['Qstart']-df['diff_e']
    return df
            

def judge_cross_over_v3(mmap2_paired,buffer,s,e):
    ##print('クエリ側のクロスオーバーの判定')
    rids=[]
    if mmap2_paired['Nth_hit'].value_counts()[1] != mmap2_paired['Nth_hit'].value_counts()[2]:
        drop_rid_nopaired = pd.DataFrame(mmap2_paired.groupby('Qname')['Nth_hit'].nunique() == 1).query('Nth_hit==True').index
        mmap2_paired = mmap2_paired.query('Qname not in @drop_rid_nopaired')
    for x,rid in enumerate(tqdm(mmap2_paired.Qname.unique())): #read_idごと
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        N=mmap2_paired_sub.Nth_hit.min()
        first_end_pos = int(mmap2_paired_sub.query('Nth_hit==@N')[e].max())
        try:
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit==@N+1')[s].min())
        except:
            assert mmap2_paired_sub['Nth_hit'].nunique()==2 ,'Nth_hitが3以上です'
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit!=@N')[s].min())
        if first_end_pos - buffer > second_start_pos:
            rids.append(rid)
    return rids

def add_exon_s_e(df,gtf_exon_path):
    df=df.assign(gene2=df['gene'].str.split("\|\|")).explode('gene2')
    df_exon=pd.read_csv(gtf_exon_path)
    df_merged=pd.merge(df,df_exon[['gene','exstart','exend']],left_on='gene2',right_on="gene")
    df_merged['diff_s']=abs(df_merged['Tstart']-df_merged['exstart'])
    df_merged['diff_e']=abs(df_merged['exend']-df_merged['Tend'])

    tmp1=df_merged.groupby(['Qname','Nth_hit'],as_index=False).diff_s.min()
    tmp2=df_merged.groupby(['Qname','Nth_hit'],as_index=False).diff_e.min()
    df_merged_t=pd.merge(df_merged,tmp1,how='inner')
    df_start=df_merged_t[['Qname','Nth_hit','exstart','diff_s']].drop_duplicates()
    df_merged_t=pd.merge(df_merged,tmp2,how='inner')
    df_end=df_merged_t[['Qname','Nth_hit','exend','diff_e']].drop_duplicates()
    df_s_e=pd.merge(df_start,df_end)
    df_out=pd.merge(df,df_s_e).sort_values(['Qname','Nth_hit'])
    df_out['diff_s']=df_out['Tstart']-df_out['exstart']
    df_out['diff_e']=df_out['exend']-df_out['Tend']
    return df_out

def fix_start_end(df_in):
    df=df_in.copy()
    df[['Qstart_fix','Qend_fix','Tstart_fix','Tend_fix']]=df[['Qstart','Qend','Tstart','Tend']].copy()
    #Nth1 dir +
    df.loc[(df['Nth_hit']==1) & (df['dir']=="+"),"Tend_fix"]=df['exend']
    df.loc[(df['Nth_hit']==1) & (df['dir']=="+"),'Qend_fix']=df['Qend']+df['diff_e']
    #Nth1 dir -
    df.loc[(df['Nth_hit']==1) & (df['dir']=="-"),"Tstart_fix"]=df['exstart']
    df.loc[(df['Nth_hit']==1) & (df['dir']=="-"),'Qend_fix']=df['Qend']+df['diff_s']
    #df.loc[(df['Nth_hit']==1) & (df['dir']=="-")]

    #Nth2 dir +
    df.loc[(df['Nth_hit']==2) & (df['dir']=="+"),"Tstart_fix"]=df['exstart']
    df.loc[(df['Nth_hit']==2) & (df['dir']=="+"),'Qstart_fix']=df['Qstart']-df['diff_s']
    #Nth1 dir -
    df.loc[(df['Nth_hit']==2) & (df['dir']=="-"),"Tend_fix"]=df['exend']
    df.loc[(df['Nth_hit']==2) & (df['dir']=="-"),'Qstart_fix']=df['Qstart']-df['diff_e']
    return df
            
def prep_subseq_read_gaponly_v2(df_in):
    res_df=pd.DataFrame()
    ##print('----start prep_subseq_read gap only -------')
    df = df_in[['Qname','Qlen' ,'Qstart_fix', 'Qend_fix','Nth_hit']].drop_duplicates()
    out_col=['Qname', 'Qstart', 'Qend']
    for rid in tqdm(df.Qname.unique()):
        df_sub = df.query('Qname in @rid')
        Nths = df_sub.Nth_hit.nunique()
        if Nths==2: 
            df_sub1=df_sub.query('Nth_hit == 1')
            df_sub2=df_sub.query('Nth_hit == 2')
            N=0
            for (_,r1) in df_sub1.iterrows():
                for (_,r2) in df_sub2.iterrows():
                    res = pd.Series([rid, int(r1["Qend_fix"]),int(r2["Qstart_fix"])],index=out_col)
                    res_df = res_df.append(res,ignore_index=True)
                    N=N+1
    return res_df

def judge_cross_over_v3(mmap2_paired,buffer,s,e):
    ##print('クエリ側のクロスオーバーの判定')
    rids=[]
    if mmap2_paired['Nth_hit'].value_counts()[1] != mmap2_paired['Nth_hit'].value_counts()[2]:
        drop_rid_nopaired = pd.DataFrame(mmap2_paired.groupby('Qname')['Nth_hit'].nunique() == 1).query('Nth_hit==True').index
        mmap2_paired = mmap2_paired.query('Qname not in @drop_rid_nopaired')
    for x,rid in enumerate(tqdm(mmap2_paired.Qname.unique())): #read_idごと
        mmap2_paired_sub = mmap2_paired.query('Qname==@rid')
        N=mmap2_paired_sub.Nth_hit.min()
        first_end_pos = int(mmap2_paired_sub.query('Nth_hit==@N')[e].max())
        try:
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit==@N+1')[s].min())
        except:
            assert mmap2_paired_sub['Nth_hit'].nunique()==2 ,'Nth_hitが3以上です'
            second_start_pos = int(mmap2_paired_sub.query('Nth_hit!=@N')[s].min())
        if first_end_pos - buffer > second_start_pos:
            rids.append(rid)
    return rids
    
def split_bp(bp):
    chr1=bp.split("___")[0].split("__")[0]
    pos1=int(bp.split("___")[0].split("__")[1])
    chr2=bp.split("___")[1].split("__")[0]
    pos2=int(bp.split("___")[1].split("__")[1])
    return pd.Series(list([chr1,pos1,chr2,pos2]))

def make_bp_clst_mode(df):
    df[["name2_chr1","name2_pos1","name2_chr2","name2_pos2"]]=df['name2'].apply(lambda x:split_bp(x))
    df['g1_g2_clst'] = df['g1_clst'] + "--" + df["g2_clst"]
    
    tmp=pd.DataFrame(df.groupby('g1_g2_clst',as_index=True)['name2_pos1'].apply(lambda x: x.mode())).reset_index().drop('level_1',axis=1).rename(columns={'name2_pos1':'name2_pos1_mode'})
    tmp2=pd.DataFrame(df.groupby('g1_g2_clst',as_index=True)['name2_pos2'].apply(lambda x: x.mode())).reset_index().drop('level_1',axis=1).rename(columns={"name2_pos2":'name2_pos2_mode'})
    df_bp_mode=pd.merge(tmp,tmp2)
    df=pd.merge(df,df_bp_mode,how='left',on='g1_g2_clst')
    df["name2_clst"]=df['name2_chr1']+"__"+df['name2_pos1_mode'].astype(str)+"___"+df['name2_chr2']+"__"+df['name2_pos2_mode'].astype(str)
    df=df.drop(['name2_chr1','name2_chr2','name2_pos1','name2_pos2'],axis=1)
    return df

def cul_gaplen(df_in,Qstart,Qend):
    df = df_in[['Qname','Qlen' ,Qstart, Qend,'Nth_hit']].drop_duplicates()
    res_df=pd.DataFrame()
    for rid in tqdm(df.Qname.unique()):
        df_sub = df.query('Qname in @rid')
        Nths = df_sub.Nth_hit.nunique()
        if Nths==2: 
            df_sub1=df_sub.query('Nth_hit == 1')
            df_sub2=df_sub.query('Nth_hit == 2')
            N=0
            for (_,r1) in df_sub1.iterrows():
                for (_,r2) in df_sub2.iterrows():
                    res = pd.Series([rid, int(r2[Qstart])-int(r1[Qend])],index=['rid','gaplen'])
                    res_df = res_df.append(res,ignore_index=True)
                    N=N+1
    return res_df

def bp_update_v3(df_in):
    df=df_in.copy()
    df['Tstart_exon']=df['Tstart']
    df['Tend_exon']=df['Tend']
    df.loc[(df['gene_gap_equal']==1)&(df["Nth_hit"]==1)&(df["dir"]=="+"),"Tend"]=df["Tend_gap"]
    df.loc[(df['gene_gap_equal']==1)&(df["Nth_hit"]==1)&(df["dir"]=="-"),"Tstart"]=df["Tstart_gap"]
    df.loc[(df['gene_gap_equal']==1)&(df["Nth_hit"]==2)&(df["dir"]=="-"),"Tend"]=df["Tend_gap"]
    df.loc[(df['gene_gap_equal']==1)&(df["Nth_hit"]==2)&(df["dir"]=="+"),"Tstart"]=df["Tstart_gap"]
    return df

def flging_gap_use_read_v2(df):
    Qnames=df.query('(gene_gap.notna()) and( gene in gene_gap or gene_gap in gene)').Qname.unique()
    #print(len(Qnames))
    df['gap_use']=0
    df.loc[df['Qname'].isin(Qnames),'gap_use']=1
    return df
def check_gene_genegap(gene,gene_gap):
    if pd.isna(gene) or pd.isna(gene_gap):
        return 0
    elif gene in gene_gap or gene_gap in gene:
        return 1
    else:
        return 0


def bp_update_v4(df_in):
    df=df_in.copy()
    #df['Tstart_exon']=df['Tstart']
    #df['Tend_exon']=df['Tend']
    df['gap_bp_hosei']=0
    df.loc[(abs(df['Tstart_gap']-df['exstart'])<=buffer) | (abs(df['Tstart_gap']-df['exend'])<=buffer),"gap_bp_hosei"]=1
    df.loc[(abs(df['Tend_gap']-df['exstart'])<=buffer) | (abs(df['Tend_gap']-df['exend'])<=buffer),"gap_bp_hosei"]=1
    df.loc[(df['gap_bp_hosei']==1)&(df['gene_gap_equal']==1)&(df["Nth_hit"]==1)&(df["dir"]=="+"),"Tend"]=df["exend"]
    df.loc[(df['gap_bp_hosei']==1)&(df['gene_gap_equal']==1)&(df["Nth_hit"]==1)&(df["dir"]=="-"),"Tstart"]=df["exstart"]
    df.loc[(df['gap_bp_hosei']==1)&(df['gene_gap_equal']==1)&(df["Nth_hit"]==2)&(df["dir"]=="-"),"Tend"]=df["exend"]
    df.loc[(df['gap_bp_hosei']==1)&(df['gene_gap_equal']==1)&(df["Nth_hit"]==2)&(df["dir"]=="+"),"Tstart"]=df["exstart"]
    return df

def make_name_col_nodev(df):
    tmp = df.query('dir1=="+" & dir2 == "+"')
    tmp["name2"] = tmp["chr1"] + "__" + tmp["end1"].astype(str) + "___" +  tmp["chr2"] + "__" + tmp["start2"].astype(str)
    tmp2 = df.query('dir1=="+"& dir2 == "-"')
    tmp2["name2"]= tmp2["chr1"] + "__" + tmp2["end1"].astype(str) + "___" + tmp2["chr2"] + "__" + tmp2["end2"].astype(str)
    tmp3 = df.query('dir1=="-" & dir2 == "+"')
    tmp3["name2"] = tmp3["chr1"] + "__" + tmp3["start1"].astype(str) + "___" + tmp3["chr2"] + "__" + tmp3["start2"].astype(str)
    tmp4 = df.query('dir1=="-" & dir2 == "-"')
    tmp4["name2"]= tmp4["chr1"] + "__" + tmp4["start1"].astype(str) + "___" + tmp4["chr2"] + "__" + tmp4["end2"].astype(str)
    df=pd.concat([tmp,tmp2], ignore_index=True, axis=0)
    df=pd.concat([df,tmp3], ignore_index=True, axis=0)
    df=pd.concat([df,tmp4], ignore_index=True, axis=0)
    return df

def add_g1_g2_clst_col_v3(df_fusioncand_clst_tmp,clst_col,g1_col,g2_col,out_g1_col,out_g2_col,out_g1_pct_col,out_g2_pct_col,criteria):
   res_df=pd.DataFrame()
   for clst in df_fusioncand_clst_tmp[clst_col].unique():
      df_fusioncand_clust_sub= df_fusioncand_clst_tmp[df_fusioncand_clst_tmp[clst_col]==clst]
      ratio1 = df_fusioncand_clust_sub[g1_col].value_counts(normalize=True)
      ratio2 = df_fusioncand_clust_sub[g2_col].value_counts(normalize=True)
      cond1 = ratio1 >= criteria
      cond2 = ratio2 >= criteria
      g1_multi_clst="_".join(list((cond1.index[cond1])))
      g2_multi_clst="_".join(list((cond2.index[cond2])))
      g1_multi_clst_pct="_".join(list((ratio1[cond1].round(2)*100).astype(int).astype(str) + '%'))
      g2_multi_clst_pct="_".join(list((ratio2[cond2].round(2)*100).astype(int).astype(str) + '%'))
      #g1_multi_clst_pct=ratio1[cond1][0].round(2)
      #g2_multi_clst_pct=ratio2[cond2][0].round(2)
      
      df_fusioncand_clust_sub[out_g1_col]=g1_multi_clst
      df_fusioncand_clust_sub[out_g2_col]=g2_multi_clst
      df_fusioncand_clust_sub[out_g1_pct_col]=g1_multi_clst_pct
      df_fusioncand_clust_sub[out_g2_pct_col]=g2_multi_clst_pct
      #res_df = res_df.append(df_fusioncand_clust_sub)
      res_df=pd.concat([res_df,df_fusioncand_clust_sub], ignore_index=True, axis=0)

   return res_df
def add_clst_count_v2(df,clst_col,support_flg=1):
    df_clst_count = df[clst_col].value_counts().to_frame().reset_index().rename(columns={"count": "clst_count"})
    df_out=pd.merge(df,df_clst_count,on=clst_col)
    if support_flg==1:
        df_out["support_read"]=df_out.apply(lambda x:int(x["clst_count"])*float(x['g1_clst_pct'].split("_")[0].replace("%",""))*float(x['g2_clst_pct'].split("_")[0].replace("%",""))*0.01*0.01,axis=1)
    else:
        pass
    assert df[clst_col].nunique()==df_out[clst_col].nunique()
    return df_out

def make_bp_clst_mode_v2(df):
    df[["name2_chr1","name2_pos1","name2_chr2","name2_pos2"]]=df['name2'].apply(lambda x:split_bp(x))
    tmp1=df.groupby('g1_g2_clst',as_index=True)['name2_pos1'].value_counts().to_frame().rename(columns={"count":"name2_pos1_count"}).reset_index().rename(columns={'name2_pos1':'name2_pos1_mode'})#.drop_duplicates("g1_g2_clst")
    tmp2=df.groupby('g1_g2_clst',as_index=True)['name2_pos2'].value_counts().to_frame().rename(columns={"count":"name2_pos2_count"}).reset_index().rename(columns={'name2_pos2':'name2_pos2_mode'})#.drop_duplicates("g1_g2_clst")
    tmp3=pd.merge(tmp1.groupby('g1_g2_clst')["name2_pos1_mode"].apply(list).to_frame().reset_index(),tmp1.groupby('g1_g2_clst')["name2_pos1_count"].apply(list).to_frame().reset_index()).rename(columns={'name2_pos1_mode':'name2_pos1_mode_list','name2_pos1_count':'name2_pos1_count_list'})
    tmp4=pd.merge(tmp2.groupby('g1_g2_clst')["name2_pos2_mode"].apply(list).to_frame().reset_index(),tmp2.groupby('g1_g2_clst')["name2_pos2_count"].apply(list).to_frame().reset_index()).rename(columns={'name2_pos2_mode':'name2_pos2_mode_list','name2_pos2_count':'name2_pos2_count_list'})
    df_bp_mode=pd.merge(tmp1.drop_duplicates("g1_g2_clst"),pd.merge(tmp2.drop_duplicates("g1_g2_clst"),pd.merge(tmp3,tmp4)))
    df=pd.merge(df,df_bp_mode,how='left',on='g1_g2_clst')
    df["name2_clst"]=df['name2_chr1']+"__"+df['name2_pos1_mode'].astype(str)+"___"+df['name2_chr2']+"__"+df['name2_pos2_mode'].astype(str)
    df=df.drop(['name2_chr1','name2_chr2','name2_pos1','name2_pos2'],axis=1)
    return df




#input
paf_dir = os.path.join(root, "FUGAREC")
paffile_name = f"{TARGET}_{genome_name}.paf"
paffile_name_refseq=f"{TARGET}_refseq.paf"
gap_genome_blat_name = f"{TARGET}_gap_blat_min15_stp5.psl"
paffile_path = os.path.join(paf_dir, paffile_name)
paffile_refseq_path = os.path.join(paf_dir, paffile_name_refseq)
gap_genome_blat_path = os.path.join(paf_dir, gap_genome_blat_name)

#outdir
res_file_dir = paf_dir
intermediate_file_dir = os.path.join(res_file_dir, "intermediate")
res_genome_dir = os.path.join(res_file_dir, "genome")
res_genome_path = os.path.join(res_genome_dir, f"{TARGET}_df_fusioncand_genome.csv")
res_refseq_path = os.path.join(res_genome_dir, f"{TARGET}_df_fusioncand_refseq.csv")
res_4_edge_alignment_dir = os.path.join(res_file_dir, "for_edge_alignment")
for_make_edge_file_path = os.path.join(res_4_edge_alignment_dir, f"{TARGET}", "gap_4make_edge.csv")
output_file_path = os.path.join(res_file_dir, f'df_res_{TARGET}.csv')

#gtf
gtf_path = os.path.join(reference_data_path, f"{genome_name}_{gtf_name}.tab.usecol")
gtf_exon_path = os.path.join(reference_data_path, f"{genome_name}_{gtf_name}.tab.exon")

mmap2_align2genome_path = os.path.join(intermediate_file_dir, f"{TARGET}_genome.csv")
mmap2_align2refseq_path = os.path.join(intermediate_file_dir, f"{TARGET}_refseq.csv")
out_col=['TARGET','hit_rid','g1_clst','g2_clst','g1_g2_clst','name','name2_clst','support_read']

#### ファイル読み込み--------------------------------------------------------------------------------------------
gtf = prep_gtf(pd.read_csv(gtf_path))
multihit_id,mmap2_refseq_org, mmap2_refseq = filter_refseq_paf(paffile_refseq_path, gtf_path)  
edge_start_end_ov = pd.read_csv(for_make_edge_file_path).rename(columns={'length':'gap_len_tmp'})
mmap2_Nth2_rmcross_rmdir = pd.read_csv(mmap2_align2genome_path)
mmap2_Nth2_rmcross_rmdir=mmap2_Nth2_rmcross_rmdir.rename(columns={'Qstart':'Qstart_org',"Qend":"Qend_org","Tstart":"Tstart_org","Tend":"Tend_org","Qstart_fix":"Qstart","Qend_fix":"Qend","Tstart_fix":"Tstart","Tend_fix":"Tend"})

#gapがヒットする遺伝子名を取得
mmap2_gap=prep_blat_edge_4gaponly(gap_genome_blat_path)
mmap2_gap=pd.merge(mmap2_gap,edge_start_end_ov[['Qname','gap_len_tmp']],on="Qname")
mmap2_gap['gap_mapping_rate']=mmap2_gap['alignment_length']/mmap2_gap['gap_len_tmp']
mmap2_gap=mmap2_gap.query('gap_mapping_rate>=@gap_mapping_rate_cutoff').query('evalue<=@gap_evalue_cutoff')
mmap2_gap['gene_gap']=mmap2_gap.apply(lambda x: get_gene_name_start_end(gtf, x['Tname'],x['Tstart'],x['Tend']), axis=1)
mmap2_gap_use=filterout_multigene_hit(mmap2_gap,"gene_gap").query('gene_gap!="intron"')

### gapの配列を使ってフィルタ----------------------------------------------------------------------------------------------------------
### gapの配列の結果とgap長をマージ
mmap2_Nth2_rmcross_rmdup_gap =pd.merge(mmap2_Nth2_rmcross_rmdir,mmap2_gap_use[['Qname','Tname','Tend','Tstart','gene_gap','alignment_length']],on=['Qname','Tname'],how='left',suffixes=['','_gap'])
mmap2_Nth2_rmcross_rmdup_gap = pd.merge(mmap2_Nth2_rmcross_rmdup_gap,edge_start_end_ov[['Qname','gap_len_tmp']],how='left',on=['Qname'])

# genoem とgap でgene名が同じもののみ採用する
mmap2_Nth2_rmcross_rmdup_gap=mmap2_Nth2_rmcross_rmdup_gap.query('gene!="intron"') #gap_len_tmpが50より大きく、gapもヒットしないものはdrop
mmap2_Nth2_rmcross_rmdup_gap_use=flging_gap_use_read_v2(mmap2_Nth2_rmcross_rmdup_gap)
mmap2_Nth2_rmcross_rmdup_gap_use["gene_gap_equal"]=mmap2_Nth2_rmcross_rmdup_gap_use.apply(lambda x:check_gene_genegap(x["gene"],x['gene_gap']),axis=1)

# gapでヒットするupdate
mmap2_Nth2_rmcross_rmdup_gap_use=bp_update_v3(mmap2_Nth2_rmcross_rmdup_gap_use)  #v24.4.2.2
mmap2_Nth2_rmcross_rmdup_gap_use=fix_start_end(mmap2_Nth2_rmcross_rmdup_gap_use)  #v24.4.2

#  フラグメントの融合のペアを算出-----------------------------------------------------------------------------------------
df_fusioncand_g = cul_fusioncand_v4(mmap2_Nth2_rmcross_rmdup_gap_use)

#  genome側のクロスオーバー除去----------------------------------------------------------------------------------------
df_fusioncand_g,drop_rid_cross_over_genome = rm_cross_over(df_fusioncand_g)
df_fusioncand_g=df_fusioncand_g.astype({"start1":int,"end1":int,"start2":int,"end2":int})

### gapでフィルタ---------------------------------------------------------------------------------------------------------
df_fusioncand_g_gap = pd.merge(df_fusioncand_g,mmap2_gap_use[['Qname','gene_gap']],left_on="hit_rid",right_on="Qname",how='left')
df_fusioncand_g_gap_use=df_fusioncand_g_gap.copy()

# gapと遺伝子名が違うものは除去
df_fusioncand_g_gap_use=pd.merge(df_fusioncand_g_gap_use,mmap2_Nth2_rmcross_rmdup_gap_use.groupby('Qname',as_index=False)['gene_gap_equal'].max(),how="left").drop("Qname",axis=1)
df_fusioncand_g_gap_use = df_fusioncand_g_gap_use.query('-1*@buffer<=gap_len<=@gap_len_cutoff or gene_gap_equal==1') #v24.4.2.3

# ### breakpointを特定---------------------------------------------------------------------------------------------------------
df_fusioncand_g_gap_use= make_name_col_nodev(df_fusioncand_g_gap_use)
df_fusioncand_g_gap_use = change_order_g1g2_v3(df_fusioncand_g_gap_use,"genome").rename(columns={'gene1':'g1','gene2':'g2'})

#name2の順番入れ替え
df_fusioncand_g_gap_use['name2']=df_fusioncand_g_gap_use['name2'].apply(lambda x: "___".join(sorted([x.split("___")[0],x.split("___")[1]],reverse=False)))

### 2geneに当たるもののみ採用
df_fusioncand_g_gap_use_2gene  = filter_only_2pairofgene(df_fusioncand_g_gap_use,'g1','g2')

# # #intronにヒットするものやg1・g2が包含されるものは除く（除ききれなかったスプライシング）
df_fusioncand_g_gap_use_2gene_filtered = df_fusioncand_g_gap_use_2gene.query('g1!="intron"&g2!="intron"')
df_fusioncand_g_gap_use_2gene_filtered = df_fusioncand_g_gap_use_2gene_filtered[df_fusioncand_g_gap_use_2gene_filtered.apply(lambda x: (x['g1'] not in x['g2']) and ( x['g2'] not in x['g1']),axis=1)]

### transcriptの結果を使うための前処理
##intronにヒットするものやg1・g2が包含されるものは除く
rid = df_fusioncand_g_gap_use_2gene_filtered.hit_rid.unique()
mmap2_refseq_use = mmap2_refseq.query('Qname in @rid')
mmap2_refseq_use = mmap2_refseq_use.drop_duplicates(subset=['Qname','gene'])
mmap2_refseq_use = add_Nth_hit(mmap2_refseq_use)
df_fusioncand_r = cul_fusioncand_v4_4refseq(mmap2_refseq_use)
df_refseq_r_tmp = df_fusioncand_r[['hit_rid','g1','g2']].drop_duplicates()
df_fusioncand_g_gap_use_2gene_filtered_refseq = pd.merge(df_fusioncand_g_gap_use_2gene_filtered,df_refseq_r_tmp,on='hit_rid',suffixes=['','_r'],how='inner')

### genomeのみ検出を捨てる
df_fusioncand_g_gap_use_2gene_filtered_refseq.query('g1_r.notna() and g2_r.notna()',inplace=True)
df_fusioncand_g_gap_use_2gene_filtered_refseq[['g1_r','g2_r']] = df_fusioncand_g_gap_use_2gene_filtered_refseq.apply(lambda x: sorted(pd.Series([x['g1_r'], x['g2_r']]), reverse=False), axis=1,result_type='expand')

# ##refsqも同様g1・g2が包含されるものは除く
df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered = df_fusioncand_g_gap_use_2gene_filtered_refseq[df_fusioncand_g_gap_use_2gene_filtered_refseq.apply(lambda x: (x['g1_r'] not in x['g2_r']) and ( x['g2_r'] not in x['g1_r']),axis=1)]
df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered['diff_refseq']=df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered.apply(lambda x:drop_different_genepair_reseq(x['g1'],x['g2'],x['g1_r'],x['g2_r']),axis=1)
df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered = df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered.query('diff_refseq==0')

### クラスタリング準備--------------------------------------------------------------------------------------------------------------------------------
df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered["name"]=df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered.apply(lambda x:make_breakpoint_divX(x['name2'],clst_bp),axis=1)

df_fusioncand_4clst=df_fusioncand_g_gap_use_2gene_filtered_refseq_filtered.query('mapQ1!=0&mapQ2!=0')
df_fusioncand_4clst=df_fusioncand_4clst.query('-1*@buffer<=gap_len<=@gap_len_cutoff or gene_gap_equal==1')
df_fusioncand_4clst = add_g1_g2_clst_col_v3(df_fusioncand_4clst, 'name', 'g1_r', 'g2_r', 'g1_clst', 'g2_clst', 'g1_clst_pct', 'g2_clst_pct',clst_percent_cutoff)

df_fusioncand_4clst_major=df_fusioncand_4clst.query('g1_clst!=""').query('g2_clst!=""')
df_fusioncand_4clst_major=add_clst_count_v2(df_fusioncand_4clst_major, 'name',1).sort_values(['clst_count','gap_len'],ascending=[False,True])
df_fusioncand_4clst_major=df_fusioncand_4clst_major.drop_duplicates("hit_rid")
df_fusioncand_4clst_major['g1_g2_clst'] = df_fusioncand_4clst_major['g1_clst'] + "--" + df_fusioncand_4clst_major["g2_clst"]

#bpを最頻値で
df_fusioncand_4clst_major_bp=make_bp_clst_mode_v2(df_fusioncand_4clst_major)

## データ出力 -------------------------------------------------------------------------------------------------------------------------------
df_fusioncand_4clst_major_bp.insert(0, 'TARGET', TARGET)   
df_out=df_fusioncand_4clst_major_bp[out_col].drop_duplicates(['hit_rid','g1_g2_clst'])
df_out.to_csv(output_file_path, index=False)
#df_fusioncand_4clst_major_bp[['TARGET','hit_rid','g1_g2_clst','support_read','name2_clst','gap_len']].to_csv(output_file_path, index=False)
#df_fusioncand_4clst_major_bp.query('name2_pos1_count>1 and name2_pos2_count>1').to_csv(output_file_path, index=False)





