"""Analytical/unit tests only: no synthetic result is a landing experiment."""
import sys
from pathlib import Path
import numpy as np
import pytest
# Run from the patched project root, or set PYTHONPATH to that root.
from analysis.rocket_recovery.review_integrity import (conservative_resample, thies_total_inertia_z_up,
 allocate_central_body, rotation_xyz_and_omega, deck_pose, contact_power, retain_full_history)
from analysis.rocket_recovery.chrono_leg_model import DeckMotion
from analysis.rocket_recovery.chrono_same_platform_multibody import landing_config, coupling_work_audit
from analysis.rocket_recovery.chrono_two_way_recovery import generalized_leg_force_from_chrono_6dof

def test_missed_pulse_is_conserved():
 t=np.array([0,.002,.003,.004,.01,.02]);f=np.array([0,0,1000,0,0,0]);q=np.array([0,.01,.02])
 assert np.trapezoid(np.interp(q,t,f),q)==0
 assert np.isclose(np.trapezoid(conservative_resample(t,f,q),q),1.)

def test_six_components_nonuniform():
 rng=np.random.default_rng(41);t=np.r_[0,np.cumsum(rng.uniform(.001,.01,150))];q=np.linspace(t[0],t[-1],21);q[7]+=.0003
 f=rng.normal(size=(len(t),6))
 np.testing.assert_allclose(np.trapezoid(conservative_resample(t,f,q),q,axis=0),np.trapezoid(f,t,axis=0),atol=1e-14)

@pytest.mark.parametrize('t,f,q',[( [0,0,1],[0,1,2],[0,1]),([0,1],[0,np.nan],[0,1]),([0,1],[0,1],[0,.9]),([0,1],[0,1],[1,0])])
def test_reject_unsafe_resampling(t,f,q):
 with pytest.raises(ValueError):conservative_resample(t,f,q)

def test_inertia_permutation_and_energy():
 I=thies_total_inertia_z_up();np.testing.assert_array_equal(np.diag(I),[2.57e7,2.57e7,3.76e5])
 R=np.array([[1,0,0],[0,0,-1],[0,1,0]]);old=np.diag([2.57e7,3.76e5,2.57e7]);w=np.array([.2,.3,-.4])
 assert np.isclose((R@w)@I@(R@w),w@old@w)

def test_mass_cg_tensor_closure_in_main_config():
 c=landing_config(.0005);a=c['rocket']['review_reference_allocation'];M=c['rocket']['landing_mass_kg'];m=c['legs']['footpad_mass_kg'];rad=c['legs']['footpad_radius_m'];az=np.radians(c['legs']['azimuths_deg']);r=c['legs']['footprint_radius_m']
 feet=np.column_stack([r*np.cos(az),r*np.sin(az),np.full(4,rad)]);g=np.array(a['total_cg_m']);gc=np.array(a['central_cg_m']);Mc=a['central_mass_kg'];pa=lambda d:np.dot(d,d)*np.eye(3)-np.outer(d,d)
 np.testing.assert_allclose((Mc*gc+m*feet.sum(axis=0))/M,g,atol=1e-13)
 closed=np.array(a['central_inertia'])+Mc*pa(gc-g)+sum((.4*m*rad**2*np.eye(3)+m*pa(x-g) for x in feet),np.zeros((3,3)))
 np.testing.assert_allclose(closed,thies_total_inertia_z_up(),atol=1e-7)
 assert c['solver']['deck_geometry_m']==dict(length=120.,beam=50.,height=3.)

def test_invalid_inertia_rejected():
 with pytest.raises(ValueError):allocate_central_body(2.,[0,0,0],np.eye(3),[1.],[[100,0,0]],[np.eye(3)])

def state(t):
 return dict(surge_m=.2*t,sway_m=-.1*t,heave_m=.3*t,roll_rad=.01*t,pitch_rad=-.02*t,yaw_rad=.03*t,
             surge_m_s=.2,sway_m_s=-.1,heave_m_s=.3,roll_rad_s=.01,pitch_rad_s=-.02,yaw_rad_s=.03)

def test_pose_velocity_matches_finite_difference():
 t=.7;dt=1e-6;p=deck_pose(state(t),3.,.35);derivative=(deck_pose(state(t+dt),3.,.35)['center']-deck_pose(state(t-dt),3.,.35)['center'])/(2*dt)
 np.testing.assert_allclose(p['velocity'],derivative,atol=1e-9)
 Rdot=(deck_pose(state(t+dt),3.,.35)['R']-deck_pose(state(t-dt),3.,.35)['R'])/(2*dt)
 np.testing.assert_allclose(Rdot@p['R'].T,np.array([[0,-p['omega'][2],p['omega'][1]],[p['omega'][2],0,-p['omega'][0]],[-p['omega'][1],p['omega'][0],0]]),atol=1e-9)

def test_plane_points_and_three_metre_datum():
 t=np.array([0.,1.]);s=[state(v) for v in t];arrays={k:np.array([x[k] for x in s]) for k in s[0]}
 d=DeckMotion(time_s=t,**arrays,reference_height_m=3.)
 for v in [0,.3,1]:
  xy=d.deck_xy(v,5.,15.);z=d.deck_z(v,*xy);pose=deck_pose(state(v),3.,.35)
  assert abs(np.dot(np.array([*xy,z])-pose['top'],pose['normal']))<1e-12
 assert d.deck_z(0,0,0)==3.

def test_reference_invariant_contact_power():
 f=np.array([1.,0,0]);p=np.array([0.,1,0]);c=p.copy();v=np.zeros(3);w=np.array([0,0,1.])
 assert contact_power(f,p,c,v,w)==0
 assert np.dot(np.cross(p,f),w)==-1 # original mixed-reference counterexample


def test_full_history_hash_and_no_overwrite(tmp_path):
 import hashlib,json
 p=tmp_path/'raw.json';sim={'time_s':[0.,.001,.002],'actual_force_n':[0.,7.,0.]};r=retain_full_history(p,sim)
 assert r['samples']==3 and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 assert json.loads(p.read_text())==sim
 with pytest.raises(FileExistsError):retain_full_history(p,sim)


def test_invalid_contact_work_is_not_zero_filled():
 r=coupling_work_audit({},{});assert r['available'] is False and r['contact_pair_work_j'] is None


def test_actual_reducer_uses_conservative_transfer_and_correct_reference():
 t=np.array([0,.002,.003,.004,.01,.02]);f=np.array([0,0,1000,0,0,0]);zeros=np.zeros(len(t)).tolist();sim={'time_s':t.tolist(),'deck':{'heave_m':(np.ones(len(t))*2).tolist()},'forces':{'leg_contact_force_xyz_n':{'leg_1':{'x':zeros,'y':f.tolist(),'z':zeros}}},'feet':{'position_m':{'leg_1':{'x_m':zeros,'y_m':zeros,'z_m':(np.ones(len(t))*5).tolist()}}}}
 q=np.array([0,.01,.02]);r=generalized_leg_force_from_chrono_6dof(sim,q,footpad_radius_m=0.)
 np.testing.assert_allclose(np.trapezoid(r['values_6dof'],q,axis=0),[0,-1,0,3,0,0],atol=1e-12)
 np.testing.assert_allclose(r['force_audit']['impulse_residual_6dof'],0,atol=1e-12)
