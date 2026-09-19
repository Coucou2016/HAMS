Article

# Dynamics Modeling and Analysis of a Vertical Landing Mechanism for Reusable Launch Vehicle

Haiquan Li <sup>1,</sup>\* , Wenzhe Xu <sup>1</sup>, Yun Zhao <sup>2</sup>, Anzhu Hong <sup>2</sup>, Mingjie Han <sup>2</sup>, Haibo Ji <sup>2</sup> and Chaoyang Sun <sup>1</sup>

<sup>1</sup> School of Mechanical Engineering, University of Science and Technology Beijing, Beijing 100083, China

2 Beijing Interstellar Glory Space Technology Co., Ltd., Beijing 100176, China

Correspondence: haiquanli@ustb.edu.cn

Abstract: In this work, a vertical landing mechanism of a reusable launch vehicle (RLV) is investigated using a flexible–rigid coupled dynamics model. The presented model takes into account the four-legged landing mechanism and the main body cabin. Flexibilities of the main components in the vertical landing mechanism are considered. The hydropneumatic spring force and thrust aftereffect caused by the sequential deactivation of the engine are introduced separately. Several simulation cases are selected to analyze the loads acting on the landing mechanism and the dynamics behavior of the whole RLV system. Simulation results show that considering flexibility in the landing mechanism is critical for dynamics analysis under various initial conditions. The adopted RLV design is capable of achieving stable landings under specified initial velocity and attitude conditions, demonstrating its feasibility for engineering applications. Moreover, the hydro-pneumatic spring plays a crucial role in absorbing the impact of the initial landing leg, ensuring a smoother landing experience and minimizing potential damage to the vehicle.

Keywords: reusable launch vehicle; landing mechanism; contact dynamics; flexible–rigid coupled dynamics model

![](P5_Li_2025_Aerospace_images/3b6879054245bc4cfc6b3f32bb56a07d3a3f3a695c7cd3d152098c2e244147a4.jpg)

Academic Editor: Jae Hyun Park

Received: 15 February 2025 Revised: 25 March 2025 Accepted: 25 March 2025 Published: 27 March 2025

Citation: Li, H.; Xu, W.; Zhao, Y.; Hong, A.; Han, M.; Ji, H.; Sun, C. Dynamics Modeling and Analysis of a Vertical Landing Mechanism for Reusable Launch Vehicle. Aerospace 2025, 12, 280. https://doi.org/ 10.3390/aerospace12040280

Copyright: © 2025 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https://creativecommons.org/ licenses/by/4.0/).

## 1. Introduction

In recent years, reusable launch vehicles (RLVs) have attracted significant attention in the field of space flight and exploration. Notable contributions in areas such as control algorithms, analytical models, numerical simulations, and hardware tests have been made. As one of the most promising developments, vertical landing technology offers advantages such as a low cost, high launch efficiency, and small landing area requirements. Therefore, the design and analysis of vertical landing mechanisms are also receiving increasing attention. The landing mechanism is a vital component of the vertical landing RLVs, which is responsible for energy dissipation during the touchdown and finally facilitating a stable landing and supporting the RLV main body cabin.

The dynamic performance of the landing mechanism has a direct impact on the state and subsequent service life of the RLV. Therefore, it is necessary to analyze the dynamic performance of the vertical landing mechanism. During the touchdown phase, the rocket engine and attitude control system are deactivated. The RLV lands under the gravity force and inertia. Due to the fact that the initial attitude, velocity, and angular velocity of the RLV are uncertain and affected by factors such as lateral wind loading and thrust aftereffect, the vertical landing mechanism faces numerous challenges in the landing and touchdown phases.

To address these challenges, multiple designs of landing mechanisms have been developed to mitigate the landing impact and accommodate various initial conditions.

However, conducting a large number of physical tests is highly impractical due to the complexity and risks associated with the contact and impact [1]. As a result, numerical simulation has emerged as an effective and economical approach to predict, evaluate, and optimize the performance of landing mechanisms. For instance, DLR [2] developed the DLR FlexibleBodies library to support the object-oriented and mathematically efficient modeling of flexible bodies for the simulation of arbitrary physical systems.

In recent years, a substantial amount of research has been conducted by scholars in the field of designing and analyzing vertical landing mechanisms. Recent studies have focused on dynamics modeling and preliminary design optimization for RLVs [3], with some research exploring the spring and damping characteristics of landing mechanisms in RLVs [4]. The passive hydro-pneumatic spring is the optimal choice for achieving excellent buffering performance under very large impact loads. The stiffness of the spring is low at little displacement during landing and increases at higher displacement of the absorber. The highest stiffness of the absorber reached at the maximum spring compression guarantees that the launcher will not sink in at parking and finally touches the ground. A notable case is the development of a model for a liquid spring damper under impact conditions during vertical soft landing by Yue et al. [5,6], which was experimentally validated to be effective in analyzing the dynamics of an RLV. Yue et al. [7] also established a new nonlinear lumped parameter hydraulic model of a liquid spring damper, which was validated by a simplified single-leg impact test. Based on the same design, network-based modeling is presented [8] and analyzed for the nonlinear liquid spring damper of a vertical landing mechanism. Witte et al. [9] presented a high-fidelity numerical simulation to analyze the lander touchdown dynamics in the presence of planetary terrain features. Yu et al. [10] proposed a novel legged deployable landing mechanism for RLV, which has proved to be a potential alternative for developing future landing mechanisms after being systematically evaluated and improved. Thies [4] developed a rigid model of a legged landing mechanism with nonlinear spring characteristics, which can be used to analyze different complex landing scenarios for a stable landing to reach the parking position. In addition, the author mentioned that the current mathematical model shall be extended to a coupled simulation between rigid and flexible, which is important for the analysis of the landing dynamics.

However, despite the progress in impact and contact dynamics modeling, little attention has been paid to the flexibility of the landing mechanism. Most of them are typically modeled as rigid bodies [11,12] or simplified single flexible beams [7,13,14]. There is very limited literature focusing on flexibilities of the landing mechanism, and simulation re sults of the existing research show that structure flexibilities of the struts influence the accelerations and forces significantly [15]. During the touchdown of a landing mechanism, flexibilities of the struts and nonlinear stiffness–damping of the hydro-pneumatic springs will significantly influence the dynamics behaviors of the whole RLV. Thus, a flexible–rigid coupled model with nonlinear spring damping–stiffness enables a better assessment of actual landing performance, which is essential for reusability evaluation. Moreover, in the initial touchdown stage, the engine will be shut down. It was observed that the engine thrust does not disappear instantaneously upon the engine shutdown but exhibits an aftereffect by a stepwise decline in about 2 s. This aftereffect impacts both the acceleration and the joint reaction forces of the RLV main body cabin. Nevertheless, few studies have focused on the aftereffect during touchdown, in particular, the aftereffect acting on a flexible landing mechanism. In order to achieve reliable simulation results for some engineering designs, it is necessary to establish a flexible dynamics model with the nonlinear hydro-pneumatic springs and the stepwise thrust after-effect.

In this paper, a flexible–rigid coupled dynamics model is presented to simulate the landing mechanism of an RLV. The landing mechanism is thoroughly described, and the system load under various working conditions is analyzed, serving as a theoretical foundation and reference for practical application. The remainder of this paper is organized as follows. The landing mechanism is introduced in Section 2, including the constraints and action forces analysis of one leg in the landing mechanism. The dynamics modeling is established in Section 3, encompassing kinematics description, constraint equations, and external forces. Section 4 presents simulation cases in detail, while Section 5 displays and discusses the simulation results. Section 6 concludes this paper and outlines future work directions.

## 2. Landing Mechanisms

In this section, the landing mechanism studied in this work is introduced in detail, including the overview of the legged design, the connections, and the interactions of different parts.

## 2.1. Overview of the System

The landing process can be divided into three phases: leg deployment, controlled descent, and touchdown. The thrust vector and throttling control are all active during the deployment and the controlled descent phases, which ensure a stable landing initial velocity and attitude. When the touchpad makes contact with the ground, the thrusts and attitude controller will be shut down and the RLV lands under the action of gravity and the initial vertical velocity. Therefore, during the touchdown phase, a stable landing mainly relies on the passive effect of the landing mechanism.

The landing mechanism of the system is depicted in Figure 1. There are four legs mounted on the main body cabin of the RLV. The four-legged landing mechanism has been demonstrated as the most promising design [4], and has been widely adopted in various studies [16]. The landing legs are folded and stowed in the main body cabin before landing to reduce aerodynamic drag and protect the struts during launch [17]. The landing legs need to be fully deployed to enable a safe landing and further reuse of the RLV. During that phase, the deployment system has to overcome harsh and challenging environmental conditions. Then, after the legs have been deployed as in Figure 1, the landing comes into<sup>VIEW</sup> the touchdown phase.

![](P5_Li_2025_Aerospace_images/48f551157ac1baf6310bbcdfceed3d1665a418382df4c143b6728158027fbc5a.jpg)  
Figure 1. The landing mechanFigure 1. The landing mechanism.

Each landing leg comprises one main strut, two auxiliary struts, and a footpad. One end of the main strut is connected to the main body cabin, and the other end is The constraints and connections are shown in Figure 2. One end of both <sub>connected to the top end of the hydro-pneumatic spring, which is mounted at the lower</sub> end of the main strut to mitigate the landing impact energy. The hydro-pneumatic spring <sub>exhibits</sub> <sub>passive</sub> <sub>nonlinear</sub> <sub>spring-damping</sub> <sub>characteristics</sub> <sub>due</sub> <sub>to</sub> <sub>its</sub> <sub>compressible</sub> <sub>fluid</sub>main body cabin, resulting in redundant constraints within this mechan design. The nonlinear characteristics provide variable stiffness at different compressions ofiary struts are rigidly fixed to the footpad. Thus, the auxiliary struts and the spring, which guarantees that the RLV will not sink in during parking [4].be treated as one part to simplify the modeling and analysis. Th

## 2.2. Constraints and Action Forces

<sub>The constraints and connections are shown in Figure 2. One end of both the main</sub>eumatic spring is connected to the touchpad by a revolute joint. The h <sub>strut</sub> <sub>and</sub> <sub>the</sub> <sub>auxiliary</sub> <sub>struts</sub> <sub>is</sub> <sub>connected</sub> <sub>to</sub> <sub>the</sub> <sub>main</sub> <sub>body</sub> <sub>cabin</sub> <sub>by</sub> <sub>a</sub> <sub>revolute</sub> <sub>joint.</sub> <sub>The</sub>spring provides a nonlinear force when compressed, so it can be model rotation axes of the two joints connecting the auxiliary struts and the main body cabin aretional joint with a nonlinear spring–damper force element. collinear and parallel with the rotation axis of the joint between the main strut and the main body cabin, resulting in redundant constraints within this mechanism. Both auxiliary struts are rigidly fixed to the footpad. Thus, the auxiliary struts and the footpad can be treated as one part to simplify the modeling and analysis. The bottom end of the main strut is fixed on <sub>the</sub> <sub>top</sub> <sub>end</sub> <sub>of</sub> <sub>the</sub> <sub>hydro-pneumatic</sub> <sub>spring.</sub> <sub>The</sub> <sub>bottom</sub> <sub>end</sub> <sub>of</sub> <sub>the</sub> <sub>hydro-pneumatic</sub> <sub>spring</sub>the third one is the footpad and the auxiliary struts. The RLV has 10 D is connected to the touchpad by a revolute joint. The hydro-pneumatic spring providesfreedom) during the touchdown phase, with 6 of the main body cabin’s a nonlinear force when compressed, so it can be modeled as a translational joint with a nonlinear spring–damper force element.

![](P5_Li_2025_Aerospace_images/275dd83c91e3c10f3d6a7b32a97ee29dd620bf3d9a3cfc63035c49916c35d91d.jpg)  
Figure 2.Figure One leg in the landing mechanism.2. One leg in the landing me

In conclusion, one leg of the landing mechanism can be treated as three bodies in the modeling and analysis. The first body is the main strut with the top end of the hydropneumatic spring, the second body is the bottom end of the hydro-pneumatic spring, and the third one is the footpad and the auxiliary struts. The RLV has 10 DOFs (degrees of freedom) during the touchdown phase, with 6 of the main body cabin’s translation and rotation and 4 of the legs.

During the touchdown phase, RLV is mainly affected by gravity and contact force between the touchpad and the ground. Due to the sequential deactivation of the thrust system, the thrust aftereffect is applied to the main-body cabin with a stepwise decrease. In addition, lateral wind loads in the landing environment acting on the RLV should be taken into account. The thrust aftereffect resulting from a multistage engine cut-off operation [18] can be presented as a nonlinear function. Nonlinear regression is employed to model the thrust profile. The resulting nonlinear function can be expressed as

$$
f _ {t} = p _ {0} + \sum_ {i = 1} ^ {n} \left(p _ {i} \tanh \left(\alpha_ {i} t + \beta_ {i}\right)\right)\tag{1}
$$

where $p _ { i } , ( i = 0 , 1 , \ldots , n )$ is the magnitudes of the thrust in different stages, $\alpha _ { i }$ and $\beta _ { i }$ determine the shape details of the thrust reference profile, and n is the number of stages during the engine cut-off operations, in this work, $n = 3$

The wind load [19] is treated as a constant force acting on the windward side of the main-body cabin. The constant wind load can be calculated as

$$
f _ {\mathrm{w}} = \frac {1}{2} \rho v _ {\mathrm{w}} ^ {2} C _ {\mathrm{w}} S\tag{2}
$$

where $\rho$ is the density of the air, $v _ { \mathrm { w } }$ is the average wind velocity, $C _ { \mathrm { w } }$ is the drag coefficient and S is the normal equivalent area of the windward side. It is worth noting that due to the low descent speed of the arrow during the touchdown phase, air resistance can usually be ignored in the analysis of the touchdown dynamics

For internal forces, the main components are the constraint reaction forces between joints and the nonlinear spring-damping force provided by hydro-pneumatic springs. In this work, the spring force and damping force are modeled by the Akima cubic curve-fitting method. A set of measured motions and forces are used to calculate the parameters of the fitting function. Then, in the simulation, a stiff force component and a damping one are calculated for the given compress length and velocity.

## 3. Dynamics Modeling of the Landing Mechanism

The dynamic modeling of the landing mechanism is discussed in this section. A rigid multibody dynamics model is established using the Cartesian coordinate method [20,21], specifically the reference point method. The floating frame method [22] is employed to model flexible bodies within the system. In the presented model, the main body, the jointed points of the struts, and the footpads are treated as rigid. On the other hand, all the slender structures of the main struts, the hydro-pneumatic springs housing, and the auxiliary struts are modeled as flexible bodies.

## 3.1. Kinematics of an Arbitrary Point and a Vector

The generalized coordinates of the multibody system are

$$
\boldsymbol {q} = \left( \begin{array}{c} \boldsymbol {q} _ {1} \\ \vdots \\ \boldsymbol {q} _ {n b} \end{array} \right)\tag{3}
$$

where nb is the number of the bodies in the system. For an arbitrary rigid part $B _ { i }$ in the landing mechanism, a set of generalized coordinates are chosen as

$$
\boldsymbol {q} _ {i} = \left( \begin{array}{c} \boldsymbol {r} _ {i} \\ \boldsymbol {\theta} _ {i} \\ \boldsymbol {a} _ {i} \end{array} \right) \in \mathbb {R} ^ {6 + s}\tag{4}
$$

where $r _ { i }$ is the position vector of the body-fixed frame, and $\mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf { \theta } \mathbf \mathbf { \theta } \mathbf { \theta } \mathbf \mathbf { \theta } \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \mathbf { \theta } \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \mathbf { \theta } \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf { \theta \theta } \mathbf \mathbf { \theta \theta } \mathbf \mathbf { \theta \theta \theta \theta } \mathbf \mathbf  \theta \theta \theta \mathbf \theta \mathbf { } \theta \mathbf \theta \mathbf { \theta } \mathbf \theta \mathbf \theta \mathbf  \theta \theta \theta \theta \theta \mathbf \theta \theta \mathbf \theta \theta \mathbf \theta \theta \mathbf \theta \mathbf \theta \mathbf \theta \theta \mathbf \theta \mathbf \theta \mathbf \theta \mathbf \mathbf \theta \mathbf \theta \mathbf \theta \mathbf \mathbf \theta \mathbf \theta \mathbf \mathbf \theta \mathbf \mathbf \mathbf \theta \mathbf \mathbf \theta \mathbf \mathbf \mathbf \theta \mathbf $ are the Cardan angles in the 1-2-3 body-fixed rotation sequence [23], and $a _ { i } \in \mathbb { R } ^ { s }$ is the vector of the truncated modal coordinates introduced to capture the deformation of flexible bodies, where s is the number of the selected first modal orders of the flexible body.

The global position of an arbitrary point $P$ of the body $B _ { i }$ could be defined as

$$
\boldsymbol {r} _ {i} ^ {P} = \boldsymbol {r} _ {i} + \boldsymbol {\rho} _ {i} ^ {P} = \boldsymbol {r} _ {i} + \boldsymbol {\rho} _ {i} ^ {P 0} + \boldsymbol {u} _ {i} ^ {P} = \boldsymbol {r} _ {i} + A _ {i} \boldsymbol {\rho} _ {i} ^ {' P 0} + A _ {i} \boldsymbol {\Phi} _ {i} ^ {' P} \boldsymbol {a} _ {i} \in \mathbb {R} ^ {3}\tag{5}
$$

where $\rho _ { i } ^ { P }$ denotes the vectors from the origin of the body-fixed frame to point $P$ expressed in the global frame after deformation. $\rho _ { i } ^ { P 0 }$ and $\rho _ { \textit { i } } ^ { \prime P 0 }$ are the vectors from the body-fixed frame to the undeformed point $P ^ { 0 }$ expressed in the global and body-fixed frame, respectively, where $\rho _ { i } ^ { \prime P 0 }$ is constant. The symbol ′ depicts the local expression in the body-fixed frame of a vector, so $\boldsymbol { d } _ { i } ^ { \prime } \in \mathbb { R } ^ { 3 }$ is the local expression of $d _ { i } . u _ { i } ^ { P } = \hat { \pmb { \rho } } _ { i } ^ { P } - \pmb { \rho } _ { i } ^ { P 0 }$ is the deformation vector of point $P , A _ { i }$ is the direction cosine matrix of $B _ { i } , \boldsymbol { \Phi } _ { i } ^ { \prime P } \in \mathbb { R } ^ { 3 \times s }$ is the translational modal matrix expressed in the body-fixed frame, which is a constant matrix. For a rigid body, the deformation $\pmb { u } _ { i } ^ { P }$ is set to be zero, then the modal coordinates $\mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf { } \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf { } \mathbf \mathbf { } \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf  \mathbf { } \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf { } \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf \mathbf$ vanish.

When the Cardan angles in 1-2-3 body-fixed rotation are used, the direction cosine matrix of $B _ { i }$ is defined as

$$
\boldsymbol {A} _ {i} = \left( \begin{array}{c c c} C _ {2} C _ {3} & - C _ {2} S _ {3} & S _ {2} \\ S _ {1} S _ {2} C _ {3} + C _ {1} S _ {3} & - S _ {1} S _ {2} S _ {3} + C _ {1} C _ {3} & - S _ {1} C _ {2} \\ - C _ {1} S _ {2} C _ {3} + S _ {1} S _ {3} & C _ {1} S _ {2} S _ {3} + S _ {1} C _ {3} & C _ {1} C _ {2} \end{array} \right) _ {i} \in \mathbb {R} ^ {3 \times 3}\tag{6}
$$

where $C _ { k } = \cos ( \theta _ { k } ) , S _ { k } = \sin ( \theta _ { k } ) , k = 1 , 2 , 3$

The velocity and acceleration of the point P can be calculated by taking the first and second derivatives of Equation (5) as

$$
\dot {\boldsymbol {r}} _ {i} ^ {P} = \dot {\boldsymbol {r}} _ {i} + \dot {\boldsymbol {\rho}} _ {i} ^ {P 0} + \dot {\boldsymbol {u}} _ {i} ^ {P} = \dot {\boldsymbol {r}} _ {i} - (\tilde {\boldsymbol {\rho}} _ {i} ^ {P 0} + \tilde {\boldsymbol {u}} _ {i} ^ {P}) \boldsymbol {\omega} _ {i} + \boldsymbol {A} _ {i} \boldsymbol {\Phi} _ {i} ^ {' P} \dot {\boldsymbol {a}} _ {i} = \dot {\boldsymbol {r}} _ {i} - \tilde {\boldsymbol {\rho}} _ {i} ^ {P} \boldsymbol {\omega} _ {i} + \boldsymbol {A} _ {i} \boldsymbol {\Phi} _ {i} ^ {' P} \dot {\boldsymbol {a}} _ {i}\tag{7}
$$

$$
\ddot {\boldsymbol {r}} _ {i} ^ {P} = \ddot {\boldsymbol {r}} _ {i} - \tilde {\boldsymbol {\rho}} _ {i} ^ {P} \dot {\boldsymbol {\omega}} _ {i} + A _ {i} \boldsymbol {\Phi} _ {i} ^ {' P} \ddot {\boldsymbol {a}} _ {i} + \tilde {\boldsymbol {\omega}} _ {i} \tilde {\boldsymbol {\omega}} _ {i} \boldsymbol {\rho} _ {i} ^ {P} + 2 \tilde {\boldsymbol {\omega}} _ {i} A _ {i} \boldsymbol {\Phi} _ {i} ^ {' P} \dot {\boldsymbol {a}} _ {i}\tag{8}
$$

where $\omega _ { i }$ is the angular velocity expressed in the global frame, and the relationship between $\omega _ { i }$ and the generalized velocities $\pmb \theta _ { i }$ is

$$
\pmb {\omega} _ {i} = \pmb {K} _ {i} \dot {\pmb {\theta}} _ {i} \in \mathbb {R} ^ {3}\tag{9}
$$

where

$$
\boldsymbol {K} _ {i} = \left( \begin{array}{c c c} 1 & 0 & S _ {2} \\ 0 & C _ {1} & - C _ {2} S _ {1} \\ 0 & S _ {1} & C _ {2} C _ {1} \end{array} \right) _ {i} \in \mathbb {R} ^ {3 \times 3}\tag{10}
$$

The symbol \~ indicates that the components of the associated vector are used to generate a skew-symmetric $3 \times 3$ matrix [24] as

$$
\boldsymbol {p} = \left( \begin{array}{c} p _ {1} \\ p _ {2} \\ p _ {3} \end{array} \right) \Leftrightarrow \tilde {\boldsymbol {p}} = \left( \begin{array}{c c c} 0 & - p _ {3} & p _ {2} \\ p _ {3} & 0 & - p _ {1} \\ - p _ {2} & p _ {1} & 0 \end{array} \right)\tag{11}
$$

To depict the rotation kinematics of the system, the global expression of an arbitrary body-fixed local vector is defined as

$$
\boldsymbol {d} _ {i} ^ {P} = \boldsymbol {A} _ {i} \boldsymbol {R} _ {i} ^ {P} \boldsymbol {d} _ {i} ^ {' P} \in \mathbb {R} ^ {3}\tag{12}
$$

where $R _ { i } ^ { P } \in \mathbb { R } ^ { 3 \times 3 }$ is the rotation matrix caused by local deformation of the mounted position of vector $d _ { i } ^ { P }$

The rotation caused by local deformation are defined as

$$
\boldsymbol {R} _ {i} ^ {P} = \boldsymbol {I} _ {3} + \widetilde {\boldsymbol {\Psi} _ {i} ^ {P} \boldsymbol {a} _ {i}} \in \mathbb {R} ^ {3 \times 3}\tag{13}
$$

where $I _ { 3 } \in \mathbb { R } ^ { 3 \times 3 }$ is the $3 \times 3$ identity matrix, and $\pmb { \mathcal { T } } _ { i } ^ { P } \in \mathbb { R } ^ { 3 \times s }$ is the rotational modal matrix.

## 3.2. Constraint Equations

In the presented system, there are two kinds of joints, the revolute joint and the cylindrical one, as shown in Figure 2.

A revolute joint between two bodies $B _ { i }$ and $B _ { j }$ consists of three relative displacement constraints and two relative rotation constraints. The three relative displacement constraint means that point P of body $B _ { i }$ coincides with point Q of body $B _ { j }$

$$
\boldsymbol {C} ^ {\mathrm{(d3)}} = \boldsymbol {r} _ {i} ^ {P} - \boldsymbol {r} _ {j} ^ {Q} = \boldsymbol {0}\tag{14}
$$

The two relative rotation constraints are defined as

$$
\boldsymbol {C} ^ {\mathrm{(r2)}} = \binom{\boldsymbol {d} _ {i} ^ {u \mathrm{T}} \boldsymbol {d} _ {j} ^ {w}}{\boldsymbol {d} _ {i} ^ {v \mathrm{T}} \boldsymbol {d} _ {j} ^ {w}} = \boldsymbol {0}\tag{15}
$$

where $d _ { i } ^ { u }$ and $d _ { i } ^ { v }$ are two vectors fixed on body $B _ { i } , d _ { j } ^ { w }$ is a vector fixed on body $B _ { j }$ in the direction of the revolute axis.

A cylindrical joint between two bodies consists of two relative displacement constraints

$$
\boldsymbol {C} ^ {\mathrm{(d2)}} = \binom{\boldsymbol {d} _ {i} ^ {u \mathrm{T}} (\boldsymbol {r} _ {i} ^ {P} - \boldsymbol {r} _ {j} ^ {Q})}{\boldsymbol {d} _ {i} ^ {v \mathrm{T}} (\boldsymbol {r} _ {i} ^ {P} - \boldsymbol {r} _ {j} ^ {Q})} = \boldsymbol {0}\tag{16}
$$

and two relative rotation constraints, as expressed in Equation (15).

The method of Lagrange multipliers can be used to describe the constraint forces as

$$
\boldsymbol {F} ^ {c} = \boldsymbol {C} _ {q} ^ {\mathrm{T}} \boldsymbol {\lambda}\tag{17}
$$

where $C _ { q }$ is the constraint Jacobian matrix and λ is a vector of the Lagrange multipliers.

## 3.3. Dynamic Equation

The principle of virtual work can be developed, and dynamic equilibrium condition for a free particle P implies that

$$
\delta \dot {\pmb {r}} _ {i} ^ {P T} (- m _ {i} ^ {P} \ddot {\pmb {r}} _ {i} ^ {P} + \pmb {F} _ {i} ^ {P}) = \pmb {0}\tag{18}
$$

where $F _ { i } ^ { P }$ is the force act on the particle $P , m _ { i } ^ { P }$ is the mass of P. If the finite element method (FEM) is used to analysis a flexible body, the particle $P$ can be replaced by a node and $m _ { i } ^ { P }$ is the lumped mass of node $P .$

The dynamic equation of a free flexible body $B _ { i }$ with $n _ { P }$ nodes can be written as

$$
\sum_ {i = 0} ^ {n _ {P}} \delta \dot {\boldsymbol {r}} _ {i} ^ {P \mathrm{T}} (- m _ {i} ^ {P} \ddot {\boldsymbol {r}} _ {i} ^ {P} + \boldsymbol {F} _ {i} ^ {P}) - \delta \dot {\boldsymbol {a}} _ {i} ^ {\mathrm{T}} (\boldsymbol {C} _ {i} \dot {\boldsymbol {a}} _ {i} + \boldsymbol {K} _ {i} \boldsymbol {a} _ {i}) = \boldsymbol {0}\tag{19}
$$

where $C _ { i }$ and $K _ { i }$ are modal damping and stiffness matrices of the body. The last term of Equation (19) describes the internal deformation force and damping between different nodes in the same flexible body.

With the use of Equations (7) and (8), Equation (19) leads to

$$
\delta \dot {\boldsymbol {q}} _ {i} ^ {\mathrm{T}} (- \boldsymbol {M} _ {i} \ddot {\boldsymbol {q}} _ {i} - \boldsymbol {f} _ {i} ^ {\mathrm{w}} + \boldsymbol {f} _ {i} ^ {\mathrm{o}} - \boldsymbol {f} _ {i} ^ {\mathrm{u}}) = \boldsymbol {0}\tag{20}
$$

where $M _ { i }$ is the generalized mass matrix of the body; $f _ { i } ^ { \mathrm { o } } , f _ { i } ^ { \mathrm { w } } ,$ , and $f _ { i } ^ { \mathrm { u } }$ are the vectors of generalized external force, generalized inertial force, and generalized deformation force, respectively. It is noticeable that the generalized mass matrix includes the translational part and the rotation part as

$$
\boldsymbol {M} _ {i} = \left( \begin{array}{c c} m _ {i} \boldsymbol {I} _ {3} & \\ & \tilde {\omega} \boldsymbol {J} \omega \end{array} \right)\tag{21}
$$

where $m _ { i }$ is the mass of the body and J is the moment of inertia matrix. By introducing the Lagrange multipliers to describe the constraints, the dynamic equation of the body can be written as

$$
\delta \dot {\pmb {q}} _ {i} ^ {\mathrm{T}} (\pmb {M} _ {i} \ddot {\pmb {q}} _ {i} + \pmb {f} _ {i} ^ {\mathrm{w}} - \pmb {f} _ {i} ^ {\mathrm{o}} + \pmb {f} _ {i} ^ {\mathrm{u}} + \pmb {C} _ {q i} ^ {\mathrm{T}} \pmb {\lambda} _ {i}) = \pmb {0}\tag{22}
$$

The augmented form of the dynamic equations, including constraints and forces, can be written as

$$
\left( \begin{array}{c c} \boldsymbol {M} & \boldsymbol {C} _ {q} ^ {\mathrm{T}} \\ \boldsymbol {C} _ {q} & \boldsymbol {0} \end{array} \right) \binom{\ddot {\boldsymbol {q}}}{\lambda} = \binom{\boldsymbol {Q}}{\gamma}\tag{23}
$$

where M is the generalized mass matrix of the system, $\ddot { \pmb q }$ is the generalized acceleration, Q is the generalized force vector, and $\gamma$ is the right term of the second order constraint equation. Given a set of initial conditions, the acceleration vector can be integrated to obtain the velocities and the generalized coordinates [22].

## 4. Numerical Simulations

Numerical simulations of the landing mechanism are performed in this section. The multibody dynamics simulation is performed with MSC Adams, and the thrust aftereffect is fitted by the nonlinear fitting library LsqFit in Julia language. The parameters of the simulation model are specified, such as mass and inertia. Several simulation cases are selected to examine the dynamic characteristics of the landing mechanism.

## 4.1. Parameters

The mass parameters of the landing mechanism are listed in Table 1, where the mass deviation caused by fuel residues before landing is included in the mass and moment of inertia. The mass center is at [0 m, 0 m, 5.64 m] from the bottom center of the main body cabin, where the first two coordinates are along the lateral direction and the third is along the vertical direction. The whole length of the main body cabin is about 15.4 m; thus, the height of the mass center is much lower than that of the geometric center.

Table 1. Mass parameters of the landing mechanism.

<table><tr><td>Part</td><td>Mass (kg)</td><td> $I_{xx}$ </td><td> $I_{yy}$ </td><td> $I_{zz}$ </td></tr><tr><td>Main body cabin</td><td>8325.38 kg</td><td> $1.628 \times 10^{5} \text{kgm}^{2}$ </td><td> $1.629 \times 10^{5} \text{kgm}^{2}$ </td><td> $9.37 \times 10^{3} \text{kgm}^{2}$ </td></tr><tr><td>Main strut</td><td>43.64 kg</td><td> $7.47 \text{kgm}^{2}$ </td><td> $7.46 \text{kgm}^{2}$ </td><td> $0.16 \text{kgm}^{2}$ </td></tr><tr><td>Auxiliary strut</td><td>191.70 kg</td><td> $65.8 \text{kgm}^{2}$ </td><td> $55.3 \text{kgm}^{2}$ </td><td> $1.18 \text{kgm}^{2}$ </td></tr><tr><td>Spring</td><td>28.38 kg</td><td> $2.55 \text{kgm}^{2}$ </td><td> $2.54 \text{kgm}^{2}$ </td><td> $0.075 \text{kgm}^{2}$ </td></tr></table>

The load parameters used in the model are listed in Table 2. And the normalized thrustle 2. Load parameters of the landing mechanism model. aftereffect fitting result is shown in Figure 3, where the value 1 of the thrust equals the initial maximum thrust. It can be observed that the fitting result as Equation (1) matches well with the measured value.

Table 2. Load parameters of the landing mechanism model.

<table><tr><td>Parameter</td><td>Value</td><td>Parameter</td><td>Value</td></tr><tr><td>Wind velocity</td><td>10 m/s</td><td>Contact stiffness</td><td> $1 \times 10^{8}$  N/m</td></tr><tr><td>Drag factor</td><td>0.9</td><td>Contact damping</td><td> $1 \times 10^{7}$  Ns/m</td></tr><tr><td>Windward area</td><td>45.3  $m^{2}$ </td><td>Contact radius</td><td>0.2 m</td></tr><tr><td>Air density</td><td>1.29 kg/ $m^{3}$ </td><td>Contact exponent</td><td>2.0</td></tr><tr><td>Static friction</td><td>0.6</td><td>Dynamical friction</td><td>0.4</td></tr></table>

![](P5_Li_2025_Aerospace_images/a8f6d0c18cc180a07a9869d117b515f629b33ac0e8c15598dfb6200a9dfff682.jpg)  
Figure 3. Fitting result of the normalized thrust aftereffect.

## 4.2. Modal Shapes of Flexible Bodies

In the floating frame formulation, several truncated modal shapes of flexible bodies are used to describe the dynamics and flexibility of RLV, and the first three modal shapes of each flexible body are illustrated in Figure 4, where different colors represent the deformations of the elements. The modal analysis is performed by the commercial software ANSYS 2020, where the tetrahedron solid elements are primarily employed for meshing. And hexahedral solid elements are adopted in regions with geometrically simple regular structures.

![](P5_Li_2025_Aerospace_images/79c067063d88fee1054dc1bd3e440a2256f6235bb45fd4987621a66414a80dce.jpg)  
(a1)

![](P5_Li_2025_Aerospace_images/02142a1e6dcbece7fb873bd3fcb95162656a0d95500568239bee63e5362529b9.jpg)

![](P5_Li_2025_Aerospace_images/d17537c10791c7199b95727c157c9b1eb3fc3bfc07990e94b849cf99b4bd348a.jpg)

![](P5_Li_2025_Aerospace_images/3d2ba78b643701429dfc01a34a2439bc3159d6fbcaaec7a349c7600b8bcedafb.jpg)  
(a2)

![](P5_Li_2025_Aerospace_images/976b47b35b8f914ba0b1ad695c998ead5e1c2af30614446fb31aa165299e0ba6.jpg)

![](P5_Li_2025_Aerospace_images/385839074df88d2ba139d9021959092e232f9c943ddd957517c4be16e64569d8.jpg)

![](P5_Li_2025_Aerospace_images/2d46991af7b009ab88978cb9087cb3e6e24c6d8561030e8f56e4abf3ce078f7c.jpg)

![](P5_Li_2025_Aerospace_images/b695435b39734d8188d6365b3b10600ada864a6bd779bc73c7e160adf25e0e86.jpg)  
(b3)

![](P5_Li_2025_Aerospace_images/baf5a179d18849c696b83423de601c3cd1055056ab780bf244baf29f58777d4e.jpg)  
(c3)  
Figure 4. The first three modal shapes of flexible bodies, (deformation unit: m): (a1–a3) the first three modal shapes of the auxiliary strut with footpad, (b1–b3) the first three modal shapes of the main strut, (c1–c3) the first three modal shapes of the spring housing.

## 4.3. Simulation Cases

Simulation CasesIn order to analyze the landing dynamics, six simulation cases are conducted as follows:

1. Cases 1 and 2 are simulations for comparison between rigid and flexible models;

2. Case 3 is the simulation for a larger initial landing velocity compared with case 2;

3. Case 4 provides results for load analysis of a single landing mechanism;

2. Case 3 is the simulation for a larger initial landing velocity compared wit<sub>4. Cases 5 and 6 are simulations for the landing stability and lateral motion analysis.</sub>

Two main landing modes are adopted as the 1-2-1 mode and the 2-2 mode [5]. The 4. Cases 5 and 6 are simulations for the landing stability and lateral motion an<sub>initial conditions of different simulations can be found in Table 3, which are illustrated in</sub> Two main landing modes are adopted as the 1-2-1 mode and the 2-2 modeFigure 5, where the wind load acts on the center of pressure of the main body cabin, and the initial conditions of diferent simulations can be found in Table 3, which are illusthrust aftereffect acts on the bottom center of the main body cabin. In the vertical landing, the 1-2-1 mode refers to a sequence in which one leg (leg 1 in Figure 5c) comes into contact with the ground first, followed by two legs (legs 2 and 4 in Figure 5c) making simultaneous contact, and the final leg (leg 1 in Figure 5c) makes contact with the ground. Due to the fact that all reaction forces act on only one leg, the load on the first contact phase is larger than in other modes, resulting in a higher bearing capacity in this leg compared to other landing modes. In contrast, the 2-2 mode exhibits the smallest torque caused by the contact between the ground and the footpad due to its shortest lever arm. Consequently, the stability of this mode is lowest compared to other landing modes. Based on the above analysis, we studied the two modes to investigate the dynamics characteristics and performance of the landing mechanism.

(d)  
Table 3. Initial conditions.

<table><tr><td>Case</td><td>Vertical Velocity</td><td>Lateral Velocity</td><td>Initial Orientation</td><td>Angular Velocity</td><td>Thrust Aftereffect</td><td>Wind Load</td></tr><tr><td>1</td><td>1.8 m/s</td><td>0 m/s</td><td> $[0, 0, 0]^{\circ}$ </td><td> $[0, 0, 0]^{\circ}/s$ </td><td>no</td><td>no</td></tr><tr><td>2</td><td>1.8 m/s</td><td>0 m/s</td><td> $[0, 0, 0]^{\circ}$ </td><td> $[0, 0, 0]^{\circ}$ </td><td>no</td><td>no</td></tr><tr><td>3</td><td>2.45 m/s</td><td>0 m/s</td><td> $[0, 0, 0]^{\circ}$ </td><td> $[0, 0, 0]^{\circ}$ </td><td>no</td><td>no</td></tr><tr><td>4</td><td>1.8 m/s</td><td>-1.5 m/s</td><td> $[0, 4, 0]^{\circ}$ </td><td> $[0, 4, 0]^{\circ}/s$ </td><td>no</td><td>yes</td></tr><tr><td>5</td><td>1.8 m/s</td><td>-1.5 m/s</td><td> $[45, 4, 0]^{\circ}$ </td><td> $[0, 4, 0]^{\circ}/s$ </td><td>yes</td><td>yes</td></tr><tr><td>6</td><td>1.8 m/s</td><td>-1.5 m/s</td><td> $[45, 4, 0]^{\circ}$ </td><td> $[3, 4, 0]^{\circ}/s$ </td><td>yes</td><td>yes</td></tr></table>

![](P5_Li_2025_Aerospace_images/7e6face9e6da75e1cc89a9caba55765af786c942fba20afb821242917f64447d.jpg)

![](P5_Li_2025_Aerospace_images/e653e8789f5a9cc6fd340396e6a2d4a7f3d8462953d30e7e397a0ef166530ad8.jpg)

![](P5_Li_2025_Aerospace_images/3ee62fe85597d257c6fdb5132ce1cc57b7f7fd145cf571981561fc1d7b69c38b.jpg)  
ground  
(c)

![](P5_Li_2025_Aerospace_images/d7fe94285e14ad68912419adab43e1cf899939a0f2547087771ac281e93e6023.jpg)  
Figure 5. Initial conditions of the landing simulation: (a) 1-2-1 mode used in case 4, (b) 2-2 Figure 5. Initial conditions of the landing simulation: (a) 1-2-1 mode used in case 4, (b) 2-2 mode used in cases 5 and $6 , ( \mathbf { c } )$ top view of the 1-2-1 mode, (d) top view of the 2-2 mode.

## 5. Discussion

Simulation results are presented and discussed in this section. The analysis began <sup>Vertical Lateral Initial Angular Thrust</sup>with a comparison between a rigid model and a flexible–rigid coupled model to assess <sup>Velocity Velocity Orientation Velocity Afterefect</sup> the impact of flexibility on landing performance, which was followed by a comparison <sup>1</sup> <sup>1.8</sup> <sup>m/s</sup> <sup>0</sup> <sup>m/s</sup> <sup>[0,</sup> <sup>0,</sup> <sup>0]°</sup> <sup>[0,</sup> <sup>0,</sup> <sup>0]°/s</sup> <sup>no</sup> <sup>no</sup>between cases 2 and 3 with different initial vertical landing velocities. Then, by comparing 2 1.8 m/s 0 m/s <sup>[0,</sup> <sup>0,</sup> <sup>0]°</sup> <sup>[0,</sup> <sup>0,</sup> <sup>0]°</sup> no nothe simulation results of cases 4–6, the lateral displacement and velocity during the landing 3 2.45 m/s 0 m/s [0, 0, 0]° [0, 0, 0]° no notouchdown phase were analyzed. Finally, the load status during single-leg landing in 4 1.8case 4 was analyzed.

## 5.1. Comparison Between the Rigid Model and the Coupled One

First, the simulation results of the rigid body model in case 1 and the flexible body model with the first five modes in case 2 are compared. Since the key aspect of vertical landing is the touchdown phase after contact occurs, the following figure shows the vertical Simulation results are presented and discussed in this section. The analysis bmotion of the main body within 0–0.2 s. It can be observed from Figures 6 and 7 that with a comparison between a rigid model and a flexible–rigid coupled model to assealthough there are no significant differences in displacement and velocity between different impact of flexibility on landing performance, which was followed by a comparisomodel simulation results, there are obvious differences in the accelerations as shown in

<sub>Figure</sub> <sub>8.</sub> <sub>The</sub> <sub>flexible</sub> <sub>body</sub> <sub>model</sub> <sub>reflects</sub> <sub>the</sub> <sub>significant</sub> <sub>vibrations</sub> <sub>caused</sub> <sub>by</sub> <sub>structural</sub>in Figure 8. The flexible body model reflects the significant vibrations caused by structural flexibility during the decay of vertical acceleration.flexibility during the decay of vertical acceleration.  
![](P5_Li_2025_Aerospace_images/c0d946bb0644c5a76ef5bc675769bfedd5f9e7b0a667d09abbce027ac80f5c37.jpg)

![](P5_Li_2025_Aerospace_images/e12db4874194fbdda807a91babf52dca063a4593ebb02c48bd7585d84eec16c5.jpg)  
Figure 6. Vertical displacement of the flexible and the rigid model: (a) displacement, (b) error be-<sub>Figure</sub> <sub>6.</sub> <sub>Vertical</sub> <sub>displacement</sub> <sub>of</sub> <sub>the</sub> <sub>flexible</sub> <sub>and</sub> <sub>the</sub> <sub>rigid</sub> <sub>model:</sub> <sub>(a)</sub> <sub>displacement,</sub> <sub>(b)</sub> <sub>error</sub> <sub>between</sub>Figure 6. Vertical displacement of the flexible and the r gid model: (a) displacement, (b) e ror between the two mthe two model.tween the two

![](P5_Li_2025_Aerospace_images/eab836e4f2400afafdd420c58fadeaf8441650aa1523237db9b1b6aab51bdb06.jpg)

![](P5_Li_2025_Aerospace_images/6a49117d978dc51e0e80365bf4bc47a4cbf74c1dec9308c672f23384651f34e1.jpg)  
Figure 7. Vertical velocity of the flexible and the rigid model: (a) velocity, (b) error between the twoFigure 7. Vertical velocity of the flexible and the rigid model: (a) velocity, (b) error between the model.two model.

To further analyze the contribution of selecting different modal orders in the flexible model on simulation results, we compared the accelerations of case 2 under different modal orders: retaining no modal shape (rigid body), and one, three, or five modal shapes. In Figure 9a, Ni represents retaining the first i modal shapes, while Figure 9b shows the error between results with different modal orders and N5. It can be observed that consistent simulation results are achieved by retaining three or more modal shapes. Therefore, in subsequent simulations, we will retain the first three modal shapes of each flexible component for analysis.

![](P5_Li_2025_Aerospace_images/444653c6a647299b615366736be52ed98b6adffe023adb0490dadac864665b58.jpg)

![](P5_Li_2025_Aerospace_images/9977429f82ea88e0a94a663c5b435d01e02549b4077c23ab0bd4a4909a76ee1f.jpg)  
Figure 8. Vertical acceleration of the flexible and the rigid model: (a) acceleration, (b) error between <sub>Figure</sub> <sub>8.</sub> <sub>Vertical</sub> <sub>acceleration</sub> <sub>of</sub> <sub>the</sub> <sub>flexible</sub> <sub>and</sub> <sub>the</sub> <sub>rigid</sub> <sub>model:</sub> <sub>(a)</sub> <sub>acceleration,</sub> <sub>(b)</sub> <sub>error</sub> <sub>between</sub>  acceleration of the flexible and the rigid model: (a) acceleration, (b) error betwee the two modelsthe two models.

![](P5_Li_2025_Aerospace_images/6911718b5e2f59339cf9bdc88b7ac41156e0dfe5ca78e2128400f0eae20dd223.jpg)

![](P5_Li_2025_Aerospace_images/32523bde239f6519764511b2ef53987310521d4f22608d68eb29e3091c61b5e4.jpg)  
<sup>Figure</sup> <sup>9.</sup> <sup>Vertical</sup> <sup>acceleration</sup> <sup>of</sup> <sup>the</sup> <sup>flexible</sup> <sup>model</sup> <sup>with</sup> <sup>diferent</sup> <sup>orders</sup> <sup>of</sup> <sup>selected</sup> <sup>modal</sup> <sup>shapes</sup>Figure 9. Vertical acceleration of the flexible model with different orders of selected modal shapes: (a) acceleration, (b) error compared with the results of N(a) acceleration, (b) error compared with the results of N5.

## <sup>5.2.</sup> <sup>Comparison</sup> <sup>Between</sup> <sup>Diferent</sup> <sup>Initial</sup> <sup>Velocities</sup>5.2. Comparison Between Different Initial Velocities

<sup>In</sup> <sup>this</sup> <sup>subsection,</sup> <sup>the</sup> <sup>influence</sup> <sup>of</sup> <sup>initial</sup> <sup>velocity</sup> <sup>is</sup> <sup>discussed</sup> <sup>by</sup> <sup>comparing</sup> <sup>the</sup> <sup>re-</sup>In this subsection, the influence of initial velocity is discussed by comparing the results sults of cases 2 and 3, where 1.8 m/s and 2.45 m/s are adopted as the initial vertical velocity <sub>of cases 2 and 3, where 1.8 m/s and 2.45 m/s are adopted as the initial vertical velocity</sub> according to the standards [25] in the U.S. and the test requirements [26] in China. The according to the standards [25] in the U.S. and the test requirements [26] in China. The contact forces and spring forces are shown in Figure 10. From the comparison, it can be contact forces and spring forces are shown in Figure 10. From the comparison, it can be observed that higher initial velocity leads to larger contact force and spring compression, <sub>o</sub>b<sub>serve</sub>d <sub>t</sub>h<sub>at</sub> h<sub>ig</sub>h<sub>er initia</sub>l <sub>ve</sub>l<sub>ocity</sub> l<sub>ea</sub>d<sub>s to</sub> l<sub>arger contact</sub> f<sub>orce an</sub>d <sub>spring compression,</sub> <sup>and</sup> <sup>the</sup> <sup>descending</sup> <sup>overall</sup> <sup>trends</sup> <sup>of</sup> <sup>the</sup> <sup>loads</sup> <sup>are</sup> <sup>similar.</sup> <sup>Due</sup> <sup>to</sup> <sup>the</sup> <sup>fact</sup> <sup>that</sup> <sup>the</sup> <sup>actual</sup> <sub>and the descending overall trends of the loads are similar. Due to the fact that the actual</sub> maximum initial velocity measured in the hardware test of the adopted RLV is slightly below 1.8 m/s, the initial value in the following cases is set to be 1.8 m/s.

![](P5_Li_2025_Aerospace_images/cd3d27514611a4b47bc7cb36d266de2c47c0cd14d38e5a24b0d1db0fa85511c3.jpg)

![](P5_Li_2025_Aerospace_images/20b4aa7a7b49836d2e6d7468085a1f4b3268be5a276716ec775b094811021601.jpg)  
igure 10. Contact and spring forces of diferent initial vertical velocities: (a) contact force, (b) Figure 10. Contact and spring forces of different initial vertical velocities: (a) contact force, pring force.(b) spring force.

## 5.3. Analysis of Lateral Motion

<sub>Figures</sub> <sub>11</sub> <sub>and</sub> <sub>12</sub> <sub>present</sub> <sub>the</sub> <sub>lateral</sub> <sub>displacement</sub> <sub>and</sub> <sub>velocity</sub> <sub>of</sub> <sub>the</sub> <sub>main</sub> <sub>body</sub>The contact forces of cases 5 and 6 are depicted in Figures 15 and 16, respectively, cabin’s center of mass during the touchdown phase under different initial conditions. As<sup>providing</sup> <sup>a</sup> <sup>comparison</sup> <sup>with</sup> <sup>single-legged</sup> <sup>landing.</sup> <sup>It</sup> <sup>is</sup> <sup>observed</sup> <sup>that</sup> <sup>the</sup> <sup>maximum</sup> <sup>con-</sup> <sub>shown, for the 1-2-1 mode in case 4, since the touchpad experiences a larger moment arm,</sub><sup>act</sup> <sup>force</sup> <sup>values</sup> <sup>in</sup> <sup>both</sup> <sup>cases</sup> <sup>5</sup> <sup>and</sup> <sup>6</sup> <sup>are</sup> <sup>significantly</sup> <sup>smaller</sup> <sup>compared</sup> <sup>to</sup> <sup>the</sup> <sup>single-</sup> <sub>it</sub> <sub>generates</sub> <sub>a</sub> <sub>greater</sub> <sub>torque</sub> <sub>than</sub> <sub>the</sub> <sub>2-2</sub> <sub>mode,</sub> <sub>ultimately</sub> <sub>enabling</sub> <sub>the</sub> <sub>RLV</sub> <sub>to</sub> <sub>stabilize</sub><sup>egged</sup> <sup>landing</sup> <sup>in</sup> <sup>case</sup> <sup>4.</sup> <sup>It</sup> <sup>can</sup> <sup>be</sup> <sup>observed</sup> <sup>that</sup> <sup>in</sup> <sup>both</sup> <sup>of</sup> <sup>these</sup> <sup>operating</sup> <sup>conditions,</sup> <sup>two</sup> <sub>relatively quickly. However, under the 2-2 mode in cases 5 and 6, the lateral oscillations</sub>egs first make contact with the ground. Subsequently, after several seconds, the other two of the main body cabin’s center of mass are significantly more intense, and even after 10 s<sup>egs</sup> <sup>touched</sup> <sup>the</sup> <sup>ground.</sup> <sup>Consequently,</sup> <sup>the</sup> <sup>entire</sup> <sup>touchdown</sup> <sup>phase</sup> <sup>becomes</sup> <sup>longer,</sup> <sup>dur-</sup> following the contact, stability has not been fully achieved. Additionally, there is a notable<sup>ng</sup> <sup>which</sup> <sup>lateral</sup> <sup>oscillations</sup> <sup>of</sup> <sup>the</sup> <sup>main</sup> <sup>body</sup> <sup>cabin</sup> <sup>occur.</sup> <sup>Moreover,</sup> <sup>it</sup> <sup>can</sup> <sup>be</sup> <sup>seen</sup> <sup>that</sup> deviation between the landing point and the horizontal position of the center of mass at<sup>he</sup> <sup>contact</sup> <sup>forces</sup> <sup>of</sup> <sup>all</sup> <sup>four</sup> <sup>legs</sup> <sup>reach</sup> <sup>a</sup> <sup>stable</sup> <sup>average</sup> <sup>value</sup> <sup>at</sup> <sup>the</sup> <sup>end</sup> <sup>of</sup> <sup>the</sup> <sup>touching</sup> the initial time. The horizontal velocity of the main body cabin’s center of mass oscillates<sup>own</sup> <sup>in</sup> <sup>both</sup> <sup>cases</sup> <sup>5</sup> <sup>and</sup> <sup>6.</sup> <sup>This</sup> <sup>stability</sup> <sup>suggests</sup> <sup>that</sup> <sup>the</sup> <sup>landing</sup> <sup>mechanism</sup> <sup>in</sup> <sup>these</sup> near the equilibrium position.<sup>wo</sup> <sup>cases</sup> <sup>is</sup> <sup>robust,</sup> <sup>even</sup> <sup>when</sup>

![](P5_Li_2025_Aerospace_images/73995680db60bdc52163bf184559832ba2aa0f99bbd576a85382752ac546702b.jpg)

![](P5_Li_2025_Aerospace_images/7242cbca5e5feb0a282469648c75e35f1da2cb156806d533d1c4bb141363ae00.jpg)  
igure 11. Lateral displacement of the main-body cabin: (a) displacement along x direction, (b) dis-Figure 11. Lateral displacement of the main-body cabin: (a) displacement along x direction, lacement along y direction.(b) displacement along y direction.

![](P5_Li_2025_Aerospace_images/a6175f3c55df1d01faab02867cadd2c2984fca122cb685b0a26d49726a946d53.jpg)

![](P5_Li_2025_Aerospace_images/7b48b2cb5f2c68410b314e5322359c4624315ce6d1b7ab09ff9aa9cf5b0fe14b.jpg)  
Figure 12. Lateral velocity of the main body cabin: (a) velocity along x direction, (b) velocity alongFigure 12. Lateral velocity of the main body cabin: (a) velocity along x direction, (b) velocity along y directiony direction.

Therefore, the following conclusions can be drawn: under the 1-2-1 mode, the RLV achieves a stable state relatively quickly after landing. However, for landing scenarios under the 2-2 mode, the lateral vibration of the main-body cabin is more obvious, and a larger lateral landing tolerance is required than cases in other modes.

## 5.4. Maximum Load Analysis

Figure 13 illustrates the contact forces experienced by the four landing legs in case 4, with Figure 11b providing a detailed view from 0 to 0.3 s. As observed initially, leg 1 bears a relatively larger contact force, followed by legs 2 and 4 due to their symmetrical distribution, resulting in nearly overlapping force curves. Finally, leg 3 makes contact, leading to a gradual decrease in contact forces across all legs, as the system’s kinetic energy is consumed, ultimately converging near an equilibrium state.

![](P5_Li_2025_Aerospace_images/639693795bc93fbd41134e0e4cb40173dac8223a8798dcd2997e560e8a66f878.jpg)

![](P5_Li_2025_Aerospace_images/0274727d8859996c545637eed6fd2c2c6916c5c28cd6aa602bec082c4b6b0ef0.jpg)  
Figure 13. Contact force in each leg of case 4: (a) contact force in 0-10s, (b) detailed view of contact Figure 13. Contact force in each leg of case 4: (a) contact force in 0-10 s, (b) detailed view of contact force in 0–0.3 s.

The joint reaction forces and spring force are depicted in Figure 14, illustrating the complex interaction between different parts of the landing mechanism. It is observed that the initial impact is transferred to the joint of the main strut. As the touching down progresses, the hydro-pneumatic spring takes over and absorbs the impact, resulting in <sub>a smaller maximum value of the reaction force compared to the contact force. Furthermore,</sub>gure 13. Contact force in each leg of case 4: (a) contact force in 0-10s, (b) detailed view of contact the reaction force on the auxiliary strut is trivial during the entire landing.<sup>rce</sup> <sup>in</sup> <sup>0–0.3s.</sup>

![](P5_Li_2025_Aerospace_images/9151bef5e3bd91716002fb4cc5303a0af3418b490b82d76b9784e705bb5f5e1f.jpg)  
gure Figure 14.14. Forces in Forces in leg 1 of case 4.leg 1 of case 4.

The contact forces of cases 5 and 6 are depicted in Figures 15 and 16, respectively, providing a comparison with single-legged landing. It is observed that the maximum contact force values in both cases 5 and 6 are significantly smaller compared to the singlelegged landing in case 4. It can be observed that in both of these operating conditions, two legs first make contact with the ground. Subsequently, after several seconds, the other two legs touched the ground. Consequently, the entire touchdown phase becomes longer, during which lateral oscillations of the main body cabin occur. Moreover, it can be seen that the contact forces of all four legs reach a stable average value at the end of the touching down in both cases 5 and 6. This stability suggests that the landing mechanism in these two cases is robust, even when starting from two-legged initial landing conditions.<sup>gure</sup> <sup>14.</sup> <sup>Forces</sup> <sup>in</sup> <sup>leg</sup> <sup>1</sup> <sup>of</sup> <sup>case</sup> <sup>4.</sup>

![](P5_Li_2025_Aerospace_images/09c38af61b39b3d2bac37f5122410cdf5f1255938ee01e18fa0d2e5e06c52882.jpg)  
Figure 15. Contact force in each leg of case 5.

![](P5_Li_2025_Aerospace_images/7f0f74294ba750ec0cafa86bde2f7ac3ba3b69f5113dee67d1ca0eb953a92554.jpg)  
ure 16. Contact force in each leg of case 6.Figure 16. Contact force in each leg of case 6.

## 6. Conclusions

This paper presents an investigation into the vertical landing mechanism of a reusable <sup>This</sup> <sup>paper</sup> <sup>presents</sup> <sup>an</sup> <sup>investigation</sup> <sup>into</sup> <sup>the</sup> <sup>vertical</sup> <sup>landing</sup> <sup>mechanism</sup> <sup>of</sup> <sup>a</sup> <sup>reus</sup>launch vehicle (RLV), with a focus on developing a comprehensive understanding of the <sup>launch</sup> <sup>vehicle</sup> <sup>(RLV),</sup> <sup>with</sup> <sup>a</sup> <sup>focus</sup> <sup>on</sup> <sup>developing</sup> <sup>a</sup> <sup>comprehensive</sup> <sup>understanding</sup> <sup>o</sup>dynamics involved. A flexible–rigid coupled dynamics model is established, allowing for <sup>dynamics</sup> <sup>involved.</sup> <sup>A</sup> <sup>flexible–rigid</sup> <sup>coupled</sup> <sup>dynamics</sup> <sup>model</sup> <sup>is</sup> <sup>established,</sup> <sup>allowin</sup>simulations of the landings in various initial conditions to be conducted. Simulation results <sup>r</sup> <sup>simulations</sup> <sup>of</sup> <sup>the</sup> <sup>landings</sup> <sup>in</sup> <sup>various</sup> <sup>initial</sup> <sup>conditions</sup> <sup>to</sup> <sup>be</sup> <sup>conducted.</sup> <sup>Simulatio</sup>highlight the importance of considering flexibility in the main components of the landing <sup>ults</sup> <sup>highlight</sup> <sup>the</sup> <sup>importance</sup> <sup>of</sup> <sup>considering</sup> <sup>flexibility</sup> <sup>in</sup> <sup>the</sup> <sup>main</sup> <sup>components</sup> <sup>of</sup> <sup>th</sup>mechanism, underscoring its critical role in achieving a successful landing. The adopted ding mechanism, underscoring its critical role in achieving a successful landing. ThRLV design is capable of achieving stable landings under the specified initial velocity and opted RLV design is capable of achieving stable landings under the specified initiattitude conditions, demonstrating its feasibility for practical applications. Notably, the locity and atitude conditions, demonstrating its feasibility for practical application1-2-1 landing mode induces higher maximum values of contact force and joint reaction tably, the 1-2-1 landing mode induces higher maximum values of contact force anforces compared to other modes, highlighting the need for careful design considerations. The hydro-pneumatic spring plays a crucial role in absorbing the impact of the initial <sub>nsiderations.</sub> <sub>The</sub> <sub>hydro-pneumatic spring</sub> <sub>plays</sub> <sub>a</sub> <sub>crucial</sub> <sub>role</sub> <sub>in</sub> <sub>absorbing</sub> <sub>the</sub> <sub>impa</sub>landing leg, ensuring a smoother landing experience and minimizing potential damage to the main body cabin.

Future work will focus on simulating landings on floating surfaces, such as ship decks, which pose unique challenges due to the dynamic nature of the environment. Further research is required to optimize the structure of landing mechanisms, ensuring they are designed to withstand the stresses and loads associated with different landing cases. Furthermore, the possible ranges of mass deviation and liquid sloshing issues caused by fuel residues is a vital topic in the field of landing dynamics, which need more attentions and further investigations in the future.

d further investigations in the future.Author Contributions: Conceptualization, Y.Z., H.J. and H.L.; methodology, H.L. and A.H.; simula tion, H.L. and W.X.; validation, C.S., W.X. and M.H.; formal analysis, C.S. and H.L.; investigation, thor Contributions: Conceptualization, Y.Z., H.J. and H.L.; methodology, H.L. and A.H.; simA.H. and M.H.; resources, Y.Z. and H.J.; data curation, H.L.; writing—original draft preparation, H.L.; writing—review and editing, Y.Z. and C.S.; visualization, H.L.; supervision, C.S. and H.J.; funding acquisition, H.L. All authors have read and agreed to the published version of the manuscript.

iting—review and editing, Y.Z. and C.S.; visualization, H.L.; supervision, C.S. and H.J.; fundinFunding: This research was funded by Fundamental Research Funds for the Central Universities uisition, H.L. All auth[No. FRF-TP-22-026A1].

Data Availability Statement: Dataset available on request from the authors.

o. FRF-TP-22-026A1].Conflicts of Interest: Y.Z., A.H., M.H. and H.J. are employed by Beijing Interstellar Glory Space Technology Co., Ltd., which provided the initial conditions to be simulated and partially funded the research. All other co-authors declare no conflicts of interest. These four authors contributed to the conceptualization of the study, validation, investigation, data collection, review and editing, the decision to publish the results, and manuscript revision.

## References

1. Wang, Y.; Yu, H.; Xie, J.; Yan, Z.; Tian, B.; Gao, H. The impact modeling and experimental verification of a launch vehicle with crushing-type landing gear. Actuators 2023, 12, 307. [CrossRef]

2. Heckmann, A.; Otter, M.; Dietz, S.; Lopez, J.D. The DLR flexiblebodies library to model large motions of beams and of flexible bodies exported from finite element programs. In Proceedings of the 5th International Modelica Conference, Wien, Austria, 4–5 September 2006; pp. 85–95.

3. Briese, L.; Acquatella, B.; Schnepper, K. Multidisciplinary Modeling and Simulation Framework for Launch Vehicle System Dynamics and Control. Acta Astronaut. 2020, 170, 652–664. [CrossRef]

4. Thies, C. Investigation of the landing dynamics of a reusable launch vehicle and derivation of dimension loading for the landing leg. CEAS Space J. 2022, 14, 565–576. [CrossRef]

5. Yue, S.; Lin, Q.; Zheng, G.; Du, Z. Modeling and experimental validation of vertical landing reusable launch vehicle under symmetric landing conditions. Chin. J. Aeronaut. 2022, 35, 156–172. [CrossRef]

6. Yue, S.; Titurus, B.; Nie, H.; Zhang, M. Liquid spring damper for vertical landing reusable launch vehicle under impact conditions. Mech. Syst. Signal Process. 2019, 121, 579–599.

7. Yue, S.; Nie, H.; Zhang, M.; Huang, M.; Zhu, H.; Xu, D. Dynamic analysis for vertical soft landing of reusable launch vehicle with landing strut flexibility. Proc. Inst. Mech. Eng. Part G J. Aerosp. Eng. 2019, 233, 1377–1396. [CrossRef]

8. Yue, S.; Titurus, B.; Li, Z.; Wu, C.; Du, Z. Analysis of liquid spring damper for vertical landing reusable launch vehicle with network-based methodology. Nonlinear Dyn. 2023, 111, 2135–2160.

9. Witte, L.; Buchwald, R.; Schröder, S. Touch-down dynamics and terrain interaction of planetary landing systems. In Proceedings of the Global Lunar Conference, Beijing, China, 31 May 2010; pp. 1–10.

10. Yu, H.; Tian, B.; Yan, Z.; Gao, H.; Zhang, H.; Wu, H.; Wang, Y.; Shi, Y.; Deng, Z. Watt linkage–based legged deployable landing mechanism for reusable launch vehicle: Principle, prototype design, and experimental validation. Engineering 2023, 20, 120–133.

11. De Oliveira, A.; Lavagna, M. Development of a controlled dynamics simulator for reusable launcher descent and precise landing. Aerospace 2023, 10, 993. [CrossRef]

12. Mo, R.; Li, W.; Su, S. UDE-based adaptive dynamic surface control for attitude-constrained reusable launch vehicle. Nonlinear Dyn. 2024, 112, 5365–5378.

13. Xu, S.; Guan, Y.; Bai, Y.; Wei, C. Practical predefined-time barrier function-based adaptive sliding mode control for reusable launch vehicle. Acta Astronaut. 2023, 204, 376–388.

14. Farì, S.; Seelbinder, D.; Theil, S. Advanced GNC-oriented modeling and simulation of vertical landing vehicles with fuel slosh dynamics. Acta Astronaut. 2023, 204, 294–306. [CrossRef]

15. Wang, C.; Chen, J.; Jia, S.; Chen, H. Parameterized design and dynamic analysis of a reusable launch vehicle landing system with semi-active control. Symmetry 2020, 12, 1572. [CrossRef]

16. Kobayakawa, T.; Kawato, H.; Mochizuki, K.; Sakamoto, N.; Habaguchi, Y. Abort recovery strategy for future vertical landing systems. Acta Astronaut. 2015, 116, 148–153. [CrossRef]

17. Schneider, A.; Desmariaux, J.; Klevanski, J.; Schröder, S.; Witte, L. Deployment dynamics analysis of CALLISTO’s approach and landing system. CEAS Space J. 2023, 15, 343–356. [CrossRef]

18. Li, W.; Zhang, X.; Dong, Y.; Lin, Y.; Li, H. Powered landing control of reusable rockets based on softmax double DDPG. Aerospace 2023, 10, 590. [CrossRef]

19. Musso, G.; Figueiras, I.; Goubel, H.; Gonçalves, A.; Costa, A.; Ferreira, B.; Azeitona, L.; Barata, S.; Souza, A.; Afonso, F.; et al. A multidisciplinary optimization framework for ecodesign of reusable microsatellite launchers. Aerospace 2024, 11, 126. [CrossRef]

20. Shabana, A.A. Dynamics of Multibody Systems; Cambridge University Press: Cambridge, UK, 2020.

21. Huang, G.; Zhu, W.; Yang, Z.; Feng, C.; Chen, X. Reanalysis-based fast solution algorithm for flexible multi-body system dynamic analysis with floating frame of reference formulation. Multibody Syst. Dyn. 2020, 49, 271–289. [CrossRef]

22. Li, H.; Yu, Z.; Guo, S.; Cai, G. Investigation of joint clearances in a large-scale flexible solar array system. Multibody Syst. Dyn. 2018, 44, 277–292.

23. Simeon, B. Computational Flexible Multibody Dynamics. A Differential-Algebraic Approach; Springer: Berlin/Heidelberg, Germany, 2013.

24. Haug, E. Computer-Aided Kinematics and Dynamics of Mechanical Systems. In Modern Methods, 4th ed.; Ed & Carol Haug Charitable Foundation: Silver City, NM, USA, 2024; Volume 2.

25. Shock Absorption Tests. Advisory Circularfrom Federal Aviation Administration, U.S. Department of Transportation, No. 25.723-1; U.S. Department of Transportation: Washington, DC, USA, 2001. Available online: https://www.faa.gov/documentLibrary/media Advisory\_Circular/AC\_25\_723-1.pdf (accessed on 25 March 2025).

26. No. HB 6645-1992; Test Methods and Requirements for Drop Shock of Aircraft Landing Gear Buffers. Chinese Industry Standard: Beijing, China, 1993. Available online: https://kns.cnki.net/kcms2/article/abstract?v=\_GofKS1StuQnNqplTb-m5y50A1 tPD2E6Ape1oprmx-CxBLFS2M6H8EBlkqY\_-JuXzusEFtUNG-fETtFtdxpvZU9zai8I5Umbyg6UDp6FjOLVRJKIaeC1MWTw7n6 pqewGVER-nGDIYkf4FbJ\_fb1ZBPbbuBX68GBpMCyGjCosy2BfpKS1N\_lQ1QITRlE3utMT&uniplatform=NZKPT&language= CHS (accessed on 25 March 2025). (In Chinese)

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content.