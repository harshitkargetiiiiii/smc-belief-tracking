from fractions import Fraction as F
import random, math
random.seed(7)
DOM=91; LO=10; N=DOM*DOM

def q(x1,s2,s3): return 1 if (x1>=s2 and x1>=s3) else 0

def exact_run(x1, outs):
    p=[F(1,N)]*N
    for o in outs:
        w=[p[i]*(1 if q(x1,LO+i//DOM,LO+i%DOM)==o else 0) for i in range(N)]
        Z=sum(w)
        if Z==0: return None
        p=[x/Z for x in w]
    marg=[sum(p[i*DOM:(i+1)*DOM]) for i in range(DOM)]
    return max(marg)

def fp_run(x1, outs, f, mode):
    S=1<<f
    def trunc(v):
        if mode=='near': return (v+(1<<(f-1)))>>f
        if mode=='floor': return v>>f
        # probabilistic truncation
        lo=v & ((1<<f)-1)
        return (v>>f) + (1 if random.randrange(1<<f)<lo else 0)
    p=[round(S/N)]*N          # fixed-point ints scaled by 2^f
    for o in outs:
        w=[p[i] if q(x1,LO+i//DOM,LO+i%DOM)==o else 0 for i in range(N)]
        Z=sum(w)
        if Z==0: return None
        # reciprocal in fixed point: inv = round(2^2f / Z) >> f  (Goldschmidt in MP-SPDZ; model as correctly-rounded)
        inv=round((1<<(2*f))/Z) if Z>0 else 0
        p=[trunc(x*inv) for x in w]
    marg=[sum(p[i*DOM:(i+1)*DOM]) for i in range(DOM)]
    return max(marg)/S

print(f"{'f':>4} {'mode':>6} {'rounds':>6} {'exact':>12} {'fixed':>12} {'abs err':>11} {'rel err':>9}")
for f in (16,20,24,28,32,40):
  for mode in ('near','prob'):
    for R in (1,3,10):
        x1=63
        outs=[]
        # a plausible sequence of query outcomes
        for r in range(R): outs.append(1 if r%2==0 else 0)
        e=exact_run(x1,outs); a=fp_run(x1,outs,f,mode)
        if e is None or a is None: continue
        ef=float(e)
        print(f"{f:>4} {mode:>6} {R:>6} {ef:>12.8f} {a:>12.8f} {abs(a-ef):>11.2e} {abs(a-ef)/ef:>8.2%}")
