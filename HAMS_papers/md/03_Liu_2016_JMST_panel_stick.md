# Motion Response Prediction by Hybrid Panel-Stick Models for a Semi-Submersible with Bracings

Liu, Yingyi Interdisciplinary Graduate School of Engineering Science, Kyushu University

Hu, Changhong Research Institute for Applied Mechanics, Kyushu University

Sueyoshi, Makoto Research Institute for Applied Mechanics, Kyushu University

Iwashita, Hidetsugu Falculty of Engineering, Hiroshima University

他

https://hdl.handle.net/2324/4060502

# Motion Response Prediction by Hybrid Panel-Stick Models for a Semi-Submersible with Bracings

Yingyi Liu<sup>1</sup>, Changhong Hu<sup>2,∗</sup>, Makoto Sueyoshi<sup>2</sup>, Hidetsugu Iwashita<sup>3</sup>, Masashi Kashiwagi<sup>4</sup>

<sup>1</sup>Interdisciplinary Graduate School of Engineering Science, Kyushu University, Kasuga, Fukuoka, JAPAN

<sup>2</sup>Research Institute for Applied Mechanics, Kyushu University, Kasuga, Fukuoka, JAPAN

<sup>3</sup>Falculty of Engineering, Hiroshima University, Kagamiyama, Higashi-Hiroshima, JAPAN

<sup>4</sup>Graduate School of Engineering, Osaka University, Suita, Osaka, JAPAN, JAPAN

## Abstract

A diffraction-radiation analysis is usually required when the hydrodynamic interactions between structura members occur in short waves. For bracings or small cylindrical members, which play important roles in the vicinity of the natural frequency of a floating platform, special care should be taken into account for the effect of viscous damping. Two hybrid panel-stick models are therefore developed, through the combination of the standard diffractionradiation method and the Morison’s formulae, considering the effect of small members differently. The fluid velocity is obtained directly by the panel model. The viscous fluid force is calculated for individual members by the stick model. A semi-submersible type platform with a number of fine cylindrical structures, which is designed as a floating foundation for multiple wind turbines, is analysed as a numerical example. The results show that viscous force has significant influence on the hydrodynamic behaviour of the floating body and can successfully be considered by the proposed hybrid models.

Keywords: Floating offshore wind turbine; semi-submersible; potential theory

## 1 Introduction

Semi-submersible type platforms are widely used in the ocean oil industry, and also become more and more popular today in the offshore wind industry. This type of structure usually constitutes several large columns and pontoons, as well as some slender members or bracings for connecting them. For the large columns and pontoons whose diameter are comparable to the water wavelength, the potential flow force is dominant, which can be computed by the existing panel codes easily nowadays; for the slender cylinders whose diameter are much smaller than the incoming wavelength, the viscous loads are not negligible, which can therefore be calculated by the Morison stick method.

For the semi-submersible platform undergoing oscillation loads in short waves, the hydrodynamic interactions between the structural members may be of great importance to the fatigue life of the platform [1]. Hooft [2] presents a method that considers the columns and pontoons separately but assumes no interaction effect between hydrodynamic forces. The Morison formulae traditionally based on the local wave kinematics, which considers only the effect of incident waves (undisturbed sea), may not be realistic. Therefore, it is necessary to perform a diffraction-radiation analysis in order to derive the fluid kinematics at any location in a disturbed wave field environment. Such a combination method for deriving the disturbed fluid kinematics has been described in Malenica [3]. Since Morison drag force is a nonlinear term, it should be linearized in the frequency domain computation. Veer [4] studied the effect of the linearization method to the motion response of a pipe lay vessel with a lot of stingers, and concluded that the energy equivalent linearization is an appropriate approach in regular waves while the stochastic linearization method seems more applicable in irregular sea states.

Another important issue for the semi-submersible type platform is the prediction of motion responses, among which the heave response near resonance may be most concerned. Hooft [2] showed that the principal dimensions of a semi-submersible can be tuned in order to make the natural periods $T _ { \mathfrak { n } }$ (periods of resonance) coincide with the periods of near-zero-excitation $T _ { 0 } ,$ so that the resonance effect could be effectively canceled. Faltinsen [5] further presented that in beam seas, the heave natural period should be less than its near-zero-excitation period. This conclusion was later confirmed by Newman [6] for almost all the cases in beam seas, except that when the draft is very close to the order of one. Newman [6] also proved that in the long-wavelength regime the heave Response Amplitude Operator (RAO) approaches to unity. These findings are very helpful in the conceptual design stage, and can be used as inspection means for the motion prediction of semi-submersibles.

The present study is motivated by a Kyushu University floating offshore wind turbine (FOWT) project, in which a semi-submersible is designed for supporting the “Wind Lens” wind turbines [7] which consists of a large number of fine cylindrical structures. In the design stage, it is necessary to know how much the slender bracings influence the performance of the semi-submersible. Furthermore, it is also concerned that which numerical tool may be the most appropriate one for prediction of such kind of platform. Taking into account both accuracy and computation time, a combination of the panel method and the Morison method is more efficient. This method is called as the hybrid panel-stick method (HPSM). There are several ways of establishing the hybrid panel-stick model, for instance, one can discard or retain the slender bracings when performing the diffraction-radiation analysis. The purpose of this study is to select an optimal model for the analysis. The fluid kinematics is derived through the source formulation of the panel method. To accelerate the computational speed, the iterative GMRES algorithm and OpenMP parallel technique are used. Contribution of the slender bracings to the inertia force and the fluid field are analyzed. The motion response predicted by the numerical methods are carried out and compared with the laboratory experiment. Influence of the wave incident angle and comparison of the computation time are also considered.

## 2 The Kyushu University FOWT

## 2.1 Conceptual design of the FOWT

The platform is designed by the research team in Research Institute of Applied Mechanics (RIAM), Kyushu University [7]. A computer graph of the FOWT is shown in Figure 1. Three ‘Wind Lens’ wind turbines designed for making better use of the offshore wind energy are installed at the corners of the triangularshaped platform, between them are solar panels which are used to harvest the solar energy. It is a multipurpose floating marine renewable energy system, from which the electricity can be also used by the surrounding aquaculture farm.

The semi-submersible is designed to be half-immersed in operation. It has three stacked large columns at the corners of the triangular-shaped platform for supporting the turbine towers, three long lower hulls which connect the columns and a bunch of small bracings over the columns and the lower hulls. Since the offshore wind turbine system is planned to be operated in the sea areas with the depth less than 100 meters, a catenary mooring system is used The catenary mooring system consists of six mooring lines, whose fairleads linked to the columns are 7.0m below the mean sea level (MSL), spreading toward the neighboring of the semi-submersible. Specifications of the structure and the mooring system are summarized in Table 1 and 2.

![](images/83757e8ac9d17afe42b336f0b863452e6cd66ed9f8e1e6f17c59b67810fe90d0.jpg)  
Figure 1. Snapshot of the semi-submersible floating platform in Kyushu University

Table 1. Definition of the full-scale properties of the semisubmersible

<table><tr><td>Diameter of the Upper Columns</td><td>4.00 m</td></tr><tr><td>Diameter of the Footings</td><td>11.5 m</td></tr><tr><td>Diameter of the Lower Hulls</td><td>1.70 m</td></tr><tr><td>Diameter of the Bracings</td><td>0.60 m</td></tr><tr><td>Number of Bracings</td><td>66</td></tr><tr><td>Distance between two columns</td><td>90.0 m</td></tr><tr><td>Total Draft</td><td>10.0 m</td></tr><tr><td>Center of Gravity</td><td>(0, 0, 5.30 m)</td></tr><tr><td>Center of Buoyancy</td><td>(0, 0, -7.15 m)</td></tr><tr><td>Platform Displacement</td><td> $2.12 \times 10^{3} \text{ m}^{3}$ </td></tr><tr><td>Platform Mass</td><td> $1.99 \times 10^{6} \text{ kg}$ </td></tr><tr><td>Platform Roll Inertia</td><td> $2.01 \times 10^{9} \text{ kg.m}^{2}$ </td></tr><tr><td>Platform Pitch Inertia</td><td> $2.01 \times 10^{9} \text{ kg.m}^{2}$ </td></tr><tr><td>Platform Yaw Inertia</td><td> $3.82 \times 10^{9} \text{ kg.m}^{2}$ </td></tr></table>

Table 2. Definition of the full-scale properties of the mooring system

<table><tr><td>Number of Mooring Lines</td><td>6</td></tr><tr><td>Angle between Adjacent Lines</td><td>60.0 degrees</td></tr><tr><td>Water Depth (Depth of Anchor)</td><td>70.0 m</td></tr><tr><td>Depth of Fairleads below MSL</td><td>7.00 m</td></tr><tr><td>Radius from Fairleads to Anchors</td><td>324.0 m</td></tr><tr><td>Unstretched Mooring Line Length</td><td>350.0 m</td></tr><tr><td>Nominal Chain Diameter</td><td>0.12 m</td></tr><tr><td>Equivalent Mooring Line Mass Density</td><td> $2.74 \times 10^{2}$  kg/m</td></tr><tr><td>Vertical Pretension of Mooring system</td><td> $1.76 \times 10^{6}$  N</td></tr></table>

## 2.2 Natural periods of the semi-submersible

Natural periods of the semi-submersible in six degrees of freedom can be obtained through an iteration calculation (see appendix) in the hydrostatic analysis. The added mass coefficients of the buoy are computed with respect to wave frequencies in advance by the panel model described in Section 3.1, and then output to a data file which can be used for interpolation in the iteration process. The calculated natural periods are listed in Table 3, as well as the corresponding value of λ/L , where λ is the wavelength, L is the length of central perpendicular line of the triangular-shaped platform. It can be observed that the heave natural period is the smallest among the six modes, which is often within the band of sea wave spectrum. For this reason, the heave motion response is usually the most concerned property for a semi-submersible platform in a practical engineering issue. The calculated theoretical natural periods will be compared with those obtained by the subsequent numerical simulation, which can be used as a mean to check the validity.

Table 3. Natural periods of the semi-submersible

<table><tr><td>Mode</td><td>Natural period (s)</td><td>λ/L</td></tr><tr><td>Surge</td><td>53.68</td><td>57.70</td></tr><tr><td>Sway</td><td>53.68</td><td>57.70</td></tr><tr><td>Heave</td><td>17.27</td><td>5.97</td></tr><tr><td>Roll</td><td>21.55</td><td>9.30</td></tr><tr><td>Pitch</td><td>21.54</td><td>9.29</td></tr><tr><td>Yaw</td><td>61.35</td><td>75.37</td></tr></table>

## 3 Methodologies for hydrodynamic analysis

## 3.1 Diffraction-radiation panel model

A diffraction-radiation panel method is used to calculate the hydrodynamic interaction between incident waves and the floating structure. With the assumption that the flow is inviscid, irrorational and incompressible, the problem is governed by the velocity potential Φ(x, t) which satisfies the Laplace equation

$$
\nabla^ {2} \Phi = 0\tag{1}
$$

in the fluid domain. The harmonic time dependence allows the definition of a complex velocity potential $\varphi ( \mathbf { x } )$ , also named as the ‘spatial component’, related to $\boldsymbol { \varPhi } ( \mathbf { x } , t )$ by

$$
\Phi = \operatorname{Re} \left(\phi e ^ {- \mathrm{i} \omega t}\right),\tag{2}
$$

where Re denotes the real part, ω is the frequency of the incident wave and t is time. In the frequencydomain analysis, the boundary-value problem (BVP) is expressed in terms of the complex velocity potential $\phi ,$ which can be further decomposed into incident $\phi _ { 0 } .$ , diffraction $\phi _ { 7 }$ and six radiation components $\phi _ { j } ( j =$ $1 , . . . , 6 )$ corresponding to six rigid body motions $\xi _ { j } ( j = 1 , . . . , 6 )$

$$
\phi = \phi_ {0} + \phi_ {7} - \mathrm{i} \omega \sum_ {j = 1} ^ {6} \xi_ {j} \phi_ {j}.\tag{3}
$$

The diffraction and radiation components are subjected to the following conditions:

$$
\left.\begin{array}{l l}\nabla^ {2} \phi_ {j} = 0&\text {in} \Omega\\\frac {\partial \phi_ {j}}{\partial z} - \nu \phi_ {j} = 0&z = 0\\\frac {\partial \phi_ {j}}{\partial n} = V _ {n}&\text {on} S _ {B}\\\frac {\partial \phi_ {j}}{\partial z} = 0 \text {or} \lim _ {z \rightarrow \infty} \left(\frac {\partial \phi_ {j}}{\partial z}\right) = 0&\text {on} S _ {D}\\\lim \left[ \sqrt {\nu R} \left(\frac {\partial \phi_ {j}}{\partial R} - \mathrm{i} \nu \phi_ {j}\right) \right] = 0&R \rightarrow \infty\end{array}\right\},\tag{4}
$$

where $V _ { n }$ denotes the body velocity, $\nu = \omega ^ { 2 } / g ,$ , and $g$ is the acceleration of gravity. In detail, the body boundary conditions are:

$$
\frac {\partial \phi_ {7}}{\partial n} = - \frac {\partial \phi_ {0}}{\partial n}, \frac {\partial \phi_ {j}}{\partial n} = n _ {j} (j = 1, \dots , 6),\tag{5}
$$

where $( n _ { 1 } , n _ { 2 } , n _ { 3 } ) = \mathbf { n }$ and $( n _ { 4 } , n _ { 5 } , n _ { 6 } ) = \mathbf { x } \times \mathbf { n } , \mathbf { x } = ( x , y , z )$ . The unit vector n is normal to the body boundary surface and points out of the fluid domain.

![](images/998d4355644f2c8349de1233d9997d8e607b1b86749dafb5d88415ed02b1b95c.jpg)  
Figure 2. Definition of the coordinate system for the diffraction-radiation analysis

The coordinate system is defined to be a right-handed Cartesian coordinate system $( x , y , z )$ with its x-y plane taken as the undisturbed sea level and the z-axis taken vertically upwards. In the framework of the Airy wave theory, the incident wave potential is defined by

$$
\phi_ {0} = - \frac {\mathrm{i} g A}{\omega} \frac {\cosh k (z + h)}{\cosh k h} e ^ {\mathrm{i} k (x \cos \beta + y \sin \beta)}\tag{6}
$$

where $\beta$ is the angle between the direction of propagation of the incident wave and the positive x-axis as defined in Figure 2.

The boundary value problem is solved by a standard boundary integral equation approach. Thus the velocity potential on the body boundary is obtained from the following equation:

$$
2 \pi \phi_ {j} (\mathrm{P}) + \iint_ {S _ {B}} \phi_ {j} (\mathrm{Q}) \frac {\partial G (\mathrm{P} ; \mathrm{Q})}{\partial \mathrm{n}} \mathrm{d} S = \iint_ {S _ {B}} G (\mathrm{P}; \mathrm{Q}) V _ {n} \mathrm{d} S,\tag{7}
$$

G is the free-surface Green function which can be written as summation of the Rankine term and the regular wave term

$$
G (\mathrm{P}; \mathrm{Q}) = \frac {1}{r (\mathrm{P} ; \mathrm{Q})} + G _ {w} (\mathrm{P}; \mathrm{Q}),\tag{8}
$$

where P and Q stand for the field and source point, respectively. Integrations of the first Rankine source term and its derivatives are evaluated by the algorithm in Newman [8], Webster [9] and Kashiwagi et al. [10]. Integrations of the second wave term can be evaluated by the algorithm in Newman [11], Kashiwagi et al. [10] or Liu et al. [12].

To avoid the expensive cost of large computation time, the OpenMP parallel technique is applied in the BIE solver in association with a diagonal preconditioned GMRES method [13, 14]. Moreover, symmetry of the structure is applied as well to reduce the computational burden where half of the body is computed for the present structure. For the sake of mesh quality, a panel mesh generator is also developed, which can generate panel mesh for the semisubmersible with cylindrical members in an arbitrary mesh number automatically. In the panel mesh generator, the cylindrical members can be in arbitrary radius, arbitrary orientation and arbitrary member numbers.

Motion of the structure can be known from the following equation:

$$
\left\{- \omega^ {2} \left(\left[ M \right] + \left[ A \right]\right) - \mathrm{i} \omega \big [ B \big ] + \left(\left[ K \right] + \left[ C \right]\right) \right\} \{\xi \} = \left\{F _ {E X} \right\},\tag{9}
$$

where - and  represent the added mass matrix and the wave damping matrix calculated by the panel method;  ,  and  represent the mass matrix, the linearized mooring stiffness matrix and the hydrostatic restoring matrix; $\{ F _ { E x } \}$ represents the wave exciting force.

## 3.2 Morison stick model

For slender members in comparison to long waves, separations of fluid in the region of the boundary layer lead to viscous effect that cannot be well accounted for by the potential panel model. In such a case, the Morison type formula is still an efficient method as the complementary part of the potential theory. Here we follow the formulation that was used by Leblanc et al. [1].

The Morison force can be modeled in terms of two components. One is called the inertia force which can be written as

$$
\vec {F} _ {M, I n e r t i a} = \vec {F} _ {M, E x} + \vec {F} _ {M, M o t i o n} + \vec {F} _ {M, E n d},\tag{10}
$$

where the first term is induced by wave excitation

$$
\vec {F} _ {M, E x} = \rho (1 + C _ {A}) \int_ {s} ^ {e} S \vec {\gamma} _ {w T} d l,\tag{11}
$$

the second term relates to the platform motions

$$
\vec {F} _ {M, M o t i o n} = - \rho C _ {A} \int_ {s} ^ {e} S \vec {\gamma} _ {m \mathrm{T}} d l,\tag{12}
$$

and the third term is the wave loading upon the ends of the members. The other component of the Morison force is called the drag force which can be further decomposed as

$$
\vec {F} _ {M, D r a g} = \frac {4}{3 \pi} \rho C _ {D} \int_ {s} ^ {e} D \left| \vec {V} _ {r \mathrm{T}} \right| \vec {V} _ {r \mathrm{T}} d l = \vec {F} _ {M, D d a m p} + \vec {F} _ {M, M d r a g},\tag{13}
$$

where the first term of the decomposition is the drag damping force

$$
\vec {F} _ {M, D d a m p} = - \frac {4}{3 \pi} \rho C _ {D} \int_ {s} ^ {e} D | \vec {V} _ {m \mathrm{T}} | \vec {V} _ {m \mathrm{T}} d l,\tag{14}
$$

and the second term of the decomposition is named as the modified drag force which can be calculated from Eq. (13) in a reverse form. This decomposition of the drag force is just to facilitate the numerical solution of the motion equation. All the load components above mentioned are calculated along each segment in the direction normal to the axis of the cylindrical member. Finally, the total loads are obtained by the summation of the forces on each segment.

In the above notations, $\vec { \gamma } _ { w \mathrm { T } }$ is the transverse component of the water particle acceleration under incident waves; $\vec { V } _ { m \mathrm { T } }$ and $\vec { \gamma } _ { m \mathrm { T } }$ are the transverse component of the velocity and the acceleration of the structure due to its motions, respectively; $\vec { V } _ { r \mathrm { T } }$ is the transverse component of the relative local velocity between ambient fluid and the structure, calculated from the difference between the fluid velocity $\vec { V } _ { w \mathrm { T } }$ and the platform velocity $\vec { V } _ { m \mathrm { T } }$ ; Note that the subscript $^ { \mathfrak { c } \mathfrak { c } } \mathrm { T } ^ { \mathfrak { s } }$ represents for transverse component of the variables in frequency domain which are all independent of time, hence Eqs. (11) and (14) are linearized forms of their time domain counterparts. In addition, $C _ { \mathrm { { A } } }$ and $C _ { \mathrm { D } }$ stands for the added inertia coefficient and drag coefficient, respectively; $\rho$ is the water density; $D$ and S are the diameter and the area of the member’s cross section, respectively.

![](images/8199e991dc68953312367278842f1ddd99077506d7ef9d1674bf6179dc23410b.jpg)  
Figure 3. Reference system for stick elements

As for the numerical implementation of the stick model, a stick mesh which records all the needed information is required as an input. A Morison-stick mesh generator is therefore developed to generate the stick mesh for describing the whole submerged structure under the water. The number of stick elements can be specified in an arbitrary number by the users in advance. In the stick mesh generator, the location and affiliation of each element (as shown in Figure 3) in each cylindrical member, the equivalent cross-section diameter, the axis length, the axis direction, and the coefficients $C _ { \mathrm { { A } } }$ and $C _ { \mathrm { D } }$ of each member, are recorded into the generated stick mesh.

Put into together all the forces mentioned above into the motion equation based on Newton’s second law, the motion of the semisubmersible can be finally obtained through the following equation

$$
\left\{- \omega^ {2} ([ M ] + [ M _ {a} ]) - \mathrm{i} \omega [ M _ {b} ] + ([ K ] + [ C ]) \right\} \{\xi \} = \left\{F _ {M, E x} \right\} + \left\{F _ {M, E n d} \right\} + \left\{F _ {M, M d r a g} \right\},\tag{15}
$$

where $[ M _ { a } ]$ is the added mass matrix calculated from Eq.(12); $[ M _ { b } ]$ is the viscous damping matrix calculated from Eq.(14); $\left\{ F _ { M , E x } \right\}$ is the wave exciting force calculated from Eq.(11); $\left\{ F _ { M , E n d } \right\}$ is the stick end force, which can be obtained by integrating the hydrodynamic pressure over the ends of members; $\left\{ F _ { M , M d r a g } \right\}$ is the modified drag force. All the quantities above are obtained by using only the Morison stick model.

## 4 Hybrid methods for calculating motion of the platform

$4 . I$ The disturbed fluid kinematics

For most of the semi-submersible type floating platform, usually the large columns and the slender members are mix-used in order to provide enough heave restoring force at meanwhile reduce the total external loads from the incoming waves. In such cases, the diffraction effect, i.e., the hydrodynamic interactions between large columns, and the viscous contribution from the slender members are both important. A hybrid model which combines the previous two models is preferred to be used. Indeed, the most common interest may lie in that through what kind of way this hybrid model will be established. Herein we considered two hybrid models, whose comparison in both accuracy and computational speed will be discussed in the following. Common process of the two hybrid models is shown in Figure 4.

Generally, in the pure Morison stick model, all the forces are calculated from the incident wave kinematics without considering the diffraction effect, which means that the input wave field is ‘undisturbed’. But in the following hybrid models, the diffracted and radiated wave field are considered as well [3]. For this purpose, we introduce the source formulation into the hybrid model to compute the fluid velocity at each section’s location, through

$$
2 \pi \sigma (\mathrm{P}) + \iint_ {S _ {B}} \sigma (\mathrm{Q}) \frac {\partial G (\mathrm{P} ; \mathrm{Q})}{\partial \mathrm{n}} \mathrm{d} S = V _ {n},\tag{16}
$$

together with

$$
\nabla \phi (P) = \iint_ {S _ {B}} \sigma (Q) \nabla G (P; Q) d S.\tag{17}
$$

The local fluid velocity and acceleration can be known from the “disturbed wave $\mathrm { f i e l d } ^ { \mathrm { , } }$ , in the form of the following equations

$$
\vec {v} = \operatorname{Re} \left\{\nabla \left(\varphi_ {0} + \varphi_ {7} - \mathrm{i} \omega \sum_ {j = 1} ^ {6} \xi_ {j} \varphi_ {j}\right) e ^ {- \mathrm{i} \omega t} \right\},\tag{18}
$$

and

$$
\bar {\gamma} = \operatorname{Re} \left\{- \mathrm{i} \omega \nabla \left(\varphi_ {0} + \varphi_ {7} - \mathrm{i} \omega \sum_ {j = 1} ^ {6} \xi_ {j} \varphi_ {j}\right) e ^ {- \mathrm{i} \omega t} \right\}.\tag{19}
$$

In Eqs. (18) and (19), the derivatives of the diffracted and radiated potentials are calculated from the source distribution method, while the derivatives of the incident potential can be easily derived from the analytical expression of the incident potential.

## 4.2 Hybrid model I

In this model, the fluid kinematics is obtained through the diffraction-radiation analysis for the immersed part of the structure, the drag force is calculated through the Morison formula for the immersed structure by setting the added inertia coefficients of each segment to zeroes. The corresponding motion equation can be written as

$$
\left\{- \omega^ {2} ([ M ] + [ A ]) - \mathrm{i} \omega ([ B ] + [ M _ {b} ]) + ([ K ] + [ C ]) \right\} \{\xi \} = \left\{F _ {E x} \right\} + \left\{F _ {M, M d r a g} \right\},\tag{20}
$$

where - and  are matrices of the added mass and the wave damping coefficient calculated by the panel method; $[ M _ { b } ]$ is the viscous damping matrix calculated from Eq.(14); $\{ F _ { E x } \}$ is the exciting force calculated by the panel method; $\left\{ F _ { M , M d r a g } \right\}$ is the modified drag force calculated from Eq. (13). All the quantities above are of the whole immersed structure including both the large columns and the bracings.

![](images/50af66e894361c9e5c5f89f74453128ebb6b3d5928d5910e0e0c8dbdd7294aec.jpg)  
Figure 4. Flow chart of the common process of the hybrid methods

## 4.3 Hybrid model II

In this model, the fluid kinematics is obtained through the diffraction-radiation analysis of the main portion of the immersed structure (constituting only large columns, without bracings), the inertia force and the drag force are calculated from the Morison formula for the rest part of the immersed structure (consists of all the bracings). The corresponding motion equation can be written as

$$
\begin{array}{r l} & {\left\{- \omega^ {2} ([ M ] + [ A ] + [ M _ {a} ]) - \mathrm{i} \omega ([ B ] + [ M _ {b} ]) + ([ K ] + [ C ]) \right\} \{\xi \}} \\ & {= \{F _ {E x} \} + \{F _ {M, E x} \} + \{F _ {M, E n d} \} + \{F _ {M, M d r a g} \}} \end{array} ,\tag{21}
$$

where - and  are matrices of the added mass and the wave damping of the main structure calculated by the panel method; $[ M _ { a } ]$ is the added mass matrix of the rest part of the structure calculated from Eq.

(12); $[ M _ { b } ]$ is the viscous damping matrix of the rest part of the structure calculated from Eq.(14); $\{ F _ { E x } \}$ is the exciting force on the main structure calculated by the panel method; $\left\{ F _ { M , E x } \right\} , \left\{ F _ { M , E n d } \right\}$ and $\left\{ F _ { M , M d r a g } \right\}$ are forces on the rest part of the structure calculate from the Morison model, as defined by the previous sections.

## 5 Results and discussions

## 5.1 Experiment measurement and computation setup

The model experiment is conducted in the towing tank of Research Institute for Applied Mechanics (RIAM), Kyushu University, Japan [15]. The tank is in cubic shape with 65m length, 5m width and 7m depth. Main purpose of the experiment is to check the hydrodynamic performance of the platform and to provide a benchmark database for validation of the numerical tools. Photograph of the 1/50 scale model is shown in Figure 5. Due to the limitation of the tank width, the platform is moored by a set of wires and springs which approximate the catenary mooring lines.

![](images/4cdbbabd75bd7d70ebca50a12a7599e54199aabb41f219d2be7f1896be87996c.jpg)  
Figure 5. Photograph of the experiment model

Firstly, in order to verify the estimation accuracy of the hydrodynamic coefficients predicted by the panel method, we carry out experiments for measuring added mass, damping coefficients and wave exciting forces. Added mass and damping coefficients in heave and pitch motions are measured by the forced excitation test. Wave exciting forces and moment are measured by fixing the model in regular waves. These results are plotted in figure 8 and 9 together with corresponding numerical results.

Secondly, in order to verify the proposed hybrid models for prediction of the motion response, we carry out experiments for measuring the motion time history of the platform. Positions of the platform throughout the measuring time are recorded by a high speed digital video camera, whose frame rate of is set to 50 fps for color images with the full resolution of $\mathrm { 1 0 2 4 ( H ) \times 1 0 2 4 ( V ) }$ pixels. Thereafter, the RAOs of 6DoF body motions are calculated by Fourier analysis of the motion time series data which is obtained from image analysis of the high-speed camera original data.

For the numerical computation, the platform mass matrix and the hydrostatic restoring matrix are calculated by the hydrostatic analysis; the stiffness matrix for the mooring lines is calculated by the linearized catenary theory; the added mass matrix and the wave damping matrix is calculated from hydrodynamic radiation problem.

Two sets of panel meshes for the immersed structure is shown in Figure 6. A total panel number of 6780 (2×3390) and 2160 (2×1080) are used to represent the wetted geometry, named “Mesh 1” and “Mesh $2 ^ { \circ }$ , respectively. The stick mesh for the same structure is shown in Figure 7, with a total number of 75 members and 1110 elements. “Mesh $1 ^ { \circ }$ will be used in the panel model and the hybrid model I; “Mesh $2 ^ { \circ }$ will be used in the hybrid model $\operatorname { I I } ;$ the stick mesh will be used in the hybrid model I, the hybrid model II and the Morison stick model.

![](images/bc76a87b4ab6491cb34975cf3e6cb5967e61766a0ab3f3f970a2fa3408331292.jpg)  
(a) Panel mesh including bracings (Mesh 1)

![](images/5c9292ed097f24b50fb28f18ee1299cd5f3ebcd1d2f5553a598332da6e67640d.jpg)  
(b) Panel mesh excluding bracings (Mesh 2)

Figure 6. Two sets of panel mesh for the immersed part of the structure  
![](images/77012ed7738c9c85eef79ef5d6c017b191f352eec2629d7c6dfc8174c737d3c7.jpg)  
Figure 7. Stick mesh for the immersed part of the structure

Results at different wave headings	 β	 are shown in Figure. 12\~14. The translational RAOs are normalized by the incident wave amplitude $\zeta _ { \mathrm { a } , }$ while the rotational RAOs are normalized by the product of the wave number k and the incident wave amplitude $\zeta _ { \mathrm { a } } .$

## 5.2 Contribution of the slender bracings to the hydrodynamic quantities of the platform

Figure 8 shows the comparison of hydrodynamic added mass and potential wave damping computed through the two panel meshes. All the quantities are normalized by the submerged volume V and the characteristic length L of the platform. Since the corresponding experiment data for heave and pitch motion are available, they are used for comparison in these two modes. It can be observed that the hydrodynamic coefficients computed from “Mesh 1” and “Mesh 2” share almost same trend and doesn’t have remarkable difference in the value, except the surge added mass. The reason may lie in that all the bracings have a much larger projection area in surge direction than in heave since a large portion of bracings stand vertically upward. Good agreement is found between the numerical results and the experiment data in heave and pitch modes, the discrepancy in small wave number region (with long wave length) is due to the difficulty in measuring accurately the added mass and the wave damping of structures in long waves using the available test facilities.

![](images/83f8788cd7fda13bd58e6e408c17dfa0bd585a21436d91d4acd1e27435e31ba7.jpg)  
(a) Surge added mass

![](images/8de25f189c7787f92edf92cab1ca4d1ecf26cf13cc9bfcfb46d5f984c9b3b869.jpg)  
(b) Surge wave damping

![](images/6b5f717f71354f6068b7684844357e68643326ffbaeea439048f36539afb20e2.jpg)  
(c) Heave added mass

![](images/343278f568e47e83c43b513e5194e7d0f31c2abea1144bbbc5bffa626c044d63.jpg)  
(d) Heave wave damping

![](images/997809a49ca26a12eec1824881bee5df2b303cd19b37d7056f986a681d40a3ab.jpg)  
(e) Pitch added mass

![](images/65925b0262c5c081269ece7fce37a9c8d65a20c2b7d751ab7505e30f1a6d5203.jpg)  
(f) Pitch wave damping  
Figure 8. Comparison for added mass and wave damping

Figure 9 shows the comparison of wave exciting force computed from the two panel meshes, where the normalization parameter B is defined as the distance between two columns. The numerical results get high agreement with the experiment data. As similar with Figure 8, there is no big discrepancy between the results computed from “Mesh 1” and “Mesh 2”, which shows that the bracings have no such big influence on the wave exciting force of the platform. Special attention should be paid on the horizontal exciting force that small difference between the two numerical results can be observed, however, the experiment data seems much closer to the result of “Mesh 2” than “Mesh 1”, which proves that the theoretical contribution from the bracings approximated by potential theory may not be so important in the computation for the whole submerged body.

![](images/752db437c0ea216b69fd2a91b815bac7a1b72f7eaa12e249a218ba358395ac82.jpg)  
(a) Horizontal exciting force

![](images/7cbf157024acd504e333b52d1273db5b255f9b96894cac74d3162b0929b1b70e.jpg)  
(b) Vertical exciting force

![](images/964bcce3614d24252b3c8f59389138b3d300b0875fb92a8ba3bf1f9966bffd14.jpg)  
(c) Exciting torque  
Figure 9. Comparison for wave exciting force

## 5.3 Influence of the slender bracings on the free surface elevation

Figure 10 and 11 show contour plots of the scattered free surface elevation (unit: m) in the vicinity of the platform with different incident wave angles. Figure 10(a), 10(b), 11(a) and 11(b) show free surface elevation at a low wave frequency. Relatively flat wave field can be observed, where the free surface has not been changed obviously by the diffraction waves, since in the case of large wavelength, the inciden wave can almost easily pass through the ‘obstacle’. Figure 10(c), 10(d), 11(c) and 11(d) show the elevation at a relative high wave frequency, where the wavelength is much more comparable to the physical dimension of the platform. In Figure 11(c) and 11(d), the largest enhancement of the elevation reaches at the neighborhood of the left-hand-side column. In Figure 10(c), 10(d), 11(c) and 11(d), with an incident angle of $\beta = 0 ^ { \circ } \ \mathrm { o r } \ \beta = 9 0 ^ { \circ }$ , the side of the platform in x-direction or y-direction experiences a standingwave-like wave field. The free surface elevation varies sharply along the incident direction, until the uppermost column in this direction. This is mainly due to the reflection of the incident wave by the main columns along the side of the platform, and the superposition of the two waves with a nearly equivalen phase. As the wave goes far away from the structure, the amplitude of elevation decreases. Figure 10(a), 10(c), 11(a) and 11(c) show free surface elevation in the presence of the platform with slender bracings (in Mesh 1), while Figure 10(b), 10(d), 11(b) and 11(d) show free surface elevation in the presence of the platform without slender bracings (in Mesh 2). Comparison between the two results shows no big difference, which proves the existence of the slender bracings does not change the flow field notably.

![](images/dce416d17044a617e23cc47762c6d297b004238a2eeaa844cbc5ba4f91f417ee.jpg)  
(a) In Mesh 1, at kL = 10.91

![](images/db01507e1bcaabec9de2ebeb074f5a51c19a37558dcfa1f9c241ddc4ddc3f9e2.jpg)  
(b) In Mesh 2, at kL = 10.91

![](images/66dd3f5c8f6facc8955135863312ad3b6079dd19ab09fa22e8243f86713b91b5.jpg)  
(c) In Mesh 1, at kL = 26.50

![](images/d959d871bf1a0b12340b376d61272d0e494c4c54761b2142ea31640c1f95ec74.jpg)  
(d) In Mesh 2, at kL = 26.50

Figure 10. Contour plot of the scattered free surface elevation for fixed platform when $\beta = 0 ^ { \circ }$  
![](images/388270d09965fa196fff88df5513af323d178f52666daf089b654198b683eac0.jpg)

(a) In Mesh 1, at kL = 10.91  
![](images/35103d7d0992339dcbeea0897e9a212fce30d176c58ae1670882e455da9d9625.jpg)  
(c) In Mesh 1, at kL = 26.50

(b) In Mesh 2, at kL = 10.91  
![](images/4bd6fae45a041b3359cf14255da55cb9dc88379e6b57ec41b22655deb175ce5f.jpg)  
(d) In Mesh 2, at kL = 26.50  
Figure 11. Contour plot of the scattered free surface elevation for fixed platform when $\beta = 9 0 ^ { \circ }$

## 5.4 Comparison of motion response by four numerical methods

Our interest lies in how the small bracings affect the motion of the platform. Therefore, we computed the motion RAOs through four different numerical methods and compare them to the measured data from the laboratory experiment. Results are shown in Figure 12\~14, at three different wave headings, i.e., $\beta = 0 ^ { \circ }$ $\beta = 9 0 ^ { \circ }$ and $\beta = 1 8 0 ^ { \circ }$

![](images/0856755ce5e67dcce30ef1021b515b37e84534b184ab96a79b9a12da837ffa74.jpg)  
(a) Surge motion response

![](images/f8d304c24ed51d09eec5b5c8bb7b404c02382a0b310ed68868fcb075027a7000.jpg)  
(b) Heave motion response

![](images/84d2f1afb7c26a98e2848e056b7beae279d300f739617465a18a744464d2591e.jpg)  
(c) Pitch motion response  
Figure 12. RAOs comparison for $\beta = 0 ^ { \circ }$

Since the natural frequency of the semi-submersible platform is pretty low in the heave direction, a resonant response can be found at the region of long wavelength (low frequency) computed by the panel method, with a peak value of 8.67. This is because that the panel model is a pure potential model with no viscous effect included, meanwhile, at the resonance region, potential wave damping plays much less important role than the viscous damping. It is also noticed that the heave resonance occurs at $\lambda / L = 6 . 0 $ which agrees fairly well with the prediction by Eigen analysis. Except for the heave motion, results in other directions show reasonable consistence between the other three numerical methods and the experiment data, which means that the potential panel model needs a supplement model to account for the viscous effect especially in the region of heave resonance, when it is applied to such kind of complex structure which consists of many slender cylinders. In the meantime, the RAOs calculated by the Morison stick method have some discrepancies with those obtained by other methods. This is largely due to the lack of potential wave damping in the pure Morison model, since within this model, no effective formula has been introduced into accounting for the potential wave damping effect, which mainly comes from the major part of the platform. However, it is noted that the Morison stick model can predict more reasonable results of motion RAO in heave direction than the other models.

On the other hand, results of the two hybrid models show quite satisfactory consistence with the experiment data in almost all the directions, but some discrepancies still can be found between each other. In the pitch mode, the hybrid method II seems to have overestimated the pitch rotational motion in the long wavelength region $( \lambda / L > 2 . 0 )$ . This may be due to slightly underestimation of the total damping of the immersed structure. In the most interested heave direction, the two hybrid models give pretty good prediction of the motion RAO in the resonance region, showing that the viscous damping has been modeled in a correct form. In addition, similar to the pitch mode, difference between the heave RAOs of the two hybrid models still can be found in the long wavelength region $( \lambda / L > 2 . 0 )$ , which should be mainly attributed to the potential wave damping from the bracings, since it has not been correctly modeled in the hybrid method II while in the hybrid method I it has been computed accurately. It shows that the heave motion in the resonant region is extremely sensitive to the total damping involved in the floating system.

![](images/b7092b927a49418654ce2569420505620c1f8710e373a707571cb62aab09acb4.jpg)  
(a) Surge motion response

![](images/77893d064a5340d4d2601e248ddee4a5f484322b45edd7b8539e705c40e49579.jpg)  
(b) Sway motion response

![](images/5503fc33d9a94111d07058d7d696d63f11a04756067078a104cc282256f49e2c.jpg)  
(c) Heave motion response

![](images/8a9449cf788a4628a6494c5230617f5528710ff9920bd6bab8c0a2eb1812905c.jpg)  
(d) Roll motion response

![](images/348f162e08cc0ab43a1783e7a7aa9bb294fe3fbbc52e47962f7de80b4bb099b7.jpg)  
(e) Pitch motion response

![](images/c0f9c0c023972dc3e17387314272408f39d02328b312c59ce424929ad435d970.jpg)  
(f) Yaw motion response  
Figure 13. RAOs comparison for $\beta = 9 0 ^ { \circ }$

![](images/dddc4900a79b73c10e35fb2ca59b7b638168982e78591a240889eb2e4d1ed115.jpg)  
(a) Surge motion response

![](images/98b25cfbdb803a4596bbcfa126da455157a85b099a9cf34205ed68f9d37cec02.jpg)  
(b) Heave motion response

![](images/79a0bd1fc471bec85b23a3881430b0b0f887597eb838a9b0ccaee8779600075b.jpg)  
(c) Pitch motion response  
Figure 14. RAOs comparison for $\beta = 1 8 0 ^ { \circ }$

## 5.5 Comparison of computational time

In addition to the accuracy in prediction of the motion RAOs by the four numerical methods mentioned above, the computational time is another important issue for considering an appropriate manner in practical engineering problems. Therefore, comparison of computational time for each method is shown in Figure 15. Numerical computations by the above four methods are carried out on a workstation with an Intel(R) Xeon(R) E5-1620 v2 CPU of 3.70 GHz and 16.0 GB memory, on 64-bit Windows operating system.

![](images/881ca6a1a8ced0a2d92a257f03fb28d1fd5ebdda009014affe80cca81340b16b.jpg)  
Figure 15. Time consumption of the four different computational methods

In the comparison, all the computations are implemented for 140 wave periods. ‘Method 1’ stands for the hybrid method I, ‘Method 2’ the hybrid method II, ‘Method 3’ the pure Morison stick method, and ‘Method 4’ the pure panel method. It can be seen that the hybrid method I requires the longest computational time, since it needs to solve a panel model for the whole immersed structure including all the small bracings, as well as the fluid kinematics which is derived from the diffracted and radiated wave field. Time consumption of the pure panel method is slightly less than the hybrid method I, which proves that the computation for the ‘disturbed’ fluid kinematics contributes relatively smaller to the entire CPU time in comparison to the panel computation. The Morison stick method requires the less computational time, almost within 1 second. This means that provided all the members of the structure are small with respect to the wavelength, the Morison stick method provides a cheapest computation tool for the practical engineering problems. At the end, it is most encouraging to see that the hybrid method II consumes only a little larger CPU time than the Morison stick method, which proves that the most time consuming part of computation depends on the panel number and that discarding all the small bracings can save a large portion of computational time without loss of so much accuracy.

## Conclusions

Two hybrid panel-stick models have been proposed to study the hydrodynamic performance of the Kyushu University FOWT in which many slender bracings are used. A comparison between four numerical methods as well as the laboratory experiment has been made to investigate the effect of the slender bracings. Results show that the inertia forces acting on the bracings does not contribute too much to the behavior of the entire platform for this kind of floating body except the heave resonant region, partly due to that the volume of the bracings is much less than the main part of the platform. The following conclusions may be obtained:

(1) A hybrid model is necessary for hydrodynamic analysis of the semi-submersible type floating body with both large members and slender members in comparison to the wavelength.

(2) The hybrid method II proposed in the paper shows best performance for prediction of the motion RAOs of the Kyushu University FOWT. The bracings almost merely take important role on the viscous effect which arises from the separation of flow around these small members.

(3) The pure Morison stick model is the fastest method for this kind of floating body. It can predict reasonable motion RAOs even in the heave resonance region of such ‘mixed’ semi-submersible platforms.

## Acknowledgements

This research is supported in part by Grants-in-Aid for Scientific Research (B), MEXT (No. 15H04215). We would like to thank ClassNK (Nippon Kaiji Kyoukai), Oshima Shipbuilding Co. Ltd., Shin Kurushima Dockyard Co. Ltd., and Tsuneishi Holdings Corp. for funding this study and for permission to publish this paper. The first author gratefully acknowledges the financial support provided by the MEXT Scholarship (Grant No. 123471) from Japanese Government during the three-year PhD research.

## References

1. Leblanc L, Petitjean F, Roy FL, Chen XB (1993). A mixed panel-stick hydrodynamic model applied to fatigue life assessment of semi-submersibles. Proceedings of 12<sup>th</sup> International Conference on Ocean, Offshore and Arctic Engineering, Glasgow, Scotland.

2. Hooft JP (1972) Hydrodynamic aspects of semi-submersible platforms. PhD thesis, Delft University of Technology.

3. Malenica S, Sireta FX, Bigot F, Derbanne Q, Chen XB (2010). An efficient hydro structure interface for mixed panel-stick hydrodynamic model. Proceedings of 25<sup>th</sup> International Workshop on Water Waves and Floating Bodies, Harbin, China.

4. Veer RV (2008) Application of linearized Morison load in pipe lay stinger design. Proceedings of 27<sup>th</sup> International Conference on Ocean, Offshore and Arctic Engineering, Estoril, Portugal.

5. Faltinsen OM (1990) Sea loads on ships and offshore structures. Cambridge University Press.

6. Newman JN (1999) Heave response of a semi-submersible near resonance. Proceedings of 14<sup>th</sup> International Workshop on Water Waves and Floating Bodies, Port Huron, USA.

7. Hu CH, Sueyoshi M, Kyozuka Y, Yoshida S, Ohya Y (2014) Development of new floating platform for multiple ocean renewable energy. Proceedings of the Grand Renewable Energy International Conference 2014, Tokyo.

8. Newman JN (1986) Distributions of sources and normal dipoles over a quadrilateral panel. Journal of Engineering Mathematics 20:113-126.

9. Webster WC (1975) The flow about arbitrary three-dimensional smooth bodies. Journal of Ship Research 19(4):206-218.

10. Kashiwagi M, Takagi K, Yoshida H, Murai M, Higo Y (2003) Fluid dynamics of floating bodies in practice: Part 1 numerical computation method of the motion response problems. Seizando Press (in Japanese).

11. Newman JN (1985) Algorithms for free-surface Green function. Journal of Engineering Mathematics 19:57–67.

12. Liu YY, Iwashita H, Hu CH (2014) A calculation method for finite depth free-surface Green function. International Journal of Naval Architecture and Ocean Engineering, 7(2). (To be appear)

13. Saad Y, Schultz MH (1986) GMRES: A generalized minimal residual algorithm for solving nonsymmetric linear systems. SIAM J Sci Stat Comput 7: 856-869.

14. Zhao Y, Graham JMR (1996) An iterative method for boundary element solution of large offshore structures using the GMRES solver. Ocean Engineering 23(6): 483-495.

15. Hu CH, Sueyoshi M, Liu C, Liu YY (2014) Hydrodynamic Analysis of a Semi-Submersible Type Floating Wind Turbine. Journal of Ocean and Wind Energy, 1(4): 202-208.

## Appendix

A procedure for calculating natural periods of a semi-submersible is given here. Since in the neighborhood region of the natural periods, the wave damping is relatively very small and can be neglected. From Eq. (6) we know the free motion equation of a semi-submersible without damping is

$$
\left\{- \omega^ {2} ([ M ] + [ a ]) + ([ K ] + [ C ]) \right\} \{\xi \} = 0.\tag{A1}
$$

In these matrices, many of the elements are zeroes, only leaves the diagonal terms and some coupling terms are nonzero. We can thus further deduce characteristic equations for each mode from Eq. (A1) as the followings. For heave motion, we have

$$
- \omega^ {2} \left(M _ {3 3} + a _ {3 3}\right) + K _ {3 3} + C _ {3 3} = 0.\tag{A2}
$$

For yaw motion, we have

$$
- \omega^ {2} (M _ {6 6} + a _ {6 6}) + K _ {6 6} = 0.\tag{A3}
$$

For surge and pitch motion, we have

$$
A _ {1} \omega^ {4} + B _ {1} \omega^ {2} + C _ {1} = 0,\tag{A4a}
$$

where

$$
A _ {1} = \left(M _ {1 1} + a _ {1 1}\right) \left(M _ {5 5} + a _ {5 5}\right) - \left(M _ {1 5} + a _ {1 5}\right) \left(M _ {5 1} + a _ {5 1}\right),\tag{A4b}
$$

$$
B _ {1} = K _ {1 5} \left(M _ {5 1} + a _ {5 1}\right) + K _ {5 1} \left(M _ {1 5} + a _ {1 5}\right) - \left(K _ {5 5} + C _ {5 5}\right) \left(M _ {1 1} + a _ {1 1}\right) - K _ {1 1} \left(M _ {5 5} + a _ {5 5}\right),\tag{A4c}
$$

and

$$
C _ {1} = \left(K _ {5 5} + C _ {5 5}\right) K _ {1 1} - K _ {1 5} K _ {5 1}.\tag{A4d}
$$

For sway and roll motion, we have

$$
A _ {2} \omega^ {4} + B _ {2} \omega^ {2} + C _ {2} = 0,\tag{A5a}
$$

where

$$
A _ {2} = \left(M _ {2 2} + a _ {2 2}\right) \left(M _ {4 4} + a _ {4 4}\right) - \left(M _ {2 4} + a _ {2 4}\right) \left(M _ {4 2} + a _ {4 2}\right),\tag{A5b}
$$

$$
B _ {2} = K _ {2 4} \left(M _ {4 2} + a _ {4 2}\right) + K _ {4 2} \left(M _ {2 4} + a _ {2 4}\right) - \left(K _ {4 4} + C _ {4 4}\right) \left(M _ {2 2} + a _ {2 2}\right) - K _ {2 2} \left(M _ {4 4} + a _ {4 4}\right),\tag{A5c}
$$

and

$$
C _ {2} = \left(K _ {4 4} + C _ {4 4}\right) K _ {2 2} - K _ {2 4} K _ {4 2}.\tag{A5d}
$$

It should be noted that, for Eq. (A4a) or Eq. (A5a), the two modes are coupled and thus should be solved simultaneously. The two positive solutions of Eq. (A4a) correspond to the surge (the smaller) and the pitch (the larger) natural angular frequencies, respectively; similarly, the two positive solutions of Eq. (A5a) correspond to the sway (the smaller) and the roll (the larger) natural angular frequencies, respectively. In addition, since the added mass coefficients which depend on the wave frequency are contained, all the above equations need to be solved through iteration processes to find the exact values.