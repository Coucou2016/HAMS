"""Auditable coordinate/transfer utilities (2026-09-26 review).
Unit tests validate these operations, not a full coupled landing or material law.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np


def conservative_resample(time_s, values, target_time_s):
    """Voronoi-bin means preserving trapezoidal impulse, including endpoints.

    Input is piecewise linear. Output node weights equal the widths of the
    Voronoi cells [t0,midpoints,tN], hence trapezoid(output)==integral(input).
    This preserves resultant impulse, NOT contact work or peak forces.
    """
    t=np.asarray(time_s,dtype=float); y=np.asarray(values,dtype=float); q=np.asarray(target_time_s,dtype=float)
    scalar=y.ndim==1
    if scalar:y=y[:,None]
    if t.ndim!=1 or q.ndim!=1 or len(t)<2 or len(q)<2 or y.ndim!=2 or len(y)!=len(t):
        raise ValueError('Require at least two times and matching one- or two-dimensional values')
    if not all(np.all(np.isfinite(x)) for x in (t,y,q)) or np.any(np.diff(t)<=0) or np.any(np.diff(q)<=0):
        raise ValueError('All data must be finite and time strictly increasing')
    if not np.allclose([t[0],t[-1]],[q[0],q[-1]],atol=1e-9,rtol=0):
        raise ValueError('Full-interval conservation requires matching endpoints')
    edges=np.r_[t[0],.5*(q[:-1]+q[1:]),t[-1]]
    dt=np.diff(t); slope=np.diff(y,axis=0)/dt[:,None]
    cum=np.vstack([np.zeros(y.shape[1]),np.cumsum(.5*(y[:-1]+y[1:])*dt[:,None],axis=0)])
    ix=np.clip(np.searchsorted(t,edges,side='right')-1,0,len(t)-2)
    u=edges-t[ix]
    integral=cum[ix]+y[ix]*u[:,None]+.5*slope[ix]*u[:,None]**2
    result=np.diff(integral,axis=0)/np.diff(edges)[:,None]
    return result[:,0] if scalar else result


def thies_total_inertia_z_up():
    """Table 3 is Y-up (Figure 7); R is a proper coordinate rotation."""
    R=np.array([[1.,0,0],[0,0,-1],[0,1,0]])
    return R@np.diag([2.57e7,3.76e5,2.57e7])@R.T


def allocate_central_body(total_mass, total_cg, total_inertia, child_masses, child_cg, child_inertia):
    """Close reference-configuration mass, CG and inertia about total CG.

    All tensors are in the same axes. Assumed child properties remain assumptions.
    Moving articulated children change the composite inertia after this pose.
    """
    M=float(total_mass);g=np.asarray(total_cg,float);I=np.asarray(total_inertia,float)
    m=np.asarray(child_masses,float);r=np.asarray(child_cg,float);J=np.asarray(child_inertia,float)
    if g.shape!=(3,) or I.shape!=(3,3) or r.shape!=(len(m),3) or J.shape!=(len(m),3,3):raise ValueError('Shape mismatch')
    if not all(np.all(np.isfinite(x)) for x in (M,g,I,m,r,J)) or np.any(m<=0) or M<=sum(m):raise ValueError('Invalid mass/inertia inputs')
    core_mass=M-sum(m);core_cg=(M*g-np.sum(m[:,None]*r,axis=0))/core_mass
    pa=lambda d:np.dot(d,d)*np.eye(3)-np.outer(d,d)
    core_I=I-sum((j+mi*pa(ri-g) for mi,ri,j in zip(m,r,J)),np.zeros((3,3)))-core_mass*pa(core_cg-g)
    if not np.allclose(core_I,core_I.T,atol=1e-6) or np.linalg.eigvalsh(core_I).min()<=0:raise ValueError('Residual central inertia is not symmetric positive definite')
    eig=np.linalg.eigvalsh(core_I)
    if eig[-1]>eig[0]+eig[1]+1e-6:raise ValueError('Residual central inertia violates triangle inequality')
    return float(core_mass),core_cg,core_I


def rotation_xyz_and_omega(angles, rates):
    """R=Rx(roll) Ry(pitch) Rz(yaw), matching existing Chrono quaternion.
    Convert Euler derivatives to spatial angular velocity; never equate them.
    """
    a,b,c=np.asarray(angles,float);ad,bd,cd=np.asarray(rates,float)
    ca,sa=np.cos(a),np.sin(a);cb,sb=np.cos(b),np.sin(b);cc,sc=np.cos(c),np.sin(c)
    rx=np.array([[1,0,0],[0,ca,-sa],[0,sa,ca]])
    ry=np.array([[cb,0,sb],[0,1,0],[-sb,0,cb]])
    rz=np.array([[cc,-sc,0],[sc,cc,0],[0,0,1]])
    return rx@ry@rz,np.array([ad,0.,0.])+rx@np.array([0.,bd,0.])+rx@ry@np.array([0.,0.,cd])


def deck_pose(row, reference_height_m, thickness_m):
    angles=[row[k] for k in ('roll_rad','pitch_rad','yaw_rad')]
    rates=[row[k] for k in ('roll_rad_s','pitch_rad_s','yaw_rad_s')]
    R,w=rotation_xyz_and_omega(angles,rates)
    origin=np.array([row[k] for k in ('surge_m','sway_m','heave_m')])
    v=np.array([row[k] for k in ('surge_m_s','sway_m_s','heave_m_s')])
    offset=R@np.array([0.,0.,reference_height_m-.5*thickness_m])
    return {'center':origin+offset,'velocity':v+np.cross(w,offset),'omega':w,'R':R,'normal':R[:,2],'origin':origin,'top':origin+R@np.array([0.,0.,reference_height_m])}


def contact_power(force, contact_point, body_cg, cg_velocity, angular_velocity):
    f,p,c,v,w=[np.asarray(x,float) for x in (force,contact_point,body_cg,cg_velocity,angular_velocity)]
    if any(x.shape[-1]!=3 for x in (f,p,c,v,w)):raise ValueError('Last axis must contain XYZ')
    return np.sum(f*(v+np.cross(w,p-c)),axis=-1)


def retain_full_history(path: Path, sim: dict):
    """Write every actually recorded solver sample, never upsample compact data."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    t=np.asarray(sim['time_s'],float)
    if len(t)<2 or np.any(np.diff(t)<=0):raise ValueError('Invalid history time')
    data=json.dumps(sim,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode('utf-8')
    path.write_bytes(data)
    return {'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'samples':len(t),'start_s':float(t[0]),'end_s':float(t[-1]),'sample_dt_median_s':float(np.median(np.diff(t))),'representation':'all recorded integration-grid samples; no resampling'}
