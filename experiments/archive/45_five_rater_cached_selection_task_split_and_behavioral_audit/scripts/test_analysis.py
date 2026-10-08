import numpy as np
from scipy.stats import kendalltau, pearsonr, spearmanr
import analyze as a

def test_vectorized_statistics_ties_and_constants():
    x=np.array([[0,.2,.2,.9,1],[1,1,1,1,1],[.1,.4,.3,.2,.9]])
    y=np.array([.2,.2,.5,.5,1]);m=a.stat_matrix(x,y,np.arange(5))
    for i in (0,2):
        assert abs(m[i,0]-spearmanr(x[i],y).statistic)<1e-12
        assert abs(m[i,1]-pearsonr(x[i],y).statistic)<1e-12
        assert abs(m[i,2]-kendalltau(x[i],y).statistic)<1e-12
    assert np.isnan(m[1,:3]).all()
    assert abs(m[0,4]-(x[0].mean()-y.mean()))<1e-12

def test_bootstrap_preserves_tasks_and_pairing():
    rows=[{'item':str(i),'task':str(i//3)} for i in range(9)]
    scores={'x':{str(i):i/10 for i in range(9)},'constant':{str(i):1. for i in range(9)}}
    targets={str(i):{'all5':i/10,'three':i/10} for i in range(9)}
    r=a.evaluate(['x','constant'],rows,scores,targets,{'x':{'x':1},'human_mirror_H2':{'x':1},'random':{'x':.5,'constant':.5}},50)
    assert r['all5']['contrasts']['x-human_mirror_H2']['lo']==0
    assert r['all5']['selectors']['x']['metrics']['spearman']['value']==1
    assert r['all5']['selectors']['random']['metrics']['spearman']['value'] is None
    assert r['target_sensitivity']['x']['lo']==0

def test_missing_is_not_zero_and_constant_ladder_zero():
    h={'config':'x','cells':[{'cell':'a','kind':'crit','level':0,'key':'i','score':0,'status':'measured'},{'cell':'b','kind':'crit','level':0,'key':'j','score':1,'status':'parse_error'}]}
    assert a.U.median_scores(h)=={'i':0}
    assert a.A.ladder_quality([0,1,2],[.3,.3,.3])==0

def test_tie_weights_and_coverage_gate():
    assert a.U.weights_max(['a','b','c'],{'a':1,'b':1,'c':None})=={'a':.5,'b':.5}
    assert a.measure_rows([{'task':'x','v':None},{'task':'y','v':1}],'v')['value'] is None
