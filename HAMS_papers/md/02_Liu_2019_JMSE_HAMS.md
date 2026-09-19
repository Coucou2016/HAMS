Article

# HAMS: A Frequency-Domain Preprocessor for Wave-Structure Interactions—Theory, Development, and Application

Yingyi Liu

Research Institute for Applied Mechanics, Kyushu University, Fukuoka 816-0811, Japan; liuyingyi@riam.kyushu-u.ac.jp; Tel.: +81-80-8565-7934

Received: 14 February 2019; Accepted: 16 March 2019; Published: 26 March 2019

![](images/807d5e99bc3da47b33053ecbafe71cbb4b5387d427a1eec9e66ebb4cf1ad9a81.jpg)

Abstract: This paper presents the theoretical background, the numerical implementation, and the applications of a new software that has been developed in recent years for the analysis of wave-structure interactions. The software is developed in the frequency domain, as a preprocessor of computing the wave excitation force, the added mass, and the wave radiation damping, for the input to a time-domain solver via the Fourier cosine and sine transforms. In addition, it can also predict the motion responses of a marine structure with sufficient accuracy, with or without the presence of a mooring system. Unlike other frequency-domain software, such as WAMIT<sup>®</sup> and Hydrostar<sup>®</sup>, the present software currently employs the least squares method in association with a partially extended boundary integral equation method to remove the so-called “irregular frequencies”. Calculation of the free-surface Green’s function employs a combination of fast-convergent series expansions in different parametric sub-regions. The solution of the resultant linear algebraic system employs the lower-upper (LU) decomposition method. Symmetry properties can be exploited, and the open multi-processing (OpenMP) parallelization technique can be applied to reduce the computation burden. The accuracy and the efficiency of the developed software are finally confirmed by numerical validations on three benchmark cases of a floating ellipsoid, a truncated circular cylinder and the OC4 DeepCwind semisubmersible floating wind turbine. A free executable version of the software is available to the research communities with a hope of facilitating the advancements in the researches that are relevant to ocean engineering and marine renewable energies.

Keywords: marine hydrodynamics; offshore engineering; offshore renewable energy; potential flow theory; Green’s function; free surface; computation method

## 1. Introduction

Safety and performance are always considered as the first priorities for a marine structure when it is in operation. The sea circumstances can be varied depending on the site location, weather condition, and many other factors. It is preferable for assessments with sufficient reliability to be done before the operation or even before the construction of the marine structure is taken into action. To this end, laboratory experiments are usually performed in advance for model calibrations, wave/load measurements, and system evaluations, etc. However, due to the expensive cost, instead of carrying out the model test for all sea conditions, a reliable numerical tool to assist the assessment in association with a model test in some critical sea conditions are normally employed, which can therefore reduce the overall cost.

So far, to evaluate the overall performance of large marine structures, the boundary integral equation method (BIEM) based on the potential flow theory may still be the first choice over other computational fluid dynamics (CFD) methods based on the N-S equations [1]. This is due to the fact that the viscous term in the N-S equations is not dominant for such a large marine structure when<sup>1 1</sup> its cross-section diameter D far exceeds 0.15L (in which L is the wavelength) [2]. It should be notedο <sub>that applying a CFD method is, of course, the best choice for consideration of the accuracy, but the</sub>(ξ<sub>3</sub>,η<sub>3</sub>) 1 1 <sub>η</sub>1 1ο tiny improvement of the accuracy in computation of such a marine structure can hardly compensate<sup>(ξ</sup><sub>4ζ</sub> the time-consuming computational cost. This problem is especially magnified when the integral�ሬ⃗3 3<sup>1 1</sup> η <sup>performance</sup> <sup>of</sup> <sup>the</sup> <sup>marine</sup> <sup>structure</sup> <sup>needs</sup> <sup>to</sup> <sup>be</sup> <sup>quickly</sup> <sup>evaluated</sup> <sup>with</sup> <sup>respect</sup> <sup>to</sup> <sup>a</sup> <sup>batch</sup> <sup>of</sup> <sup>input4 4</sup>ξ <sup>ζ</sup> ξ environmental conditions and parameters. In such cases, the computation time of applying a CFD�ሬ⃗ method is incredibly excessive and still not acceptable on up-to-date modern computers.<sup>Figure</sup> <sup>3.</sup> <sup>Illustration</sup> <sup>of</sup> <sup>the</sup> <sup>local</sup> <sup>coordinate</sup> <sup>system</sup> <sup>o</sup>

The BIEM is fundamentally based on the Green’s theorem, by using a free-surface Green’s function<sup>shape,</sup> <sup>respectively.</sup> <sup>The</sup> <sup>origin</sup> <sup>o</sup> <sup>normally</sup> <sup>locates</sup> <sup>at</sup> <sup>the</sup> <sup>centroid</sup> <sup>o</sup> <sub>that satisfies boundary conditions on the free surface, the seabed, and the far field, the unknowns are</sub>points to the normal direction of the panel. The sequence of vertFigure 3. Illustration of the local coordinate system of each panel, in triangular sha <sub>reduced to those merely on the immersed body boundary such that the computational burden can be</sub>the normal direction that points into the inside of the body.shape, respectively. The origin o normally locate at the centroid  each panel, and reduced significantly. The remaining computational cost involves two aspects,<sup>points</sup> <sup>to</sup> <sup>the</sup> <sup>normal</sup> <sup>direction</sup> <sup>of</sup> <sup>the</sup> <sup>panel.</sup> <sup>The</sup> <sup>sequence</sup> $\mathrm { i . e . , }$ <sub>the calculation of</sub>ertices is arranged i the free-surface Green’s function and the solution of the resultant linear algebraic system. There are<sup>the</sup> <sup>normal</sup> <sup>direction</sup> <sup>that</sup> <sup>points</sup> <sup>into</sup> <sup>the</sup> <sup>inside</sup> <sup>of</sup> <sup>the</sup> <sup>body.</sup> several existing numerical algorithms for fast evaluation of the free-surface Green’s function, e.g.,In order to solve the linear algebraic system Equation Newman [3,4], Telste and Noblesse [5], and Wu et al. [6] for the deep water, and Newman [3,4],elimination will commonly be adopted. These direct solvers are Chen [7,8], and Liu et al. [9,10] for the finite-depth water. Worth noting is that Telste and Noblesse [5]computations (N denotes matrix size). For a large-scale compuIn order to solve the linear alg braic system Equation (8), a direct s and Liu et al. [10] also released their open-source codes respectively for the deep water and theoffshore structures, a direct inversion or inefficient iteration ofelimination will commonly be adopted. These direct solvers are generally rob fi<sub>nite</sub> d<sub>ept</sub>h <sub>water. In respect to t</sub>h<sub>e so</sub>l<sub>ution o</sub>f l<sub>inear equations, t</sub>h<sub>ere are</sub> b<sub>asica</sub>ll<sub>y two</sub> b<sub>ranc</sub>h<sub>es o</sub>fequations with �ሺ�<sup>ସ</sup>ሻ unknowns for a set of wave frequencies computations (N den tes matrix size). For a large-scale computation of compl approaches to choose, i.e., the direct solution methods and the indirect iterative methods. The directeven with modern computers. On the other hand, although soffshore structures, a direct inversion or inefficient itera ion of such a large, d <sub>met</sub>h<sub>o</sub>d<sub>s, suc</sub>h <sub>as t</sub>h<sub>e Gauss e</sub>l<sub>imination met</sub>h<sub>o</sub>d<sub>, requires a computationa</sub>l <sub>e</sub>ff<sub>ort o</sub>fGMRES method [11], can reduce the effort to equations with �ሺ�<sup>ସ</sup>ሻ unkn wns for  set of wave frequenci $\mathcal { O } ( N ^ { 3 } )$ <sup>ଶ</sup>ሻ <sub>operatio</sub> <sub>operationsms</sub> <sub>prohibit</sub> methods can easily have a problem of ill preconditions. In additiwhere N is the dimension of the linear systems. The iterative methods, such as the generalizedeven with modern computers. On th other hand, a though some iter tive the radiation-diffraction problminimum residual (GMRES) method [11], can reduce the effort toGMRES method [11], c n reduce the effort to $\mathcal { O } ( N ^ { 2 } )$ eds to be solved with mul<sup>ଶ</sup>ሻ <sub>operations;</sub> <sub>ho ever,</sub> <sub>thoperations but may have</sub> wave frequency, the computation effort of using either a direct methods can easily have a problem of ill reconditions. In addition, consideringa problem of ill preconditions. Meanwhile, taking into consideration the fact that, normally, the not acceptable because it needs to successively solve the linear ethe radiation-diffraction problem needs to be solved w th multiple wav hearadiation-diffraction problem needs to be solved with multiple wave headings for each single wave this reason, the LU decomposition is adopted in the solver, sincwave frequency, the computation effort of using e ther a direct method or an itfrequency, the computation effort of using such an iterative method is still high because it needs to not acceptable because it needs to successisuccessively solve the linear equations for every wave heading.

this reason, the LU decomposition is adopted in the solver, since it only needs tIn addition, another computational issue that should be given attention is the suppression of the so-called “irregular frequencies”. The discrete boundary integral equation is ill-conditioned and not uniquely solvable at these frequencies. The occurrence of such phenomena was firstly discovered by Ref. [12] and later studied by several scholars. There are basically two branches of numerical methods to remove these irregular frequencies: modification of the integral operator or modification of the domain of the integral operator [13,14], and extension of the boundary conditions in Dirichlet or Neumann type [15–17]. Although the first branch of methods can theoretically find the unique solutions at all frequencies, they have a critical numerical drawback in calculating the double derivatives of free-surface Green’s function. The second branch of methods requires the solution of a set of completely extended boundary integral equations for which an additional computational effort of evaluating the logarithmic singularity on the free surface is necessary.

This paper presents a new software that solves the above challenging issues. It has been developed for years and tested repeatedly via a series of research and industrial projects. The calculation of free-surface Green’s function employs a combination of series expansions in different parametric subregions with the aid of the epsilon acceleration algorithm, while compromising the accuracy and efficiency of calculations. The solution of the resultant linear algebraic system adopts the lower-upper (LU) decomposition method, which needs to be evaluated only once for the left-hand side matrix over a distribution of wave headings. Removal of the irregular frequencies uses a partially extended boundary integral equation method in association with the least squares method, which reduces the computational effort and avoids evaluation of the logarithmic singularity on the free surface. In addition, symmetry properties are exploited wherever possible for bodies with 1\~2 symmetry planes, and the open multi-processing (OpenMP) parallelization technique is applied to the codes in order to reduce the computation time on multi-core machines. The software is therefore named HAMS (Hydrodynamic Analysis of Marine Structures). In the subsequent computations, the computer codes are compiled by $\mathrm { I n t e l ^ { \mathrm { ( B ) } } }$ Fortran Compiler 18.0 $\mathrm { ( I n t e l ^ { \mathrm { ( B ) } } }$ Parallel Studio XE 2018) and Microsoft<sup>®</sup> Visual Studio 2015.

The remaining part is organized into the following sections: The background theory and the mathematical algorithms of wave-structure interactions are introduced in Section 2. The special techniques of numerical implementation are introduced as separate topics in Section 3. Validation of the software for a simple analytical geometry is given in Section 4.1. Application of the software to marine hydrodynamics of a complex floating structure is carried out in Section 4.2. The conclusions are given in Section 5.

## 2. Theory and Algorithm

## 2.1. Governing Equation and Boundary Conditions

The flow is assumed to be inviscid, free of separation or lifting effects, irrorational, and incompressible. In this potential flow framework, the flow can be described by a velocity potential $\phi ( x , y , z )$ which can be further decomposed into three parts: the incident wave potential $\phi _ { i } ( x , y , z )$ the diffracted wave potential $\phi _ { d } ( x , y , z )$ , and the radiated wave potential $\phi _ { r } ( x , y , z )$

$$
\phi = \phi_ {i} + \phi_ {d} + \phi_ {r}.\tag{1}
$$

Mathematically, the above velocity potentials satisfy the Laplace equation in the entire fluid domain

$$
\left(\frac {\partial^ {2}}{\partial x ^ {2}} + \frac {\partial^ {2}}{\partial y ^ {2}} + \frac {\partial^ {2}}{\partial z ^ {2}}\right) \phi (x, y, z) = 0,\tag{2}
$$

subjecting to boundary conditions respectively at the free surface, on the body surface, at the sea bottom, and in the far field, as shown in Figure 1, which can be expressed as

$$
\left. \begin{array}{c} \frac {\partial \phi}{\partial z} \Big | _ {z = 0} = v \phi \\ \frac {\partial \phi}{\partial n} \Big | _ {S _ {B}} = V _ {\mathrm{n}} \\ \frac {\partial \phi}{\partial z} \Big | _ {z = - h} = 0 o r \lim _ {z \to \infty} \left(\frac {\partial \phi}{\partial z}\right) = 0 \\ \lim _ {R \to \infty} \left[ \sqrt {v R} \left(\frac {\partial \phi}{\partial R} - \mathrm{i} v \phi\right) \right] = 0 \end{array} \right\},\tag{3}
$$

where $v = \omega ^ { 2 } / g$ is the wave number in deep water, $g$ is the acceleration of gravity, $V _ { n }$ denotes the normal velocity at a point on the immersed body boundary $S _ { \mathrm { B } } .$ , h is the water depth in case of finite depth water, and R denotes the horizontal distance from the body.

The last boundary condition in Equation (3), also referred to as the Sommerfeld radiation condition, shows that the velocity potential gradually decays with the horizontal distance and eventually vanishes in the far field. It should be noted that the Sommerfeld radiation condition applies only to the scattered potential (including diffracted and radiated wave potentials).

If further using subscripts from 0 to 7 to denote the incident wave potential, the six components of the radiated wave potential, and the diffracted wave potential, then the total velocity potential is expressed as

$$
\phi = \phi_ {0} + \phi_ {7} - \mathrm{i} \omega \sum_ {k = 1} ^ {6} \xi_ {k} \phi_ {k},\tag{4}
$$

where the constant $\xi _ { k } \left( k = 1 , 2 , \dots , 6 \right)$ denotes the complex amplitudes of the body oscillation motion in its six rigid-body degrees of freedom, and $\phi _ { k } \left( k = 1 , 2 , \ldots , 6 \right)$ denotes the corresponding unit-amplitude radiation potentials. In the framework of the Airy wave theory, the incident wave potential $\phi _ { 0 }$ is defined by

$$
\phi_ {0} = - \frac {\mathrm{i} g A}{\omega} e ^ {v z} e ^ {\mathrm{i} v (x c o s \beta + y s i n \beta)}\tag{5}
$$

for infinite depth water and

$$
\phi_ {0} = - \frac {\mathrm{i} g A}{\omega} \frac {\cosh k (z + h)}{\cosh k h} e ^ {\mathrm{i} k (x \cos \beta + y \sin \beta)}\tag{6}
$$

for finite depth water, where $\beta$ is the angle between the direction of propagation of the incident wave and the positive x-axis, and k is the real positive root of the water wave dispersion equation.

![](images/ab9e9d7fe8e59eae0df3232808f4722da5738be8ad0756f9924936fa5e0ac717.jpg)  
Figure 1. Definition of the coordinate system in the three-dimensional space. Q denotes the source point on the immersed body boundary $S _ { \mathrm { B } } ,$ and P denotes the field point anywhere in the fluid domain.

## 2.2. Mixed Source/Dipole Formulation and Discretization of the Integral Equations

By applying Green’s theorem, the radiated and diffracted wave velocity potentials on the immersed body surface $S _ { \mathrm { B } }$ are solved by the mixed source/dipole boundary integral equations. <sup>B</sup>The integral equation satisfied by the radiation velocity potential on the body boundary takes the ntegral <sub>form of</sub>

$$
2 \pi \phi_ {k} (\boldsymbol {x}) + \iint_ {S _ {\mathrm{B}}} \phi_ {k} (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\xi}} \mathrm{d} S _ {\xi} = \iint_ {S _ {\mathrm{B}}} V _ {\mathrm{n}, k} (\boldsymbol {\xi}) G (\boldsymbol {\xi}; \boldsymbol {x}) \mathrm{d} S _ {\xi}, (k = 1, 2, \dots , 7),\tag{7}
$$

where $\pmb { \xi }$ <sup>ా ా</sup>denotes the source point, x denotes the field point, and $V _ { \mathrm { n } , k }$ denotes the kth component of the where � denotes the source point,<sub>body surface boundary condition.</sub>

<sup>ody</sup> <sup>surface</sup> <sup>boundary</sup> <sup>condition.</sup> The boundary surfaces are discretized into a set of quadrilateral or triangular plane panels to <sup>The</sup> <sup>boundary</sup> <sup>surfaces</sup> <sup>are</sup> <sup>discretized</sup> <sup>into</sup> <sup>a</sup> <sup>set</sup> <sup>of</sup> <sup>quadrilateral</sup> <sup>or</sup> <sup>triangular</sup> <sup>plane</sup> <sup>panels</sup> <sup>to</sup> approximate the exact geometry. The vertices of each panel are numbered in the counter-clockwise approximate the exact geometry. The vertices of each panel are numbered in the counter-clockwise <sub>direction when the panel is viewed from the fluid domain. The radiation and diffraction velocity</sub> <sup>direction</sup> <sup>when</sup> <sup>the</sup> <sup>panel</sup> <sup>is</sup> <sup>viewed</sup> <sup>from</sup> <sup>the</sup> <sup>fluid</sup> <sup>domain.</sup> <sup>The</sup> <sup>radiation</sup> <sup>and</sup> <sup>diffraction</sup> <sup>velocity</sup> potentials are also represented by piecewise constant functions over each panel. By applying such potentials are also rep<sub>a “collection method</sub> $\therefore$ sented by piecewise constant functions over each panel. By applying such a <sub>as shown in Figure 2, the boundary integral equations (Equation (7)) are</sub> <sup>“collection</sup> <sup>met</sup>discretized into

$$
2 \pi \phi_ {k} (\boldsymbol {x} _ {i}) + \sum_ {j = 1} ^ {N _ {p}} D _ {i j} \phi_ {k} (\boldsymbol {x} _ {j}) = \sum_ {j = 1} ^ {N _ {p}} S _ {i j} V _ {\mathrm{n}, k} (\boldsymbol {x} _ {j}), (i = 1, 2, \dots , N _ {p}; k = 1, 2, \dots , 7),\tag{8}
$$

where $N _ { p }$ is the number of panels. The integrations of sources and dipoles over each panel are where �<sub>௣</sub> is th<sub>represented by</sub>

$$
S _ {i j} = \iint_ {S _ {\mathrm{B}, j}} G (\boldsymbol {\xi}; \boldsymbol {x} _ {i}) \mathrm{d} S _ {\xi},\tag{9}
$$

$$
D _ {i j} = \iint_ {S _ {\mathrm{B}, j}} \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x} _ {i})}{\partial n _ {\xi}} \mathrm{d} S _ {\xi},\tag{10}
$$

where $S _ { \mathrm { B } , j }$ denotes the jth panel surface.

![](images/ee91766b21400f74297609274216e94b0bef2604f4e10852a470b0aeff373058.jpg)  
Figure 2. Illustration of the collection method: Collection points are located at the centroid of each panel,subsequently. and the influence coefficients $S _ { i j }$ and $D _ { i j }$ between each two of these points are evaluated subsequently.

## <sup>subsequently.</sup> 2.3. Evaluation of Green’s Function and Self-Influences

In the boundary integral equations (Equation (7)), numerical evaluation of free-surface Green’s. function $G ( x ; \pmb { \xi } )$ becomes the most essential task due to its highly complex nature. It is not trivial, <sup>In</sup> <sup>the</sup> <sup>boundary</sup> <sup>integral</sup> <sup>equations</sup> <sup>(Equation</sup> <sup>(7)),</sup> <sup>numerical</sup> <sup>evaluation</sup> <sup>of</sup> <sup>free-surface</sup> <sup>Green</sup>because of the three sticking points that need to be overcome: the singularity in the denominator of theon of Green’s Function and Self-Influences <sup>function</sup> <sup>G(x;</sup> <sup>ξ)</sup> <sup>becomes</sup> <sup>the</sup> <sup>most</sup> <sup>essential</sup> <sup>task</sup> <sup>due</sup> <sup>to</sup> <sup>its</sup> <sup>highly</sup> <sup>complex</sup> <sup>nature.</sup> <sup>It</sup> <sup>is</sup> <sup>not</sup> <sup>trivia</sup>integrand, the oscillation nature of the Bessel function, and the integration range from 0 to infinity. <sup>because</sup> <sup>of</sup> <sup>the</sup> <sup>thr</sup>The Green function $G ( x ; \pmb { \xi } )$ <sup>ing</sup> <sup>points</sup> <sup>that</sup> <sup>need</sup> <sup>to</sup> <sup>be</sup> <sup>overcome:</sup> <sup>the</sup> <sup>singularity</sup> <sup>in</sup> <sup>the</sup> <sup>denominator</sup> , or source potential, is usually defined as the velocity potential at the field <sup>the</sup> <sup>inte</sup>point (x, $y , z )$ d, the oscillation nature of the Bessel function, and the integration ra <sub>due</sub> <sub>to</sub> <sub>a</sub> <sub>point</sub> <sub>source</sub> <sub>of</sub> <sub>strength</sub> <sub>(−4π)</sub> <sub>located</sub> <sub>at</sub> <sub>the</sub> <sub>source</sub> <sub>point</sub> $( \xi , \eta , \zeta )$ 0 to infinit<sub>. The Green</sub> <sup>The</sup> <sup>Green</sup> <sup>function</sup> function is defined by

$$
G = \frac {1}{r} + \frac {1}{r _ {1}} + \frac {2 v}{\pi} \oint_ {0} ^ {\infty} \frac {e ^ {\mu (z + \zeta)}}{\mu - v} J _ {0} (\mu R) d \mu\tag{11}
$$

<sup>for</sup> <sup>infinite</sup> <sup>water</sup> <sup>depth</sup>for infinite water depth anddefined by

$$
G = \frac {1}{r} + \frac {1}{r _ {2}} + 2 \oint_ {0} ^ {\infty} \frac {(\mu + v) \cos h \mu (z + h) \cos h \mu (\zeta + h)}{\mu \sin h \mu h - v \cos h \mu h} e ^ {- \mu h} J _ {0} (\mu R) d \mu\tag{12}
$$

� = + + 2∳<sub>଴</sub> � �<sub>଴</sub>(��)d� <sup>water</sup> <sup>depth</sup> <sup>and</sup> <sub>for finite water depth, where the path of the contour integral passes below the pole at</sub> $\mu = v$ <sup>(12)</sup>in Equation 1<sub>(11) and at</sub> $\mu = k$ <sub>ஶ</sub> (� + �)cosh�(<sub>in Equation (12).</sub> $J _ { 0 } ( x )$ )cosh�(� + ℎ)<sub>is the Bessel function of zero order. r is the distance between</sub> <sup>for</sup> <sup>finite</sup> <sup>water</sup> <sup>depth,</sup> <sup>where</sup> <sup>the</sup> � �<sub>ଶ</sub> <sup>଴</sup> �sinh�ℎ<sub>the source point and the field point,</sub> $r _ { 1 }$ <sup>ath</sup> <sup>of</sup> <sup>the</sup> <sup>contour</sup> <sup>integral</sup> <sup>passes</sup> <sup>below</sup> <sup>the</sup> <sup>pole</sup> <sup>at</sup>  <sup>i</sup>�cosh�ℎ<sub>denotes the distance between the field point and the image of</sub> <sup>Equation</sup> <sup>(11)</sup> <sup>and</sup> <sup>at</sup>  <sup>in</sup> <sup>Equation</sup> <sup>(12).</sup> <sup>J0(x)</sup> <sup>is</sup> <sup>the</sup> <sup>Be</sup>the source point with respect to the mean free-surface, and $r _ { 2 }$ el function of zero order. r is the distanc<sub>denotes the distance between the field</sub> <sup>between</sup> <sup>the</sup> <sup>source</sup> <sup>point</sup> <sup>and</sup> <sup>the</sup> <sup>field</sup> <sup>point,</sup> <sup>ଵ</sup> <sup>denotes</sup> <sup>the</sup> <sup>dista</sup>point and the image of source point with respect to the sea bottom:

$$
r = \left\{R ^ {2} + (z - \zeta) ^ {2} \right\} ^ {1 / 2},\tag{13}
$$

$$
r _ {1} = \left\{R ^ {2} + (z + \zeta) ^ {2} \right\} ^ {1 / 2},\tag{14}
$$

$$
r _ {2} = \{R ^ {2} + (z + \zeta + 2 h) ^ {2} \} ^ {1 / 2}.\tag{15}
$$

<sup>ଶ</sup>        <sup>(15)developed</sup> <sup>special</sup> <sup>algorithm</sup> <sup>[10]</sup> <sup>has</sup> <sup>been</sup> <sup>applied</sup> <sup>to</sup> <sup>evaluate</sup> <sup>Equation</sup> <sup>(12).</sup>  Currently, the algorithm in Ref. [18] has been applied to evaluate Equation (11), and a newly developed Currently, the algorithm in Ref. [18] has been applied to e<sup>Due</sup> <sup>to</sup> <sup>the</sup> <sup>strong</sup> <sup>singularity</sup> <sup>of</sup> <sup>the</sup> <sup>Rankine</sup> <sup>source</sup> <sup>r ,</sup>ሼ <sup>ଶ</sup> ( )<sup>ଶ</sup>ሽ<sup>ଵ ଶ⁄</sup> <sup>special algorithm [10] has been applied to evaluate Equation (12).</sup>

veloped special algorithm [10] has been applied to ev<sup>evaluated</sup> <sup>separately</sup> <sup>using</sup> <sup>an</sup> <sup>analytical</sup> <sup>algorithm</sup> Due to the strong singularity of the Rankine source $r ^ { - 1 }$ ate Equation (12). <sup>.</sup> <sup>To</sup> <sup>this</sup> <sup>end,</sup> <sup>as</sup> <sup>shown</sup> <sup>in</sup> <sup>Figure</sup> <sup>3,</sup> <sup>a</sup> , the integration of it over each panel is Due to the strong singularity of the Rankine source r−1, the integration of it over each panel <sup>coordinate</sup> <sup>system,</sup> <sup>,</sup> <sup>needs</sup> <sup>to</sup> <sup>be</sup> <sup>established</sup> <sup>for</sup> <sup>each</sup> <sup>panel</sup> <sup>by</sup> <sup>taking</sup> <sup>the</sup>  <sup>plane</sup> <sup>at</sup> <sup>the</sup> <sup>pthe</sup> <sup>alg ithm</sup> <sup>in</sup> <sup>Ref.</sup> <sup>[18]</sup> <sup>has</sup> <sup>been</sup> <sup>applied</sup> <sup>to</sup> <sup>evaluat</sup> <sup>Equation</sup> <sup>(11),</sup> <sup>and</sup> <sup>a</sup> <sup>newly</sup> evaluated separately using an analytical algorithm [19]. To this end, as shown in Figure 3, a local evaluated separa<sup>surface</sup> <sup>and</sup> <sup>thpecial</sup> <sup>algorithm</sup> <sup>[1</sup>coordinate system, $o \xi \eta \zeta ,$ sing an analytical algorithm [19]. To this end, as sh<sup>xis</sup> <sup>along</sup> <sup>its</sup> <sup>normal</sup> <sup>direction.</sup> <sup>Assuming</sup> <sup>the</sup> <sup>field</sup> <sup>po</sup> <sup>been</sup> <sup>applied</sup> <sup>to</sup> <sup>evaluate</sup> <sup>Equation</sup> <sup>(12).</sup> , needs to be established for each panel by taking the $\xi o \eta$ in Figure 3, a loc<sup>n</sup> <sup>the</sup> <sup>new</sup> <sup>local</sup> <sup>sy</sup>plane at the panel coordinate sy<sup>to</sup> <sup>be</sup>   <sup>the</sup> <sup>strong</sup> <sup>sin</sup>surface and the $\zeta$ em, ����, needs to be established for each panel by taking the ��� plane at the pan<sup>,</sup> <sup>and</sup> <sup>the</sup> <sup>coordinates</sup> <sup>of</sup> <sup>vertices</sup> <sup>of</sup> <sup>each</sup> <sup>panel</sup> <sup>in</sup> <sup>a</sup> <sup>counter-clockwise</sup> <sup>direction</sup> <sup>larity</sup> <sup>of</sup> <sup>the</sup> <sup>Rankine</sup> <sup>ource</sup> <sup>r ,</sup> <sup>the</sup> <sup>integration</sup> <sup>of</sup> <sup>it</sup> <sup>over</sup> <sup>each</sup> <sup>panel</sup>  axis along its normal direction. Assuming the field point in the new local system to be $\left( x , y , z \right)$ ce and the � axis along its normal direction. Assuming the field point in the new௡ ௡ ௡ <sup>,</sup> <sup>where</sup>      ௩<sup>,</sup> ௩ <sup>is</sup> <sup>the</sup> <sup>number</sup> <sup>of</sup> <sup>vertices</sup> <sup>on</sup> <sup>each</sup> <sup>panel,</sup> <sup>the</sup> <sup>ly</sup> <sup>using</sup> <sup>an</sup> <sup>analytical</sup> <sup>algorithm</sup> <sup>[19].</sup> <sup>To</sup> <sup>this</sup> <sup>end,</sup> <sup>as</sup> <sup>shown</sup> <sup>in</sup> <sup>Figure</sup> <sup>3,</sup> <sup>a</sup> <sup>local</sup> , and the coordinates of vertices of each panel in a counter-clockwise direction to be $\left( \xi _ { n } , \eta _ { n } , \zeta _ { n } \right)$ <sub>to</sub> <sub>be</sub><sup>casystem,</sup><sub>where</sub> $n = 1 , 2 , \cdots , N _ { v } , N _ { v }$ oordinates of vertices of each panel in a counter-clockwise direction to b<sup>e</sup> <sup>part</sup> <sup>integration</sup> <sup>can</sup> <sup>be</sup> <sup>derived</sup> <sup>as</sup> <sup>follows:</sup> <sup>stablished</sup> <sup>for</sup> <sup>each</sup> <sup>panel</sup> <sup>by</sup> <sup>taking</sup> <sup>the</sup>  <sup>plane</sup> <sup>at</sup> <sup>the</sup> <sup>panel</sup> is the number of vertices on each panel, the formulation for calculating the (� , � , � ), where � = 1,2, ⋯ , � , � is the num <sup>the</sup>  <sup>axis</sup> <sup>along</sup> <sup>its</sup> <sup>normal</sup> <sup>direction.</sup> <sup>Assuming</sup> <sup>t</sup>Rankine part integration can be derived as follows:

$$
\mathcal {H} _ {i j} = \iint_ {S _ {\mathrm{B}, i}} \frac {\partial}{\partial n _ {\xi}} \left(\frac {1}{r}\right) \mathrm{d} S _ {\xi} = \sum_ {n = 1} ^ {N _ {v}} \left[ \arctan \left(\frac {c _ {n , n + 1} Q _ {n} - P _ {n}}{z R _ {n}}\right) - \arctan \left(\frac {c _ {n , n + 1} Q _ {n + 1} - P _ {n + 1}}{z R _ {n + 1}}\right) \right]\tag{16}
$$

$$
\mathcal {K} _ {i j} = \iint_ {S _ {\mathrm{B}, j}} \frac {1}{r} \mathrm{d} S _ {\xi} = \sum_ {n = 1} ^ {N _ {v}} \left[ \frac {(x - \xi_ {n}) (\eta_ {n + 1} - \eta_ {n}) - (y - \eta_ {n}) (\xi_ {n + 1} - \xi_ {n})}{L _ {n , n + 1}} \right] l o g \left(\frac {R _ {n} + R _ {n + 1} + L _ {n , n + 1}}{R _ {n} + R _ {n + 1} - L _ {n , n + 1}}\right) - z \mathcal {H} _ {i j}\tag{17}
$$

where

$$
P _ {n} = (x - \xi_ {n}) (y - \eta_ {n}),\tag{18}
$$

$$
Q _ {n} = \left\{(x - \xi_ {n}) ^ {2} + z ^ {2} \right\} ^ {1 / 2},\tag{19}
$$

$$
R _ {n} = \left\{(y - \eta_ {n}) ^ {2} + Q _ {n} ^ {2} \right\} ^ {1 / 2},\tag{20}
$$

$$
c _ {n, n + 1} = (\eta_ {n + 1} - \eta_ {n}) / (\xi_ {n + 1} - \xi_ {n}),\tag{21}
$$

$$
L _ {n, n + 1} = \left\{(\xi_ {n + 1} - \xi_ {n}) ^ {2} + (\eta_ {n + 1} - \eta_ {n}) ^ {2} \right\} ^ {1 / 2}.\tag{22}
$$

By taking advantage of the above formulation, the singularities encountered in the boundary integral<sup>By</sup> <sup>taking</sup> <sup>advantage</sup> <sup>of</sup> <sup>the</sup> <sup>above</sup> <sup>formulation,</sup> <sup>the</sup> <sup>singularities</sup> <sup>encountered</sup> <sup>in</sup> <sup>the</sup> <sup>boundary</sup> <sup>int</sup> equations can be evaluated successfully without difficulties.<sup>equations</sup> <sup>can</sup> <sup>be</sup> <sup>evaluated</sup> <sup>successfully</sup> <sup>without</sup> <sup>difficu</sup>

(a)  
(b)  
![](images/245c7b9b3ca26835ccbae6c42c14e9d6cb6d5a8d2392f364d366f7b9c77dc84a.jpg)  
Figure 3. Illustration of the local coordinate system of each panel, in triangular shape (a) or quadrilateral shape (b). The origin o normally locates at the centroid of each panel, and the positive ζ-axis points to the normal direction of the panel. The sequence of vertices is arranged in accordance with the normal direction that points into the inside of the body.

## <sup>the</sup> <sup>normal</sup> <sup>direction</sup> <sup>that</sup> <sup>points</sup> <sup>in</sup>2.4. Solution of the Linear Algebraic System

In order to solve the linear algebraic system Equation (8), a direct solver such as Gauss elimination will commonly be adopted. These direct solvers are generally robust but require $\mathcal { O } ( N ^ { 3 } )$ computations (N denotes matrix size). For a large-scale computation of complex three-dimensional offshore structures, a direct inversion or inefficient iteration of such a large, dense system of linear equations with $\mathcal { O } \big ( N ^ { 4 } \big )$ unknowns for a set of wave frequencies seems prohibitively time consuming even with modern computers. On the other hand, although some iterative methods, such as the GMRES method [11], can reduce the effort to $\mathcal { O } \big ( N ^ { 2 } \big )$ operations; however, these kinds of iterative methods can easily have a problem of ill preconditions. In addition, considering the usual cases when the radiation-diffraction problem needs to be solved with multiple wave headings for each single wave frequency, the computation effort of using either a direct method or an iterative method is still not <sup>the</sup> <sup>radiation-diffraction</sup> <sup>problem</sup> <sup>needs</sup> <sup>to</sup> <sup>be</sup> <sup>solved</sup> <sup>with</sup> <sup>multiple</sup> <sup>wave</sup> <sup>headings</sup> <sup>for</sup> <sup>each</sup> <sup>s</sup>acceptable because it needs to successively solve the linear equations for every wave heading. For this reason, the LU decomposition is adopted in the solver, since it only needs to decompose the left-hand side matrix once for each wave frequency. This decomposition can be applied to calculate the wave forces for a distribution of wave headings via a forward and backward substitution for triangular matrices (L and U), which can be solved directly without using the Gaussian elimination process.

## 3. Numerical Techniques in Specialized Topics

## 3.1. Removal of Irregular Frequencies

Numerical solutions of Equation (7) possess substantial errors in the neighborhood of the so-called “irregular frequencies”. This phenomenon is caused by the water-plane section of the members of floating bodies that intersects the free water surface. The irregular frequencies actually coincide with the eigenfrequencies of the corresponding sloshing modes of the interior tank (assuming flow filling inside the tank).

In order to suppress these frequencies, a kind of partially extended boundary integral equation can be developed, which assumes that the potentials on the interior water plane are zero. This method originates from Ref. [20]. Therefore, by applying Green’s theorem in the interior domain of the floating body, an additional boundary integral equation is introduced in a combined application with Equation (7):

$$
\iint_ {S _ {\mathrm{B}}} \phi_ {k} (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S _ {\boldsymbol {\xi}} = \iint_ {S _ {\mathrm{B}}} V _ {\mathrm{n}, k} (\boldsymbol {\xi}) G (\boldsymbol {\xi}; \boldsymbol {x}) \mathrm{d} S _ {\boldsymbol {\xi}}, (k = 1, 2, \dots , 7, \boldsymbol {x} \in S _ {\mathrm{WP}}, \boldsymbol {\xi} \in S _ {\mathrm{B}}),\tag{23}
$$

where $S _ { W P }$ denotes the interior water-plane area. By discretizing $S _ { \cal { W \mathrm { P } } }$ into M elements, a set of over-determined linear algebraic equations can be obtained as follows:

$$
[ A ] _ {(M + N) \times N} \{\phi \} _ {N} = \{B \} _ {(M + N) \times N}.\tag{24}
$$

Equation (24) can be solved by the least squares method. Defining the square error function as

$$
E = \sum_ {m = 1} ^ {M + N} \left[ \sum_ {n = 1} ^ {N} A _ {m n} \phi_ {k} (\boldsymbol {x} _ {n}) - B _ {k} (\boldsymbol {x} _ {m}) \right] ^ {2},\tag{25}
$$

and optimizing Equation (25) to be of minimum square error

$$
\frac {\partial E}{\partial \phi_ {k} (\boldsymbol {x} _ {n})} = 0, (n = 1, 2, \dots , N),\tag{26}
$$

a new set of equations which are free of irregular frequencies can be developed instead of Equation (8):

$$
\sum_ {n = 1} ^ {N} \left\{\sum_ {m = 1} ^ {M + N} A _ {m n} A _ {m p} \right\} \phi_ {k} (\boldsymbol {x} _ {n}) = \sum_ {m = 1} ^ {M + N} A _ {m p} B _ {k} (\boldsymbol {x} _ {m}), (p = 1, 2, \dots , N),\tag{27}
$$

which is not over-determined and thus can be solved directly.

The present method for removing irregular frequencies avoids evaluation of the logarithmic singularity [21] of free-surface Green’s function occurring in the limiting case when that panel is on the free surface. This can be viewed as an advantage which makes the programming simpler. Besides, since the size of the left-hand side matrix in Equation (27) is $N \times N ,$ which is less than that of $( M + N ) \times ( M + N )$ in Lee’s method [21], the additional numerical work on resolving a larger linear algebraic system can be avoided.

## 3.2. Exploitation of Symmetrical Properties

The efficiency of the solution method for the boundary integral equations may dramatically increase for bodies having one or two planes of symmetry, because the computation time and storage are saved. In the analysis below, symmetry is therefore exploited wherever possible [22,23].

The discretized form of the boundary integral equation, i.e., Equation (8) or Equation (27), can be expressed in the following matrix form:

$$
[ A ] \{\phi \} = \{B \}.\tag{28}
$$

It is possible to partition the matrix A, the vector $\phi ,$ and B according to the number of symmetry planes. For the body having two planes of symmetry, the following partitions can be found

$$
[ A ] = \left[ \begin{array}{c c c c} A _ {1 1} & A _ {1 2} & A _ {1 3} & A _ {1 4} \\ A _ {2 1} & A _ {2 2} & A _ {2 3} & A _ {2 4} \\ A _ {3 1} & A _ {3 2} & A _ {3 3} & A _ {3 4} \\ A _ {4 1} & A _ {4 2} & A _ {4 3} & A _ {4 4} \end{array} \right],\tag{29}
$$

$$
\{\phi \} = \left\{ \begin{array}{l l l l} \phi_ {1} & \phi_ {2} & \phi_ {3} & \phi_ {4} \end{array} \right\} ^ {T},\tag{30}
$$

$$
\left\{B \right\} = \left\{ \begin{array}{c c c c} B _ {1} & B _ {2} & B _ {3} & B _ {4} \end{array} \right\} ^ {T},\tag{31}
$$

where $A _ { 1 1 }$ is the submatrix of coefficients associated with the discretization of boundary region 1, while $A _ { 1 2 } , A _ { 1 3 } ,$ , and $A _ { 1 4 }$ are corresponding submatrices arising from the coupling between the boundaries 1 and $2 , 3 ,$ and 4, respectively. $\phi _ { 1 } , \phi _ { 2 } , \phi _ { 3 } .$ , and $\phi _ { 4 }$ are the vectors of components of the velocity potential corresponding to elements in boundaries 1, 2, 3 and 4 respectively. Similarly, $B _ { 1 } , B _ { 2 } , B _ { 3 } ,$ , and $B _ { 4 }$ are the right-hand side vectors associated with boundaries $1 , 2 , 3 ,$ and 4 respectively. Additionally, the following relations are necessary to be employed in the calculation:

$$
\left. \begin{array}{l} A _ {1 1} = A _ {1 2} = A _ {1 3} = A _ {1 4} \\ A _ {2 1} = A _ {2 2} = A _ {2 3} = A _ {2 4} \\ A _ {3 1} = A _ {3 2} = A _ {3 3} = A _ {3 4} \\ A _ {4 1} = A _ {4 2} = A _ {4 3} = A _ {4 4} \end{array} \right\}.\tag{32}
$$

An orthogonal transformation matrix [R] can be introduced to reduce the size of the linear system such that

$$
\bigl [ \hat {A} \bigr ] = \frac {1}{N _ {s}} [ R ] [ A ] [ R ],\tag{33}
$$

$$
\{\hat {\phi} \} = [ R ] \{\phi \},\tag{34}
$$

$$
\bigl \{\hat {B} \bigr \} = [ R ] \{B \},\tag{35}
$$

where $N _ { s }$ denotes the number of symmetry planes. This transformation enables the linear system resulting into a simplified diagonal form:

$$
\left[ \begin{array}{c c c c} \hat {A} ^ {(1)} & 0 & 0 & 0 \\ 0 & \hat {A} ^ {(2)} & 0 & 0 \\ 0 & 0 & \hat {A} ^ {(3)} & 0 \\ 0 & 0 & 0 & \hat {A} ^ {(4)} \end{array} \right] \left\{ \begin{array}{l} \hat {\phi} ^ {(1)} \\ \hat {\phi} ^ {(2)} \\ \hat {\phi} ^ {(3)} \\ \hat {\phi} ^ {(4)} \end{array} \right\} = \left\{ \begin{array}{l} \hat {B} ^ {(1)} \\ \hat {B} ^ {(2)} \\ \hat {B} ^ {(3)} \\ \hat {B} ^ {(4)} \end{array} \right\},\tag{36}
$$

which leads to

$$
\left\{\hat {\phi} ^ {(k)} \right\} = \left[ \hat {A} ^ {(k)} \right] ^ {- 1} \Bigl \{\hat {B} ^ {(k)} \Bigr \}, \text {where} k = 1, 2, \dots , N _ {s}\tag{37}
$$

Combining Equation (37) with Equations (33)–(35), the solution of $\{ \phi \}$ can be finally obtained with sufficient accuracy. The partition process is also illustrated in Figure 4.

(b)  
(a)  
![](images/7c5486e0fc7141cac85cb6d13e1ccc42a1ccebd5c23c171cf77ce0532758f976.jpg)

![](images/f74f7002a051d53f2c55f8b1a7e522616968c50c7a2f443ff5d1084b413aeee8.jpg)  
Figure 4. Partitions of the computation domain (a) when the body has unique symmetry and (b) when the body has two symmetries.

## <sup>(b)</sup> <sup>when</sup> <sup>the</sup> <sup>body</sup> <sup>has</sup> <sup>two</sup> <sup>symmet</sup>3.3. OpenMP Parallelization on Multi-core Machines

The problems to be solved are often of a very large size such that resolving the resultant linear systems requires huge computational resources. Nowadays, with the facility of a fast multi-core computer, it is natural to maximize the advantages of the current hardware technology in our computations. A large portion of programs that people write and run daily are serial programs, especially in the marine hydrodynamic field as far as the author knows. The serial program runs on a <sup>with</sup> <sup>Ref.</sup> <sup>[25]</sup> <sup>in</sup> <sup>the</sup> <sup>following</sup> <sup>new</sup> <sup>Figure</sup> <sup>8.</sup> <sup>Correspondingly,</sup> <sup>in</sup> <sup>the</sup> <sup>text</sup> <sup>paragraph</sup> <sup>bef</sup>single computer, typically on a single processor, which might be considered as a waste of computational <sup>Figure</sup> <sup>8,</sup> <sup>“Kudo</sup> <sup>(1977)”</sup> <sup>should</sup> <sup>better</sup> <sup>be</sup> <sup>changed</sup> <sup>with</sup> <sup>“Kudou</sup> <sup>(1978)”,</sup> <sup>as</sup> <sup>the</sup> <sup>follows.</sup> resources. For this reason, it is better to code the program in parallel mode, which will enable the program to run simultaneously on multiple processors. Taking into consideration that in a typical case, the number of panels involved in the hydrodynamic computation is usually below 10\~30 thousand, A comparison of the hydrodynamic coefficients against the normalized length �� isand that off-the-shelf computation machines contain multiple processors, the OpenMP technique is in Figure 8. The rotation center of the torque is evidently the most suitable for the work in the present study.

results show good coincidence with the analytical results obtained by Kudoh (19771978The OpenMP standard for Fortran was first released in 1997. It is a standard application programming interface (API) for writing shared memory parallel applications in C, C++, and Fortran. OpenMP has the advantage of being very easy to implement on currently existing serial codes and allowing incremental parallelization [24]. It also has the advantage of being widely used, highly portable, and ideally suited to multi-core architectures, which are becoming increasingly popular in up-to-date desktop computers.

As shown in Figure 5, an OpenMP program usually begins with a single process called the master thread. The master thread executes sequentially until a parallel region is encountered. At this point, the master thread “forks” into a number of parallel worker threads, each of which shares a portion of the computation task. The instructions in the parallel region are then executed by the team of worker threads. At the end of the parallel region, the threads synchronize and join to become the single master thread again [24].

Parallel task 1: Computation of Green’s function  
Parallel task 2: Resolving the complex linear system  
![](images/98759f25405bea49c21010383ac889de5c1278b5bb0645f7f9add6a470ea1cde.jpg)  
Figure 5. Schematic of the two main OpenMP parallel processes in the HAMS (Hydrodynamic Analysis <sup>Figure</sup> <sup>5.</sup> <sup>Schematic</sup> <sup>of</sup> <sup>the</sup> <sup>tw</sup>of Marine Structures) program.

Based on the Amdahl’s Law, if we suppose $p \left( 0 < p < 1 \right)$ part of the program can be run in parallel, on an $N _ { t } .$ <sup>sed</sup> <sup>on</sup> <sup>the</sup> <sup>Amdahl’s</sup> <sup>Law,</sup> <sup>if</sup> <sup>we</sup> <sup>suppose</sup> <sup>p</sup> <sup>(0</sup> <sup><</sup> <sup>p</sup> <sup><</sup> <sup>1)</sup> <sup>part</sup> -thread computational platform, the speed-up ratio $R _ { s }$ he program can be run<sub>can be expressed as</sub>

$$
R _ {s} = \frac {1}{(1 - p) + \frac {p}{N _ {t}}}.\tag{38}
$$

This means that the maximum speed-up ratio will be N<sub>t</sub> by letting p approach unity. However, This means that the maximum speed-up ratio will be Nt by letting p approach unity. However, since the sequential part of work in typical cases is not always zero, this maximum speed-up ratio since the sequential part of work in typical cases is not always zero, this maximum speed-up ratio will will generally not be easily reached. Nevertheless, enhancing the serial code to minimize the generally not be easily reached. Nevertheless, enhancing the serial code to minimize the sequential sequential work is quite necessary to improve the computational<sub>work</sub> <sub>is</sub> <sub>quite</sub> <sub>necessary</sub> <sub>to</sub> <sub>improve</sub> <sub>the</sub> <sub>computational</sub> <sub>speed.</sub>

## <sup>4.</sup> <sup>Applications</sup> <sup>to</sup> <sup>Waves–Structure</sup> <sup>Interactions</sup> <sub>4. Applications to Waves–Structure Interactions</sub>

## <sup>4.1.</sup> <sup>Computation</sup> <sup>of</sup> <sup>an</sup> <sup>Analytical</sup> <sup>Geometry</sup> <sup>for</sup> <sup>Verification</sup> <sub>4.1. Computation of an Analytical Geometryfor Verification</sub>

<sup>A</sup> <sup>numerical</sup> <sup>benchmark</sup> <sup>case</sup> <sup>is</sup> <sup>performed</sup> <sup>on</sup> <sup>a</sup> <sup>floating</sup> <sup>ellipsoid</sup> <sup>(since</sup> <sup>the</sup> <sup>geometry</sup> <sup>of</sup> <sup>which</sup> <sub>A numerical benchmark case is performed on a floating ellipsoid (since the geometry of which</sub> can be precisely expressed) to demonstrate the validity of the developed solver. The geometry is firstly meshed by $2 0 \times 2 0$ panels (20 in longitude and 20 in latitude directions) on the immersed body surface, and additional $1 0 \times 2 0$ panels (10 in longitude and 20 in latitude directions) at the interior waterplane other two meshes that have one symmetry plane and two symmetry planes are also employed for to suppress the so-called “irregular frequencies”. To check its symmetrical property, the other two comparison in altogether 300 panels and 150 panels, respectively. All the meshes are shown in Figure meshes that have one symmetry plane and two symmetry planes are also employed for comparison in 6, where lengths of the major axis and the minor axis of the ellipsoid are L/A = 1.0 and B/A = 0.5, altogether 300 panels and 150 panels, respectively. All the meshes are shown in Figure 6, where lengths respectively, and normalized by the unit amplitude of a reg<sub>of the major axis and the minor axis of the ellipsoid are</sub> $L / A = 1 . 0$ nt wa<sub>and</sub> $B / A = 0 . 5$ <sup>owards</sup> <sup>the</sup> , respectively, and <sup>positive</sup> <sup>x-direction.</sup> normalized by the unit amplitude of a regular incident wave coming towards the positive x-direction.

Figure 7 shows the effect of the irregular frequencies. In the vicinity of the irregular frequencies, un-removal of them results in sharp leaps and declines within small intervals, leading to substantial numerical errors. In contrast, the “Removed” method based on the modified boundary integral equation obtains smooth results in the entire neighborhood. It is interesting to see that the irregular frequencies are different in the horizontal and the vertical exciting forces since they correspond to solutions of the interior sloshing problem in different modes.

A comparison of the hydrodynamic coefficients against the normalized length vL is given in Figure 8. The rotation center of the torque is defined at the origin. The present numerical results show good coincidence with the analytical results obtained by Kudoh (1978) [25], in both the translational mode and rotational mode. Meanwhile, the comparison also shows that although utilization of the symmetrical properties decreases the computation burden, it does not affect the accuracy of results.

![](images/5452af458a80384a0175ed526b27be2639fe7709e8b54500bc942f9f09b4f600.jpg)

![](images/3a3ef379822e02563ae139501e2379e008b33d7a00e3dbf608958e01319af238.jpg)

(c)  
![](images/f04abfb9b61bcae3dd4ee5c1e3009ae2e29fac20fa82b8ca6f1315645796e885.jpg)

Figure 6. Mesh of the floating ellipsoid (a) without symmetry in 600 panels; (b) with one symmetry in 300 panels; and (c) with two symmetries in 150 panels.  
<sup>nel</sup>(a)  
![](images/c98bdc0b6a88ca8ef7dab86cbc2ec5dd2d231da142a3682b8c6021dc32d2f142.jpg)

(b)  
![](images/223dd98fb0ab19bbbd7e8e4d4f6d4070bf93303ccdb5c90383c34a17ec1cd268.jpg)  
Figure 7. Modulus of the complex exciting wave forces of a floating ellipsoid, as a function of the normalized length ��. (a) Horizontal exciting force. (b) Vertical exciting force. angular wave frequency ω. (a) Horizontal exciting force. (b) Vertical exciting force.

(a)  
![](images/0ff434d40df7200c811c55c3cbe31f76c961e9ce482c937f690a14fdf06c6ca6.jpg)

(b)  
![](images/b60b04fea66de09adff11875f6633151a74b9acc831a1db3ae25f122de631ef1.jpg)  
Figure 8. Added mass and radiation damping coefficients of a floating ellipsoid as a function of the angular wave frequency ω: (a) diagonal terms of the surge added mass and radiation damping due to surge motion and (b) cross terms of the surge added mass and radiation damping due to pitch motion.

## damping due to pitch motion. 4.2. Computation of a Truncated Circular Cylinder

Circular cylinder is another common element in the offshore structures. In this test, a truncated circular cylinder with a radius of 1.0 m and a draft of 0.5 m is chosen as a basic example, as displayed in Figure 9. Thanks to its two symmetry planes, a quarter of the cylinder is discretized into $1 6 \times 8 \times 8$ constant panels (16 in circumferential, 8 in radial, and 8 in vertical directions) of a quadrilateral or <sup>4.</sup> <sup>In</sup> <sup>the</sup> <sup>Concluding</sup> <sup>Remarks,</sup> <sup>a</sup> <sup>case</sup> <sup>statement</sup> <sup>is</sup> <sup>missed.</sup> <sup>It</sup> <sup>has</sup> <sup>been</sup> <sup>corrected</sup> <sup>as</sup> <sup>the</sup> <sup>follows</sup>triangular element shape. To remove the irregular frequencies, the water-plane area is discretized into $1 6 \times 8$ <sup>using</sup> <sup>the</sup> <sup>Word</sup> <sup>“Track</sup> <sup>Changes”</sup> <sup>functionality:</sup> constant panels (16 in circumferential, and 8 in radial directions). Computations are performed using the HAMS solver as well as the commercial software ${ \cal W } \mathrm { A M I T } ^ { \circledast } ,$ , and $\mathrm { H y d r o s t a r } ^ { \mathbb { \exp } } .$ , for comparison.

Hydrodynamic quantities involving added mass and wave damping are compared between the computation results derived from the three software. Dimensional results are shown against the wave angular frequency ω in Tables 1 and 2. In Table 1, the computations are carried out in the deep water, while in Table 2, the water is shallow with a depth of $h = 1 . 0 \mathrm { m }$ . The tables illustrate that no matter if the water depth is infinite or finite, the results from HAMS and ${ W A M I T } ^ { \mathbb { B } }$ are much closer between each other against the wave frequency, while those from Hydrostar<sup>®</sup> are a bit shifted away. It may possibly be due to Hydrostar<sup>®</sup> being based on the source distribution method while the other two are® ® based on the mixed source/dipole method in calculating the wave potentials.

![](images/31c67125506a70301444c93794c4e359ea005e39adc0da3a2284ef0d930125d6.jpg)  
Figure 9. Hydrodynamic mesh of the immersed part of a truncated circular cylinder for use in HAMS,Figure 9. Hydrodynamic mesh of the immersed part of a truncated circular cylinder for use in HAMS, ${ \bf W A M I T } ^ { \circledast } ,$ , and Hydrostar<sup>®.</sup>, and Hydrostar<sup>®.</sup>

Table 1. Hydrostatic quantities of the truncated circular cylinder calculated by HAMS, ${ \cal W } \mathrm { A M I T } ^ { \circledast }$ , and Hydrostar<sup>®</sup>, under the infinite water depth.

<table><tr><td colspan="4"> $A_{11}$  (kg)</td><td colspan="3"> $B_{11}$  (kg/s)</td></tr><tr><td> $\omega$ </td><td>HAMS</td><td>WAMIT®</td><td>Hydrostar®</td><td>HAMS</td><td>WAMIT®</td><td>Hydrostar®</td></tr><tr><td>0.2</td><td> $6.7543 \times 10^{2}$ </td><td> $6.7568 \times 10^{2}$ </td><td> $6.9207 \times 10^{2}$ </td><td> $1.7266 \times 10^{-5}$ </td><td> $1.7268 \times 10^{-5}$ </td><td> $1.8018 \times 10^{-5}$ </td></tr><tr><td>0.4</td><td> $6.7910 \times 10^{2}$ </td><td> $6.7936 \times 10^{2}$ </td><td> $6.9587 \times 10^{2}$ </td><td> $2.2008 \times 10^{-3}$ </td><td> $2.2011 \times 10^{-3}$ </td><td> $2.2972 \times 10^{-3}$ </td></tr><tr><td>0.6</td><td> $6.8554 \times 10^{2}$ </td><td> $6.8579 \times 10^{2}$ </td><td> $7.0252 \times 10^{2}$ </td><td> $3.7342 \times 10^{-2}$ </td><td> $3.7344 \times 10^{-2}$ </td><td> $3.8977 \times 10^{-2}$ </td></tr><tr><td>0.8</td><td> $6.9525 \times 10^{2}$ </td><td> $6.9549 \times 10^{2}$ </td><td> $7.1257 \times 10^{2}$ </td><td> $2.7704 \times 10^{-1}$ </td><td> $2.7705 \times 10^{-1}$ </td><td> $2.8915 \times 10^{-1}$ </td></tr><tr><td>1</td><td> $7.0898 \times 10^{2}$ </td><td> $7.0922 \times 10^{2}$ </td><td> $7.2679 \times 10^{2}$ </td><td> $1.3046 \times 10^{0}$ </td><td> $1.3046 \times 10^{0}$ </td><td> $1.3616 \times 10^{0}$ </td></tr><tr><td>1.2</td><td> $7.2764 \times 10^{2}$ </td><td> $7.2788 \times 10^{2}$ </td><td> $7.4612 \times 10^{2}$ </td><td> $4.6032 \times 10^{0}$ </td><td> $4.6031 \times 10^{0}$ </td><td> $4.8047 \times 10^{0}$ </td></tr><tr><td>1.4</td><td> $7.5214 \times 10^{2}$ </td><td> $7.5238 \times 10^{2}$ </td><td> $7.7152 \times 10^{2}$ </td><td> $1.3292 \times 10^{1}$ </td><td> $1.3291 \times 10^{1}$ </td><td> $1.3876 \times 10^{1}$ </td></tr><tr><td>1.6</td><td> $7.8308 \times 10^{2}$ </td><td> $7.8334 \times 10^{2}$ </td><td> $8.0363 \times 10^{2}$ </td><td> $3.3087 \times 10^{1}$ </td><td> $3.3080 \times 10^{1}$ </td><td> $3.4547 \times 10^{1}$ </td></tr><tr><td>1.8</td><td> $8.2032 \times 10^{2}$ </td><td> $8.2058 \times 10^{2}$ </td><td> $8.4225 \times 10^{2}$ </td><td> $7.3328 \times 10^{1}$ </td><td> $7.3303 \times 10^{1}$ </td><td> $7.6586 \times 10^{1}$ </td></tr><tr><td>2</td><td> $8.6221 \times 10^{2}$ </td><td> $8.6241 \times 10^{2}$ </td><td> $8.8561 \times 10^{2}$ </td><td> $1.4765 \times 10^{2}$ </td><td> $1.4757 \times 10^{2}$ </td><td> $1.5426 \times 10^{2}$ </td></tr><tr><td>2.2</td><td> $9.0462 \times 10^{2}$ </td><td> $9.0476 \times 10^{2}$ </td><td> $9.2939 \times 10^{2}$ </td><td> $2.7338 \times 10^{2}$ </td><td> $2.7317 \times 10^{2}$ </td><td> $2.8566 \times 10^{2}$ </td></tr><tr><td>2.4</td><td> $9.4047 \times 10^{2}$ </td><td> $9.4056 \times 10^{2}$ </td><td> $9.6610 \times 10^{2}$ </td><td> $4.6820 \times 10^{2}$ </td><td> $4.6770 \times 10^{2}$ </td><td> $4.8918 \times 10^{2}$ </td></tr><tr><td>2.6</td><td> $9.6011 \times 10^{2}$ </td><td> $9.6010 \times 10^{2}$ </td><td> $9.8548 \times 10^{2}$ </td><td> $7.4309 \times 10^{2}$ </td><td> $7.4201 \times 10^{2}$ </td><td> $7.7582 \times 10^{2}$ </td></tr><tr><td>2.8</td><td> $9.5346 \times 10^{2}$ </td><td> $9.5338 \times 10^{2}$ </td><td> $9.7703 \times 10^{2}$ </td><td> $1.0927 \times 10^{3}$ </td><td> $1.0906 \times 10^{3}$ </td><td> $1.1391 \times 10^{3}$ </td></tr><tr><td>3</td><td> $9.1418 \times 10^{2}$ </td><td> $9.1415 \times 10^{2}$ </td><td> $9.3441 \times 10^{2}$ </td><td> $1.4891 \times 10^{3}$ </td><td> $1.4858 \times 10^{3}$ </td><td> $1.5488 \times 10^{3}$ </td></tr></table>

Table 2. Hydrostatic quantities of the truncated circular cylinder calculated by HAMS, ${ \bf W A M I T } ^ { \circledast } ,$ , and Hydrostar<sup>®</sup>, under a finite water depth $h = 1 . 0$ m.

<table><tr><td colspan="4"> $A_{11}$  (kg)</td><td colspan="3"> $B_{11}$  (kg/s)</td></tr><tr><td> $\omega$ </td><td>HAMS</td><td>WAMIT®</td><td>Hydrostar®</td><td>HAMS</td><td>WAMIT®</td><td>Hydrostar®</td></tr><tr><td>0.2</td><td> $8.3818 \times 10^{2}$ </td><td> $8.3854 \times 10^{2}$ </td><td> $8.6347 \times 10^{2}$ </td><td> $5.9702 \times 10^{-1}$ </td><td> $5.9721 \times 10^{-1}$ </td><td> $6.2698 \times 10^{-1}$ </td></tr><tr><td>0.4</td><td> $8.5111 \times 10^{2}$ </td><td> $8.5148 \times 10^{2}$ </td><td> $8.7701 \times 10^{2}$ </td><td> $4.8315 \times 10^{0}$ </td><td> $4.8329 \times 10^{0}$ </td><td> $5.0754 \times 10^{0}$ </td></tr><tr><td>0.6</td><td> $8.6790 \times 10^{2}$ </td><td> $8.6824 \times 10^{2}$ </td><td> $8.9452 \times 10^{2}$ </td><td> $1.6554 \times 10^{1}$ </td><td> $1.6558 \times 10^{1}$ </td><td> $1.7395 \times 10^{1}$ </td></tr><tr><td>0.8</td><td> $8.8657 \times 10^{2}$ </td><td> $8.8693 \times 10^{2}$ </td><td> $9.1401 \times 10^{2}$ </td><td> $3.9904 \times 10^{1}$ </td><td> $3.9913 \times 10^{1}$ </td><td> $4.1945 \times 10^{1}$ </td></tr><tr><td>1</td><td> $9.0548 \times 10^{2}$ </td><td> $9.0584 \times 10^{2}$ </td><td> $9.3367 \times 10^{2}$ </td><td> $7.9279 \times 10^{1}$ </td><td> $7.9292 \times 10^{1}$ </td><td> $8.3352 \times 10^{1}$ </td></tr><tr><td>1.2</td><td> $9.2291 \times 10^{2}$ </td><td> $9.2323 \times 10^{2}$ </td><td> $9.5164 \times 10^{2}$ </td><td> $1.3917 \times 10^{2}$ </td><td> $1.3918 \times 10^{2}$ </td><td> $1.4633 \times 10^{2}$ </td></tr><tr><td>1.4</td><td> $9.3720 \times 10^{2}$ </td><td> $9.3726 \times 10^{2}$ </td><td> $9.6595 \times 10^{2}$ </td><td> $2.2390 \times 10^{2}$ </td><td> $2.2386 \times 10^{2}$ </td><td> $2.3536 \times 10^{2}$ </td></tr><tr><td>1.6</td><td> $9.4581 \times 10^{2}$ </td><td> $9.4593 \times 10^{2}$ </td><td> $9.7449 \times 10^{2}$ </td><td> $3.3699 \times 10^{2}$ </td><td> $3.3692 \times 10^{2}$ </td><td> $3.5412 \times 10^{2}$ </td></tr><tr><td>1.8</td><td> $9.4700 \times 10^{2}$ </td><td> $9.4728 \times 10^{2}$ </td><td> $9.7517 \times 10^{2}$ </td><td> $4.8075 \times 10^{2}$ </td><td> $4.8064 \times 10^{2}$ </td><td> $5.0489 \times 10^{2}$ </td></tr><tr><td>2</td><td> $9.3921 \times 10^{2}$ </td><td> $9.3948 \times 10^{2}$ </td><td> $9.6609 \times 10^{2}$ </td><td> $6.5558 \times 10^{2}$ </td><td> $6.5535 \times 10^{2}$ </td><td> $6.8779 \times 10^{2}$ </td></tr><tr><td>2.2</td><td> $9.2083 \times 10^{2}$ </td><td> $9.2108 \times 10^{2}$ </td><td> $9.4576 \times 10^{2}$ </td><td> $8.5924 \times 10^{2}$ </td><td> $8.5877 \times 10^{2}$ </td><td> $9.0016 \times 10^{2}$ </td></tr><tr><td>2.4</td><td> $8.9104 \times 10^{2}$ </td><td> $8.9127 \times 10^{2}$ </td><td> $9.1343 \times 10^{2}$ </td><td> $1.0865 \times 10^{3}$ </td><td> $1.0857 \times 10^{3}$ </td><td> $1.1362 \times 10^{3}$ </td></tr><tr><td>2.6</td><td> $8.4981 \times 10^{2}$ </td><td> $8.5006 \times 10^{2}$ </td><td> $8.6922 \times 10^{2}$ </td><td> $1.3295 \times 10^{3}$ </td><td> $1.3283 \times 10^{3}$ </td><td> $1.3873 \times 10^{3}$ </td></tr><tr><td>2.8</td><td> $7.9810 \times 10^{2}$ </td><td> $7.9838 \times 10^{2}$ </td><td> $8.1423 \times 10^{2}$ </td><td> $1.5780 \times 10^{3}$ </td><td> $1.5761 \times 10^{3}$ </td><td> $1.6426 \times 10^{3}$ </td></tr><tr><td>3</td><td> $7.3805 \times 10^{2}$ </td><td> $7.3801 \times 10^{2}$ </td><td> $7.5047 \times 10^{2}$ </td><td> $1.8209 \times 10^{3}$ </td><td> $1.8180 \times 10^{3}$ </td><td> $1.8902 \times 10^{3}$ </td></tr></table>

## 4.3. Computation of a Complex Marine Structure

To illustrate the capabilities of the HAMS preprocessor in the wave-structure interaction analysis, the floating foundation of the complex OC4 DeepCwind semisubmersible floating wind turbine is presented herein as a benchmark test in practice. The platform consists of a central column, three outer offset columns, and a host of slender bracings to connect between the columns and make the floating structure sufficiently stiff. Geometrical specifications of the DeepCwind semi-submersible are found in Ref. [26].

A hydrodynamic mesh is only generated for the wetted part of the floater, and the waterplane at the cross-sections of the columns intersecting the mean sea surface. Around 3000 panels are chosen as an appropriate number of panels for the following computation, as displayed in Figure 10. Each of the three footings is discretized into $3 8 \times 8 \times 4$ constant panels (38 in circumferential, 8 in radial, and 4 in vertical directions) of a quadrilateral or triangular element shape. Each of the three outer offset columns and the central column are discretized into $2 0 \times 4 \times 8$ panels and $1 2 \times 2 \times 1 2$ panels, respectively.<sub>mmetry</sub> <sub>plane</sub> <sub>x-z</sub> <sub>is</sub> The bracings are also meshed by sufficiently dense panels. A symmetry plane x-z is applied to remarkably reduce the computation time. Computation results using the same hydrodynamic mesh® from the commercial software Hydrostar<sup>®</sup> are also given to validate the present numerical results.

![](images/5f253878e62b4e076dfa77e6cf6c3ba0388c3b6dbbd353e6e87b5853563eba86.jpg)  
Figure 10. Hydrodynamic mesh of the immersed part of the OC4 DeepCwind floater, for use in HAMSFigure 10. Hydrodynamic mesh of the immersed part of the OC4 DeepCwind floater, for use in HAMS and Hydrostar<sup>®.</sup>and Hydrostar<sup>®.</sup>

Hydrostatic properties including displacement, center of buoyancy, water plane, restoring, etc., of the OC4 DeepCwind floater have been calculated by HAMS and Hydrostar<sup>®</sup>, as displayed in Table 3. These properties are evaluated based on the input hydrodynamic mesh of the immersed part of the floater. The comparison shows that the results generated by the two software are very close to each other, with quite small relative errors. A sound accuracy of the hydrostatic properties ensures a good prediction of the motion responses in subsequent calculations.

Table 3. Hydrostatic properties of the OC4 DeepCwind floater calculated by HAMS and Hydrostar<sup>®.</sup>

<table><tr><td>Properties</td><td>HAMS</td><td>Hydrostar®</td><td>Relative Error</td></tr><tr><td>Displacement</td><td> $1.3683 \times 10^{4} \text{m}^{3}$ </td><td> $1.3683 \times 10^{4} \text{m}^{3}$ </td><td>0.00</td></tr><tr><td>z-Coordinate of the Buoyancy Center</td><td> $-1.3157 \times 10^{1} \text{m}$ </td><td> $-1.3185 \times 10^{1} \text{m}$ </td><td> $2.12 \times 10^{-3}$ </td></tr><tr><td>Area of the Immersed Body Surface</td><td> $6.5010 \times 10^{3} \text{m}^{2}$ </td><td> $6.5007 \times 10^{3} \text{m}^{2}$ </td><td> $4.61 \times 10^{-5}$ </td></tr><tr><td>Inner Water Plane Area</td><td> $3.7027 \times 10^{2} \text{m}^{2}$ </td><td> $3.7128 \times 10^{2} \text{m}^{2}$ </td><td> $-2.72 \times 10^{-3}$ </td></tr><tr><td>Hydrodynamic Restoring in Heave</td><td> $3.7219 \times 10^{6} \text{N/m}$ </td><td> $3.7736 \times 10^{6} \text{N/m}$ </td><td> $-1.37 \times 10^{-2}$ </td></tr><tr><td>Hydrodynamic Restoring in Roll</td><td> $-3.7649 \times 10^{8} \text{Nm/rad}$ </td><td> $-3.6278 \times 10^{8} \text{Nm/rad}$ </td><td> $3.78 \times 10^{-2}$ </td></tr><tr><td>Hydrodynamic Restoring in Pitch</td><td> $-3.7649 \times 10^{8} \text{Nm/rad}$ </td><td> $-3.6278 \times 10^{8} \text{Nm/rad}$ </td><td> $3.78 \times 10^{-2}$ </td></tr></table>

Figure 11 shows distributions of the wave excitation force in the x-direction on the OC4 DeepCwind floater with respect to the wave angular frequency and wave headings. Firstly, it is seen that the distributions computed by respectively HAMS and Hydrostar<sup>®</sup> are in good agreement with each other. Secondly, due to the symmetry of the OC4 DeepCwind floater, the distributions are symmetric with respect to the line of the wave heading $\beta = 1 8 0 ^ { ^ { \circ } }$ . It should be noted that there are several major regions where the floater is acted on significantly by the wave force. The maximum value occurs at the region of $1 7 0 ^ { \circ } < \beta < 1 9 0 ^ { \circ }$ and $1 . 0 < \omega < 1 . 2$ . Outputting such distributions of wave excitation forces may be of great importance to the design of such floaters in practice [27].<sup>J.</sup> <sup>Mar.</sup> <sup>Sci.</sup> <sup>Eng.</sup> <sup>2019,</sup> <sup>7,</sup> <sup>x</sup> <sup>FOR</sup> <sup>PEER</sup> <sup>REVIEW</sup> <sup>16</sup> <sup>of</sup> <sup>21</sup>

(a)  
![](images/9dedb0a797b251ddd141bdf494fa230402ea6c0fc52ee8e04a9bf08748274590.jpg)

(b)  
![](images/9fd28234fa576c9a1670a03d44f777600714e5126365c4ab3baa38c67e9dcac0.jpg)  
Figure 11. Modulus of the wave excitation force in x-direction acting on the OC4 DeepCwind floater as a function of the wave angular frequency ω and wave headings $\beta ,$ computed by (a) HAMS and (b) (b) HydrosHydrostar<sup>®</sup>, respectively.

<sup>Figure</sup> <sup>12</sup> <sup>shows</sup> <sup>the</sup> <sup>analysis</sup> <sup>of</sup> <sup>response</sup> <sup>amplitude</sup> <sup>operators</sup> <sup>(RAOs)</sup> <sup>on</sup> <sup>the</sup> <sup>motions</sup> <sup>of</sup> <sup>the</sup> <sup>OC4</sup> Figure 12 shows the analysis of response amplitude operators (RAOs) on the motions of the OC4 DeepCwind floating wind turbine in no-wind and parking condition, and a comparison between the present results and those computed by the commercial software Hydrostar<sup>®</sup>. The floating wind turbine symmetrically about the platform z-axis [26]. The mooring system is considered in the calculation, is moored with three catenary lines at the near bottom of the outer columns spread symmetrically <sup>and</sup> <sup>the</sup> <sup>mooring</sup> <sup>stiffness</sup> <sup>matrix</sup> <sup>is</sup> <sup>obtained</sup> <sup>via</sup> <sup>linearization</sup> <sup>of</sup> <sup>the</sup> <sup>mooring</sup> <sup>system.</sup> <sup>The</sup> <sup>motion</sup> about the platform z-axis [26]. The mooring system is considered in the calculation, and the mooring stiffness matrix is obtained via linearization of the mooring system. The motion RAOs are measured basically coincide well with each other, except for some tiny differences below the scale of the 10−4by the motion response amplitude over the incident wave amplitude. The RAOs are plotted in the <sup>degree.</sup> <sup>The</sup> <sup>peaks</sup> <sup>at</sup> <sup>the</sup> <sup>resonance</sup> <sup>region</sup> <sup>(0.0</sup> <sup><</sup> <sup>ω</sup> <sup><</sup> <sup>0.5)</sup> <sup>predicted</sup> <sup>by</sup> <sup>the</sup> <sup>two</sup> <sup>software</sup> <sup>packages</sup> <sup>are</sup> logarithmic coordinate to clearly show the comparison. It is seen that the two results basically coincide well with each other, except for some tiny differences below the scale of the 10<sup>−4</sup> degree. The peaks at the resonance region $( 0 . 0 < \omega < 0 . 5 )$ predicted by the two software packages are also in quite good agreement. The motion RAOs generally decreases with the increase of the wave angular frequency to a negligible level when the wave angular frequency exceeds 2.0.

![](images/71c44bfc1610191a2dea55a5055167c1e2897d7273149c2f91d60663229ed5fe.jpg)

(a)  
![](images/45db05da70980890301bf2a02f959f76a25a612b1daccaf90dac4ffbca1239b7.jpg)  
(b)

![](images/f49d7f5153c528f2d8a3fc2b60c5cb8808fb9e924e8edecba0991b22f7289463.jpg)  
(c)  
Figure 12. Motion response of the OC4 DeepCwind floating wind turbine in no-wind and parking conditions as a function of the wave angular frequency ω: (a) surge response; (b) heave response; and (c) pitch response. The results denoted by symbols are computed by the commercial software Hydrostar<sup>®</sup>.

The computation time and the speed-up ratio of the present case against the number of OpenMP threads for each wave frequency are shown in Figure 13. The elapsed time is an average of the computation time for 60 wave frequencies. The speedup ratio is calculated by the ratio of the computation time of a single thread over that of $N _ { t }$ OpenMP threads. It is found that the computation time in either finite depth or infinite depth decreases with the increase of the number of threads. The computation time in finite depth is a bit less than two times of that in infinite depth. For instance, when eight threads are used, the computation time for every frequency is 9.10 s for the finite depth and 4.86 s for the infinite depth due to the fact that the calculation of the finite depth Green’s function is much more time-consuming than that of infinite depth. The speedup ratio generally increases proportionally with the number of threads but seems to drop a bit when the number of threads exceeds six. Moreover, it is worth noting that the speed-up ratio is less than the number of threads because not all of the codes in the solver can be run in parallel, as indicated in Equation (38).<sup>J.</sup> <sup>Mar.</sup> <sup>Sci.</sup> <sup>Eng.</sup> <sup>2019,</sup> <sup>7,</sup> <sup>x</sup> <sup>FOR</sup> <sup>PEER</sup> <sup>REVIEW</sup>

![](images/7e5cbb3850b2fe11a1965482f9112ea07c2b3b752274ca55c008ec7ba15868b8.jpg)  
Figure 13. Computation efficiency of the HAMS solver for each wave frequency against the number of threads in finite and infinite depth, respectively.

## 5. Concluding Remarks

A new software is presented herein for analysis of wave-structure interactions in the frequency domain. To give a clear map of how the software has been developed, the background theory as well as its numerical methodologies and techniques have been introduced in detail. The irregular frequencies have been removed based on the partially extended boundary integral equation method, and symmetry properties can be exploited to reduce the computation burden significantly. The free-surface Green’s function is calculated by a combination of series expansions in both infinite depth and finite depth. OpenMP parallelization is employed to speed up computations on multi-core machines. The accuracy and the efficiency of the developed software were confirmed by numerical validations on three benchmark cases of a floating ellipsoid, a truncated circular cylinder and the OC4 DeepCwind semisubmersible floating wind turbine.

Author Contributions: Y.L. designed the code structure, developed the software, performed the computation, and drafted and polished the paper.

Funding: Development of the software was based on the author’s personal interest, but received no specific Funding: Development of the software was based on the author’s personal interest, but received no specifi<sub>external funding. A part of the APC (395 CHF) for publishing this paper is funded by the Q-PIT (Kyushu</sub> external funding. A part of the APC (395 CHF) for publishing this paper is funded by the Q-PIT (KyushuUniversity Platform of Inter/Transdisciplinary Energy Research) Support Program for Young Researchers (Grant Number 18112).

Acknowledgments: The author appreciates many helpful discussions with Bin Teng, Hidetsugu Iwashita, and Masashi Kashiwagi regarding the issues of calculating free-surface Green’s function, removing irregular frequencies, exploiting symmetrical properties, and integrating Rankine terms, etc. The author appreciates the support from Changhong Hu and Makoto Sueyoshi on many other issues when he was undertaking his Ph.D. The author also appreciates Shigeo Yoshida for providing the commercial software Hydrostar<sup>®</sup> used in the case validations in Sections 4.2 and 4.3, and Hongzhong Zhu for providing the commercial software WAMIT<sup>®</sup> used in the case validation in Section 4.2.

Conflicts of Interest: No potential conflict of interest was reported by the author.

Instructions for the software acquisition: An academic version of the software is freely available on contacting the author. The software can read a mesh file in the \*.gdf format. Moreover, it is able to output the frequency-domain calculation results to the WAMIT<sup>®</sup> or the Hydrostar<sup>®</sup> format.

## Nomenclature

API Application Programming Interface BIEM Boundary Integral Equation Method CFD Computational Fluid Dynamics GMRES Generalized Minimum Residual JONSWAP Joint North Sea Wave Observation Project LU Lower–Upper N-S Navier-Stokes OpenMP Open Multi-Processing RAO Response Amplitude Operator

## References

1. Li, Y.; Yu, Y.H. A synthesis of numerical methods for modeling wave energy converter-point absorbers. Renew. Sustain. Energy Rev. 2012, 16, 4352–4364. [CrossRef]

2. Li, Y.; Teng, B. Wave Action on Maritime Structures, 3rd ed.; Ocean Press: Beijing, China, 2015.

3. Newman, J.N. Algorithms for free-surface Green function. J. Eng. Math. 1985, 19, 57–67. [CrossRef]

4. Newman, J.N. The approximation of free-surface Green functions. In Wave Asymptotics; Retirement Meeting for Professor Fritz Ursell, University of Manchester; Martin, P.A., Wickham, G.R., Eds.; Cambridge University Press: Cambridge, UK, 1992; pp. 107–135.

5. Telste, J.G.; Noblesse, F. Numerical evaluation of the Green function of water-wave radiation and diffraction. J. Ship Res. 1986, 30, 69–84.

6. Wu, H.; Zhang, C.; Zhu, Y.; Li, W.; Wan, D.; Noblesse, F. A global approximation to the Green function for diffraction radiation of water waves. Eur. J. Mech.-B/Fluids 2017, 65, 54–64. [CrossRef]

7. Chen, X.B. Evaluation de la fonction de Green du probleme de diffraction/radiation en profondeur d’eau finie-une nouvelle méthode rapide et précise, Actes des 4e Journées de l’Hydrodynamique. Nantes (Franc.) 1993, 371–384.

8. Chen, X.B. Hydrodynamics in offshore and naval applications—Part I. In Proceedings of the 6th International Conference on Hydrodynamics, Perth, Australia, 24–26 November 2004.

9. Liu, Y.; Iwashita, H.; Hu, C. A calculation method for finite depth free-surface green function. International. J. Nav. Archit. Ocean Eng. 2015, 7, 375–389. [CrossRef]

10. Liu, Y.; Yoshida, S.; Hu, C.; Sueyoshi, M.; Sun, L.; Gao, J.; Cong, P.; He, G. A reliable open-source package for performance evaluation of floating renewable energy systems in coastal and offshore regions. Energy Convers. Manag. 2018, 174, 516–536. [CrossRef]

11. Saad, Y.; Schultz, M.H. GMRES: A generalized minimal residual algorithm for solving nonsymmetric linear systems. SIAM J. Sci. Stat. Comput. 1986, 7, 856–869. [CrossRef]

12. John, F. On the motion of floating bodies II. Commun. Pure Appl. Math. 1950, 3, 45–101. [CrossRef]

13. Ursell, F. Irregular frequencies and the motion of floating bodies. J. Fluid Mech. 1981, 105, 143–156. [CrossRef]

14. Lee, C.H.; Sclavounos, P.D. Removing the irregular frequencies from integral equations in wave-body interactions. J. Fluid Mech. 1989, 207, 393–418. [CrossRef]

15. Lee, C.H.; Newman, J.N.; Zhu, X. An extended boundary integral equation method for the removal of irregular frequency effects. Int. J. Numer. Methods Fluids 1996, 23, 637–660. [CrossRef]

16. Malenica, S.; Chen, X.B. On the irregular frequencies appearing in wave diffraction-radiation solutions. Int. J. Offshore Polar Eng. 1998, 8, 110–114.

17. Sun, L.; Teng, B.; Liu, C.F. Removing irregular frequencies by a partial discontinuous higher order boundary element method. Ocean Eng. 2008, 35, 920–930. [CrossRef]

18. Kashiwagi, M.; Takagi, K.; Yoshida, H.; Murai, M.; Higo, Y. Fluid Dynamics of Floating Bodies in Practice: Part 1 Numerical Computation Method of the Motion Response Problems; Seisando Press: Tokyo, Japan, 2003.

19. Newman, J.N. Distributions of sources and normal dipoles over a quadrilateral panel. J. Eng. Math. 1986, 20, 113–126. [CrossRef]

20. Lau, S.M.; Hearn, G.E. Suppression of irregular frequency effects in fluid–structure interaction problems using a combined boundary integral equation method. Int. J. Numer. Methods Fluids 1989, 9, 763–782. [CrossRef]

21. Lee, C.H. WAMIT Theory Manual: MIT Report 95-2; Dept. of Ocean Engineering, Massachusetts Institute of Technology: Cambridge, MA, USA, 1995.

22. Chau, F.P. The Second Order Velocity Potential for Diffraction of Waves by Fixed Offshore Structures. Ph.D. Thesis, University College London, London, UK, 1989.

23. Matsui, T.; Kato, K.; Shirai, T. A hybrid integral equation method for diffraction and radiation of water waves by three-dimensional bodies. Comput. Mech. 1987, 2, 119–135. [CrossRef]

24. Kiessling, A. An Introduction to Parallel Programming with OpenMP. In A Pedagogical Seminar; Edinburgh University: Edinburgh, UK, 2009.

25. Kudou, K.; Kobayashi, K. The drifting force acting on a three-dimensional body in waves (2nd Report). J. Soc. Nav. Arch. Jap. 1978, 144, 155–162. [CrossRef]

26. Robertson, A.; Jonkman, J.M.; Masciola, M.; Song, H.; Goupee, A.; Coulling, A.; Luan, C. Definition of the Semisubmersible Floating Systemfor Phase II ofOC4; National Renewable Energy Laboratory (NREL): Golden, CO, USA, 2014.

27. McCormick, M.E. Ocean Engineering Mechanics: With Applications; Cambridge University Press: Cambridge, UK, 2009.

© 2019 by the author. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (http://creativecommons.org/licenses/by/4.0/).