## Accepted Manuscript

A global approximation to the Green function for diffraction radiation of water waves

Huiyu Wu, Chenliang Zhang, Yi Zhu, Wei Li, Decheng Wan, Francis Noblesse

![](images/4b6a80776fd1aab804fa478370cf9f8a14f16816c2820df0d55e59ef8382e6f4.jpg)

PII: S0997-7546(16)30506-4

DOI: http://dx.doi.org/10.1016/j.euromechflu.2017.02.008

Reference: EJMFLU 3143

To appear in: European Journal ofMechanics B/Fluids

Received date: 27 October 2016

Please cite this article as: H. Wu, C. Zhang, Y. Zhu, W. Li, D. Wan, F. Noblesse, A global approximation to the Green function for diffraction radiation of water waves, European Journal ofMechanics B/Fluids (2017), http://dx.doi.org/10.1016/j.euromechflu.2017.02.008

This is a PDF file of an unedited manuscript that has been accepted for publication. As a service to our customers we are providing this early version of the manuscript. The manuscrip will undergo copyediting, typesetting, and review of the resulting proof before it is published in its final form. Please note that during the production process errors may be discovered which could affect the content, and all legal disclaimers that apply to the journal pertain.

# A global approximation to the Green function for difraction radiation of water waves

Huiyu Wu, Chenliang Zhang, Yi Zhu, Wei Li, Decheng Wan, Francis Noblesse∗

State Key Laboratory of Ocean Engineering,

Collaborative Innovation Centerfor Advanced Ship and Deep-Sea Exploration,

School of Naval Architecture, Ocean & Civil Engineering, Shanghai Jiao Tong University, Shanghai, China

## Abstract

The Green function of the theory of difraction radiation of time-harmonic (regular) waves by an ofshore structure, or a ship at low speed, in deep water is considered. The Green function G and its gradient G are expressed in the usual manner as the sum of three components that correspond to the fundamental free-space singularity, a non-oscillatory local flow, and waves. Simple approximations that only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments are given for the local flow components in G and G. These approximations are global approximations valid within the entire flow region, rather than within complementary contiguous regions as can be found in the literature. The analysis of the errors associated with the approximations to the local flow components given in the study shows that the approximations are suficiently accurate for practica purposes. These global approximations provide a particularly simple and highly eficient way of numerically evaluating the Green function and its gradient for difraction radiation of time-harmonic waves in deep water.

Keywords: regular water waves, difraction radiation, Green function, local flow, global approximation

## 1. Introduction

Difraction radiation of time-harmonic water waves by an ofshore structure within the classical framework of linear potential flow theory and the Green function method is routinely used to predict added-mass and wave-damping coeficients, mo tions, and wave loads. Wave difraction radiation by a ship that advances in ambient waves at low forward speed is also often analyzed using the zero-speed Green function at the encounter frequency. This Green function, which represents the velocity potential due to a pulsating source at a singular point under the free surface as is well known, is an essential element of the the ory of wave difraction radiation. Accordingly, the Green function has been studied in a broad literature, e.g. Havelock [1, 2], Thorne [3], Haskind [4], Wehausen [5], Kim [6], Noblesse [7], especially for the simplest case of deep water that is considered here.

The Green function G can be expressed as the sum of the fundamental free-space singularity and a flow component that accounts for free-surface efects. Moreover, this free-surface component is commonly decomposed into a wave component W that represents the waves radiated by the pulsating source, and a non-oscillatory local flow component L. This basic decomposition into a wave component and a local flow component is not unique. Indeed, three alternative decompositions and related single-integral representations of the Green function G are given in Noblesse [7].

Several alternative mathematical representations and approximations of G and G that are well suited for numerical evaluation can be found in the literature. In particular, complementary near-field and far-field asymptotic expansions and Taylor series are given in Noblesse [7], Martin [8] and Telste & Noblesse [9]. Several practical approximate methods for computing G and G have also been given. These alternative methods include polynomial approximations within complementary contiguous flow regions, given in Newman [10, 11], Chen [12, 13], Wang [14] and Zhou et al. [15], and table interpolation associated with function and coordinate transformations, given in Ba et al. [16] and Ponizy et al. [17]. Other useful practical methods can be found in the literature, notably in Peter & Meylan [18], Yao et al. [19], D’el´ıa et al. [20] and Shen et al. [21].

Accuracy and eficiency are essential requirements of meth ods for numerically evaluating G and G, and these important aspects are considered in the practical approximate methods listed in the foregoing. Indeed, the alternative methods proposed in these studies provide accurate and eficient methods for computing G and G.

Numerical errors associated with potential-flow panel meth ods stem from several well-known sources, including:

(i) discretization of the wetted hull surface of an ofshore structure or a ship; i.e. the number and the type (flat or curved) of panels,

(ii) approximation of the variations (piecewise constant, lin ear, quadratic, or higher-order) of the densities of the singularity (source, dipole) distributions over a surface panel,

(iii) numerical integration of the Green function and its gra dient over a (flat or curved) panel, and

(iv) numerical approximation of the Green function and its gradient.

Moreover, the Green function G (as well as its gradient G) is given by the sum of the fundamental free-space singularity, a wave component W and a non-oscillatory local flow component L, as was already noted. Thus, numerical errors that stem from the approximations of the local flow components in the representations of G and G are only one part among several sources of errors associated with panel methods. While ideal approxi mations to G and G should be highly accurate and eficient as well as very simple, this ideal goal is hard to reach in prac tice because accuracy, eficiency and simplicity are competing requirements.

The level of accuracy that is actually required for useful practical approximations to G and G therefore is a fairly complicated issue. This issue is partly considered in Wu et al. [22] for the similar theory of steady ship waves (linear potential flow around a ship hull that advances at a constant speed in calm water). Specifically, the errors due to a simple analytical approximation to the local flow component L in the Green function for steady ship waves are considered in that study. This approximate local flow component $L ,$ given in Noblesse et al. [23], is very simple and highly eficient, but not particularly accurate. Yet, this simple relatively crude approximation to the Green function for steady ship waves is found in Wu et al. [22] to yield predictions of sinkage, trim and drag that do not difer appreciably from the predictions obtained if the Green function is computed with high accuracy. This finding suggests that highly accurate approximations to the local flow components in the Green function G and its gradient G for the theory of wave difraction radiation similarly may not be necessary for many practical purposes.

Simple approximations to the local flow components in the representations of G and G for wave difraction radiation are given here. These approximations are based on a pragmatic hybrid approach that combines numerical approximations with near-field and far-field analytical expansions, in a manner similar to that used in Noblesse et al. [23] for the Green function of the theory of ship waves. The approximations obtained here are valid within the entire flow region, i.e. are global approximations, unlike the approximations for complementary contiguous regions given in the literature. The approximations to the loca flow components given here only involve elementary continu ous functions (algebraic, exponential, logarithmic) of real arguments, and provide an eficient and particularly simple method for numerically evaluating the Green function G, and its gra dient G, for difraction radiation of time-harmonic waves in deep water. The global approximations to the local flow com ponents in G and G given here are similar to, but considerably more accurate than, the approximations given in Wu et al. [24].

## 2. Basic integral representations

A Cartesian system of coordinates $\mathbf { X } \equiv ( X , Y , Z )$ is used. The Z axis is vertical and points upward, and the undisturbed free surface is taken as the plane $Z = 0$ . Difraction radiation of time harmonic waves with radian frequency ω and wavelength $\lambda = 2 \pi g / \omega ^ { 2 }$ , where $g$ denotes the gravitational acceleration, is considered. Nondimensional coordinates

$$
\mathbf {x} \equiv (x, y, z) \equiv (X, Y, Z) \omega^ {2} / g\tag{1}
$$

are defined.

The Green function $G ( \mathbf { x } , \tilde { \mathbf { x } } )$ corresponds to the spatial com ponent of a nondimensional velocity potential

$$
\operatorname{Re} \left[ G (\mathbf {x}, \tilde {\mathbf {x}}) e ^ {- \mathrm{i} \omega T} \right]\tag{2}
$$

![](images/1b7f5482a68c1eccf3f872b236ff5331cd4aa717b4ca49c6b5ca74d46da3aab9.jpg)  
Figure 1: Definition sketch.

where T denotes time. Expression (2) represents the potential of the flow created at the point $\mathbf { x } \equiv ( x , y , z \le 0 )$ by a pulsating source located at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } < 0 )$ , or by a flux through the free surface at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } = 0 )$ . Specifically, Noblesse [7, 25] show that the Green function satisfies the equations

$$
\left. \begin{array}{l} \nabla^ {2} G = \delta (x - \tilde {x})   \delta (y - \tilde {y})   \delta (z - \tilde {z})    \text { in }    z <   0 \\ G _ {z} - G = 0    \text { on }    z = 0 \end{array} \right\}    \text { if }    \tilde {z} <   0\tag{3a}
$$

$$
\left. \begin{array}{l} \nabla^ {2} G = 0 \text {in} z <   0 \\ G _ {z} - G = - \delta (x - \tilde {x})   \delta (y - \tilde {y}) \text {on} z = 0 \end{array} \right\} \text {if} \tilde {z} = 0\tag{3b}
$$

where $\delta ( \cdot )$ stands for the usual Dirac delta function, and $G _ { z }$ is the z-derivative of the Green function $G$

The nondimensional distances between the flow-field point x and the source point x˜ or its mirror image $\tilde { \mathbf { x } } _ { 1 } \equiv ( \tilde { x } , \tilde { y } , - \tilde { z } )$ with respect to the undisturbed free-surface plane $z = 0$ are denoted as r and $d ,$ as is shown in Fig.1, and are given by

$$
r \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2} + (z - \tilde {z}) ^ {2}}\tag{4a}
$$

$$
d \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2} + (z + \tilde {z}) ^ {2}}\tag{4b}
$$

The horizontal and vertical components of the distance $d$ between the points x and $\tilde { \mathbf { X } } _ { 1 }$ are given by

$$
0 \leq h \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2}} \text { and } v \equiv z + \tilde {z} \leq 0\tag{5}
$$

The Green function G is expressed as

$$
4 \pi G = - 1 / r + L + W\tag{6}
$$

where $- 1 / r$ is the fundamental free-space Green function, and L and W represent a local flow component and a wave component that account for free-surface efects. The component L corresponds to a non-oscillatory local flow and the component W represents circular surface waves radiated by the pulsating singularity located at the source point $\tilde { \mathbf { x } } .$ . The basic decomposition (6) into a local flow and waves is non unique, as was already noted. Indeed, three alternative decompositions and related integral representations are given in Noblesse [7].

![](images/b91159a1a89d1ce6fdf1c43adba2268a0b50b71c1366ec964efe4b1f10eb210f.jpg)  
Figure 2: Functions H<sub>0</sub>(h), H<sub>1</sub>(h) 2/π, J<sub>0</sub>(h), J<sub>1</sub>(h) for $0 \leq h \leq 2 5$

The so-called near-field integral representation in Noblesse [7] is considered here. The wave component W in this representation is given by

$$
W (h, v) \equiv 2 \pi [ \widetilde {H} _ {0} (h) - \mathrm{i} J _ {0} (h) ] e ^ {v}\tag{7}
$$

where $\widetilde { H } _ { 0 } ( \cdot )$ and $J _ { 0 } ( \cdot )$ denote the zeroth-order Struve function eand the zeroth-order Bessel function of the first kind. The corresponding local flow component L is given by

$$
L (h, v) \equiv - \frac {1}{d} - \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \operatorname{Re} e ^ {M} E _ {1} (M) d \theta \text {   where   } M \equiv v + \mathrm{i} h \cos \theta\tag{8}
$$

and $E _ { 1 } ( \cdot )$ is the usual complex exponential integral function.

The gradient $\nabla G \equiv ( G _ { x } , G _ { y } , G _ { z } )$ of the Green function G is expressed in Noblesse [7] as

$$
4 \pi G _ {z} \equiv \frac {z - \tilde {z}}{r ^ {3}} + L _ {z} + W \text {where} L _ {z} = \frac {v}{d ^ {3}} - \frac {1}{d} + L\tag{9a}
$$

$$
4 \pi G _ {h} \equiv \frac {h}{r ^ {3}} + L _ {h} + W _ {h} \text {where} L _ {h} = \frac {h}{d ^ {3}} + L _ {*}\tag{9b}
$$

$$
4 \pi G _ {x} \equiv G _ {h} \frac {x - \tilde {x}}{h} \mathrm{and} 4 \pi G _ {y} \equiv G _ {h} \frac {y - \tilde {y}}{h}\tag{9c}
$$

The wave component $W _ { h }$ in (9b) is given by

$$
W _ {h} (h, v) \equiv 2 \pi [ 2 / \pi - \widetilde {H} _ {1} (h) + \mathrm{i} J _ {1} (h) ] e ^ {v}\tag{10}
$$

where $\widetilde { H } _ { 1 } ( \cdot )$ and $J _ { 1 } ( \cdot )$ edenote the first-order Struve function and ethe first-order Bessel function of the first kind. The local flow component $L _ { * }$ in (9b) is given by

$$
L _ {*} (h, v) \equiv \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \operatorname{Im} \left[ e ^ {M} E _ {1} (M) - 1 / M \right] \cos \theta d \theta\tag{11}
$$

where M is defined by (8).

The exponential function $e ^ { \nu }$ and the Bessel and Struve functions in expressions (7) and (10) for the wave components W and $W _ { h }$ are infinitely diferentiable. Moreover, several practical and eficient alternative approximations for the Bessel and Struve functions are given in the literature; notably in Hitchcock [26], Abramowitz & Stegun [27], Luke [28], Newman [29]. Fig.2 depicts the Struve functions $\widetilde { H } _ { 0 } ( h )$ and $\widetilde { H } _ { 1 } ( h ) - 2 / \pi$ and the Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ efor $0 \leq h \leq 2 5$

![](images/33c4c39677694a87c3b52a9270ae6991c631263ee61524089cfc2ee644585d6f.jpg)  
Figure 3: Local flow component L and imaginary part of the wave component Im W for $h = 0 \mathrm { ~ a n d } - 1 0 \leq \nu \leq 0$

## 3. Special cases

In the special case $h = 0$ , expressions (7) and (10) for the wave components W and $W _ { h }$ become

$$
W (h = 0, v) = - \mathrm{i} 2 \pi e ^ {v} \text { and } W _ {h} (h = 0, v) = 4 e ^ {v}\tag{12a}
$$

Moreover, expression (8) yields $M = \nu$ and the integral repre sentations (8) and (11) simplify as

$$
\begin{array}{l} L (h = 0, v) = 1 / v - 2 e ^ {v} \operatorname{Re} E _ {1} (v + \mathrm{i} 0) \\ L _ {*} (h = 0, v) = - 4 e ^ {v} \end{array}\tag{12b}
$$

(12c)

Equations (9b), (12a) and (12c) then yield $G _ { h } = 0$ for $h = 0$ in agreement with symmetry considerations. Fig.3 depicts the functions $L ( h = 0 , \nu )$ and Im $W ( h = 0 , \nu ) \mathrm { f o r } - 1 0 \leq \nu \leq 0$

At the free-surface plane $\nu = 0$ , expressions (4-7), (9) and (10) yield

$$
4 \pi \operatorname{Re} G = - 1 / h + L (h, v = 0) + 2 \pi \widetilde {H} _ {0} (h) = 4 \pi \operatorname{Re} G _ {z}\tag{13a}
$$

$$
4 \pi \operatorname{Re} G _ {h} = 2 / h ^ {2} + L _ {*} (h, v = 0) + 2 \pi [ 2 / \pi - \widetilde {H} _ {1} (h) ]\tag{13b}
$$

The real parts 4π Re G and 4π $\operatorname { R e } G _ { z }$ of the Green function G and its vertical derivative $G _ { z }$ at the free surface $\nu = 0$ , and the related local flow and wave components

$$
- 1 / h + L (h, v = 0) \mathrm{and} 2 \pi \widetilde {H} _ {0} (h)\tag{14a}
$$

are depicted in Fig.4 for $0 \leq h \leq 1 5$ . Similarly, the real part $4 \pi \operatorname { R e } G _ { h }$ of the horizontal derivative $G _ { h }$ of the Green function at the free surface $\nu = 0$ , and the related local flow and wave components

$$
2 / h ^ {2} + L _ {*} (h, v = 0) \text { and } 2 \pi [ 2 / \pi - \widetilde {H} _ {1} (h) ]\tag{14b}
$$

are depicted in Fig.5 for $0 \leq h \leq 1 5$

Fig.4 and Fig.5 show that, at the free surface $\nu = 0$ , the local flow components dominate the wave components W and $W _ { h }$ for $0 \leq h < 1$ . However, the local flow components are significantly smaller than W and $W _ { h }$ for $1 5 \leq h \mathrm { o r } 4 \leq h .$ , respectively. The wave components W and $W _ { h }$ are infinitely diferentiable and can readily be evaluated, as was already noted. Simple approximations to the local flow components L and $L _ { * }$ defined by the integral representations (8) and (11) are now considered.

##

![](images/68875229694672e7a2fc7b706aa18d0a305d134f6010586053eed03d0c0f61ba.jpg)  
Figure 4: Real parts of the Green function and its vertical derivative, and related local flow and wave components, at the free surface $\nu = 0$ for $0 \leq h \leq 1 5$

## 4. Near-field and far-field approximations

The variables $0 \leq \alpha \leq 1$ and $0 \leq \beta \leq 1$ defined as

$$
\alpha \equiv - v / d \equiv \sqrt {1 - \beta^ {2}} \mathrm{and} \beta \equiv h / d \equiv \sqrt {1 - \alpha^ {2}}\tag{15}
$$

are used hereafter. The related variable $0 \leq \sigma \leq 1$ defined as

$$
\sigma \equiv h / (d - v) \equiv \beta / (1 + \alpha) \equiv \sqrt {(1 - \alpha) / (1 + \alpha)}\tag{16}
$$

is also used in this section and the next.

The behaviors of the local flow component L defined by the integral representation (8) in the near-field and far-field limits $d \to 0$ and d are considered in Noblesse [7]. In particular, expressions (7.7), (7.8), (7.22) and (7.23) in Noblesse [7] yield the near-field approximation

$$
\begin{array}{l} L = - \frac {1}{d} + 2 \left(\log \frac {d - v}{2} + \gamma\right) + 2 v \left(\log \frac {d - v}{2} + \gamma - 1\right) \\ \quad + 2 h (\sigma - 2) + O (d ^ {2} \log d) \text {as} d \to 0 \end{array}\tag{17}
$$

where $\gamma = 0 . 5 7 7 \dots$ . is Euler’s constant. For $\alpha \neq 0$ , expression (6.14) in Noblesse [7] yields the far-field approximation

$$
L = \frac {1}{d} + \frac {2 \alpha}{d ^ {2}} - \frac {2 - 6 \alpha^ {2}}{d ^ {3}} + O \left(\frac {1}{d ^ {4}}\right) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0\tag{18a}
$$

For $\alpha = 0$ , expressions (6.8) in Noblesse [7] and (12.1.30) in Abramowitz & Stegun [27] yield the far-field approximation

$$
L = - \frac {3}{d} + \frac {2}{d ^ {3}} + O \left(\frac {1}{d ^ {5}}\right) \text {   as   } d \to \infty \text {   if   } \alpha = 0\tag{18b}
$$

Expression (9b) and the partial derivatives, with respect to $h ,$ of expressions (7.7), (7.8), (7.22) and (7.23) in Noblesse [7] yield the near-field approximation

$$
\begin{array}{l} L _ {*} = \frac {2 \sigma}{d} + 2 (\sigma - 2) - h \left(\log \frac {d - v}{2} + \gamma + \sigma \beta + 2 \alpha - \frac {3}{2}\right) \\ - 4 v + O (d ^ {2} \log d) \text {   as   } d \to 0 \end{array}\tag{19}
$$

![](images/f2ca10b2be0ef2cda7e465315154ea0703423c2dc999084f571a987ab9c81631.jpg)  
Figure 5: Real part of the horizontal derivative of the Green function and related local flow and wave components at the free surface $\nu = 0$ for $0 \leq h \leq 1 5$

For $0 < \alpha < 1 , ( 9 \mathrm { b } )$ and (18a) similarly yield the far-field approximation

$$
L _ {*} = - \frac {2 \beta}{d ^ {2}} - \frac {6 \alpha \beta}{d ^ {3}} + O \left(\frac {1}{d ^ {4}}\right) \text {   as   } d \to \infty \text {   if   } 0 <   \alpha <   1\tag{20a}
$$

In the special case $\alpha = 0$ , equation (12.1.31) in Abramowitz & Stegun [27] and the derivative of (18b) yield the far-field approximation

$$
L _ {*} = \frac {2}{d ^ {2}} + O \left(\frac {1}{d ^ {4}}\right) \text {   as   } d \to \infty \text {   if   } \alpha = 0\tag{20b}
$$

In the special case $\alpha = 1$ , one has $L _ { * } \equiv - 4 e ^ { \nu }$ as was already noted in (12c).

## 5. Approach

The infinite flow region $0 \leq h < \infty , - \infty < \nu \leq 0$ is mapped onto the unit square

$$
0 \leq \rho \equiv d / (1 + d) \leq 1 \qquad 0 \leq \beta \equiv h / d \leq 1\tag{21a}
$$

via the relations

$$
d = \rho / (1 - \rho) \qquad h = \beta d \qquad v = - \sqrt {1 - \beta^ {2}} d\tag{21b}
$$

A pragmatic hybrid approach similar to that used in Noblesse et al. [23] for the Green function of steady ship waves is adopted here, as was already noted in the introduction. This approach combines numerical approximations with the near-field and far field analytical expansions given in the previous section.

## 5.1. Thefunction L

The local flow component L defined by (8) is expressed as

$$
L = - \frac {1}{d} + \frac {2 P}{1 + d ^ {3}} + 2 L ^ {\prime}\tag{22a}
$$

$$
\text { where } P \equiv e ^ {\nu} \left(\log \frac {d - \nu}{2} + \gamma - 2 d ^ {2}\right) + d ^ {2} - \nu\tag{22b}
$$

$$
\mathrm{and} L ^ {\prime} \equiv \frac {- P}{1 + d ^ {3}} - \frac {2}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \mathrm{Re} e ^ {M} E _ {1} (M) d \theta\tag{22c}
$$

##

![](images/3baeec4221c4ca89198893c67061d0add7c039e1a143bc417801f26c311cab89.jpg)

![](images/9b9695f2f6d84951efac3b8192fcedc26c673bed2541a3b4909797055b7b03e3.jpg)

Figure 6: Variations of the function L0 with respect to $0 \leq \beta \leq 1$ for $\rho = 0 . 0 5 , 0 . 2 , 0 . 3 5 , 0 . 5 , 0 . 6 5 , 0 . 8 , 0 . 9 5$ (left side) or with respect to $0 \leq \rho \leq 1$ for $\beta =$ 0, 0.2, 0.4, 0.6, 0.8, 1 (right side).  
![](images/f624f41352db3a096d0284ef716bae98cdefaf056f14085ee7a1c893d65dc702.jpg)

![](images/7a16dcd0f91191d4bb10757df563fda30365c62e1deb6c2ea683bce9f32345b4.jpg)  
Figure 7: Variations of the function $L _ { * } ^ { \prime }$ with respect to $0 \le \beta \le$ 1 for $\rho = 0 . 0 5 , 0 . 2 , 0 . 3 5 , 0 . 5 , 0 . 6 5 , 0 . 8 , 0 . 9 5$ (left side) or with respect to $0 \leq \rho \leq 1$ for $\beta =$ 0, 0.2, 0.4, 0.6, 0.8, 1 (right side)

Moreover, $\gamma$ in (22b) is Euler’s constant. The decomposition (22a) expresses the local flow L as the sum of two dominant terms that are defined analytically and are related to the nearfield and far-field expansions (17) and (18), and the correction $2 L ^ { \prime }$ . The correction term $2 L ^ { \prime }$ defined by (22c) is numerically approximated further on.

Eqs (17), (22a) and (22b) yield the near-field approximation

$$
L ^ {\prime} \sim d (\sigma \beta - 2 \beta) \mathrm{as} d \to 0\tag{23}
$$

Eqs (18), (22a) and (22b) yield the far-field approximations

$$
L ^ {\prime} \sim \frac {1}{d ^ {3}} (3 \alpha^ {2} - 1) \text {   as   } d \to \infty \text {   if   } \alpha \neq 0\tag{24a}
$$

$$
L ^ {\prime} \sim - \frac {1}{d ^ {3}} \left(\log \frac {d}{2} + \gamma - 1\right) \text {   as   } d \to \infty \text {   if   } \alpha = 0\tag{24b}
$$

The near-field approximations (17) and (23) and the far

field approximations (18) and (24) yield

$$
L ^ {\prime} / L = O (d ^ {2}) \mathrm{as} d \to 0\tag{25a}
$$

$$
L ^ {\prime} / L = O (1 / d ^ {2}) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0\tag{25b}
$$

$$
L ^ {\prime} / L = O (\log d / d ^ {2}) \mathrm{as} d \to \infty \mathrm{if} \alpha = 0\tag{25c}
$$

These relations show that $L ^ { \prime } \ll L$ in both the near field $d \to 0$ and the far field $d  \infty$ . Expressions (21) and the asymptotic approximations (23) and (24) show that the function $L ^ { \prime }$ is asymptotically similar to $\rho ( 1 - \rho ) ^ { 3 }$ as $\rho \to 0$ and as $\rho \to 1$

The variations of the function $L ^ { \prime }$ given by (22c) with respect to the variables $\beta$ and $\rho$ defined by (21) are depicted in Fig.6. An approximation to the function $L ^ { \prime }$ of the form

$$
L ^ {\prime} (\rho , \beta) \approx \rho (1 - \rho) ^ {3} R \text { where }\tag{26a}
$$

$$
R \equiv (1 - \beta) A - \beta B - \frac {\alpha C}{1 + 6 \alpha \rho (1 - \rho)} + \beta (1 - \beta) D\tag{26b}
$$

is considered in Section $^ { 6 . }$ The terms $A ( \rho ) , B ( \rho ) , C ( \rho )$ and $D ( \rho )$ in (26b) are polynomials in $\rho .$

![](images/ffdeb7d278a98877bef0cc88fb1ff188e7ff399993aaa98ec90d42a5afac606f.jpg)  
Figure 8: Local flow components $L$ (lines without symbols) and $L ^ { a }$ (lines with symbols) defined by the integral representation (8) or the related approximation (33) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

![](images/5a9566b9d7fe234bf2bc79ed52e8e4c03c1936a326b822d8e4cafd5192331ecc.jpg)  
Figure 10: Local flow components $L _ { z }$ (lines without symbols) and $L _ { z } ^ { a }$ (lines with symbols) defined by the integral representation (8), (9a) or the related approximation (32b), (33) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

## 5.2. Thefunction L

The local flow component $L _ { * }$ associated with the horizontal derivative $G _ { h }$ of the Green function $G$ in (9b) is now considered. This flow component, defined by (11), is expressed as

$$
L _ {*} = \frac {2 P _ {*}}{1 + d ^ {3}} - 4 Q _ {*} + 2 L _ {*} ^ {\prime}\tag{27a}
$$

$$
\left\{P _ {*} \equiv \frac {\beta + h}{d - v} - 2 \beta + 2 e ^ {v} d - h \right.
$$

where

$$
\left\{Q _ {*} \equiv e ^ {- d} (1 - \beta) \left(1 + \frac {d}{1 + d ^ {3}}\right) \right.\tag{27b}
$$

$$
\text { and } L _ {*} ^ {\prime} \equiv \frac {- P _ {*}}{1 + d ^ {3}} + 2 Q _ {*} + \frac {2}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \operatorname{Im} \left[ e ^ {M} E _ {1} (M) - \frac {1}{M} \right] \cos \theta d \theta\tag{27c}
$$

The decomposition (27a) expresses the local flow $L _ { * }$ as the sum of two dominant terms and the correction $2 L _ { * } ^ { \prime }$ defined by (27c). This correction term is numerically approximated further on.

![](images/6b7abaf93d3ff6d71b1ac80e73f57bfc57f820a23f86d4d27405f3f7e2a0f002.jpg)  
Figure 9: Local flow components $L _ { * }$ (lines without symbols) and $L _ { * } ^ { a }$ (lines with symbols) defined by the integral representation (11) or the related approximation (34) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

![](images/4a9bc94462430cba06d07eeaffe7ef02176234eeff4460cd344d0d76be367dd7.jpg)  
Figure 11: Local flow components $L _ { h }$ (lines without symbols) and $L _ { h } ^ { a }$ (lines with symbols) defined by the integral representation (9b), (11) or the related approximation (32b), (34) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

Eqs (19), (27a) and (27b) yield the near-field approximation

$$
L _ {*} ^ {\prime} \sim - d \left[ \frac {\beta}{2} \left(\log \frac {d - v}{2} + \gamma + \sigma \beta + 2 \alpha - \frac {7}{2}\right) - 2 \alpha + 2 \right] \text {   as   } d \rightarrow 0\tag{28}
$$

Eqs (20), (27a) and (27b) yield the far-field approximation

$$
L _ {*} ^ {\prime} \sim \frac {1}{d ^ {3}} (2 \beta - \sigma - 3 \alpha \beta) \text { as } d \rightarrow \infty \text { if } \alpha \neq 1\tag{29}
$$

Moreover, expressions (12c), (27a) and (27b) yield $L _ { * } ^ { \prime } \ \equiv \ 0$ along the vertical axis $\alpha = 1$

The near-field approximations (19), (28) and the far-field approximations (20) and (29) yield

$$
L _ {*} ^ {\prime} / L _ {*} = O (d ^ {2} \log d) \mathrm{as} d \to 0
$$

$$
L _ {*} ^ {\prime} / L _ {*} = O (1 / d) \text {   as   } d \to \infty\tag{30a}
$$

(30b)

![](images/cd7bd5bc52c1af8b1d5eb5b47dbd17c5d0af6513ada89ee1904180384869b33e.jpg)  
Figure 12: Absolute error 4πe $\equiv L - L ^ { a }$ between the local flow components L and L<sup>a</sup> defined by the integral representation (8) or the related approximation (33) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

where the identity $L _ { * } ^ { \prime } \equiv 0 { \mathrm { ~ i f ~ } } \alpha = 1$ was used. The relations (30) show that one has $L _ { * } ^ { \prime } \ll L$ in both the near field $d \to 0$ and the far field $d  \infty$ . Expressions (21) and the asymp totic approximations (28) and (29) show that the function $L _ { * } ^ { \prime }$ is asymptotically similar to $\rho ( 1 - \rho ) ^ { 3 }$ as $\rho \to 0$ and as $\rho \to 1$

The variations of the function $L _ { * } ^ { \prime }$ given by (27c) with respect to the variables β and ρ defined by (21) are depicted in Fig.7. The right side of Fig.7 shows that $L _ { * } ^ { \prime } \equiv 0$ along the vertical axis $\beta = 0$ as was already noted. An approximation to the function $L _ { * } ^ { \prime }$ of the form

$$
L _ {*} ^ {\prime} (\rho , \beta) \approx \rho (1 - \rho) ^ {3} R _ {*} \text { where }\tag{31a}
$$

$$
R _ {*} \equiv \beta A _ {*} - (1 - \alpha) B _ {*} + \beta (1 - \beta) \rho (1 - 2 \rho) C _ {*}\tag{31b}
$$

is considered in the next section. The terms $A _ { * } ( \rho ) , B _ { * } ( \rho )$ and $C _ { * } ( \rho )$ in (31b) are polynomials in $\rho .$

## 6. Practical approximations

The local flow components L and $L _ { * }$ defined by the integral representations (8) and (11) and the related local flow components $L _ { z }$ and $L _ { h }$ are approximated as

$$
L \approx L ^ {a} \quad \text { and } \quad L _ {*} \approx L _ {*} ^ {a}\tag{32a}
$$

$$
L _ {z} \approx L _ {z} ^ {a} \equiv \frac {v}{d ^ {3}} - \frac {1}{d} + L ^ {a} \quad \mathrm{and} \quad L _ {h} \approx L _ {h} ^ {a} \equiv \frac {h}{d ^ {3}} + L _ {*} ^ {a}\tag{32b}
$$

Hereafter, $L ^ { a } , L _ { * } ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ denote approximations to the local flow components $L , L _ { * } , L _ { z }$ and $L _ { h } ,$ , respectively.

Expressions (22a), (22b) and (26) define the approximate local flow component L<sup>a</sup> as

$$
L ^ {a} \equiv - \frac {1}{d} + \frac {2 P}{1 + d ^ {3}} + 2 \rho (1 - \rho) ^ {3} R\tag{33a}
$$

where $P$ and R are defined by (22b) and (26b) as

$$
P \equiv e ^ {v} \left(\log \frac {d - v}{2} + \gamma - 2 d ^ {2}\right) + d ^ {2} - v\tag{33b}
$$

$$
R \equiv (1 - \beta) A - \beta B - \frac {\alpha C}{1 + 6 \alpha \rho (1 - \rho)} + \beta (1 - \beta) D\tag{33c}
$$

![](images/1786e3e8069eed913f54ae9fd7f9be1bd1b11c8eeca90645c60c19ee26616a6c.jpg)  
Figure 13: Absolute error 4 $\pi e _ { * } \equiv L _ { * } - L _ { * } ^ { a }$ between the local flow components $L _ { * }$ and $L _ { * } ^ { a }$ defined by the integral representation (11) or the related approximation (34) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

Here, $\gamma = 0 . 5 7 7 \dots$ . is Euler’s constant, and $\alpha , \beta , \rho$ are defined by (15) and (21a). Moreover, the polynomials $A ( \rho ) , B ( \rho ) , C ( \rho )$ and $D ( \rho )$ in (33c) are defined as

$$
\begin{array}{r l} A & \equiv 1. 2 1 - 1 3. 3 2 8 \rho + 2 1 5. 8 9 6 \rho^ {2} - 1 7 6 3. 9 6 \rho^ {3} + 8 4 1 8. 9 4 \rho^ {4} \\ & - 2 4 3 1 4. 2 1 \rho^ {5} + 4 2 0 0 2. 5 7 \rho^ {6} - 4 1 5 9 2. 9 \rho^ {7} + 2 1 8 5 9 \rho^ {8} \\ & - 4 8 3 8. 6 \rho^ {9} \end{array} \tag {3}\tag{33d}
$$

$$
B \equiv 0. 9 3 8 + 5. 3 7 3 \rho - 6 7. 9 2 \rho^ {2} + 7 9 6. 5 3 4 \rho^ {3} - 4 7 8 0. 7 7 \rho^ {4}
$$

$$
+ 1 7 1 3 7. 7 4 \rho^ {5} - 3 6 6 1 8. 8 1 \rho^ {6} + 4 4 8 9 4. 0 6 \rho^ {7}
$$

$$
- 2 9 0 3 0. 2 4 \rho^ {8} + 7 6 7 1. 2 2 \rho^ {9}\tag{33e}
$$

$$
C \equiv 1. 2 6 8 - 9. 7 4 7 \rho + 2 0 9. 6 5 3 \rho^ {2} - 1 3 9 7. 8 9 \rho^ {3} + 5 1 5 5. 6 7 \rho^ {4}
$$

$$
- 9 8 4 4. 3 5 \rho^ {5} + 9 1 3 6. 4 \rho^ {6} - 3 2 7 2. 6 2 \rho^ {7}\tag{33f}
$$

$$
\begin{array}{r l} D \equiv 0. 6 3 2 - 4 0. 9 7 \rho + 6 6 7. 1 6 \rho^ {2} - 6 0 7 2. 0 7 \rho^ {3} + 3 1 1 2 7. 3 9 \rho^ {4} \\ & - 9 6 2 9 3. 0 5 \rho^ {5} + 1 8 1 8 5 6. 7 5 \rho^ {6} - 2 0 5 6 9 0. 4 3 \rho^ {7} \\ & + 1 2 8 1 7 0. 2 \rho^ {8} - 3 3 7 4 4. 6 \rho^ {9} \end{array} \tag {3}\tag{33g}
$$

Expressions (27a), (27b) and (31) define the approximate local flow component $L _ { * } ^ { a }$ as

$$
L _ {*} ^ {a} \equiv \frac {2 P _ {*}}{1 + d ^ {3}} - 4 Q _ {*} + 2 \rho (1 - \rho) ^ {3} R _ {*}\tag{34a}
$$

where $P _ { * } , Q _ { * }$ and $R _ { * }$ are defined by (27b) and (31b) as

$$
P _ {*} \equiv \frac {\beta + h}{d - v} - 2 \beta + 2 e ^ {v} d - h\tag{34b}
$$

$$
Q _ {*} \equiv e ^ {- d} (1 - \beta) \left(1 + \frac {d}{1 + d ^ {3}}\right)\tag{34c}
$$

$$
R _ {*} \equiv \beta A _ {*} - (1 - \alpha) B _ {*} + \beta (1 - \beta) \rho (1 - 2 \rho) C _ {*}\tag{34d}
$$

![](images/7f1a42a3ebacb52bf9dc55686e769f8cf6e1512911ea4e54ba7db60b9e4aa96e.jpg)  
Figure 14: Approximate relative error $e ^ { \prime } \equiv ( L - L ^ { a } ) / L ^ { \nu = 0 }$ between the local flow components L and $L ^ { a }$ defined by the integral representation (8) or the approximation (33) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2$ , 0.4, 0.6, 0.8, 1.

![](images/975cfb311962ffe67cb2e7245c5118ff87990a9951d32ed62e092693a49fff37.jpg)  
Figure 16: Approximate relative error $e _ { h } ^ { \prime } \equiv ( L _ { h } - L _ { h } ^ { a } ) / L _ { h } ^ { \nu = 0 }$ between the local flow components $L _ { h }$ and $L _ { b } ^ { a }$ defined by the integral representation (9b), (11) or the approximation (32b), (34) for $0 \leq \rho \leq 0 . 8$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

The polynomials $A _ { * } ( \rho ) , B _ { * } ( \rho )$ and $C _ { * } ( \rho )$ in (34d) are defined as

$$
A _ {*} \equiv 2. 9 4 8 - 2 4. 5 3 \rho + 2 4 9. 6 9 \rho^ {2} - 7 5 4. 8 5 \rho^ {3} - 1 1 8 7. 7 1 \rho^ {4}
$$

$$
\begin{array}{l} + 1 6 3 7 0. 7 5 \rho^ {5} - 4 8 8 1 1. 4 1 \rho^ {6} + 6 8 2 2 0. 8 7 \rho^ {7} - 4 6 6 8 8 \rho^ {8} \\ + 1 2 6 2 2. 2 5 \rho^ {9} \end{array} \tag {3}\tag{34e}
$$

$$
\begin{array}{r l} B _ {*} \equiv 1. 1 1 + 2. 8 9 4 \rho - 7 6. 7 6 5 \rho^ {2} + 1 5 6 5. 3 5 \rho^ {3} - 1 1 3 3 6. 1 9 \rho^ {4} \\ & + 4 4 2 7 0. 1 5 \rho^ {5} - 9 7 0 1 4. 1 1 \rho^ {6} + 1 1 8 8 7 9. 2 6 \rho^ {7} \\ & - 7 6 2 0 9. 8 2 \rho^ {8} + 1 9 9 2 3. 2 8 \rho^ {9} \end{array} \tag {3}\tag{34f}
$$

$$
\begin{array}{r l} C _ {*} & \equiv 1 4. 1 9 - 1 4 8. 2 4 \rho + 8 4 7. 8 \rho^ {2} - 2 3 1 8. 5 8 \rho^ {3} + 3 1 6 8. 3 5 \rho^ {4} \\ & - 1 5 9 0. 2 7 \rho^ {5} \end{array} \tag {3}\tag{34g}
$$

The approximations $L ^ { a }$ and $L _ { * } ^ { a }$ given by (33) and (34) hold within the entire flow region $0 \leq d .$ , and only involve elemen tary continuous functions (algebraic, exponential, logarithmic) of real arguments.

Fig.8 depicts the local flow components L and $L ^ { a }$ defined by the integral representation (8) or the related approximation (33) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$ . Fig.9 similarly depicts the local flow components $L _ { * }$ and $L _ { * } ^ { a }$ given by the integral representation (11) or the related approximation (34) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$

![](images/0878e3feed4cc504778ac1c875161b07359117c760b5ace51a4ce4e1320082c2.jpg)  
Figure 15: Approximate relative error $e _ { z } ^ { \prime } \equiv ( L _ { z } - L _ { z } ^ { a } ) / L _ { z } ^ { \nu = 0 }$ between the local flow components $L _ { z }$ and L<sup>a</sup> defined by the integral representation (8), (9a) or the approximation $( 3 2 \mathrm { b } ) , ( 3 3 )$ for $0 \leq \rho \leq$ 1 and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

![](images/de5a88a0854138768884712ca9beacd9d4217723947981eec05b3247259ca0ef.jpg)  
Figure 17: Approximate relative error $e _ { h } ^ { \prime } \equiv ( L _ { h } - L _ { h } ^ { a } ) / L _ { h } ^ { \nu = 0 }$ between the local flow components $L _ { h }$ and $L _ { h } ^ { a }$ defined by the integral representation (9b), (11) or the approximation (32b), (34) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

Fig.10 depicts the local flow components $L _ { z }$ and $L _ { z } ^ { a }$ defined by the integral representation (8), (9a) or the related approximation (32b), (33) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$ Fig.11 similarly depicts the local flow components $L _ { h }$ and $L _ { h } ^ { a }$ given by the integral representation (9b), (11) or the related approximation (32b), (34) for $0 ~ \leq ~ \rho ~ \leq ~ 1$ and six values of $0 \leq \alpha \leq 1$

The functions $L$ and $L ^ { a }$ in Fig.8, the functions $L _ { * }$ and $L _ { * } ^ { a }$ in Fig.9, the functions $L _ { z }$ and $L _ { z } ^ { a }$ in Fig.10, and the functions $L _ { h }$ and $L _ { h } ^ { a }$ in Fig.11 cannot be distinguished.

## 7. Errors in the Green function and its gradient

The errors associated with the approximations L<sup>a</sup> and $L _ { * } ^ { a }$ given by (33) and (34) are now considered.

## 7.1. Definition ofabsolute and relative errors

The absolute errors e and e between the local flow components L and $L _ { * }$ and the corresponding approximations $L ^ { a }$ and $L _ { * } ^ { a }$ in expressions (6) and (9) for the Green function and its gradient are defined as

$$
4 \pi e \equiv L - L ^ {a} \equiv L _ {z} - L _ {z} ^ {a}\tag{35a}
$$

$$
4 \pi e _ {*} \equiv L _ {*} - L _ {*} ^ {a} \equiv L _ {h} - L _ {h} ^ {a}\tag{35b}
$$

As was already noted, one has $L _ { * } ^ { a } \equiv L$ along the vertical axis $\alpha = 1$ , and (35b) then yields

$$
e _ {*} \equiv 0 \mathrm{if} \alpha = 1\tag{36}
$$

The relative errors associated with the approximate local flow components $L ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ are defined as

$$
e ^ {r} \equiv (L - L ^ {a}) / L \equiv 4 \pi e / L\tag{37a}
$$

$$
e _ {z} ^ {r} \equiv (L _ {z} - L _ {z} ^ {a}) / L _ {z} \equiv (L - L ^ {a}) / L _ {z} \equiv 4 \pi e / L _ {z}\tag{37b}
$$

$$
e _ {h} ^ {r} \equiv (L _ {h} - L _ {h} ^ {a}) / L _ {h} \equiv (L _ {*} - L _ {*} ^ {a}) / L _ {h} \equiv 4 \pi e _ {*} / L _ {h}\tag{37c}
$$

Figs 8, 10 and 11 show that the functions $L ( h , \nu ) , L _ { z } ( h , \nu )$ and $L _ { h } ( h , \nu )$ vanish at a point $\rho < 1 \mathrm { i f } \nu < 0$ , but do not vanish for $\rho < 1 \mathrm { i f } \nu = 0$ . The relative errors $e ^ { r } , e _ { z } ^ { r }$ and $e _ { h } ^ { r }$ defined by (37) are then approximated here via the modified relative errors $e ^ { \prime } , e _ { z } ^ { \prime }$ and $\boldsymbol { e } _ { h } ^ { \prime }$ defined as

$$
e ^ {\prime} \equiv \frac {L - L ^ {a}}{L ^ {\nu = 0}}, e _ {z} ^ {\prime} \equiv \frac {L _ {z} - L _ {z} ^ {a}}{L _ {z} ^ {\nu = 0}} \equiv e ^ {\prime} \frac {L ^ {\nu = 0}}{L _ {z} ^ {\nu = 0}}, e _ {h} ^ {\prime} \equiv \frac {L _ {h} - L _ {h} ^ {a}}{L _ {h} ^ {\nu = 0}}\tag{38}
$$

where $L ^ { \nu = 0 } \equiv L ( h , \nu = 0 )$ , and $L _ { z } ^ { \nu = 0 }$ and $L _ { h } ^ { \nu = 0 }$ similarly denote the functions $L _ { z } ( h , \nu = 0 )$ and $L _ { h } ( h , \nu = 0 )$ The functions $e ^ { \prime } ,$ $e _ { z } ^ { \prime }$ and $\boldsymbol { e } _ { h } ^ { \prime }$ defined by (38) provide meaningful approximations to the relative errors associated with the approximations $L ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ within the entire flow region $0 \leq d .$

Expression (9a) yields $L _ { z } ^ { \nu = 0 } \stackrel { - } { = } L ^ { \nu = 0 } - 1 / h$ . This expression and the asymptotic approximations (17) and (18b) then yield

$$
\frac {L ^ {\nu = 0}}{L _ {z} ^ {\nu = 0}} \approx \frac {1}{2} \text {   as   } h \to 0 \text {   and   } \frac {L ^ {\nu = 0}}{L _ {z} ^ {\nu = 0}} \approx \frac {3}{4} - \frac {1}{8 h ^ {2}} \text {   as   } h \to \infty\tag{39}
$$

These relations show that the (approximate) relative errors $e _ { \tau } ^ { \prime }$ and $e ^ { \prime }$ in (38) are closely related, and that one has $e _ { z } ^ { \prime } \approx 3 e ^ { \prime } / 4$ over most of the flow region, as is illustrated further on in Fig.14 and Fig.15.

## 7.2. Asymptotic analysis ofabsolute and relative errors

Equations (17), (18) and (33) show that the absolute error e defined by (35a) behaves as

$$
e = O (d) \mathrm{as} d \to 0\tag{40a}
$$

$$
e = O (1 / d ^ {3}) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0\tag{40b}
$$

$$
e = O (\log d / d ^ {3}) \mathrm{as} d \to \infty \mathrm{if} \alpha = 0\tag{40c}
$$

Equations (19), (20), (34), (35b) and (36) similarly yield

$$
e _ {*} = O (d \log d) \text {   as   } d \to 0
$$

$$
e _ {*} = O (1 / d ^ {3}) \mathrm{as} d \to \infty\tag{41a}
$$

(41b)

The relative errors (37) are now considered. Equations (9a), (17) and (18) yield

$$
L _ {z} \sim - \alpha / d ^ {2} \text {as} d \rightarrow 0 \text {if} \alpha \neq 0
$$

$$
L _ {z} \sim - 2 / d \text { as } d \rightarrow 0 \text { if } \alpha = 0\tag{42a}
$$

$$
L _ {z} \sim \alpha / d ^ {2} \text { as } d \rightarrow \infty \text { if } \alpha \neq 0\tag{42b}
$$

$$
L _ {z} \sim - 4 / d \text {   as   } d \to \infty \text {   if   } \alpha = 0\tag{42c}
$$

(42d)

Similarly, equations (9b), (19) and (20) yield

$$
L _ {h} \sim \beta / d ^ {2} \mathrm{as} d \to 0 \mathrm{if} \alpha \neq 1
$$

$$
L _ {h} \rightarrow - 4 \mathrm{as} d \rightarrow 0 \mathrm{if} \alpha = 1\tag{43a}
$$

$$
L _ {h} \sim - \beta / d ^ {2} \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0 \mathrm{or} 1\tag{43b}
$$

$$
L _ {h} \sim 3 / d ^ {2} \mathrm{as} d \to \infty \mathrm{if} \alpha = 0\tag{43c}
$$

(43d)

Moreover, equations (9b) and (12c) yield $L _ { h } = - 4 e ^ { \nu } \operatorname { i f } \alpha = 1$

The asymptotic approximations (17), (18) and (40) show that the relative error e<sup>r</sup> defined by (37a) behaves as

$$
e / L = O (d ^ {2}) \mathrm{as} d \to 0\tag{44a}
$$

$$
e / L = O (1 / d ^ {2}) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0
$$

$$
e / L = O (\log d / d ^ {2}) \mathrm{as} d \to \infty \mathrm{if} \alpha = 0\tag{44b}
$$

(44c)

One then has $e \ \ll \ L$ in both the near field and the far field. Expressions (40) and (42) similarly show that the relative error $e _ { z } ^ { r }$ defined by (37b) behaves as

$$
e / L _ {z} = O (d ^ {3}) \mathrm{as} d \to 0 \mathrm{if} \alpha \neq 0
$$

$$
e / L _ {z} = O (d ^ {2}) \mathrm{as} d \to 0 \mathrm{if} \alpha = 0\tag{45a}
$$

$$
e / L _ {z} = O (1 / d) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 0\tag{45b}
$$

(45c)

$$
e / L _ {z} = O (\log d / d ^ {2}) \mathrm{as} d \to \infty \mathrm{if} \alpha = 0\tag{45d}
$$

One then has e $L _ { z }$ in both the near field and the far field. Expressions (41) and (43) likewise show that the relative error $e _ { h } ^ { r }$ defined by (37c) behaves as

$$
e _ {*} / L _ {h} = O (d ^ {3} \log d) \mathrm{as} d \to 0 \mathrm{if} \alpha \neq 1\tag{46a}
$$

$$
e _ {*} / L _ {h} = O (1 / d) \mathrm{as} d \to \infty \mathrm{if} \alpha \neq 1\tag{46b}
$$

Along the vertical axis $\alpha = 1$ , one has $e _ { * } \equiv 0$ in accordance with (36). One then has $e _ { * }$ $L _ { h }$ in both the near field and the far field.

## 7.3. Numerical analysis ofabsolute and relative errors

Computations within the entire region $0 \leq d$ show that the absolute errors e and $e _ { * }$ defined by (35) vary within the ranges

$$
- 3 \times 1 0 ^ {- 4} <   e <   3 \times 1 0 ^ {- 4}, - 2. 4 \times 1 0 ^ {- 4} <   e _ {*} <   2. 6 \times 1 0 ^ {- 4} \tag {47}
$$

Fig.12 and Fig.13 depict the errors e and $e _ { * }$ for $0 ~ \leq \rho ~ \leq ~ 1$ and six values of $0 \leq \alpha \leq 1$ . Fig.12 and Fig.13 show that the errors e and $e _ { * }$ vanish both as $\rho \to 0$ and as $\rho  1 , \mathrm { i . e }$ . in the near field $d \to 0$ and the far field $d \to \infty ,$ , in accordance with (40) and (41) and the fact that the global approximations

![](images/9b2902c0b067efca88c6d6476b0924f672ccb7a3d9c3c935366381aac753414a.jpg)  
Figure 18: Relative error $\varepsilon ^ { G }$ defined by (51) for 1 $\leq x ^ { m a x }$ 25 and $- z ^ { m a x } / x ^ { m a x } =$ 0.04, 0.08, 0.12, 0.16.

$L ^ { a }$ and $L _ { * } ^ { a }$ given by (33) and (34) are asymptotically correct in the limits $d \to 0$ and $d \to \infty$ . Specifically, Fig.12 shows that the absolute error e associated with the approximations $L ^ { a }$ and $L _ { z } ^ { a }$ is relatively small in the near field $0 \leq \rho \leq 0 . 1 5$ and in the far field $0 . 8 1 \leq \rho \leq 1$ , Fig.13 shows that the absolute error $e _ { * }$ associated with the approximation $L _ { h } ^ { a }$ is relatively small in the far field $0 . 7 5 \leq \rho \leq 1$ 9

The errors e and $e _ { * }$ for the six values of α considered in Fig.12 and Fig.13 are of the same order of magnitude, and oscillate between positive and negative values that are distributed more or less evenly. Fig.13 shows that $e _ { * } \equiv 0$ along the vertical axis $\alpha = 1$ , in accordance with (36).

Fig.14 and Fig.15 depict the approximate relative errors $e ^ { \prime }$ and $e _ { z } ^ { \prime }$ for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$ . Computations within the entire region $0 \leq d$ show that $e ^ { \prime }$ and $e _ { z } ^ { \prime }$ vary within the ranges

$$
- 0. 4 5 \times 1 0 ^ {- 2} <   e ^ {\prime} <   0. 4 3 \times 1 0 ^ {- 2}\tag{48a}
$$

$$
- 0. 3 4 \times 1 0 ^ {- 2} <   e _ {z} ^ {\prime} <   0. 3 2 \times 1 0 ^ {- 2}\tag{48b}
$$

Fig.16 and Fig.17 similarly depict the approximate relative error $\boldsymbol { e } _ { h } ^ { \prime }$ for $0 \leq \rho \leq 0 . 8 ~ \mathrm { o r } ~ 0 \leq \rho \leq 1$ and the same six values of $0 \leq \alpha \leq 1$ . The errors $e ^ { \prime } , e _ { z } ^ { \prime }$ and $\boldsymbol { e } _ { h } ^ { \prime }$ in Fig.14-Fig.16 are relatively small and of the same order of magnitude. Fig.17 shows that the error $\boldsymbol { e } _ { h } ^ { \prime }$ is significantly larger in the far field $0 . 8 ~ \leq ~ \rho ~ \leq ~ 1$ . Indeed, computations within the entire region $0 \leq d$ show that $\boldsymbol { e } _ { h } ^ { \prime }$ vary within the range

$$
- 4. 3 3 \times 1 0 ^ {- 2} <   e _ {h} ^ {\prime} <   4. 7 3 \times 1 0 ^ {- 2}\tag{48c}
$$

However, Fig.13 shows that the absolute error $e _ { * }$ that corresponds to the relative error $\boldsymbol { e } _ { h } ^ { \prime }$ is small in the range $0 . 8 \leq \rho \leq 1$ within which $\boldsymbol { e } _ { h } ^ { \prime }$ is large. Specifically, Fig.13 shows that the absolute error e is smaller than $1 0 ^ { - 4 }$ for $0 . 8 \le \rho \le 0 . 9$ and smaller than $0 . 5 \times 1 0 ^ { - 4 } \mathrm { f o r } 0 . 9 \leq \rho \leq 1$

Fig.14-Fig.17 show that the relative errors $e ^ { \prime } , e _ { \tau } ^ { \prime }$ and $\boldsymbol { e } _ { h } ^ { \prime }$ vanish in both the near field $\rho \to 0$ and the far field $\rho \to 1$ . These errors are very small in the near field, where the functions $L , L _ { z }$ and $L _ { h }$ are large as is shown in Fig.8, Fig.10 and Fig.11. More over, Fig.16 and Fig.17 show that one has $e _ { * } \equiv 0$ and therefore $\boldsymbol { e } _ { h } ^ { \prime } \equiv 0$ along the vertical axis $\alpha = 1$

![](images/a8d0594c5a30d9cb20d7b744ac30dc12b7cbe54dda8ae7eeec9b659ed29270cc.jpg)  
Figure 19: Relative error ε<sup>z</sup> defined by (51) for $1 \leq x ^ { m a x } \leq 2 5$ and $- z ^ { m a x } / x ^ { m a x } =$ 0.04, 0.08, 0.12, 0.16.

![](images/26ccb272042aa2280b9e46bebe7e6d2c84aeb639924093bfed2600b8819d0995.jpg)  
Figure $2 0 \colon$ Relative error $\varepsilon ^ { h }$ defined by (51) for $1 ~ \leq ~ x ^ { m a x } ~ \leq ~ 2 5$ and $- \overline { { z } } ^ { m a x } / x ^ { m a x } = 0 . 0 4 , 0 . 0 8 , 0 . 1 2 , 0 . 1 6$

## 7.4. Numerical analysis ofglobal errors

The errors associated with the analytical approximations $G ^ { a } , G _ { \tau } ^ { a }$ and $G _ { h } ^ { a }$ to the Green function G and its derivatives $G _ { z }$ and $G _ { h }$ can be further analyzed by considering flow field points $\mathbf { x } _ { i j } \equiv ( x _ { i } , 0 , z _ { j } )$ and source points $\tilde { \mathbf { x } } _ { m n } \equiv ( \tilde { x } _ { m } , 0 , \tilde { z } _ { n } )$ where $x _ { i } , z _ { j } ,$ $\widetilde { x } _ { m }$ and $\tilde { z } _ { n }$ are defined as

$$
x _ {i} \equiv (i - 1) \delta^ {x} \mathrm{with} 1 \leq i \leq N ^ {x} + 1\tag{49a}
$$

$$
z _ {j} \equiv - (j - 1) \delta^ {z} \text { with } 1 \leq j \leq N ^ {z} + 1\tag{49b}
$$

$$
\tilde {x} _ {m} \equiv (m - 1 / 2) \delta^ {x} \mathrm{with} 1 \leq m \leq N ^ {x}
$$

$$
\tilde {z} _ {n} \equiv - (n - 1 / 2) \delta^ {z} \mathrm{with} 1 \leq n \leq N ^ {z}\tag{49c}
$$

(49d)

The flow field points $\mathbf { X } _ { i j }$ are knots of a rectangular grid within the region $0 \leq x \leq x ^ { m a x } \equiv N ^ { x } \delta ^ { x } , - z ^ { m a x } \equiv N ^ { z } \delta ^ { z } \leq z \leq 0$ . The grid size is chosen as $\delta ^ { x } = 0 . 0 1$ and $\delta ^ { z } = 0 . 0 1$ for $x ^ { m a x } \leq 5 ,$ , or as $\delta ^ { x } = 0 . 1$ and $\delta ^ { z } = 0 . 1$ for $5 < x ^ { m a x }$ . The source points $\tilde { \mathbf { X } } _ { m n }$ are the centroids of the panels defined by the rectangular grid associated with the flow field points $\mathbf { X } _ { i j }$

The integrated Green function $\overline { G }$ and the related functions $\overline { { G _ { z } } }$ and $\overline { { G _ { h } } }$ defined as

$$
\overline {{G}} \equiv \Sigma_ {i = 1} ^ {i = N ^ {x} + 1} \Sigma_ {j = 1} ^ {j = N ^ {z} + 1} \Sigma_ {m = 1} ^ {m = N ^ {x}} \Sigma_ {n = 1} ^ {n = N ^ {z}} G (\mathbf {x} _ {i j}, \tilde {\mathbf {x}} _ {m n})\tag{50a}
$$

$$
\overline {{G _ {z}}} \equiv \Sigma_ {i = 1} ^ {i = N ^ {x} + 1} \Sigma_ {j = 1} ^ {j = N ^ {z} + 1} \Sigma_ {m = 1} ^ {m = N ^ {x}} \Sigma_ {n = 1} ^ {n = N ^ {z}} G _ {z} (\mathbf {x} _ {i j}, \tilde {\mathbf {x}} _ {m n})\tag{50b}
$$

$$
\overline {{G _ {h}}} \equiv \Sigma_ {i = 1} ^ {i = N ^ {x} + 1} \Sigma_ {j = 1} ^ {j = N ^ {z} + 1} \Sigma_ {m = 1} ^ {m = N ^ {x}} \Sigma_ {n = 1} ^ {n = N ^ {z}} G _ {h} (\mathbf {x} _ {i j}, \tilde {\mathbf {x}} _ {m n})\tag{50c}
$$

are considered together with the integrated Green function $\overline { { G ^ { a } } }$ and the related functions $\overline { { G _ { z } ^ { a } } }$ and $\overline { { G _ { h } ^ { a } } }$ defined by (50) where the Green function G and its derivatives $G _ { z }$ and $G _ { h }$ are replaced by their corresponding approximations $G ^ { a } , G _ { z } ^ { a }$ and $G _ { h } ^ { a } .$

The relative errors

$$
\varepsilon^ {G} \equiv 1 - \overline {{G ^ {a}}} / \overline {{G}}, \varepsilon^ {z} \equiv 1 - \overline {{G _ {z} ^ {a}}} / \overline {{G _ {z}}}, \varepsilon^ {h} \equiv 1 - \overline {{G _ {h} ^ {a}}} / \overline {{G _ {h}}}\tag{51}
$$

provide an estimate of the relative errors that may be expected in numerical computations of added-mass and wave-damping coeficients based on a panel method as a result of the approximations $G ^ { a } , G _ { z } ^ { a }$ and $G _ { h } ^ { a }$ to the Green function $G$ and its derivatives. The relative errors $\varepsilon ^ { G } , \varepsilon ^ { z }$ and $\varepsilon ^ { h }$ defined by (51), where the wave components W and $W _ { h }$ in expressions (6), (9a) and (9b) are ignored because the components W and $W _ { h }$ can be evaluated with very high accuracy, are considered here to estimate the global integrated errors that may be expected as a result of the approximations to the local flow components in the Green function G and its gradient.

Fig.18, Fig.19 and Fig.20 depict the relative errors $\varepsilon ^ { G } , \varepsilon ^ { z }$ and $\varepsilon ^ { h }$ defined by (51) for flow regions defined by nine values of $x ^ { m a x }$ within the range $1 \leq x ^ { m a x } \leq 2 5$ and four values $\operatorname { o f } { - z ^ { m a x } } / x ^ { m a x }$ taken as 0.04, 0.08, 0.12 and 0.16. These three figures show that the relative errors $\varepsilon ^ { G } , \varepsilon ^ { z }$ and $\varepsilon ^ { h }$ vary between positive and negative values within the ranges

$$
- 4 \times 1 0 ^ {- 4} <   \varepsilon^ {G} <   5 \times 1 0 ^ {- 4}\tag{52a}
$$

$$
- 4 \times 1 0 ^ {- 4} <   \varepsilon^ {z} <   6 \times 1 0 ^ {- 4}\tag{52b}
$$

$$
- 1 \times 1 0 ^ {- 4} <   \varepsilon^ {h} <   6 \times 1 0 ^ {- 4}\tag{52c}
$$

These errors are relatively small, especially for small values of $x ^ { m a x }$ , and are of the same order of magnitude for the four values of $- z ^ { m a x } / x ^ { m a x }$

## 8. Conclusion

The Green function G in the classical theory of wave difraction radiation by an ofshore structure, or a ship at low forward speed, in deep water is expressed in the usual manner as the sum of the fundamental free-space Green function $- 1 / r ,$ a nonoscillatory local flow component $L$ and a wave component W. The gradient of G is similarly expressed as the sum of three basic components. The wave components W and $W _ { h }$ in these basic decompositions of G and its gradient G are expressed in terms of real functions of one variable, specifically the exponential function $e ^ { \nu } ,$ the Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ and the Struve functions $\bar { H } _ { 0 } ( h )$ and $\widetilde { H } _ { 1 } ( h )$ . These functions are infinitely dif e eferentiable and can be readily evaluated; e.g. Hitchcock [26], Abramowitz & Stegun [27], Luke [28], Newman [29].

Expressions (6), (7), (9), (10) and (32)-(34) provide a prac tical basis for evaluating the Green function G and its gradient G. The analytical approximations (33) and (34) to the loca flow components in the expressions for G and G are global ap proximations valid within the entire flow region, unlike the ap proximations for complementary contiguous flow regions given in the literature. The global approximations obtained here only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments. The analysis of the errors associated with the approximations to the local flow compo nents given in the study shows that the approximations are sufficiently accurate for practical purposes. These global approximations provide a particularly simple and highly eficient way of numerically evaluating the Green function and its gradient for difraction radiation of time-harmonic waves in deep water.

[1] T.H. Havelock, The damping of the heaving and pitching motion of a ship, The London, Edinburgh, and Dublin Philosophical Magazine and Journal of Science 33 (224) (1942) 666-673.

[2] T.H. Havelock, Waves due to a floating sphere making periodic heaving oscillations, Proceedings of the Royal Society of London A: Mathemati cal, Physical and Engineering Sciences 231 (1184) (1955) 1-7.

[3] R.C. Thorne, Multipole expansions in the theory of surface waves, Mathematical Proceedings of the Cambridge Philosophical Society 49 (4) (1953) 707-716.

[4] M.D. Haskind, On wave motion of a heavy fluid, Prikladnaya Matematika i Mekhanika 18 (1954) 15-26.

[5] J.V. Wehausen, E.V. Laitone, Surface waves, Handbuch der Physik, Volume 9, Springer-Verlag, Berlin (1960) 446-778.

[6] W.D. Kim, On the harmonic oscillations of a rigid body on a free surface, Journal of Fluid Mechanics 21 (3) (1965) 427-451.

[7] F. Noblesse, The Green function in the theory of radiation and difraction of regular water waves by a body, Journal of Engineering Mathematics 16 (2) (1982) 137-169.

[8] D. Martin, Resolution num ´ erique du probl ´ eme lin \` earis ´ e de la tenue ´ a la \` mer, Association Technique Maritime et Aeronautique (1980).´

[9] J.G. Telste, F. Noblesse, Numerical evaluation of the Green function of water-wave radiation and difraction, Journal of Ship Research 30 (2) (1986) 69-84.

[10] J.N. Newman, An expansion of the oscillatory source potential, Applied Ocean Research 6 (2) (1984) 116-117.

[11] J.N. Newman, Algorithms for the free-surface Green function, Journal of Engineering Mathematics 19 (1) (1985) 57-67.

[12] X.B. Chen, Free surface Green function and its approximation by polynomial series, Bureau Veritas’ Research Report No. 641 DTO/XC, Bureau Veritas, France, (1991).

[13] X.B. Chen, Evaluation de la fonction de Green du probleme de difraction/radiation en profondeur d’eau finie-une nouvelle methode rapide et´ precise, 4e Journ´ ees de l’Hydrodynamique, Nantes, France, (1993) 371-´ 384.

[14] R.S. Wang, The numerical approach of three dimensional free-surface Green function and its derivatives, Journal of Hydrodynamics (Ser.A) 7 (3) (1992) 277-286.

[15] Q. Zhou, G. Zhang, L. Zhu, The fast calculation of free-surface wave Green function and its derivatives, Chinese Journal of Computational Physics 16 (2) (1999) 113-120.

[16] M. Ba, B. Ponizy, F. Noblesse, Calculation of the Green function of waterwave difraction and radiation, The Second International Ofshore and Polar Engineering Conference, San Francisco, USA, (1992) 60-63.

[17] B. Ponizy, F. Noblesse, M. Ba, M. Guilbaud, Numerical evaluation of free-surface Green functions, Journal of Ship Research 38 (3) (1994) 193- 202.

[18] M.A. Peter, M.H. Meylan, The eigenfunction expansion of the infinite depth free surface Green function in three dimensions, Wave Motion 40 (1) (2004) 1-11.

[19] X.L. Yao, S.L. Sun, S.P. Wang, S.T. Yang, The research on the highly eficient calculation method of 3-D frequency-domain Green function, Journal of Marine Science and Application 8 (3) (2009) 196-203.

[20] J. D’el´ıa, L. Battaglia, M. Storti, A semi-analytical computation of the Kelvin kernel for potential flows with a free surface, Computational & Applied Mathematics 30 (2) (2011) 267-287.

[21] Y. Shen, D. Yu, W. Duan, H. Ling, Ordinary diferential equation algorithms for a frequency-domain water wave Green’s function, Journal of Engineering Mathematics 100 (1) (2016) 53-66.

[22] H. Wu, C. Zhang, C. Ma, F. Huang, C. Yang, F. Noblesse, Errors due

to a practical Green function for steady ship waves, European Journal of Mechanics-B/Fluids 55 (2016) 162-169.

[23] F. Noblesse, G. Delhommeau, F. Huang, C. Yang, Practical mathematical representation of the flow due to a distribution of sources on a steadily advancing ship hull, Journal of Engineering Mathematics 71 (4) (2011) 367-392.

[24] H. Wu, C. Ma, Y. Zhu, Z. Yang, W. Li, F. Noblesse, Approximations of the Green function for difraction radiation of water waves, The 26th International Ocean and Polar Engineering Conference, Rhodes, Greece, (2016) 134-139.

[25] F. Noblesse, Integral identities of potential theory of radiation and difraction of regular water waves by a body. Journal of Engineering Mathemat ics 17 (1) (1983) 1-13.

[26] A.J.M. Hitchcock, Polynomial approximations to Bessel functions of order zero and one and to related functions, Mathematics of Computation 11 (58) (1957) 86-88.

[27] M. Abramowitz, I.A. Stegun, Handbook of mathematical functions, Dover, New York (1965).

[28] Y.L. Luke, Mathematical functions and their approximations, Academic Press, New York (1975).

[29] J.N. Newman, Approximations for the Bessel and Struve functions, Math ematics of Computation 43 (168) (1984) 551-556.

\`A global approximation to the Green function for diffraction radiation of water waves

by Huiyu Wu et al. (Shanghai Jiao Tong Univ. China)

## Highlights

1. The Green function of the theory of diffraction radiation of timeharmonic (regular) waves by an offshore structure, or a ship at low speed, in deep water is considered.

2. The Green function G and its gradient are expressed in the usual manner as the sum of three components that correspond to the fundamental free-space singularity, a non-oscillatory local flow, and waves.

3. Simple approximations that only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments are given for the local flow components in G and its gradient.

4. These approximations are global approximations valid within the entire flow region, rather than within complementary contiguous regions as can be found in the literature.

5. The analysis of the errors associated with the approximations to the local flow components given in the study shows that the approximations are sufficiently accurate for practical purposes.

6. These global approximations provide a particularly simple and highly efficient way of numerically evaluating the Green function and its gradient for diffraction radiation of time-harmonic waves in deep water.