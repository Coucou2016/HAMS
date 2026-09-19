# A reliable open-source package for performance evaluation of floating renewable energy systems in coastal and offshore regions

Liu, Yingyi Research Institute for Applied Mechanics, Kyushu University

Yoshida, Shigeo Research Institute for Applied Mechanics, Kyushu University

Hu, Changhong Research Institute for Applied Mechanics, Kyushu University

Sueyoshi, Makoto Research Institute for Applied Mechanics, Kyushu University

他

https://hdl.handle.net/2324/1955654

# A reliable open-source package for performance evaluation of floating renewable energy systems in coastal and offshore regions

Yingyi Liu<sup>a,\*</sup>, Shigeo Yoshida<sup>a</sup>, Changhong Hu<sup>a</sup>, Makoto Sueyoshi<sup>a</sup>, Liang Sun<sup>b,\*</sup>, Junliang Gao<sup>c</sup>, Peiwen Cong<sup>d,e,\*</sup>, Guanghua He<sup>f,g,\*</sup>

<sup>a</sup>Research Institute for Applied Mechanics, Kyushu University, Kasuga 8168580, Japan

<sup>b</sup>Departments of Naval Architecture, Ocean and Structural Engineering, School of Transportation, Wuhan University of Technology, Wuhan 430063, China

<sup>c</sup>School of Naval Architecture and Ocean Engineering, Jiangsu University of Science and Technology, Zhenjiang 212003, China

<sup>d</sup>State Key Laboratory of Coastal and Offshore Engineering, Dalian University of Technology, Dalian 116024, China

<sup>e</sup>Department of Civil and Environmental Engineering, National University of Singapore, 1 Engineering Drive 2, 117576, Singapore

<sup>f</sup>School of Naval Architecture and Ocean Engineering, Harbin Institute of Technology, Weihai 264209, China

<sup>g</sup>Australian Maritime College, University of Tasmania, Launceston, Tasmania 7250, Australia

## Abstract

The booming developments of coastal/offshore renewable energies in recent years call for a powerful numerical code, ideally open-source packaged, to accelerate the researches in the spotlight. This paper presents such an efficient software package for evaluating the performance of floating renewable energy systems in the coastal and offshore regions. It aims to contribute an open-source effort in numerical simulations for ocean energy converters. Though computation of the freesurface effect in moderate depth region is extremely troublesome due to the singularities, the software package proposed in the present paper gives a satisfactory solution to keep the balance of accuracy and efficiency. In the present paper, the interface and structure of the package are introduced in detail so as to be well understood by the reader. Benchmark tests for various types of converters have confirmed the accuracy and efficiency of the package which can be incorporated easily with a frequency domain solver for efficient analysis. By contributing as one of the pioneer works in the opensource effort of evaluating the moderate-depth free-surface Green’s function, with its advantages of a reliable accuracy and a relatively low cost, the authors are hoping that the publication of the present software package will promote the continuous researches in developing robust and reliable coastal and offshore renewable energy systems.

Keywords: offshore wind turbine; wave energy converter; tidal energy converter; ocean renewable energy; optimized configuration; open source

## 1. Introduction

Due to the explosion of energy consumption in household life, industrial production and public service in cities (as discussed in Ref. [1]), fossil resources are getting exhausted and there is a great need to establish sustainable energy systems for substitution. In recent years, coastal/ offshore renewable energies are becoming promising alternatives for the traditional fossil energies, attracting people’s interest. Colmenar-Santos et al. [2] reviewed the state of the art of offshore wind technology and the most popular types of turbines, transmission systems and support structures in Europe. Lehmann et al. [3] reviewed the current state of ocean wave energy conversion technologies and industry status in the United States including research, development, commercia activities and governmental support. Khan et al. [4] reviewed the potentials of tidal current power as well as other ocean energy technologies and their environmental impacts. A great effort has been paid on the development of new methodologies, e.g., Vazquez and Iglesias [5] developed a new holistic method for selecting suitable tidal stream hotspots; Pavković et al. [6] presented a modeling, parameterization and control system design for the high-altitude wind energy system ground station power-plant. Efforts have also been made on finding new solutions from the existing theories, e.g., Bontempo and Manna [7] gave the exact solutions of the equations involved in the axial momentum theory for several kinds of radially variable load distributions; Liu and Yoshida [8] extended the Generalized Actuator Disc Theory to enable prediction of the axial velocity profile at the rotor plane of diffuser-augmented wind turbines. On the other hand, interests are focused on the laboratory development of a number of emerging offshore renewable energy devices, most of them being wave energy converters (WECs) because wave energy is a relatively nascent field, e.g., Elhanafi et al. [9] carried out a towing tank test on a floating–moored oscillating water column (OWC) wave energy converter and also conducted numerical investigations on the device performance and the effects from wave forces, wave height and power take-off damping, etc.; Wu et al. [10] studied the performance of a solo Duck wave energy converter in arrays under motion constraints; Ramos et al. [11] conducted a series of studies on assessing the feasibility of a CECO wave energy converter under the influences of water depth; Ning et al. [12] did extensive researches using both numerical tools and experimental facilities on the hydrodynamic performance of OWC devices. These case studies laid the foundations for the continuous future development of new efficient devices and technologies.

Hydrodynamic forces have a significant influence on the substructures of these offshore energy devices [13]. Liu et al. [14] reviewed the recent advancements of floating foundations for particularly the offshore wind turbines (OWTs) which have been turned into industrial applications. Oh et al. [15] further discussed their future trends and challenges. Note that in the design process of the coastal/ offshore renewable energy devices, one of the critical considerations is to evaluate the feasibility of these devices under some localized sea conditions (see e.g. [16]), i.e., to compute their wave loads and motion responses under various normal/extreme circumstances. In recent years, a variety of floating concepts have been proposed and developed for ocean energy converters (OECs), such as OWTs, WECs and tidal energy converters (TECs), for the industrial commercialization purpose. Several representatives of these newly developed floating OECs are shown in Table 1 and Fig. 1. These devices frequently employ floating foundations in the form of spar, tension-leg spar, semisubmersible, raft, and buoyancy-stabilized floater, etc., which are designed to be installed under the water depth going from approximately 20 meters to around 200 meters. Within such a range of moderate water depth, for the consideration of the offshore structure safety, it is more reasonable to use the finite-depth wave theory instead of assuming the installation water depth to be infinity.

Table 1. Representative offshore renewable energy devices developed in recent years

<table><tr><td>Device Name</td><td>Device Type</td><td>R&amp;D Company</td><td>Offshore Site</td><td>Floater Type</td><td>Water Depth (m)</td><td>Rated Power</td><td>Current Status</td></tr><tr><td>Hywind® [17]</td><td>HAWT</td><td>Statoil</td><td>Norway</td><td>Spar</td><td>210</td><td>2.3 MW</td><td>Launched in 2009</td></tr><tr><td>WindFloat® [18]</td><td>HAWT</td><td>Principle Power</td><td>Portugal</td><td>Semi-submersible</td><td>50</td><td>2 MW</td><td>Launched in 2011</td></tr><tr><td>SWAY® [19]</td><td>HAWT</td><td>SWAY A/S</td><td>Norway</td><td>Tension leg spar</td><td>121</td><td>2.5~10 MW</td><td>Scaled Prototype in 2012</td></tr><tr><td>HiPR®-Wind [14]</td><td>HAWT</td><td>EU FP7 Team</td><td>Spain</td><td>Semi-submersible</td><td>50~90</td><td>1.5 MW</td><td>Designing stage in 2018</td></tr><tr><td>SCD®-nezzy [20]</td><td>HAWT</td><td>Aerodyn</td><td>Japan</td><td>Semi-submersible</td><td>52</td><td>6~8 MW</td><td>Under demonstration in 2018</td></tr><tr><td>SeaTwirl® [21]</td><td>VAWT</td><td>SeaTwirl</td><td>Sweden</td><td>Buoyancy stabilized</td><td>50</td><td>30 kW~1 MW</td><td>S1 released in 2015, S2 to be released in 2020</td></tr><tr><td>Pelamis® [22]</td><td>WEC</td><td>Pelamis Wave Power</td><td>Scotland</td><td>Raft</td><td>50</td><td>750 kW</td><td>Field test in 2010</td></tr><tr><td>SEAREV® [23]</td><td>WEC</td><td>CNRS</td><td>France</td><td>Semi-submersible</td><td>30~50</td><td>68~188 kW</td><td>G21 demonstrated in 2014</td></tr><tr><td>BlueTEC® [24]</td><td>TEC</td><td>Bluewater et al.</td><td>Netherland</td><td>Semi-submersible</td><td>20~</td><td>200 kW~2.5 MW</td><td>Launched in 2016</td></tr></table>

![](images/0ec44c3b72864db714cb87ac18fcbb13dba002aa57a7a104813e9a2d4f0fb9f5.jpg)

![](images/8271d279a7bc8d275a74624a42af339a326601d1e7cb604bd08bd9eed1724ca0.jpg)

![](images/a15bfcf7449c0e3253e09d5eaf2b0f6e6c01bc2db76f6e4502bedaf3798a5e1b.jpg)  
Fig. 1. Typical offshore renewable energy devices for the next generation applications: (a) WINFLO semi-submersible OWT [25], (b) WaveStar WEC [26], and (c) BlueTEC TEC [24]. Their designing installation water depth is intermediate rather than infinite.

So far, the boundary integral equation method (BIEM) (see e.g. [27]) has been widely applied in the assessment of offshore renewable energy systems. It is still one of the appropriate choices to solve efficiently their performance with wave-interactions (see e.g. [28]). That is because all its unknowns are restricted merely on the specified boundaries, which enables the computational burden to be greatly reduced. In BIEM, the boundary integral equations (BIEs) are derived via Green’s theorem within a confined or unconfined space [29]. The BIEs can be numerically solved by discretizing the boundaries into a large number of mesh and physical elements. In the formulation of the influence matrices, Green’s function and its derivatives must be evaluated successively for each pair of the source and the field points. The evaluation times of the ‘core’ function (Green’s function) increase quadratically with the number of unknowns on boundary surfaces, especially for structures with complex geometries. In this context, accuracy and efficiency of computing the Green’s function are crucial to a numerical solver for evaluating the performance of coastal/offshore renewable energy devices.

Computational issues related with free-surface Green’s function in hydrodynamics remain to be in the spotlight due to the popularity of the BIEM in the numerical analysis of ocean wind/wave/tidal energy devices. In the frequency domain, especially for problems in infinite depth, important work was done by several researchers. Newman [30] developed an efficient method based on the combination of asymptotic expansion, rational-fraction approximation, and multi-dimensional polynomial approximation. At nearly the same time, Telste & Noblesse [31] proposed another powerful method via a decomposition of the pulsating source into a wave component and a non-oscillatory local flow component. It was later verified by Chakrabarti [32]. The method of Telste & Noblesse was recently simplified by Wu et al. [33] with approximations, but without loss of too much accuracy. However, the evaluation of free-surface Green’s function for the finite-depth problem is even more troublesome than that for infinite-depth due to the more complex singular nature of its oscillating integrand. Newman [30] obtained a slow-varying component by subtracting the infinite-depth Green’s function from that in finite depth, which could then be evaluated using the Chebyshev polynomial approximation method. Pidcock [34] derived a family of series expansions that are useful for understanding the Green function’s behavior. Cuer [35] presented several propositions from the computational point of view but insufficient numerical results were provided in his work. Linton [36] proposed a set of rapid convergent representations based on the Ewald’s method [37]. Chen [38] extended the method of Newman by subtracting six Rankine terms so that the remaining part could be much smoother and Chebyshev approximations could be applied. All the works mentioned above provide helpful references to the subsequent researches.

It is really a pity that nowadays an open-source software package is still unavailable for the free-surface Green’s function in finite water depth. The difficulties for computing the finite-depth Green’s function lies in mainly the following three aspects: (1) the singularity in the denominator of the integrand; (2) the oscillation nature of the Bessel function; and (3) the integration ranges from 0 to infinity. The present work aims to contribute to this issue by developing a reliable algorithm and providing a well-packaged numerical library with a user-friendly interface. The present software package has been developed and tested over recent years in our research projects for offshore renewable energies. The corresponding theory and methodology are introduced in Section 2. The interface and structure of the software package are introduced in detail in Section 3. Verifications of the software package are given in Section 4. Benchmark tests for wave-structure interactions are carried out in Section 5, which confirms again the accuracy and efficiency of the present package. Conclusions have been drawn in Section 6 based on the previous analysis.

## 2. Theory and Algorithm

In order to elucidate the target problem with a deep understanding of the physics, the basic mathematical theory and the developed numerical algorithm for evaluation of the free-surface Green’s function are clearly presented below.

## 2.1 Mathematical expressions of free-surface Green’s function

Evaluation of the free-surface Green’s function $G ( { \pmb x } ; { \pmb \xi } )$ is traditionally considered as one of the most essential tasks in the analysis of wave-structure interactions within the potential flow framework. The Green’s function $\operatorname { G } ( \pmb { x } ; \pmb { \zeta } )$ , or source potential, is usually defined as the velocity potential at the point $( \xi , \eta , \zeta )$ due to a point source of strength −4π located at the field point $( x , y , z )$ as shown in Fig. 2. Mathematically, the freesurface Green’s function satisfies the following equation in the fluid domain,

$$
\left(\frac {\partial^ {2}}{\partial x ^ {2}} + \frac {\partial^ {2}}{\partial y ^ {2}} + \frac {\partial^ {2}}{\partial z ^ {2}}\right) G (x, y, z; \xi , \eta , \zeta) = \delta (x - \xi) (y - \eta) (z - \zeta)\tag{1}
$$

and corresponding boundary conditions can be expressed as

$$
\left. \begin{array}{c} \frac {\partial G}{\partial z} = v G \quad z = 0 \\ \frac {\partial G}{\partial z} = 0 \quad z = - h \\ \lim _ {R \to \infty} \left[ \sqrt {v R} \left(\frac {\partial G}{\partial R} - \mathrm{i} v G\right) \right] = 0 \quad R \to \infty \end{array} \right\},\tag{2}
$$

where $\delta$ is the Dirac delta function, $v = \omega ^ { 2 } / g$ is the wave number in deep water, and R is the horizontal distance between the source point and the field point, i.e.,

$$
R = \{(x - \xi) ^ {2} + (y - \eta) ^ {2} \} ^ {1 / 2}.\tag{3}
$$

The last boundary condition in Eq. (2), referred to as the Sommerfeld radiation condition, shows that the pulsating potential gradually decays with the horizontal distance and eventually vanishes in the far field. A rigorous theoretical solution to Eq. (1) and Eq. (2) has been found by John [39], which can be expressed in the following form

$$
G = \frac {1}{r} + \frac {1}{r _ {2}} + 2 \oint_ {0} ^ {\infty} \frac {(\mu + v) \cosh \mu (z + h) \cosh \mu (\zeta + h)}{\mu \sinh \mu h - v \cosh \mu h} e ^ {- \mu h} J _ {0} (\mu R) \mathrm{d} \mu ,\tag{4}
$$

where the path of the contour integral in Eq. (4) passes below the pole at $\mu = k , h$ is the water depth, r is the distance between the source point and the field point, and $r _ { 2 }$ is the distance between the field point and the image of the source point with respect to the sea bottom, i.e.,

$$
r = \{R ^ {2} + (z - \zeta) ^ {2} \} ^ {1 / 2},\tag{5}
$$

$$
r _ {2} = \{R ^ {2} + (z + \zeta + 2 h) ^ {2} \} ^ {1 / 2}.\tag{6}
$$

The Bessel function of the first kind $J _ { 0 } ( { \boldsymbol { \mu R } } )$ in the integrand shows the oscillation nature of the Green’s function. D is the positive root of the water wave dispersion equation

$$
k \mathrm{tanh} k h = v,\tag{7}
$$

and $\mu _ { m } \left( m { = } 0 , 1 , 2 { \ldots } \right)$ satisfy the following equation

$$
\mu_ {m} \mathrm{tanh} \mu_ {m} h = - v,\tag{8}
$$

where $\mu _ { 0 }$ is imaginary, $\mu _ { 0 } = - \mathrm { i } k$ (i is the imaginary unit), and $\mu _ { m } \ ( m { = } 1 , 2 . . . )$ are positive, characterizing the evanescent modes of the eigenfunction expansion as described in the following sections. A Fortran subroutine (named ‘Dispersion’) has been recently developed in the present package to obtain the accurate numerical solution of Eq. (7) and Eq. (8), using a higher-order iterative procedure suggested by Newman [40].

The free-surface Green’s function contains two parts which are referred to as the Rankine part and the waveterm part. The decomposed form of Green’s function can be written as

$$
G = \frac {1}{r} + \frac {1}{r _ {1}} + G _ {w},\tag{9}
$$

where the first two terms in the right-hand side of Eq. (9) comprise the Rankine part, and the last term is the wave-term part. $r _ { 1 }$ denotes the distance between the field point and the image of the source point with respect to the mean free-surface

$$
r _ {1} = \{R ^ {2} + (z + \zeta) ^ {2} \} ^ {1 / 2}.\tag{10}
$$

The first term $1 / r$ in the right-hand side of $\operatorname { E q . } \left( 9 \right)$ is strongly singular where the majority of singularity comes from. The second term $1 / r _ { 1 }$ in the right-hand side of Eq. (9) is less singular comparing to $1 / r$ in most of the cases. However, the second term $1 / r _ { 1 }$ shows equivalent singularity to $1 / r$ when the source and the field point are both locating on the free-surface. The reason for subtraction of these two strongly singular Rankine terms from the Green’s function is that, in traditional panel methods, these two terms should be integrated analytically over each panel [41] as direct numerical integration would introduce substantial errors. Taking consideration of Eq. (4), the wave-term $G _ { w }$ can be expressed as

$$
G _ {w} = \frac {1}{r _ {2}} - \frac {1}{r _ {1}} + 2 \oint_ {0} ^ {\infty} \frac {(\mu + v) \cosh \mu (z + h) \cosh \mu (\zeta + h)}{\mu \sinh \mu h - v \cosh \mu h} e ^ {- \mu h} J _ {0} (\mu R) \mathrm{d} \mu .\tag{11}
$$

It can be easily seen that the wave term $G _ { w }$ is a complex function with respect to R and $z ,$ satisfying the Sommerfeld radiation condition in the far field in Eq. (2). The behavior of $G _ { w }$ in three-dimensional space is studied in detail in Section 4.2, with the facility of the developed FinGreen3D package, as described in Sections 2 and 3.

![](images/f2b54fb7d4dd659fdbc5fb0a8ada47c60c6fec283166b65244dd1a796ae219f8.jpg)  
Fig. 2. Definition of the coordinate system in three-dimensional space. $\boldsymbol { Q }$ denotes the pulsating source and P denotes the field point. $Q _ { 1 }$ and $Q _ { 2 }$ are the image points of $\boldsymbol { Q }$ with respect to the mean sea level and the seabed, respectively.

## 2.2 The region-decomposition strategy in calculations of Green’s function

Since the integral form of Green’s function in Eq. (4) is difficult to be directly evaluated in an accurate and efficient manner, a region-decomposition strategy is developed. The entire parametric domain of interest is decomposed into four sub-regions according to R/h and appropriate series or asymptotic expansions are applied in different sub-regions. Based on this strategy, the non-trivial integration form of the Green’s function, i.e., Eq. (4), can be avoided throughout the entire domain. In addition to that, fast convergence at the neighborhood of \$ = 0 can be achieved. Details of the present algorithm are given in the subsequent sections.

## 2.2.1 Algorithm in the external region

The eigenfunction expansion proposed by John [39] is the most appropriate scheme in this region, as suggested by Newman [30]. There could be many derivative expressions from John’s original one. In the present work, the following form is employed for the sake of the consistency between real and imaginary terms:

$$
G = \mathrm{i} \frac {\pi}{N _ {0}} \cosh k (z + h) \cosh k (\zeta + h) H _ {0} ^ {(1)} (k R) + \sum_ {m = 1} ^ {\infty} \frac {2}{N _ {m}} \cos \mu_ {m} (z + h) \cos \mu_ {m} (\zeta + h) K _ {0} (\mu_ {m} R),\tag{12}
$$

where $H _ { 0 } ^ { ( 1 ) }$ denotes Hankel function of the first kind, and $K _ { 0 }$ denotes modified Bessel function of the second kind. The denominators $N _ { m } \left( m = 0 , 1 , \dots \right)$ in the above expansion are defined as

$$
N _ {0} = \frac {h}{2} \left(1 + \frac {\sinh 2 k h}{2 k h}\right)\tag{13}
$$

and

$$
N _ {m} = \frac {h}{2} \left(1 + \frac {\sin 2 \mu_ {m} h}{2 \mu_ {m} h}\right) (m = 1, 2, \ldots).\tag{14}
$$

The number of terms necessary for a given accuracy depends on the ratio R/h. In FinGreen3D, a convergence check is carried out from the second term of Eq. (12), making sure that the series is truncated at the condition when the absolute values of $G , G _ { R }$ , and $G _ { z }$ are all less than the prescribed tolerance, $\mathrm { e . g . , 1 0 ^ { - 6 } }$ . By this way, satisfactory convergence could be achieved in this region with a maximum number of 10 terms.

## 2.2.2 Algorithm in the first intermediate region

More terms in the eigenfunction expansion are required to achieve good convergence when R/h becomes smaller. To accelerate the convergence rate in the region of $0 . O 5 { \leq } R { \ / h \ < } 0 . 5 ,$ , a nonlinear series-acceleration method named “Epsilon Algorithm”, which was first proposed by Wynn [42] and described in detail by Mishonov & Penev [43], has been implemented in FinGreen3D. In this package, the Epsilon Algorithm has been successfully interfaced to and incorporated with the eigenfunction expansion as written in Eq. (12).

In our numerical tests on the Epsilon-Algorithm-accelerated method, 10\~50 terms are sufficient to obtain a satisfactory accuracy (10 terms at $R / h = 0 . 5$ and 50 terms at $R / h = 0 . 0 5 )$ . The requisite number of terms is approximated by the following expression:

$$
M = - 8 8. 8 9 R / h + 5 4. 4 5.\tag{15}
$$

## 2.2.3 Algorithm in the second intermediate region

When $0 . O O O 5 { \leq } R / h < 0 . O 5 .$ , convergent results of eigenfunction expansion in Eq. (12) can no longer be achieved using the Epsilon-Algorithm-accelerated method. This urges us to search for another possible way of accelerating the convergence of the series. In this region, the following formulation is derived based on Pidcock [34], with an improvement on the calculation of the Rankine-source summation:

$$
G = \frac {1}{r} + \frac {1}{r _ {1}} + \sum_ {p = 1} ^ {\infty} (R s) _ {p} + \frac {2}{h} \left[ \gamma + \log \left(\frac {R}{4 h}\right) \right] + \mathrm{i} \varLambda H _ {0} ^ {(1)} (k R) + 4 \sum_ {m = 1} ^ {\infty} \left[ C _ {m} ^ {(1)} K _ {0} (\mu_ {m} R) - C _ {m} ^ {(2)} K _ {0} (\mu_ {m} ^ {*} R) \right],\tag{16}
$$

where $\gamma$ denotes the Euler constant, $\mu _ { m } ^ { * }$ is an approximation of $\mu _ { m }$ when m is large, i.e., $\mu _ { m } ^ { * } = m \pi / h$ . The principle of Eq. (16) is to accelerate the convergence through subtracting a simplified series with the same asymptotic form when m is large. Detailed form of the multiple Rankine terms $R s ,$ the series expansion coefficient $C _ { m } ^ { ( 1 ) } , C _ { m } ^ { ( 2 ) }$ and  are given in Pidcock [34]. To calculate the Rankine-source summation in a more efficient manner, a new formulation using the Chebyshev approximation method is derived here:

$$
\frac {1}{r} + \frac {1}{r _ {1}} + \sum_ {p = 1} ^ {\infty} (R s) _ {p} = \frac {1}{h} \Bigl \{\sum_ {p = - 1} ^ {1} \bigl (b _ {p} + c _ {p} \bigr) + \sum_ {m, n} a _ {m, n} \left(\frac {r}{h}\right) ^ {2 m} \left[ \left(\frac {z - \zeta}{h}\right) ^ {2 n} + \left(\frac {z + \zeta + 2 h}{h}\right) ^ {2 n} \right] - 2 \Bigr \},\tag{17}
$$

where

$$
b _ {p} = \{(R / h) ^ {2} + [ (z - \zeta) / h + 2 p ] ^ {2} \} ^ {- 1 / 2},\tag{18}
$$

$$
c _ {p} = \{(R / h) ^ {2} + [ (z + \zeta + 2 h) / h + 2 p ] ^ {2} \} ^ {- 1 / 2},\tag{19}
$$

where $a _ { m , n } ( m , n = 1 , 2 , 3 \ldots )$ are Chebyshev coefficients and the corresponding values are given in Table 7.2 of Ref. [44]. Up to m=4 and n=4 terms in the Chebyshev expansion are sufficient to reach an accuracy of six decimals.

Generally, 50\~100 terms are needed in this region for a satisfactory accuracy (50 at $R / h = 0 . 0 5$ and 100 at $R / h { = } 0 . 0 0 0 5 )$ . The requisite number of terms is approximated by the following expression:

$$
M = - 1 0 1 0. 1 0 R / h + 1 0 0. 5 0.\tag{20}
$$

## 2.2.4 Algorithm in the region of singularity

In the region when the parameter R/h approaches zero, all the previous formulations become invalid due to their singularity in the neighborhood of zero. A more suitable series expansion is therefore preferred, which should not contain any singularity near the origin (apart from the Rankine terms).

The rapidly convergent representation of the free-surface Green’s function proposed by Linton [36] using Ewald’s method [37] is suitable for this region and hence is implemented in the present software package

$$
\begin{array}{c} G = \mathrm{i} \frac {\pi}{N _ {0}} \cosh k (z + h) \cosh k (\zeta + h) J _ {0} (k R) + \sum_ {m = 1} ^ {\infty} \frac {\Lambda_ {m}}{N _ {m}} \cos \mu_ {m} (z + h) \cos \mu_ {m} (\zeta + h) + \frac {1}{r} \operatorname{erfc} \left(\frac {r}{a h}\right) + \\ \frac {1}{r _ {1}} \operatorname{erfc} \left(\frac {r _ {1}}{a h}\right) + \sum_ {i = 1} ^ {4} \frac {1}{\left(R ^ {2} + \chi_ {i} ^ {2}\right) ^ {1 / 2}} \operatorname{erfc} \left(\frac {\left(R ^ {2} + \chi_ {i} ^ {2}\right) ^ {1 / 2}}{a h}\right) + 2 v \int_ {0} ^ {a h / 2} e ^ {v ^ {2} t ^ {2} - R ^ {2} / 4 t ^ {2}} \sum_ {i = 1} ^ {4} e ^ {- v \chi_ {i}} \operatorname{erfc} \left(\frac {\chi_ {i}}{2 t} - v t\right) \frac {\mathrm{d} t}{t}, \end{array}\tag{21}
$$

where erfc is the complementary error function and the vertical distance components $\chi _ { i }$ are

$$
\left. \begin{array}{c} \chi_ {1} = - \zeta - z, \chi_ {2} = 2 h - \zeta + z \\ \chi_ {3} = 2 h + \zeta - z, \chi_ {4} = 4 h + \zeta + z \end{array} \right\}.\tag{22}
$$

Details of the expansion coefficients $\Lambda _ { m }$ are given in Linton [36]. Note that these coefficients could be calculated through a combination of Taylor series expansion and integration formulation, depending on the value of R/a. The integrals are expressed explicitly in Eq. (21) and implicitly in the expansion coefficients $\Lambda _ { m } ,$ which should be calculated through numerical quadrature methods. In the present software package, these integrals are computed by calling a global adaptive Gauss-Kronrod quadrature subroutine with a higher degree of accuracy, which was developed in the work of Liu [45]. This subroutine is capable of calculating the Green’s function in the extreme case of $R / h = 0$ where the source point overlaps the field point. The expansion coefficients $\Lambda _ { m }$ degrade to exponential integral functions when $R / h = 0 ;$ , which could be evaluated analytically using series expansions as well. An important thing to mention is that the convergence rate of Eq. (21) highl depends on the product value of a and h. An appropriate choice of this parameter would guarantee the convergence of the series expansion in an efficient way. Two schemes are hence embedded in the subroutine, with one using 0.25h as suggested by Linton and McIver [46] and the other using a more complex process as described in Liu et al. [47]. Through this way, the calculation of Linton’s representation [36] is able to achieve a good accuracy in most of the cases by using up to 3\~10 terms.

## 3. Interface and Structure of the Software Package

To provide the readers and the users with a clear map of how to manipulate the software, the interface between the software and the external routines is displayed with explanations for the background below. The hierarchical code structure with multi-level subroutines is also explained in details.

## 3.1 Input and output parameters

The algorithm described in section 2 has been implemented in a released software package FinGreen3D which is written in Fortran 90. The input and output parameters to interact with hydrodynamic solvers in the frequency domain are introduced in Table 2.

Table 2. Input and output variables

<table><tr><td>R</td><td>Input, REAL (8)</td><td>The horizontal distance between the field point and the source point</td></tr><tr><td>ZF, ZP</td><td>Input, REAL (8)</td><td>z coordinates of the field point and the source point, respectively</td></tr><tr><td>V</td><td>Input, REAL (8)</td><td>Corresponding wave number in deep water</td></tr><tr><td>WVN</td><td>Input, REAL (8)</td><td>Array, with NK elements, restoring the roots of the dispersion equation</td></tr><tr><td>NK</td><td>Input, INTEGER</td><td>Number of elements in the array WVN</td></tr><tr><td>H</td><td>Input, REAL (8)</td><td>Dimensional finite water depth</td></tr><tr><td>TAG</td><td>Input, INTEGER</td><td>A flag to determine whether the Rankine part is to be calculated or not</td></tr><tr><td>GRN</td><td>Output, Complex (16)</td><td>Array, values of Green&#x27;s function and its derivatives with respect to R and z</td></tr></table>

The information of the field point and source point locations should be first given to the driver subroutine. $v = \omega ^ { 2 } / g$ is the deep water wave number, where ω is the wave angular frequency and g is the gravitational acceleration. WVN is a variable to store the roots of the water wave dispersion equation, in which the first element is the positive root k of Eq. (7) and the rest elements are the real roots of Eq. (8), i.e., $\mu _ { m } \ : ( m = 1 , 2 .$ NK-1). NK defines the size of the array WVN. H is the dimensional water depth and a positive real number should be given prior to the calculations. The integer variable TAG is used to determine whether the Rankine part is to be calculated (TAG =1) or not (TAG =0). The reason is that in some hydrodynamic solvers, especially in those applying the lower-order discretization, the Rankine part is normally integrated separately through an analytical algorithm, such as the one proposed in Newman [41] and described in Section 2.1. Whereas for the other solvers applying the higher-order discretization, the Rankine part is normally integrated together with the wave-term in Green’s function, taking advantage of some special strategies for the singular and near singular integrals (Sun et al. [48]). GRN is a 3-element complex array defining the output of FinGreen3D, in which GRN (1) is the value of Green’s function. GRN (2) and GRN (3) are the derivatives of Green’s function with respect to R and z, respectively.

## 3.2 Structure of the package

The released package includes several subroutines which can be categorized into three levels, i.e., Level\_1 (top level), Level\_2 (intermediate level) and Level\_3 (low level), as shown in Fig. 3. Major subroutines are listed below:

∙ FINGREEN3D – A driver subroutine (Level\_1), which decomposes the entire parametric domain into four regions and calls the various algorithms accordingly.

∙ DISPERSION – An intermediate level subroutine (Level\_2), which solves the water-wave dispersion equation, i.e., Eq. (7) and Eq. (8), using a higher-order iterative procedure based on the method suggested by Newman [40].

∙ EIGEN – An intermediate level subroutine (Level\_2), which calculates the Green’s function by applying the eigenfunction expansion method in the region R/h ≥ 0.5.

∙ EIGENE – An intermediate level subroutine (Level\_2), which calculates the Green’s function by applying a combination of the eigenfunction expansion method and the Epsilon Algorithm in the region 0.05≤ R/h <0.5.

∙ PIDCOCK – An intermediate level subroutine (Level\_2), which calculates the Green’s function applying a combination of the Pidcock’s expansion method and the Epsilon Algorithm in the region 0.0005≤ R/h <0.05.

∙ LINTON – An intermediate level subroutine (Level\_2), which calculates the Green’s function by applying Linton’s expansion method in the region R/h <0.0005.

∙ COEF – A lower level subroutine (Level\_3), which calculates the expansion coefficients in Linton’s expansion method using a combination of special functions, Taylor expansions, and adaptive quadrature methods.

∙ DCOEF – A lower level subroutine (Level\_3), which calculates the derivatives of expansion coefficients with respect to R in Linton’s expansion method using a combination of special functions, Taylor expansions, and adaptive quadrature methods.

The driver subroutine, FINGREEN3D, is the only Level\_1 subroutine, from which all the Level\_2 subroutines are called. Level\_2 subroutines are corresponding to the four expansion methods in the corresponding regions as described in Section 2, respectively. In addition to that, the Level\_2 subroutines can also be implemented for other specific-purpose computations alone, as long as their necessarily associated subroutines are included. Level\_3 subroutines consist of affiliated subroutines and external subroutines. The affiliated subroutines are called by two Level\_2 subroutines, i.e., PIDCOCK and LINTON, used for integrations by the Chebyshev approximation, series expansions or adaptive quadrature algorithms. The majority of external subroutines are from the book of Zhang & Jin [49], used for calculating some special functions, such as exponential integral function, error function, Gamma function, and many kinds of Bessel functions, based on continued fractions. Since so frequently called, the external subroutines of Bessel functions are hereby modified into several derivative versions, in order to improve the computation speed. Another external subroutine is from Mishonov & Penev [43], used for predicting the limit of a series in which the first several terms are known through the Epsilon Algorithm.

All the communications between subroutines in the present package are strictly restricted via explicit interfaces, without using any common data blocks. Therefore, it can be parallelized without any difficulty on Windows or Linux platform using parallelization techniques, such as OpenMP or MPI.

![](images/eab08bdf43e548857f2484755bbad911c2b0ebd2a7be8a550049a22b5aa56c11.jpg)  
Fig. 3. Multi-level subroutines in the hierarchical code structure

## 4. Verifications and Discussions of the Software Package

To verify implementations of present algorithms in the released package, a comparison is made with the Newman’s method [30] using multi-dimensional polynomial approximations to calculate the Green’s function and its derivatives in finite water depth. The behaviors of the wave-term in the Green’s function is studied and discussed in detail thereafter. In addition, the computation efficiency of the software package is also presented with an in-depth discussion.

## 4.1 Verifications of the software package

Comparison results between Newman’s method [30] are shown in Figs. 4 and 5, for a high pulsating frequency and a low pulsating frequency, respectively. Both the pulsating point source and the fluid field point are selected on the free surface in present tests because the free-surface Green’s function is believed to be more difficult to evaluate when z+ζ=0. As clearly shown in Figs. 4 and 5, even under such extreme conditions, perfect agreements can still be achieved between the present results and those using Newman’s method [30]. It can be seen in Fig. 4 that periodic oscillations can be found in the values of the free-surface Green’s function and its derivatives. Worthwhile to note, the oscillation amplitude of the Green’s function value decreases with the increasing of R/h (Fig. 4a and b), indicating that the influence from a point source to a fluid field point decays with the horizontal distance. A similar pattern is not observed in Fig. 5, since the wavelength is much larger than that in Fig. 4. Nevertheless, no matter how much the pulsating frequency is, our principle knowledge is proved that the potential influence is appreciably large at the neighborhood of the pulsating point source, as clearly shown in these figures (Fig. 4a and b, Fig. 5a and b).

(a)  
![](images/e0c696ee2188e9655aa350cb664670f421152a58c7fb8edd7a75ed97898558cc.jpg)

![](images/592939c21cafd88435b32f1e73020d3a5bc3caf441dbd768e16885ef0b8a7ef6.jpg)

(c)  
![](images/c90accd359232d7ed725af4c3c6512fd49ad13df43687f056830592037432389.jpg)

(d)  
![](images/aa34f6267f252ab55381e2b1fa4bb52ea8930ba3c2cd807409bad0c8524de7fd.jpg)

(e)  
![](images/2e5f0e9c71a2ed4ed31994ea541fe35cf935a989fa82c1e93a80b8fd895d9466.jpg)

(f)  
![](images/b32d534d5c03965f7ec6466f640aef063f1ad5fba88f0b75037e17b6585e24dd.jpg)

Fig. 4. Values of free-surface Green’s function 	 and its gradient ∇	, as a function of R/h, when the point source and the field point locate at the free surface with a high pulsating frequency of $f = 1 . 1 1 4 5 s ^ { - 1 }$ (i.e., wave number $v =$ $5 . 0 \mathrm { m } ^ { - 1 } ) { : ( \mathrm { a } ) }$ real part of G; (b) imaginary part of G; (c) real part of $\partial G / \partial R ;$ (d) imaginary part of $\partial G / \partial R .$ ; (e) real part of $\partial G / \partial z ;$ (f) imaginary part of $\partial G / \partial z$ . The red solid-circle line stands for results calculated using Newman’s polynomial approximation, the green dash-dotted line stands for results calculated by the present FinGreen3D code.

(a)  
![](images/e17f7b16946f26a6733c31eecaffcbe030966645513fd209b10fd44503cbf2c4.jpg)

![](images/1dc75ebff7bbeec5b763005a51d3fb4e3631e844e4d94cfb58f2aa31add3e6fc.jpg)

![](images/8998e65edc15ffff34a6ded6812e043afaedff953b032524aae788ee93a96f07.jpg)

(d)  
![](images/77b08f88530a5d26246cd9888b32617cbbd257e21359c1c1d2c257b4e56bbe54.jpg)

(e)  
![](images/97b7469cb2a2152a618273842d205e93ee3023def4272f587b3d5f2984ff364e.jpg)

(f)  
![](images/7b52a72990a19c4578af29638a792340caee92b5f369c05ca1337469389c9514.jpg)

Fig. 5. Values of free-surface Green’s function 	 and its gradient ∇	, as a function of R/h, when the point source and the field point locate at the free surface with a low pulsating frequency of $f = 1 . 5 7 6 1 \times 1 0 ^ { - 2 } s ^ { - 1 }$ ( i.e., wave number $1 . 0 \times 1 0 ^ { - 3 } \mathrm { m } ^ { - 1 }$ ). Description of the subplots is given in Fig. 4.

## 4.2 Behaviors of the wave-term in Green’s function

Fig. 6 shows the variations of the essential part of the Green’s function, i.e., the wave term $G _ { w } .$ , in a wide domain near the point source which is located on the free surface with a high pulsating frequency, as a function of the distance between the field and the source points. The horizontal component R and the vertical component z of the distance are both normalized by the water depth h. The real part is shown here alone because the imaginary part is relatively simpler. From either the oblique view or the contour plot of the function and derivative values, the fluctuations appear to be steepest at the neighborhood of the source point. The fluctuation magnitude decays along the two directions, with either increase of the horizontal distance R/h or the vertica distance z/h. The potential influence generated by the point source transmits from the origin (source point) to the far field along the horizontal direction, like a sinusoidal/ cosinusoidal wave with its amplitude decreasing as the horizontal distance increases. Deep below the free surface, the influence caused by the point source inclines to become weaker and weaker, as observed from the near-flat variation distribution in the oblique view or the contour plot, in the case when vertical position of the field point is approaching the seabed

(a)  
![](images/4247f959b23a98332fa81ce518fe1f303010d7acea04a116aac11ff35fc9afb2.jpg)

![](images/d1c1ca5e0548e18faabe9fbf312b6b0481ccf65c4c562886e06d9bfc12e69d40.jpg)

(c)  
![](images/8463d0448c42c50521c9dca116f99ff88e1c9cfdd2cd9ebd32579aa7ce093c94.jpg)

![](images/7e8e4cfa3517bbf2a6e0b80a47bc5c1da925111c2f5a4a7fc0f55e2fcd7155b4.jpg)

(e)  
![](images/ce3e5099e18d7e20fdf90b9d55e82cf4e8df236ce6f6eb015d2b44d2dd5e0b03.jpg)

(f)  
![](images/1f98f0ff068a1ba7a80b53a84b084581eabf86c3d43831c4e7d18f8172b74a9e.jpg)  
Fig. 6. Real part of the complex harmonic wave term $G _ { w }$ and its derivatives $\nabla G _ { w }$ in free-surface Green’s function, when a point source locates at the free surface with a high pulsating frequency of $f = 8 . 6 3 2 7 \times 1 0 ^ { - 1 } { s ^ { - 1 } }$ ( i.e., wave number $v = 3 . 0 \ \mathrm { m } ^ { - 1 } )$ . They are oblique views (left column) and contour plots (right column) of the $G _ { \mathrm { w } }$ value (top row), its derivatives with respect to R (intermediate row) and z (bottom row), as a function of R/h and z/h, in which h is the water depth.

(a)  
![](images/2988f251a7d12f35f41a4cbed6bd35b40b1cb15307066ba409f3f7aba910c97c.jpg)

![](images/225e106d0610a7f125d25898e9ed068c4f4905b3da2b2ab04a944097fe958976.jpg)

(c)  
![](images/f36ea0c7efc8c266a997431d8361f67a02fbb70e02dfa74f3c58efaee9c943dd.jpg)

![](images/4d5319094695a9235e976131c60a8ee2c4accfd5e2501db3791d571b9e511cdc.jpg)

(e)  
![](images/ade623e91bb8fa4eb06a4dd3895b924a47063eb88a47e972f6934b197759f255.jpg)

(f)  
![](images/94d3a380e44f05e63fb328be2c1af8f6a251bf83fb24d44671f014e101fcff7b.jpg)  
Fig. 7. Real part of the complex harmonic wave term $G _ { w }$ and its derivatives $\nabla G _ { w }$ in free-surface Greens’ function, when a point source locates at the free surface with an extremely low pulsating frequency of $f = 4 . 9 8 4 1 \times 1 0 ^ { - 3 } \ : s ^ { - 1 }$ ( i.e., wave number $v = 1 . 0 \times 1 0 ^ { - 4 } \mathrm { m } ^ { - 1 }$ ). Description of the subplots is given in Fig. 6.

Fig. 7 shows the variations of the wave term $G _ { w }$ in a wide domain near the point source which is located on the free surface with a low pulsating frequency, as a function of the distance between the field and the source points. From either the oblique view or the contour plot of the function and derivative values, the fluctuation tends to be much milder in contrast to the high-frequency case. There is seemingly little fluctuation along the horizontal direction as the horizontal distance R/h increases, as inferred from the flat distribution with respect to R/h. The fluctuation magnitude increases as the vertical distance z/h increases, to a maximum value being reached at the seabed.

## 4.3 Computation efficiency of the software package

Fig. 8 shows CPU time (unit: µs) of per evaluation of the Green’s function and its derivatives using FinGreen3D of present version, on a SONY laptop with an Intel(R) Core(TM) i7-2670QM CPU of 2.2 GHz and a 64-bit Windows 7 operating system. The computation is performed sequentially on one single thread, which costs a total CPU time of $4 . 6 9 3 6 \times 1 0 ^ { 2 }$ s for the 200 input wave numbers, and $5 . 9 7 4 6 \times 1 0 ^ { 2 }$ s for the

200 input point distances (i.e., in each case, 0.2 billion evaluations of the code FinGreen3D have been performed). Fig. 8(a) shows that one implementation of the code, i.e., one evaluation of the Green’s function and its derivatives consumes approximately 2\~4 µs. The low cost of computation means that for a practical offshore structure with nearly 5000 constant elements, only 50\~100 s are sufficient for the computation of the influence matrix in each wave period. This will noteworthily facilitate the hydrodynamic analysis process for the practical offshore structures. Fig. 8(b) reveals that the R/h-lowest region is the most time-consuming part for evaluation, due in large part to the fact that several adaptive numerical integrations are applied in that region to the expansion coefficients of the Linton’s formulation. The CPU time gradually reduces as a function of R/h until it gets stable with the increase of R/h. The possible reason is that the intrinsic characteristic (i.e., the strong singularity at the source point) of Eq. (1) determines that its series expansion solutions converge slower when R/h becomes smaller, regardless of the expansion type. Consequently, calculations based on the eigenfunction expansion and the Pidcock’s expression appear to be faster than the Linton’s, since no numerical integration is involved in these two formulations.

(a)  
![](images/631fba5cdc569401dc31cda69aae78e57cf6d0895f2d3cd4709d02bac44b5b3e.jpg)

(b)  
![](images/f9a27a760888f4ac2e1d8b130b2a1e5123093fea37fc9b37d91a25afb3e2dca0.jpg)  
Fig. 8. Computation time for per implementation of FinGreen3D, as a function of wavenumber 	(left) and normalized point distance R/h (right). The left figure is obtained based on averaged CPU time of 1 million evaluations of FinGreen3D for each input wave number , so does the right figure for each input point distance R/h.

## 5. Applications to Waves-structure Interactions

In the very recent years, a plenty of ocean energy converters have been designed and turned into applications. Normally, their feasibility and safety in the oceanic circumstances need to be evaluated in advance. For this purpose, in the present section, the developed software package is firstly validated with benchmark cases, and thereafter with industrial applications.

## 5.1 The boundary element theory in the offshore hydrodynamic analysis

The free-surface Green’s function is the crucial fundamental component in the analysis of wave-structure interactions within the potential-flow frame in coastal/offshore renewable energies. Applying the Green’s second identity on the governing equation of velocity potential $\varphi ( x )$ with several predefined boundary conditions, a following integral equation can be obtained

$$
C (\pmb {x}) \varphi_ {j} (\pmb {x}) + \iint_ {S _ {B}} \varphi_ {j} (\pmb {\xi}) \frac {\partial G (\pmb {\xi} ; \pmb {x})}{\partial n _ {\pmb {\xi}}} \mathrm{d} S _ {\pmb {\xi}} = \iint_ {S _ {B}} V (\pmb {\xi}) G (\pmb {\xi}; \pmb {x}) \mathrm{d} S _ {\pmb {\xi}}, (j = 1 \sim 7, \pmb {x} \in S _ {B}, \pmb {\xi} \in S _ {B}),\tag{23}
$$

where  represents the field point and $\xi$ represents the source point; $C ( x )$ is referred to as "solid angle", which depends on the local shape of geometry, having a value of $2 \pi$ in the traditional constant panel method; the boundary condition on the immersed body surface $S _ { B }$ is impermeable and can be further represented by

$$
V (\pmb {\xi}) = \left\{ \begin{array}{l l} n _ {j} (\pmb {\xi}), j = 1 \sim 6 \\ - \frac {\partial \varphi_ {0} (\pmb {\xi})}{\partial n _ {\pmb {\xi}}}, j = 7, \end{array} \right.\tag{24}
$$

where $n _ { j } ( \pmb { \xi } )$ stand for the normal derivatives on the geometrical surface and $\varphi _ { j } ( \pmb { \xi } )$ stand for the incident wave potential when $\scriptstyle j = 0 ,$ the radiation potentials when $j = 1 { \sim } 6 ,$ and the diffraction potential when $\scriptstyle 1 j = 7$ . The simulation is steady and conducted in the frequency domain. After finding the solution to the wave potentials from the boundary integration equation Eq. (23), a series of physical quantities can be obtained through direct integration of the corresponding wave potential on the immersed body surface.

Computation efficiency can be improved by applying one or two planes of symmetry. In addition, the multiple-thread shared-memory parallel computation technique can be employed using standard OpenMP clauses at the following two places: (1) evaluation and storage of the free-surface Green’s function between arbitrary two panels (in addition to planes of symmetry, computation burden can be reduced to half due to the symmetry between the source and the field points); (2) calculation of the influence coefficients and assembling the influence matrix for the boundary integral equations.

Therefore, the present package FinGreen3D has been successfully interfaced to a wave-structure-interaction panel code HAMS (Hydrodynamic Analysis of Marine Structures) [50]. In the following computations, the present package is compiled by the Intel® Fortran Compiler 18.0 (Intel® Parallel Studio XE 2018) and the Microsoft® Visual Studio 2015.

## 5.2 Case No.1: a submerged spherical wave energy converter

A submerged sphere is presented as the first benchmark test for validating the package. As a basic regular geometrical concept, the spherical shape is frequently employed to design wave energy converters (see e.g. [51], [52] and [53]). Parameters of the present benchmark case are listed as follows: associated with the sphere radius $^ { a , }$ the ratio of radius to water depth is 0.3, and the ratio of immersion depth to the radius is 1.5. Since the accuracy of the numerical results may rely on the mesh quality, firstly, a grid convergence test is conducted. Five mesh types are used, in which the number of panels increases as the grid divisions on the two directions (warp and weft) increase, see Table 3 for more details.

Table 3. Specifications of the grid divisions on the sphere in the convergence test

<table><tr><td>Mesh</td><td>Warp Direction</td><td>Weft Direction</td><td>Number of Panels</td></tr><tr><td>Mesh 1</td><td>10</td><td>20</td><td>200</td></tr><tr><td>Mesh 2</td><td>20</td><td>30</td><td>600</td></tr><tr><td>Mesh 3</td><td>30</td><td>40</td><td>1200</td></tr><tr><td>Mesh 4</td><td>40</td><td>50</td><td>2000</td></tr><tr><td>Mesh 5</td><td>50</td><td>60</td><td>3000</td></tr></table>

Modulus of the horizontal exciting wave force of the submerged sphere is shown in Fig. 9(a). The comparison shows that the numerical result converges fast with respect to the number of panels. When the number of panels exceeds 600, the numerical result approaches almost very close to the analytical solution [54]. This is further confirmed by the relative error analysis of the computation as shown in Fig. 9(b), the absolute value of the relative error between the computation and the analytical solution is confined within 4% when the number of panels exceeds 600.

(a)  
![](images/59a952ac8c5a95b00e1becb72d19833ae3f0dda007d33a49301f8524609e61c6.jpg)

(b)  
![](images/4a8b09fab8358b6b54b35ca17cde328a8e22d04ea4f75afe8dc5b03277bbf2c0.jpg)  
Fig. 9. Convergent test of the wave excitation force of a submerged sphere, as a function of the normalized radius	q: (a) comparison between Linton’s results with respect to the number of panels, and (b) relative error analysis of (a).

Based on the convergence test performed above, around 2000 panels are chosen as an appropriate number of panels for the following computation. To further check the influence of mesh structure on the computation accuracy, both a structured mesh (‘Mesh A’) and an unstructured mesh (‘Mesh B’) are hereby used in the comparison, as displayed in Fig. 10. In the structured mesh, the sphere surface is discretized into 40×50 constant panels (40 in warp and 50 in weft directions) of a quadrilateral or triangular element shape. In the unstructured mesh, the sphere surface is discretized into 1920 triangular panels of a uniform size. Exact theoretical results from the multipole expansion method given in Linton [54] are used to validate the present numerical results, as given in Fig. 11.

(a)  
![](images/75b960921b98d19f878abeda38f29007321dcb0b1b6fc91b1161c49fc674015f.jpg)

![](images/0fd9c96dfc6b5bfa3dc3a23eb777a71ff1d34a87cf072caa4a8fca862191382f.jpg)  
Fig. 10. Pretty fine mesh for the submerged sphere: (a) structured mesh (“Mesh A”); (b) unstructured mesh (“Mesh B”)

Fig. 11 shows results of the surge and the heave hydrodynamic coefficients, where all the quantities are normalized by volume of the submerged sphere, say, $V = 4 / 3 \pi a ^ { 3 } .$ . First of all, Fig. 11 clearly illustrates that no matter which mesh structure is employed, the present numerical results generally agree fairly well with the analytical results [54], which confirms the accuracy of the present algorithm for evaluating the free-surface Green’s function in the hydrodynamic analysis of structure with a smooth surface. On the other hand, while the numerical results for radiation damping coefficient using both meshes highly agree with those of the analytical method, some discrepancies are found in the comparisons of added mass of the surge mode. The numerica results based on the unstructured mesh, though having a less number of panels, are much closer to the analytical results. This may suggest that the unstructured mesh of a uniform size is recommended to improve the computation accuracy and efficiency.

(a)  
![](images/0b1eafa0050e6b703744a2094502a47392206d1d93f842325e48ce10e5a34a50.jpg)

(b)  
![](images/1e9901b9d5b3d3d63be529adde4cc94cd4146c55d3be0993bc2545939de24692.jpg)  
Fig. 11. Added mass and radiation damping coefficients of a submerged sphere, as a function of the normalized radius	q: (a) surge added mass and radiation damping and (b) heave added mass and radiation damping. “Linton (1991)” used the analytical multipole expansion method described in [54] which is extremely accurate. “Mesh $\mathbf { A } ^ { \astrosun }$ and “Mesh $\mathbf { B } ^ { \ast }$ denotes the numerical results computed by the HAMS frequency-domain solver incorporating with the FinGreen3D package, using meshes specified in Fig. 10.

## 5.3 Case No.2: a floating circular cylindrical column

A circular cylinder in moderate water depth is selected as the second testing case for validation, since it is an essential component (e.g., buoyancy column of the floater) of the offshore renewable energy devices (see e.g. [55], [56] and [57]). Firstly, a grid test is performed to ensure the convergence of the numerical results. Several basic parameters of the geometry are as follows: cylinder radius a, draft $T { = } 0 . 5 a$ and the water depth h =0.75a. Five mesh types are used, in which the grid resolution relies on the divisions on the three directions (annular, radial and draft), see Table 4 for more details

Table 4. Specifications of the grid divisions on the cylinder in the convergence test

<table><tr><td>Annular Direction</td><td>Radial Direction</td><td>Draft Direction</td><td>Body Panels</td><td>Waterplane Panels</td><td>Total Panels</td></tr><tr><td>10</td><td>5</td><td>4</td><td>72</td><td>40</td><td>112</td></tr><tr><td>20</td><td>10</td><td>8</td><td>360</td><td>200</td><td>560</td></tr><tr><td>35</td><td>15</td><td>15</td><td>960</td><td>480</td><td>1440</td></tr><tr><td>40</td><td>20</td><td>15</td><td>1400</td><td>800</td><td>2200</td></tr><tr><td>50</td><td>25</td><td>18</td><td>2064</td><td>1200</td><td>3264</td></tr></table>

Note that there are two planes of symmetry in the case of a circular cylinder. Hence, the number of panels for computation in reality can be reduced to one quarter. Meshes on the waterplane are used to suppress the socalled “irregular frequencies”. Two representative meshes with coarser and finer grid resolutions are visualized in Fig. 12.

(a)  
![](images/2dc39f589265cef5093de9190c459bd2492860f6201a7104630772752f6cc593.jpg)

![](images/440cf06ce5c2fa33080d144b89c643cb345229d1ef89e45c4d60a16d3a103e50.jpg)  
Fig. 12. Mesh of the circular cylinder for a convergence test: (a) with 560 panels and (b) with 2200 panels

Modulus of the horizontal exciting wave force of the floating cylindrical column is shown in Fig. 13(a). Exact analytical results from the eigenfunction method given in Garret [58] are used to validate the present numerical results. Similar to the Case No.1, the comparison shows that the numerical result converges really fast with respect to the total number of panels. When the total number of panels exceeds 560, the numerical result approaches almost exactly to the analytical solution [58]. This is further confirmed by the relative error analysis of the computation as shown in Fig. 13(b), the absolute value of the relative error between the computation and the analytical solution is confined within 4% when the number of panels exceeds 560. Based on the convergence test, for such a cylinder, around 1400 panels appear to be sufficient for the computational accuracy.

(a)  
![](images/a6a73a41c585e350b7b0f7618f561374eaa7033d5d782a6186c33d6b51df159d.jpg)

![](images/0eef1731cd315dff758937d3fd99c374d2e98c6961fedf4efa1906f5d4597921.jpg)  
Fig. 13. Modulus of the complex exciting wave forces of a circular cylinder, as a function of the normalized radius	q: (a) horizontal exciting force, (b) vertical exciting force. “Garret (1971)” used the analytical eigenfunction expansion method described in [58] which is extremely accurate. The others denote numerical results computed by the FinGreen3D & HAMS codes, using meshes specified in Table 4.

In order to provide more validations, a comprehensive numerical comparison is performed as described in Table 5. Thanks to the extensive data set of added mass and added damping available in Yeung [59], in which an eigenfunction calculation was carried out for the circular cylinder, validation with precise analytical results with respect to a variety of geometrical and environmental parameters becomes possible. In Yeung’s analysis [59], the finite water depth was set to be unit, while the geometrical size of the circular cylinder and its relative position to the seabed were changing, so as to make the ratio of geometrical size over water depth variable. The terminology ‘clearance’ stands for the distance from the seabed to the bottom of the cylinder. The numerical example has been grouped into 8 cases, according to different values of the aspect ratio (ratio of the draft over the radius). All the meshes are generated by an automatic analytical mesh generator so that the quality of grids can be controlled. The number of panel division in each direction is determined by ensuring that the panels in the water plane and the bottom are of comparable size to those in the rectangular enclosed-lateral surface.

Table 5. Data summary of the implemented cases for the circular cylinder with various parameters

<table><tr><td rowspan="2">Case No.</td><td rowspan="2">Added mass/ radiation damping</td><td colspan="3">Geometry</td><td colspan="3">Mesh</td></tr><tr><td>Radius (a/H)</td><td>Draft (T/H)</td><td>Annular</td><td>Radial</td><td>Vertical</td><td>Total panels</td></tr><tr><td>1</td><td rowspan="3"> $A_{11}, B_{11}$ </td><td>1.00</td><td>0.80</td><td>44</td><td>10</td><td>10</td><td>1320</td></tr><tr><td>2</td><td>1.00</td><td>0.50</td><td>48</td><td>10</td><td>8</td><td>1344</td></tr><tr><td>3</td><td>0.20</td><td>0.25</td><td>48</td><td>10</td><td>8</td><td>1344</td></tr><tr><td>4</td><td></td><td>0.20</td><td>0.10</td><td>52</td><td>10</td><td>6</td><td>1352</td></tr><tr><td>5</td><td rowspan="4"> $A_{33}, B_{33}$ </td><td>1.00</td><td>0.75</td><td>52</td><td>10</td><td>8</td><td>1456</td></tr><tr><td>6</td><td>1.00</td><td>0.25</td><td>56</td><td>10</td><td>6</td><td>1456</td></tr><tr><td>7</td><td>0.20</td><td>0.90</td><td>48</td><td>8</td><td>15</td><td>1488</td></tr><tr><td>8</td><td>0.20</td><td>0.10</td><td>52</td><td>10</td><td>6</td><td>1352</td></tr></table>

In each of the 8 cases, computation is performed over 40 wave periods. Computation results for hydrodynamic coefficients against the dimensionless radius ka are given in Fig. 14, with respect to a variety of the cylinder radius a and the draft T. Added mass $( A _ { 1 1 }$ and $A _ { 3 3 } )$ is contributed by the real part of Green’s function, involving both the Rankine term and the Cauchy principal value of the complex integral as shown in Eq. (4). On the contrary, radiation damping $( B _ { 1 1 }$ and $B _ { 3 3 } )$ is contributed by the imaginary part of Green’s function, consisting of the residues of the complex integral in Eq. (4). From the comparison in Fig. 14, the results for added mass and radiation damping by the present numerical solver generally agree well with those of the multipole expansion method. The high agreements of added mass and radiation damping in all cases suggest excellent accuracy in the computation of the real part and the imaginary part of the Green’s function.

(a)  
![](images/0a1c58e5abeb88a7665d133b0e5cb222dfda722df4deff3dff7474e6c899eb79.jpg)

(b)  
![](images/e44895015f8d331551e685e96d9a1fbab65cd8533621dd25ba2a861350430808.jpg)  
(b) surge radiation damping for $a = 1 . 0$

(a) surge added mass for $a = 1 . 0$  
(c)  
![](images/b60c6bef339bac0caf68d333eb05df4c68e980727d3abd731f4ebfdd1606c5cb.jpg)

(d)  
![](images/c750dccfe77f06b1bb9647c91d1e4e4652544921aa13706e09c013b8533cac43.jpg)

(c) surge added mass for $a = 0 . 2$  
(e)  
![](images/0b41d9a75b39a6e6b6bdd15c70e64774a098e547111558955f1a18636d8973dc.jpg)  
(e) heave added mass for $a = 1 . 0$

(d) surge radiation damping for $a = 0 . 2$

(f)  
![](images/b36819894ced80e84c42437b6d49d2074e3c0e2fd736a15d7efa955f1224370f.jpg)  
(f) heave radiation damping for $a = 1 . 0$

(g)  
![](images/1cf0f4939f55b5f7c3f5864a3a81fe8c530e65c8886a6bbb1530d2a109ffccea.jpg)

(h)  
![](images/3231e20d2c8eb23f75a47caa7a03f8ec834ccf2386cb09617683881df7c1f6ad.jpg)  
(g) heave added mass for $a = 0 . 2$  
(h) heave radiation damping for $a = 0 . 2$  
Fig. 14. Added mass and radiation damping coefficients of a circular cylinder in various conditions, as a function of the normalized radius	Dq: (a) \~ (d) for surge coefficients and (e) \~ (h) for heave coefficients. Left column: added mass; Right column: radiation damping. Two different sizes of cylinders are used: $a = 1 . 0$ in (a), (b), (e) and (f); $a = 0 . 2$ in (c), (d), (g) and (h). “Yeung (1981)” denotes the analytical results of [59] calculated by the eigenfunction expansion method. “Present” denotes numerical results computed by the FinGreen3D & HAMS codes, using meshes specified in Table 5.

## 5.4 Case No.3: a semi-submersible offshore wind turbine with complex truss members

A triangular platform with complex geometry is served as the third testing case to show the capability of practical applications to the offshore renewable energy. The platform was initially designed for supporting multiple diffuser-augmented wind turbines in Kyushu University [60] at the $3 ^ { \mathrm { r d } }$ development phase, with a submerged volume $V = 2 1 2 0 \mathrm { m } ^ { 3 }$ . It has three stacked large compound columns at the corners of the platform to support the turbine towers, three long pontoons which connect the columns and a large number of small bracings strengthening the platform structure. More details of the semisubmersible are listed in Table 6. The present floating wind turbine system was designed to operate in a water depth of 70 m.

Table 6. Definition of the full-scale properties of the semisubmersible

<table><tr><td>Properties</td><td>Values</td></tr><tr><td>Diameter of the Upper Columns</td><td>4.00 m</td></tr><tr><td>Diameter of the Lower Columns</td><td>11.5 m</td></tr><tr><td>Diameter of the Pontoons</td><td>1.70 m</td></tr><tr><td>Diameter of the Bracings</td><td>0.60 m</td></tr><tr><td>Number of the Trussed Bracings</td><td>66</td></tr><tr><td>Distance between Compound Columns</td><td>90.0 m</td></tr><tr><td>Draft in Operation</td><td>10.0 m</td></tr><tr><td>Center of Gravity</td><td>(0, 0, 5.30 m)</td></tr><tr><td>Center of Buoyancy</td><td>(0, 0, -7.15 m)</td></tr><tr><td>Platform Displacement</td><td> $2.12 \times 10^{3} \text{m}^{3}$ </td></tr></table>

![](images/cc4a88d3d30b3cb39aaf92f2b44ca3660243413c4c1c5f184d98ea05d4250b2d.jpg)  
Fig. 15. Model test of the semi-submersible floating wind turbine in Kyushu University, Japan

![](images/d037ef96b16282e65d3cf16a67c0b6909c0d1dbadc92bb0f123ae15bdf498d85.jpg)  
Fig. 16. Mesh of the submerged part of the platform in altogether 5040 panels, with 4110 panels on the immersed body surface (in dark red color) and 930 panels on the water planes (in light blue color).

Table 7. Specifications of the grid divisions on members of the semi-submersible floating wind turbine

<table><tr><td rowspan="2">Mesh</td><td colspan="3">Main Columns</td><td colspan="3">Pontoons</td><td colspan="3">Bracings</td></tr><tr><td>Circumferential</td><td>Radial</td><td>Draft</td><td>Circumferential</td><td>Radial</td><td>Draft</td><td>Circumferential</td><td>Radial</td><td>Draft</td></tr><tr><td>Mesh 1</td><td>8</td><td>4</td><td>4</td><td>8</td><td>4</td><td>6</td><td>5</td><td>2</td><td>4</td></tr><tr><td>Mesh 2</td><td>12</td><td>4</td><td>4</td><td>8</td><td>4</td><td>10</td><td>8</td><td>2</td><td>5</td></tr><tr><td>Mesh 3</td><td>24</td><td>4</td><td>4</td><td>12</td><td>4</td><td>10</td><td>10</td><td>2</td><td>5</td></tr><tr><td>Mesh 4</td><td>30</td><td>6</td><td>6</td><td>15</td><td>4</td><td>12</td><td>10</td><td>2</td><td>5</td></tr></table>

A 1/50-scale model experiment has been conducted at the water tank of the Research Institute for Applied Mechanics (RIAM), Kyushu University, as displayed in Fig. 15. Added mass and radiation damping coefficients in heave motions are measured by the forced excitation test. Wave exciting forces are measured by fixing the model in the regular waves. Numerical computations are performed by incorporating and compiling the FinGreen3D & HAMS codes. First of all, a mesh grid convergent test is performed in association with a validation by the experimental measurement. The meshes are divided into four types as shown in Table 7, varying on the grid resolution of different members, from coarse meshes to fine meshes. A representative of the fine meshes is displayed in Fig. 16. Comparison between the numerical results and the model test data are given in Fig. 17, where the quantities are normalized by the water density ρ, the gravity acceleration g and the platform displaced volume V. The comparison shows that accuracy of the numerical results depends heavily on the grid resolution, especially in the gravity direction in the diffraction problem (or the heave mode in the radiation problem). As the grids become finer, the numerical results get closer to the experimental data. Generally, the agreement between the two results is satisfactory.

(a)  
![](images/bb920003bb2375ca25db48427e0431609e2b2f99567681b2d1ec47e61c324a95.jpg)

![](images/8fb35c73cea9c01d6343d52e69992b8584be76b5991cc914616d8854bbdef445.jpg)

(c)  
![](images/f9c266a896b295b4462af11674eb19b8a906a06457c4524f1ceb148ca96da653.jpg)

(d)  
![](images/fcb748bf1ce3158e4b84c57958ea383cf10e6910614daa7e33a4045f4e3846c0.jpg)  
Fig. 17. Wave forces upon the triangular platform as a function of the wave angular frequency	ä: (a) exciting force in the x-direction, (b) exciting force in the z-direction, (c) heave added mass, (d) heave radiation damping. “Mesh 1”, “Mesh $2 ^ { \circ }$ “Mesh 3” and “Mesh $4 ^ { \dag }$ denote numerical results computed by the FinGreen3D & HAMS codes, using meshes specified in Table 7. Solid dot denotes experiment data measured from the tank model test.

Fig. 18 shows contour plots of the scattered free surface elevation (normalized by the incident wave amplitude) in the vicinity of the platform in which the waves incident from different directions. As shown in Figs. 18(a) and (b), when the waves incident at a lower wave frequency, the scattered wave fields are relatively flat. In other words, the free surface has not been changed noticeably by the scattered waves. That is because waves of a large wavelength can easily transmit over a floating ‘obstacle’ of a smaller dimension. The elevations at a relative higher wave frequency are shown in Figs. 18(c) and (d), where the wavelength is more comparable to the physical dimension of the platform. In Fig. 18(c), the wave field is symmetric because of the symmetry of the platform with respect to the wave incident direction. In Fig. 18(d), with an incident angle of $\beta = 9 0 ^ { \circ }$ the side of the platform in y-direction experiences a standing-wave-like wave field. The free surface elevation varies sharply along the incident wave direction, until the uppermost column in this direction. This should mainly be attributed to the reflection of the incident waves by the main columns along the side of the platform, and the superposition of the two waves with a nearly equivalent phase. In addition, it can be noticed that the largest enhancement of the elevation always occurs at the neighborhood of the three large compound columns, regardless of the wave frequency and direction, showing that the diameter of the column is the main factor of diffraction. As the waves go far away from the structure, the amplitude of elevation decreases substantially, which agrees with our knowledge in common practice.

![](images/a91b3033a33b72f2816dcaa9464d71109578c1ac10036b517db4880cc709f912.jpg)

![](images/1e0f6ba5c1f1fcf49b5dc09d6bd658248cb1ad9df6b52ff67f506fba97cf6d87.jpg)

![](images/3e9f4cd3997bf323f208e94f291f6102c229a9ad6e7518577a49349d9b51c190.jpg)

(d)  
![](images/8923cba4cba48bbb31c7e9181683a03a0bce2fbf29078ae89ed01758aa53db90.jpg)  
Fig. 18. Contour plot of free surface elevation (normalized by the incident wave amplitude) in the following conditions: (a) $\beta = 0 ^ { \circ } , \omega = 0 . 1$ , (b) , (c) $\beta = 0 ^ { \circ } , \omega = 0 . 3$ , and (d) $\beta = 9 0 ^ { \circ } , \omega = 0 . 3$ . The upper column shows the free-surface elevation for a low-frequency incident wave, while the bottom column shows the free-surface elevation for a high-frequency incident wave.

## 5.5 Case No.4: a next-generation floating wind turbine moored by single-point turret system

A new-type SCD®-nezzy offshore floating wind turbine is used as the fourth testing case, as shown in Fig. 19. The two-bladed floating wind turbine has the ability of self-aligning with the change of wind direction, attributed to the latest technologies of an airfoil-shaped leaning tower and a single-point turret system. Its Yshaped floating foundation consists of three separate leaning columns, three horizontal pontoons, and a center column being also the lower part of the tower. The spreading mooring lines are allocated to a single fairlead at the end of the Y-shaped foundation which has a torsional degree of freedom. The floating wind turbine is designed to operate in a water depth of 52 m, at the coastal area of Japan. More details of the SCD®-nezzy floating wind turbine are listed in Table 8.

Table 8. Hydrostatic properties of the SCD®-nezzy floater

<table><tr><td>Properties</td><td>Values</td></tr><tr><td>Displacement</td><td>5210.00  $m^{3}$ </td></tr><tr><td>Total Draft</td><td>14.75 m</td></tr><tr><td>Area of the Immersed Body Surface</td><td>3678.17  $m^{2}$ </td></tr><tr><td>Inner Water Plane Area</td><td>144.69  $m^{2}$ </td></tr><tr><td>Equivalent Floating Body Roll Inertia</td><td> $2.9206 \times 10^{9} \text{ kg.m}^{2}$ </td></tr><tr><td>Equivalent Floating Body Pitch Inertia</td><td> $4.3879 \times 10^{9} \text{ kg.m}^{2}$ </td></tr><tr><td>Equivalent Floating Body Yaw Inertia</td><td> $5.8750 \times 10^{9} \text{ kg.m}^{2}$ </td></tr><tr><td>Hydrodynamic Restoring in Heave</td><td> $1.4549 \times 10^{6} \text{ N/m}$ </td></tr><tr><td>Hydrodynamic Restoring in Roll</td><td> $1.6258 \times 10^{8} \text{ Nm/rad}$ </td></tr><tr><td>Hydrodynamic Restoring in Pitch</td><td> $5.1859 \times 10^{8} \text{ Nm/rad}$ </td></tr></table>

![](images/b8bd1c9e059e4a5fa21cb954cf96bcdc02b7022c24bdcbceff9bbc8820522c0c.jpg)  
Fig. 19. Schematic of the SCD®-nezzy floating wind turbine [20]

![](images/cec9e79796a1c43c3efa8999403b759382f50087e448f190d08de205d3a04d07.jpg)  
Fig. 20. Mesh of the SCD®-nezzy floater: (a) perspective view of the entire floater and (b) local bottom view of the turret mooring point

The floating foundation is discretized by a pretty fine mesh, with the consideration of the wave orbital trajectory and the local details, as displayed in Fig. 20. Since the circular orbits of the water particles decrease with the increase of the immersion depth in water, and decrease to zero if the immersion depth exceeds half wavelength, the mesh grid density is specifically generated to be the largest in the region close to the mean sea level and decreasing with the depth. In addition, since at the turret mooring point the structure geometry has a complex local detail, the mesh grid there is intentionally generated to be denser than its neighboring areas, as shown in Fig. 20(b).

(a)  
![](images/badd8ce2633dc718881fd61a8999c6185043cbe812310c5142d0cd01ec6739ec.jpg)

(b)  
![](images/9662ece1f565d2654bfc4a879f25ad98010f7f8bd005651fd55809cb6cb029e5.jpg)

(c)  
![](images/e42003fda25c47c17c722663c1ddbf9f39b0293f37042c68ccc124888d81eebd.jpg)  
Fig. 21. Modulus of the wave excitation force/moment acting on the SCD®-nezzy floater as a function of the wave angula frequency ω: (a) surge wave excitation force, (b) heave wave excitation force, and (c) pitch wave excitation moment.

Fig. 21 shows the distribution of wave excitation force/moment on the SCD®-nezzy floater with respect to the wave angular frequency and wave headings. It is seen that due to the symmetry of the SCD®-nezzy floater, the distributions are symmetric with respect to the line of wave heading $\beta = 9 0 ^ { ^ { \circ } }$ . Note that there are several major regions where the floater is attacked heavily by the wave force/moment. For the surge wave force, the maximum value occurs at the places of $0 ^ { \circ } < \beta < 4 0 ^ { \circ }$ $1 4 0 ^ { \circ } < \beta < 1 8 0 ^ { \circ }$ and $0 . 8 < \omega < 1 . 6$ . For the heave wave force, the maximum value occurs at two major places, i.e., the small band $0 < \omega < 0 . 2$ and the region in the neighborhood of the peak at $\beta = 9 0 ^ { ^ { \circ } }$ and $\omega = 0 . 6 5$ . For the pitch wave moment, the maximum value occurs in the frequency band $0 . 5 < \omega < 1 . 5$ , and near the wave heading $\beta = 9 0 ^ { ^ { \circ } }$ as well as the regions of $0 ^ { \circ } < \beta <$ $4 0 ^ { \circ }$ ， $1 4 0 ^ { \circ } < \beta < 1 8 0 ^ { \circ }$ . Outputting such distributions of wave excitation force/moment has significant meanings to the design of such floaters in practice.

(a)  
![](images/68b0ca375f0bffaf7509fa40e27cd4abd92541df5786e157e1c2f97956110a23.jpg)

(b)  
![](images/497b9ea28d5888de47e55e036daedac36564ecf0ed6620681f514e835d24d331.jpg)

(c)  
![](images/c6651a5208adaf5312c88ca0a5a2853c3682c3c9e6b7c9e97a550deaa57356e3.jpg)  
Fig. 22. Motion response of SCD®-nezzy floating wind turbine, as a function of the wave angular frequency ω: (a) surge response; (b) heave response; and (c) pitch response. The results denoted by symbols are computed by the commercial version of the Hydrostar® software.

Fig. 22 shows the analysis of response amplitude operators (RAOs) on the motions of the SCD®-nezzy floating wind turbine, and a comparison between the present results and those computed by the commercial software Hydrostar®. The motion RAOs are measured by the motion response amplitude over the incident wave amplitude. In order to show clearly the differences, the data are plotted using the semi-logarithmic coordinate. It is seen that, except for some small differences which are hard to distinguish, the two results coincide perfectly well with each other. The peaks at the resonance region (0.0<ω<0.5) predicted by the two software are also in quite good agreements. The motion RAOs generally decrease with the increase of the wave angular frequency, to a negligible level when the wave angular frequency exceeds 2.0. This is also in consistency with the energy distribution in the ocean spectrums, e.g., Jonswap spectrum, Pierson–Moskowitz spectrum, etc., which almost concentrates within the angular frequency band of [0, 2.0].

## 6. Conclusions

A reliable numerical software package - FinGreen3D has been presented, using a region-decomposition strategy for evaluation of the free-surface Green’s function in moderate depth, which is widely considered as the essential part but is difficult to be calculated in the analysis of wave-structure interactions. An advantage of the present method is that although it needs a lower computational cost than the computational fluid dynamics (CFD) methods thanks to its fast evaluation speed, it still preserves a high accuracy of computation. The present method is appropriate for large-scale floating structures on the purpose of quickly evaluating their integral performance with respect to a batch of input environmental conditions/parameters. The package is written in Fortran 90 with optimized structure and can be implemented on either Windows or Linux. The package structure and its interface have been clearly illustrated so as to make it well understandable by the reader/user. The accuracy and efficiency of the present software package have been confirmed by extensive validations.

The software package code can be distributed freely for either academic research or industrial application purpose. Acknowledgment is appreciated to be addressed by properly citing this paper in the relevant publications.

## Acknowledgment

The financial support from the Grant-in-Aid for Early-Career Scientists (JSPS KAKENHI Grant Number JP18K13939), the Open Research Fund (Grant Number LP1815) of the State Key Laboratory of Coastal and Offshore Engineering (SKLCOE) of Dalian University of Technology and the Overseas Collaborative Research Program (Grant Number PJT-8) of the Japan Society of Naval Architects and Ocean Engineers (JASNAOE) are gratefully acknowledged. The verification, Case 4 was conducted in “Next Generation Floating Offshore Wind Turbine System Demonstration Project (Elemental Technologies)” of New Energy and Industrial Technology Development Organization (NEDO), 2016-18. The first author would also like to acknowledge the financial support from the MEXT Scholarship (Grant Number 123471) provided by the Japanese Government during his three-year Ph.D. research.

## Appendix I: Download Instructions

The software package - FinGreen3D is released open-publicly on Mendeley and GitHub. The Mendeley release is the first (original) release of the FinGreen3D package and can be freely downloaded via the link: https://data.mendeley.com/datasets/pkyvcfgv82/1. The subsequent future versions can be tracked via its GitHub site: https://github.com/liuyingyi-ukyushu/FinGreen3D. Tutorials have been given under the ‘Test\_ Examples folder to illustrate how to use the package. Makefiles have also been supplied for its easy compilation on Windows or Linux.

## Appendix II: Program summary

Program title: FINGREEN3D

Licensing provisions: LGPL, Version 3.0, https://www.gnu.org/licenses/lgpl-3.0.html

No. of subroutines in distributed program: 48

No. of lines in distributed program, including test data, etc.: 4727

No. of bytes in distributed program, including test data, etc.: 219036

Distribution format: tar.gz

Programming language: Fortran 90.

Computer: Laptop PC/Workstation/HPC cluster.

Operating system: Windows/Linux.

## Nature of the problem:

Calculation of the source potential influence at point x due to an oscillating source of strength −4π located at the point ξ, in the presence of ocean waves.

## Potential application fields:

The numerical package can be applied in combination with a potential flow solver to simulate wave interactions with offshore renewable energy devices, e.g., offshore wind turbine, wave energy converter, and etc.

## Running time:

One typical sequential call of the driver subroutine takes averagely 2\~4 µs for each frequency on a single thread on Windows 64-bit system with an Intel (R) Core (TM) i7-2670QM 2.2Hz CPU.

## References

[1] Kammen DM, Sunter DA. City-integrated renewable energy for urban sustainability. Science 2016; 352: 922-928. DOI: 10.1126/science.aad9302

[2] Colmenar-Santos A, Perera-Perez J, Borge-Diez D. Offshore wind energy: A review of the current status, challenges and future development. Renewable and Sustainable Energy Reviews 2016; 64: 1-18. DOI: 10.1016/j.rser.2016.05.087

[3] Lehmann M, Karimpour F, Goudey CA, Jacobson PT, Alam MR. Ocean wave energy in the United States: Current status and future perspectives. Renewable and Sustainable Energy Reviews 2017; 74: 1300-1313. DOI: 10.1016/j.rser.2016.11.101

[4] Khan N, Kalair A, Abas N, Haider A. Review of ocean tidal, wave and thermal energy technologies. Renewable and Sustainable Energy Reviews 2017; 72: 590-604. DOI: 10.1016/j.rser.2017.01.079

[5] Vazquez A, Iglesias G. A holistic method for selecting tidal stream energy hotspots under technical, economic and functional constraints. Energy Conversion and Management 2016; 117: 420-430. DOI: 10.1016/j.enconman.2016.03.012

[6] Pavković D, Cipek M, Hrgetić M, Sedić A. Modeling, parameterization and damping optimum-based control system design for an airborne wind energy ground station power plant. Energy Conversion and Management 2018, 164, 262-276. DOI: 10.1016/j.enconman.2018.02.090

[7] Bontempo R, Manna M. The axial momentum theory as applied to wind turbines: some exact solutions of the flow through a rotor with radially variable load. Energy Conversion and Management 2017; 143: 33-48. DOI: 10.1016/j.enconman.2017.02.031

[8] Liu Y, Yoshida S. An extension of the Generalized Actuator Disc Theory for aerodynamic analysis of the diffuser-augmented wind turbines. Energy 2015; 93: 1852-1859. DOI: 10.1016/j.energy.2015.09.114

[9] Elhanafi A, Macfarlane G, Fleming A, Leong Z. Experimental and numerical investigations on the hydrodynamic performance of a floating–moored oscillating water column wave energy converter. Applied Energy 2017; 205: 369-390. DOI: 10.1016/j.apenergy.2017.07.138

[10] Wu J, Yao Y, Zhou L, Chen N, Yu H, Li W, Göteman M. Performance analysis of solo Duck wave energy converter arrays under motion constraints. Energy 2017; 139: 155-169. DOI: 10.1016/j.energy.2017. 07.152

[11] Ramos V, López M, Taveira-Pinto F, Rosa-Santos P. Performance assessment of the CECO wave energy converter: Water depth influence. Renewable Energy 2018, 117, 341-356. DOI: 10.1016/j.renene.2017.10.064

[12] Ning DZ, Wang RQ, Zou QP, Teng B. An experimental investigation of hydrodynamics of a fixed OWC Wave Energy Converter. Applied Energy 2016; 168: 636-648. DOI: 10.1016/j.apenergy.2016.01.107

[13] Benitz MA, Lackner MA, Schmidt DP. Hydrodynamics of offshore structures with specific focus on wind energy applications. Renewable and Sustainable Energy Reviews 2015; 44: 692-716. DOI: 10.1016/j.rser.2015.01.021

[14] Liu Y, Li S, Yi Q, Chen D. Developments in semi-submersible floating foundations supporting wind turbines: A comprehensive review. Renewable and Sustainable Energy Reviews 2016; 60: 433-449. DOI: 10.1016/j.rser.2016.01.109

[15] Oh KY, Nam W, Ryu MS, Kim JY, Epureanu BI. A review of foundations of offshore wind energy convertors: Current status and future perspectives. Renewable and Sustainable Energy Reviews 2018; 88:16- 36. DOI: 10.1016/j.rser.2018.02.005

[16] Astariz S, and Iglesias G. Selecting optimum locations for co-located wave and wind energy farms. Part II: A case study. Energy Conversion and Management 2016; 122: 599-608. DOI: 10.1016/j.enconman.2016. 05.078

[17] Skaare B, Nielsen FG, Hanson TD, Yttervik R, Havmøller O, Rekdal A. Analysis of measurements and simulations from the Hywind Demo floating wind turbine. Wind Energy 2015; 18(6): 1105-1122. DOI: 10.1002/we.1750

[18] Roddier D, Cermelli C, Aubault A, and Weinstein A. WindFloat: A floating foundation for offshore wind turbines. Journal of Renewable Sustainable Energy 2010; 2(3): 033104. DOI: 10.1063/1.3435339

[19] Koh JH, Ng EYK, Robertson A, Jonkman J, Driscoll F. Validation of a FAST Model of the SWAY Prototype Floating Wind Turbine (No. NREL/TP--5000-61744). National Renewable Energy Lab. (NREL), Golden, CO (United States); 2016. DOI: 10.2172/1259950

[20] SCD®-nezzy Website http://www.scd-technology.com/scd-technology-scd-nezzy/

[21] SeaTwirl Website https://seatwirl.com/products/

[22] Yemm R, Pizer D, Retzler C, Henderson R. Pelamis: experience from concept to connection. Proceedings of The Royal Society A: Mathematical, Physical and Engineering Sciences 2012; 370(1959): 365-380. DOI: 10.1098/rsta.2011.0312

[23] Cordonnier J, Gorintin F, De Cagny A, Clément AH, Babarit A. SEAREV: Case study of the development of a wave energy converter. Renewable Energy 2015; 80: 40-52. DOI: 10.1016/j.renene.2015.01.061

[24] BlueTEC Texel Prototype Website http://www.bluewater.com/new-energy/texel-project/

[25] WINFLO News https://theecologist.org/2015/nov/11/floating-platforms-offshore-wind-cost-set-plunge

[26] WaveStar Website http://wavestarenergy.com/concept

[27] Lee CH. WAMIT Theory Manual: MIT Report 95-2. Dept. of Ocean engineering, Massachusetts Institute of Technology, Cambridge, MA; 1995.

[28] Li Y, Yu YH. A synthesis of numerical methods for modeling wave energy converter-point absorbers. Renewable and Sustainable Energy Reviews 2012; 16(6): 4352-4364.

[29] Mei CC, Stiassnie M, Yue DKP. Theory and applications of ocean surface waves: nonlinear aspects. World scientific; 2005.

[30] Newman JN. Algorithms for free-surface Green function. Journal of Engineering Mathematics 1985; 19: 57-67. DOI: 10.1007/BF00055041

[31] Telste JG, Noblesse F. Numerical evaluation of the Green function of water-wave radiation and diffraction. Journal of Ship Research 1986; 30: 69-84.

[32] Chakrabarti SK. Application and verification of deepwater Green function for water waves. Journal of Ship Research 2001; 45: 187-196.

[33] Wu H, Zhang C, Zhu Y, Li W, Wan D, Noblesse F. A global approximation to the Green function for diffraction radiation of water waves. European Journal of Mechanics-B/Fluids 2017; 65; 54-64. DOI: 10.1016/j.euromechflu.2017.02.008

[34] Pidcock MK. The calculation of Green functions in three dimensional hydrodynamic gravity wave problems. International Journal for Numerical Methods in Fluids 1985; 5: 891-909. DOI: 10.1002/fld.1650051004

[35] Cuer M. Computation of a Green's function for the three-dimensional linearized transient gravity waves problem. IMPACT of Computing in Science and Engineering 1989; 1: 313-325. DOI: 10.1016/0899- 8248(89)90015-3

[36] Linton CM. Rapidly convergent representations for Green functions for Laplace's equation. Proceedings of The Royal Society A: Mathematical, Physical and Engineering Sciences 1999; 455: 1767-1797. DOI: 10.1098/rspa.1999.0379

[37] Ewald P. Die berechnung optischer und electrostatischer gitterpotentiale. Annalen der Physik 1921; 369: 253-287. DOI: 10.1002/andp.19213690304

[38] Chen XB. Hydrodynamics in offshore and naval applications - Part I. In: Proc. Of the 6th Intl. Conf. Hydrodynamics, Perth, Australia; 2004.

[39] John F. On the motion of floating bodies II. Communications on Pure and Applied Mathematics 1950; 3: 45-101. DOI: 10.1002/cpa.3160030106

[40] Newman JN. Numerical solutions of the water-wave dispersion relation. Applied Ocean Research 1990; 12: 14-18. DOI: 10.1016/S0141-1187(05)80013-6

[41] Newman JN. Distributions of sources and normal dipoles over a quadrilateral panel. Journal of Engineering Mathematics 1986; 20: 113-126. DOI: 10.1007/BF00042771

[42] Wynn P. On a Device for Computing the em(Sn) Transformation. Mathematics of Computation 1956; 10(54): 91-96. <http://www.ams.org/journals/mcom/1956-10-054/S0025-5718-1956-0084056-6/S0025-5718- 1956-0084056-6.pdf>

[43] Mishonov T, Penev E. Thermodynamics of Gaussian fluctuations and paraconductivity in layered superconductors. Int. J. Mod. Phys. B 2000; 14: 3831-3879. DOI: 10.1142/S0217979200001680

[44] Newman JN. The approximation of free-surface Green functions. Retirement Meeting for Professor Fritz Ursell, University of Manchester, published in “Wave Asymptotics” edited by Martin PA and Wickham GR, pp. 107-135. Cambridge University Press, Cambridge; 1992.

[45] Liu Y, Gou Y, Teng B, Yoshida S. An Extremely Efficient Boundary Element Method for Wave Interaction with Long Cylindrical Structures Based on Free-Surface Green’s Function. Computation 2016; 4(3): 36. DOI: 10.3390/computation4030036

[46] Linton CM, McIver P. Handbook of mathematical techniques for wave/structure interactions. London: Chapman and Hall/CRC Press; 2001.

[47] Liu Y, Iwashita H, Hu C. A calculation method for finite depth free-surface green function. International Journal of Naval Architecture and Ocean Engineering 2015; 7: 375-389. DOI: 10.1515/ijnaoe-2015-0026

[48] Sun L, Teng B, Liu CF. Removing irregular frequencies by a partial discontinuous higher order boundary element method. Ocean Engineering 2008; 35: 920-930. DOI: 10.1016/j.oceaneng.2008.01.011

[49] Zhang S, Jin JM. Computation of special functions. Wiley-Interscience; 1996.

[50] Liu Y, Hu C, Sueyoshi M, Iwashita H, Kashiwagi M. Motion response prediction by hybrid panel-stick models for a semi-submersible with bracings. Journal of Marine Science and Technology 2016; 21(4): 742- 757. DOI: 10.1007/s00773-016-0390-1

[51] Vicente PC, Falcão AF, Justino PA. Nonlinear dynamics of a tightly moored point-absorber wave energy converter. Ocean engineering 2013; 59: 20-36. DOI: 10.1016/j.oceaneng.2012.12.008

[52] Sergiienko NY, Cazzolato BS, Ding B, Hardy P, Arjomandi M. Performance comparison of the floating and fully submerged quasi-point absorber wave energy converters. Renewable Energy 2017; 108: 425-437. DOI: 10.1016/j.renene.2017.03.002

[53] Bharath A, Nader JR, Penesis I, Macfarlane G. Nonlinear hydrodynamic effects on a generic spherical wave energy converter. Renewable Energy 2018; 118: 56-70. DOI: 10.1016/j.renene.2017.10.078

[54] Linton CM. Radiation and diffraction of water waves by a submerged sphere in finite depth. Ocean Engineering 1991; 18: 61-74. DOI: 10.1016/0029-8018(91)90034-N

[55] Wang YL. Design of a cylindrical buoy for a wave energy converter. Ocean Engineering 2015; 108: 350- 355. DOI: 10.1016/j.oceaneng.2015.08.012

[56] Wang X, Zeng X, Yang X, Li J. Feasibility study of offshore wind turbines with hybrid monopile foundation based on centrifuge modeling. Applied Energy 2018; 209: 127-139. DOI: 10.1016/j.apenergy.2017.10.107

[57] Xu D, Stuhlmeier R, Stiassnie M. Assessing the size of a twin-cylinder wave energy converter designed for real sea-states. Ocean Engineering 2018; 147: 243-255. DOI: 10.1016/j.oceaneng.2017.10.012

[58] Garret CJR. Wave forces on a circular dock. Journal of Fluid Mechanics 1971; 46: 129-139. DOI: 10.1017/S0022112071000430

[59] Yeung RW. Added mass and damping of a vertical cylinder in finite-depth waters. Applied Ocean Research 1981; 3: 119-133. DOI: 10.1016/0141-1187(81)90101-2

[60] Hu C, Sueyoshi M, Liu C, Liu Y. Hydrodynamic analysis of a semi-submersible type floating wind turbine. In: Proc. of the Eleventh ISOPE Pacific/Asia Offshore Mechanics Symposium, Shanghai, China; 2014. < http://www.isope.org/publications/jowe/jowe-01-4/jowe-01-4-p202-jcr16-hu.pdf >