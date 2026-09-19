# A GLOBAL APPROXIMATION TO THE GREEN FUNCTION FOR DIFFRACTION-RADIATION OF REGULAR WATER WAVES IN DEEP WATER

HUIYU WU, YI ZHU, CHAO MA, WEI LI, HUIPING FUAND FRANCIS NOBLESSE

State Key Laboratory of Ocean Engineering Collaborative Innovation Center for Advanced Ship and Deep-Sea Exploration School of Naval Architecture, Ocean & Civil Engineering Shanghai Jiao Tong University, Shanghai, China e-mail: why2277@sjtu.edu.cn

Key words: Regular Water Waves, Difraction Radiation, Green Function, Local Flow, Global Approximation

Abstract. The Green function of the theory of difraction radiation of time-harmonic (regular) waves by an ofshore structure, or a ship at low speed, in deep water is considered. The Green function G and its gradient G are expressed in the usual manner as the sum of three components that correspond to the fundamental free-space singularity, a non-oscillatory local flow, and waves. Simple approximations that only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments are given for the local flow components in G and G. These approximations are global approximations valid within the entire flow region, rather than within complementary contiguous regions as can be found in the literature.

## 1 INTRODUCTION

Difraction radiation of time-harmonic water waves by an ofshore structure, or a ship at low speed, within the classical framework of linear potential flow theory and the Green function method, is routinely used to predict added-mass and wave-damping coeficients, motions, and wave loads. The Green function, which represents the velocity potential due to a pulsating source at a singular point under the free surface as is well known, is an essential element of this method. Accordingly, the Green function has been studied in a broad literature, especially for the simplest case of deep water that is considered here.

The Green function G can be expressed as the sum of the fundamental free-space singularity and a flow component that accounts for free-surface efects. Moreover, this free-surface component is commonly decomposed into a wave component W that represents the waves radiated by the pulsating source, and a non-oscillatory local flow component L. This basic decomposition into a wave and a local flow component is not unique. Indeed, three alternative decompositions and related single-integral representations of the Green function G are given in Noblesse [1].

Several alternative mathematical representations and approximations of G and G that are well suited for numerical evaluation can be found in the literature. In particular, complementary near-field and far-field asymptotic expansions and Taylor series are given in Noblesse [1] and Telste & Noblesse [2]. Several practical approximate methods for computing G and G have also been given. These alternative methods include polynomial approximations within complementary contiguous flow regions, given in Newman [3, 4], Wang [5] and Zhou et al. [6], and table interpolation associated with function and coordinate transformations, given in Ponizy et al. [7]. Other useful practical methods can be found in the literature, notably in Peter & Meylan [8], Yao et al. [9], D’el´ıa et al. [10] and Shen et al. [11].

Accuracy and eficiency are essential requirements of methods for numerically evaluating G and G, and these important aspects are considered in the practical approximate methods listed in the foregoing. Indeed, the alternative methods proposed in these studies provide accurate and eficient methods for computing G and G.

Numerical errors associated with potential-flow panel methods stem from several well-known sources, including: (i) discretization of the wetted hull surface of an ofshore structure or a ship; i.e. the number and the type (flat or curved) of panels, (ii) approximation of the variations (piecewise constant, linear, quadratic, or higher-order) of the densities of the singularity (source, dipole) distributions over a surface panel, (iii) numerical integration of the Green function and its gradient over a panel, and (iv) numerical approximation of the Green function and its gradient.

Moreover, the Green function G (as well as its gradient G) is given by the sum of the funda mental free-space singularity, a wave component W and a non-oscillatory local flow component L, as was already noted. Thus, numerical errors that stem from the approximation of the loca flow components in the representations of G and G are only one part among several sources of errors associated with panel methods. While the ideal approximations to G and G are highly accurate and eficient as well as very simple, this ideal goal is hard to reach in practice because accuracy, eficiency and simplicity are competing requirements.

The level of accuracy that is actually required for useful practical approximations to G and G therefore is a fairly complicated issue. This issue is partly considered in Wu et al. [12] for the similar theory of steady ship waves (linear potential flow around a ship hull that advances at a constant speed in calm water). Specifically, the errors due to a simple analytical approximation to the local flow component L in the Green function for steady ship waves are considered in that study. This approximate local flow component L, given in Noblesse et al. [13], is very simple and highly eficient, but not particularly accurate. Yet, this simple relatively crude approximation to the Green function for steady ship waves is found in Wu et al. [12] to yield predictions of sinkage, trim and drag that do not difer appreciably from the predictions obtained if the Green function is computed with high accuracy. This finding suggests that highly accurate approximations to the local flow components in the Green function G and its gradient G for the theory of wave difraction radiation similarly may not be necessary for practical purposes.

Simple approximations to the local flow components in the representations of G and G for wave difraction radiation considered in Wu et al. [14] are given here. These approximations are based on a pragmatic hybrid approach that combines numerical approximations with nearfield and far-field analytical expansions, in a manner similar to that used in Noblesse et al. [13] for the Green function of the theory of ship waves. The approximations obtained here are valid within the entire flow region, i.e. are global approximations, unlike the approximations for complementary contiguous regions given in the literature. The approximations to the local flow components given here only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments, and provide an eficient and particularly simple method for numerically evaluating the Green function $G _ { i }$ , and its gradient $_ { \nabla G }$ , for difraction radiation of time-harmonic waves in deep water. The global approximations to the local flow components in G and G given here are similar to, but considerably more accurate than, the approximations given in Wu et al. [15].

## 2 BASIC INTEGRAL REPRESENTATIONS

A Cartesian system of coordinates $\mathbf { X } \equiv ( X , Y , Z )$ is used. The Z axis is vertical and points upward, and the undisturbed free surface is taken as the plane $Z = 0$ . Difraction radiation of time harmonic waves with radian frequency ω and wavelength $\lambda = 2 \pi g / \omega ^ { 2 }$ , where g denotes the gravitational acceleration, is considered. Nondimensional coordinates

$$
\mathbf {x} \equiv (x, y, z) \equiv (X, Y, Z) \omega^ {2} / g\tag{1}
$$

are defined.

The Green function $G ( \mathbf { x } , \tilde { \mathbf { x } } )$ corresponds to the spatial component of a nondimensional velocity potential

$$
\mathrm{Re} \left[ G (\mathbf {x}, \tilde {\mathbf {x}}) e ^ {- \mathrm{i} \omega T} \right]\tag{2}
$$

where T denotes time. Expression (2) represents the potential of the flow created at the point $\mathbf { x } \equiv ( x , y , z \ \leq \ 0 )$ by a pulsating source located at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } \textrm { < } 0 )$ ), or by a flux through the free surface at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } = 0 )$

The nondimensional distances between the flow-field point x and the source point x˜ or its mirror image $\tilde { \mathbf { x } } _ { 1 } \equiv ( \tilde { x } , \tilde { y } , - \tilde { z } )$ with respect to the undisturbed free-surface plane $z = 0$ are denoted as r and d, and are given by

$$
r \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2} + (z - \tilde {z}) ^ {2}} \quad \text {and} \quad d \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2} + (z + \tilde {z}) ^ {2}}\tag{3}
$$

The horizontal and vertical components of the distance d between the points x and $\tilde { \mathbf { x } } _ { 1 }$ are given by

$$
0 \leq h \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2}} \quad \mathrm{and} \quad v \equiv z + \tilde {z} \leq 0\tag{4}
$$

The Green function G is expressed as

$$
4 \pi G = - 1 / r + L + W\tag{5}
$$

where $\cdot 1 / r$ is the fundamental free-space Green function, and L and W represent a local flow component and a wave component that account for free-surface efects. The component L corresponds to a non-oscillatory local flow and the component $W$ represents circular surface waves radiated by the pulsating singularity located at the source point $\tilde { \bf x }$ . The basic decomposition (5) into a local flow and waves is non unique, as was already noted. Indeed, three alternative decompositions and related integral representations are given in Noblesse [1].

The so-called near-field integral representation in Noblesse [1] is considered here. The wave component W in this representation is given by

$$
W (h, v) \equiv 2 \pi [ \widetilde {H} _ {0} (h) - \mathrm{i} J _ {0} (h) ] e ^ {v}\tag{6}
$$

![](images/0caa6ed2831b0bafba966b5e18a1b5362e0eb9c598d74c3218774a85272d9cbd.jpg)

![](images/4937d0cfc3a3f4ff15cf60c77ea6678b724747270c92581b7157d26abdb53493.jpg)  
Figure 1: Functions $\widetilde { H } _ { 0 } ( h )$ ), $\widetilde { H } _ { 1 } ( h ) - 2 / \pi , J _ { 0 } ( h )$ $J _ { 1 } ( h )$ for $0 \leq h \leq 2 5$  
Figure 2: Local flow component L and imaginary part of the wave component Im W for $h = 0$ and ${ \boldsymbol { \cdot } } 1 0 \leq v \leq 0$

where $\widetilde { H } _ { 0 } ( \cdot )$ and $J _ { 0 } ( \cdot )$ denote the zeroth-order Struve function and the zeroth-order Bessel function of the first kind. The corresponding local flow component L is given by

$$
L (h, v) \equiv - \frac {1}{d} - \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \mathrm{Re} e ^ {M} E _ {1} (M) d \theta \quad \mathrm{where} \quad M \equiv v + \mathrm{i} h \cos \theta\tag{7}
$$

and $E _ { 1 } ( \cdot )$ is the usual complex exponential integral function.

The gradient $\nabla G \equiv \left( G _ { x } , G _ { y } , G _ { z } \right)$ of the Green function G is expressed in Noblesse [1] as

$$
4 \pi G _ {z} \equiv \frac {z - \tilde {z}}{r ^ {3}} + L _ {z} + W \quad \mathrm{where} \quad L _ {z} = \frac {v}{d ^ {3}} - \frac {1}{d} + L\tag{8a}
$$

$$
4 \pi G _ {h} \equiv \frac {h}{r ^ {3}} + L _ {h} + W _ {h} \quad \mathrm{where} \quad L _ {h} = \frac {h}{d ^ {3}} + L _ {*}\tag{8b}
$$

$$
4 \pi G _ {x} \equiv G _ {h} \frac {x - \tilde {x}}{h} \quad \mathrm{and} \quad 4 \pi G _ {y} \equiv G _ {h} \frac {y - \tilde {y}}{h}\tag{8c}
$$

The wave component $W _ { h }$ in (8b) is given by

$$
W _ {h} (h, v) \equiv 2 \pi \left[ 2 / \pi - \widetilde {H} _ {1} (h) + \mathrm{i} J _ {1} (h) \right] e ^ {v}\tag{9}
$$

where $\widetilde { H } _ { 1 } ( \cdot )$ and $J _ { 1 } ( \cdot )$ denote the first-order Struve function and the first-order Bessel function of the first kind. The local flow component $L _ { * }$ in (8b) is given by

$$
L _ {*} (h, v) \equiv \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \mathrm{Im} [ e ^ {M} E _ {1} (M) - 1 / M ] \cos \theta d \theta\tag{10}
$$

where M is defined by (7).

The exponential function $e ^ { v }$ and the Bessel and Struve functions in expressions (6) and (9) for the wave components W and $W _ { h }$ are infinitely diferentiable. Moreover, several practical and eficient alternative approximations for the Bessel and Struve functions are given in the literature; notably in Hitchcock [16], Abramowitz & Stegun [17], Luke [18], Newman [19]. Fig.1 depicts the Struve functions $\widetilde { H } _ { 0 } ( h )$ and $\widetilde { H } _ { 1 } ( h ) - 2 / \pi$ and the Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ for $0 \leq h \leq 2 5$

![](images/0ecdda6343c7a4908c993197bc082fb74c94e33b26f340747ef4f370df674eec.jpg)

![](images/018e91261cac7441b128c52c2a238aa944182f29e3dd47504e4189d259b0a5e5.jpg)  
Figure 3: Real parts of the Green function and its vertical derivative, and related local flow and wave components, at the free surface $v = 0$ for $0 \leq h \leq 1 5$  
Figure 4: Real part of the horizontal derivative of the Green function and related local flow and wave components at the free surface $v = 0$ for $0 \leq$ $h \leq 1 5$

## 3 SPECIAL CASES

In the special case $h = 0$ , expressions (6) and (9) for the wave components $W$ and $W _ { h }$ become

$$
W (h = 0, v) = - \mathrm{i} 2 \pi e ^ {v} \quad \text { and } \quad W _ {h} (h = 0, v) = 4 e ^ {v}\tag{11a}
$$

Moreover, expression (7) yields $M = v$ and the integral representations (7) and (10) simplify as

$$
L (h = 0, v) = 1 / v - 2 e ^ {v} \operatorname{Re} E _ {1} (v + \mathrm{i} 0) \quad \text { and } \quad L _ {*} (h = 0, v) = - 4 e ^ {v}\tag{11b}
$$

Equations (8b), (11a) and (11b) then yield $G _ { h } = 0$ for $h = 0$ , in agreement with symmetry considerations. Fig.2 depicts the functions $L ( h = 0 , v )$ and Im $W ( h = 0 , v )$ for $- 1 0 \leq v \leq 0$

At the free-surface plane $v = 0$ , expressions (3-6), (8) and (9) yield

$$
4 \pi \mathrm{Re} G = - 1 / h + L (h, v = 0) + 2 \pi \widetilde {H} _ {0} (h) = 4 \pi \mathrm{Re} G _ {z}\tag{12a}
$$

$$
4 \pi \mathrm{Re} G _ {h} = 2 / h ^ {2} + L _ {*} (h, v = 0) + 2 \pi [ 2 / \pi - \widetilde {H} _ {1} (h) ]\tag{12b}
$$

The real parts 4π Re G and 4π Re $G _ { z }$ of the Green function G and its vertical derivative $G _ { z }$ at the free surface $v = 0$ , and the related local flow and wave components

$$
- 1 / h + L (h, v = 0) \quad \text { and } \quad 2 \pi \widetilde {H} _ {0} (h)\tag{13a}
$$

are depicted in Fig.3 for $0 \leq h \leq 1 5$ . Similarly, the real part 4π Re $G _ { h }$ of the horizontal derivative $G _ { h }$ of the Green function at the free surface $v = 0$ , and the related local flow and wave components

$$
2 / h ^ {2} + L _ {*} (h, v = 0) \quad \mathrm{and} \quad 2 \pi [ 2 / \pi - \widetilde {H} _ {1} (h) ]\tag{13b}
$$

are depicted in Fig.4 for $0 \leq h \leq 1 5$

Fig.3 and Fig.4 show that, at the free surface $v = 0$ , the local flow components dominate the wave components W and $W _ { h }$ for $0 ~ \leq ~ h ~ < ~ 1$ . However, the local flow components are significantly smaller than $W$ and $W _ { h }$ for $1 5 \leq h \ \mathrm { o r } \ 4 \leq \ h .$ , respectively. The wave components $W$ and $W _ { h }$ are infinitely diferentiable and can readily be evaluated, as was already noted. Simple approximations to the local flow components L and $L _ { * }$ defined by the integral representations (7) and (10) are now considered.

![](images/72e78e8f34ec9534dced8ebb0e7b03f7e3909239c0972b082575ec3fed68b29d.jpg)  
Figure 5: Local flow components L (lines without symbols) and $L ^ { a }$ (lines with symbols) defined by the integral representation (7) or the related approximation (17) for $0 \leq \rho \leq 1$ and $\alpha = 0$ , 0.2, 0.4, 0.6, 0.8, 1.

![](images/dd88352905f5591c06913fe0a2c0fb3dd26edb36d9fc8e12566fa54877361e68.jpg)  
Figure 6: Local flow components $L ,$ (lines without symbols) and $L _ { * } ^ { a }$ (lines with symbols) defined by the integral representation (10) or the related approximation (18) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2$ 1 0.4, 0.6, 0.8, 1.

## 4 PRACTICAL APPROXIMATIONS

The infinite flow region $0 \leq h < \infty , - \infty < v \leq 0$ is mapped onto the unit square

$$
0 \leq \rho \equiv d / (1 + d) \leq 1 \quad 0 \leq \beta \equiv h / d \leq 1\tag{14a}
$$

via the relations

$$
d = \rho / (1 - \rho) \qquad h = \beta d \qquad v = - \sqrt {1 - \beta^ {2}} d\tag{14b}
$$

The related variable $0 \leq \alpha \leq 1$ defined as

$$
\alpha \equiv - v / d \equiv \sqrt {1 - \beta^ {2}}\tag{15}
$$

is also used hereafter.

The local flow components $L$ and $L _ { * }$ defined by the integral representations (7) and (10) and the related local flow components $L _ { z }$ and $L _ { h }$ are approximated as

$$
L \approx L ^ {a} \qquad L _ {*} \approx L _ {*} ^ {a} \qquad L _ {z} \approx L _ {z} ^ {a} \equiv \frac {v}{d ^ {3}} - \frac {1}{d} + L ^ {a} \qquad L _ {h} \approx L _ {h} ^ {a} \equiv \frac {h}{d ^ {3}} + L _ {*} ^ {a}\tag{16}
$$

Hereafter, $L ^ { a } , L _ { * } ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ denote approximations to the local flow components $L , L _ { * } , L _ { z }$ and $L _ { h }$ , respectively.

The approximate local flow component $L ^ { a }$ is given by

$$
L ^ {a} \equiv - \frac {1}{d} + \frac {2 (d ^ {2} - v)}{1 + d ^ {3}} + \frac {2 e ^ {v}}{1 + d ^ {3}} \left(\log \frac {d - v}{2} + \gamma - 2 d ^ {2}\right) + 2 \rho (1 - \rho) ^ {3} R\tag{17a}
$$

![](images/6af0ae90dd7e53e1f03ab0952fa35620ab40f6ce36878a25cf652147c5193af6.jpg)  
Figure 7: Local flow components $L _ { z }$ (lines without symbols) and $L _ { z } ^ { a }$ (lines with symbols) defined by the integral representation (7), (8a) or the related approximation (16), (17) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

![](images/5f868310a66967921db4a7117886b8bd2440e0c4cc783bd0b9d593a28fa27fb7.jpg)  
Figure 8: Local flow components $L _ { h }$ (lines without symbols) and $L _ { h } ^ { a }$ (lines with symbols) defined by the integral representation (8b), (10) or the related approximation (16), (18) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

where $\gamma = 0 . 5 7 7 \dots$ . is Euler’s constant, $\rho$ is defined by (14a), and R is defined as

$$
R \equiv (1 - \beta) A - \beta B - \frac {\alpha C}{1 + 6 \alpha \rho (1 - \rho)} + \beta (1 - \beta) D\tag{17b}
$$

Here, α and $\beta$ are defined by (15) and (14a), and the polynomials $A ( \rho ) , B ( \rho ) , C ( \rho )$ and $D ( \rho )$ in (17b) are defined as

$$
A \equiv 1. 2 1 - 1 3. 3 2 8 \rho + 2 1 5. 8 9 6 \rho^ {2} - 1 7 6 3. 9 6 \rho^ {3} + 8 4 1 8. 9 4 \rho^ {4} - 2 4 3 1 4. 2 1 \rho^ {5} + 4 2 0 0 2. 5 7 \rho^ {6}
$$

$$
- 4 1 5 9 2. 9 \rho^ {7} + 2 1 8 5 9 \rho^ {8} - 4 8 3 8. 6 \rho^ {9}\tag{17c}
$$

$$
B \equiv 0. 9 3 8 + 5. 3 7 3 \rho - 6 7. 9 2 \rho^ {2} + 7 9 6. 5 3 4 \rho^ {3} - 4 7 8 0. 7 7 \rho^ {4} + 1 7 1 3 7. 7 4 \rho^ {5} - 3 6 6 1 8. 8 1 \rho^ {6}
$$

$$
+ 4 4 8 9 4. 0 6 \rho^ {7} - 2 9 0 3 0. 2 4 \rho^ {8} + 7 6 7 1. 2 2 \rho^ {9}\tag{17d}
$$

$$
C \equiv 1. 2 6 8 - 9. 7 4 7 \rho + 2 0 9. 6 5 3 \rho^ {2} - 1 3 9 7. 8 9 \rho^ {3} + 5 1 5 5. 6 7 \rho^ {4} - 9 8 4 4. 3 5 \rho^ {5} + 9 1 3 6. 4 \rho^ {6}\tag{17e}
$$

$$
D \equiv 0. 6 3 2 - 4 0. 9 7 \rho + 6 6 7. 1 6 \rho^ {2} - 6 0 7 2. 0 7 \rho^ {3} + 3 1 1 2 7. 3 9 \rho^ {4} - 9 6 2 9 3. 0 5 \rho^ {5} + 1 8 1 8 5 6. 7 5 \rho^ {6}
$$

$$
- 2 0 5 6 9 0. 4 3 \rho^ {7} + 1 2 8 1 7 0. 2 \rho^ {8} - 3 3 7 4 4. 6 \rho^ {9}\tag{17f}
$$

The approximate local flow component $L _ { * } ^ { a }$ is given by

$$
L _ {*} ^ {a} \equiv \frac {2}{1 + d ^ {3}} \left(\frac {\beta + h}{d - v} - 2 \beta + 2 e ^ {v} d - h\right) - 4 e ^ {- d} (1 - \beta) \left(1 + \frac {d}{1 + d ^ {3}}\right) + 2 \rho (1 - \rho) ^ {3} R _ {*}\tag{18a}
$$

where $R _ { * }$ is defined as

$$
R _ {*} \equiv \beta A _ {*} - (1 - \alpha) B _ {*} + \beta (1 - \beta) \rho (1 - 2 \rho) C _ {*}\tag{18b}
$$

![](images/161dbd57a71f19369f98798d094213f73e75dd604be2669b7107547beb6a4742.jpg)  
Figure 9: Absolute error 4π $e \equiv L - L ^ { a }$ between the local flow components $L$ and $L ^ { a }$ defined by the integral representation (7) or the related approximation (17) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6$ , 0.8, 1.

![](images/9656353f0fca90e4fc1c0137b7432541f8769630eb2db3c05ccb47b54b751753.jpg)  
Figure 10: Absolute error 4π $e _ { * } \equiv L _ { * } - L _ { * } ^ { a }$ between the local flow components $L _ { * }$ and $L _ { * } ^ { a }$ defined by the integral representation (10) or the related approximation (18) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2$ , 0.4, 0.6, 0.8, 1.

Here, the polynomials $A _ { * } ( \rho ) , B _ { * } ( \rho )$ and $C _ { * } ( \rho )$ in (18b) are defined as

$$
A _ {*} \equiv 2. 9 4 8 - 2 4. 5 3 \rho + 2 4 9. 6 9 \rho^ {2} - 7 5 4. 8 5 \rho^ {3} - 1 1 8 7. 7 1 \rho^ {4} + 1 6 3 7 0. 7 5 \rho^ {5} - 4 8 8 1 1. 4 1 \rho^ {6}
$$

$$
+ 6 8 2 2 0. 8 7 \rho^ {7} - 4 6 6 8 8 \rho^ {8} + 1 2 6 2 2. 2 5 \rho^ {9}\tag{18c}
$$

$$
B _ {*} \equiv 1. 1 1 + 2. 8 9 4 \rho - 7 6. 7 6 5 \rho^ {2} + 1 5 6 5. 3 5 \rho^ {3} - 1 1 3 3 6. 1 9 \rho^ {4} + 4 4 2 7 0. 1 5 \rho^ {5} - 9 7 0 1 4. 1 1 \rho^ {6}
$$

$$
+ 1 1 8 8 7 9. 2 6 \rho^ {7} - 7 6 2 0 9. 8 2 \rho^ {8} + 1 9 9 2 3. 2 8 \rho^ {9}\tag{18d}
$$

$$
C _ {*} \equiv 1 4. 1 9 - 1 4 8. 2 4 \rho + 8 4 7. 8 \rho^ {2} - 2 3 1 8. 5 8 \rho^ {3} + 3 1 6 8. 3 5 \rho^ {4} - 1 5 9 0. 2 7 \rho^ {5}\tag{18e}
$$

The approximations $L ^ { a }$ and $L _ { * } ^ { a }$ given by (17) and (18) hold within the entire flow region $0 \leq d$ and only involve real elementary continuous functions (algebraic, exponential, logarithmic).

Fig.5 depicts the local flow components L and $L ^ { a }$ defined by the integral representation (7) or the related approximation (17) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$ . Fig.6 similarly depicts the local flow components $L _ { * }$ and $L _ { * } ^ { a }$ given by the integral representation (10) or the related approximation (18) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$

Fig.7 depicts the local flow components $L _ { z }$ and $L _ { z } ^ { a }$ defined by the integral representation $( 7 )$ (8a) or the related approximation (16), (17) for $0 \leq \rho \leq 1$ and six values of $0 \leq \alpha \leq 1$ . Fig.8 similarly depicts the local flow components $L _ { h }$ and $L _ { h } ^ { a }$ given by the integral representation (8b), (10) or the related approximation (16), (18) for $0 \leq \rho \leq 1$ and six values of $0 < \alpha < 1$

The functions $L$ and $L ^ { a }$ in Fig.5, the functions $L _ { * }$ and $L _ { * } ^ { a }$ in Fig.6, the functions $L _ { z }$ and $L _ { z } ^ { a }$ in Fig.7, and the functions $L _ { h }$ and $L _ { h } ^ { a }$ in Fig.8 cannot be distinguished.

## 5 ERRORS IN THE GREEN FUNCTION AND ITS GRADIENT

The errors associated with the approximations $L ^ { a }$ and $L _ { * } ^ { a }$ given by (17) and (18) are now considered. The absolute errors e and $e _ { * }$ between the local flow components $L$ and $L _ { * }$ and the corresponding approximations $L ^ { a }$ and $L _ { * } ^ { a }$ in expressions (5) and (8) for the Green function and

![](images/d0ec8277f72043260a16389cefdb6aee7bc3805d1349d45f4d9399f3927f9585.jpg)

![](images/d4904c29bf0ff82fd1dce14938c83141389b08c2d4829a1a31c44311d785775b.jpg)  
Figure 11: Approximate relative error $e ^ { \prime } \equiv ( L -$ $L ^ { a } ) / L ^ { v = 0 }$ between the local flow components L and $L ^ { a }$ defined by the integral representation (7) or the approximation (17) for $0 \leq \rho \leq 1$ and $\alpha = 0$ 2 0.2, 0.4, 0.6, 0.8, 1.  
Figure 12: Approximate relative error $e _ { z } ^ { \prime } \equiv ( L _ { z } -$ $L _ { z } ^ { a } ) / L _ { z } ^ { v = 0 }$ between the local flow components $L _ { z }$ and $L _ { z } ^ { a }$ defined by the integral representation (7), (8a) or the approximation (16), (17) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

its gradient are defined as

$$
4 \pi e \equiv L - L ^ {a} \equiv L _ {z} - L _ {z} ^ {a} \qquad 4 \pi e _ {*} \equiv L _ {*} - L _ {*} ^ {a} \equiv L _ {h} - L _ {h} ^ {a}\tag{19}
$$

Along the vertical axis $\alpha = 1$ , one has $L _ { * } ^ { a } \equiv L _ { * }$ and therefore $e _ { * } \equiv 0$ . The relative errors associated with the approximate local flow components $L ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ are defined as

$$
e ^ {r} \equiv \frac {L - L ^ {a}}{L} \equiv \frac {4 \pi e}{L} \qquad e _ {z} ^ {r} \equiv \frac {L _ {z} - L _ {z} ^ {a}}{L _ {z}} \equiv \frac {4 \pi e}{L _ {z}} \qquad e _ {h} ^ {r} \equiv \frac {L _ {h} - L _ {h} ^ {a}}{L _ {h}} \equiv \frac {4 \pi e _ {*}}{L _ {h}}\tag{20}
$$

Figs 5, 7 and 8 show that the functions $L ( h , v ) , L _ { z } ( h , v )$ and $L _ { h } ( h , v )$ vanish at a point $\rho < 1$ if $v < 0$ , but do not vanish for $\rho < 1$ if $v = 0$ . The relative errors $e ^ { r } , e _ { z } ^ { r }$ and $e _ { h } ^ { r }$ defined by (20) are then approximated here via the modified relative errors $e ^ { \prime } , e _ { z } ^ { \prime }$ and $e _ { h } ^ { \prime }$ defined as

$$
e ^ {\prime} \equiv \frac {L - L ^ {a}}{L ^ {v = 0}} \qquad e _ {z} ^ {\prime} \equiv \frac {L _ {z} - L _ {z} ^ {a}}{L _ {z} ^ {v = 0}} \qquad e _ {h} ^ {\prime} \equiv \frac {L _ {h} - L _ {h} ^ {a}}{L _ {h} ^ {v = 0}}\tag{21}
$$

where $L ^ { v = 0 } \equiv L ( h , v = 0 ) , L _ { z } ^ { v = 0 } \equiv L _ { z } ( h , v = 0 )$ and $L _ { h } ^ { v = 0 } \equiv L _ { h } ( h , v = 0 )$ . The functions $e ^ { \prime } , e _ { z } ^ { \prime }$ and $e _ { h } ^ { \prime }$ defined by $( 2 1 )$ provide meaningful approximations to the relative errors associated with the approximations $L ^ { a } , L _ { z } ^ { a }$ and $L _ { h } ^ { a }$ within the entire flow region $0 \leq d$

It can be shown that the absolute errors e and $e _ { * }$ defined by (19) behave as

$$
e = O (d) \quad \text { as } d \to 0\tag{22a}
$$

$$
e = O (1 / d ^ {3}) \mathrm{if} \alpha \neq 0 \quad \mathrm{or} \quad e = O (\log d / d ^ {3}) \mathrm{if} \alpha = 0 \quad \mathrm{as} d \to \infty\tag{22b}
$$

$$
e _ {*} = O (d \log d) \quad \mathrm{as} d \to 0 \qquad e _ {*} = O (1 / d ^ {3}) \quad \mathrm{as} d \to \infty\tag{23}
$$

The relative errors (20) are now considered. The behaviors of the local flow components L and $L _ { * }$ defined by the integral representations (7) and (10) in the near-field and far-field limits d 0 and $d \to \infty$ are considered in Noblesse [1]. In particular, one has

![](images/95c9073c044965094a6d236f0d8c6cf63df2543eade678c7c95e7571591d7d29.jpg)

![](images/ed66668954d1588359ebd27cfcdcd7ce10131287cd9072b88e3643bed859d6ff.jpg)  
Figure 13: Approximate relative error $e _ { h } ^ { \prime } \equiv ( L _ { h } -$ $L _ { h } ^ { a } ) / L _ { h } ^ { v = 0 }$ between the local flow components $L _ { h }$ and $L _ { h } ^ { a }$ defined by the integral representation (8b), (10) or the approximation (16), (18) for $0 \le \rho \le$ 0.8 and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$  
Figure 14: Approximate relative error $e _ { h } ^ { \prime } \equiv ( L _ { h } -$ $L _ { h } ^ { a } ) / L _ { h } ^ { v = 0 }$ between the local flow components $L _ { h }$ and $L _ { h } ^ { a }$ defined by the integral representation (8b), (10) or the approximation (16), (18) for $0 \leq \rho \leq 1$ and $\alpha = 0 , 0 . 2 , 0 . 4 , 0 . 6 , 0 . 8 , 1$

$$
L _ {z} \sim - \alpha / d ^ {2} \mathrm{if} \alpha \neq 0 \quad \mathrm{or} \quad L _ {z} \sim - 2 / d \mathrm{if} \alpha = 0 \quad \mathrm{as} d \to 0\tag{24a}
$$

$$
L _ {z} \sim \alpha / d ^ {2} \mathrm{if} \alpha \neq 0 \mathrm{or} L _ {z} \sim - 4 / d \mathrm{if} \alpha = 0 \mathrm{as} d \to \infty\tag{24b}
$$

$$
L _ {z} \sim - \alpha / d ^ {2} \text {if} \alpha \neq 0 \text {or} L _ {z} \sim - 2 / d \text {if} \alpha = 0 \text {as} d \to 0\tag{25a}
$$

$$
L _ {z} \sim \alpha / d ^ {2} \mathrm{if} \alpha \neq 0 \mathrm{or} L _ {z} \sim - 4 / d \mathrm{if} \alpha = 0 \mathrm{as} d \to \infty\tag{25b}
$$

$$
L _ {h} \sim \beta / d ^ {2} \mathrm{if} \alpha \neq 1 \quad \mathrm{or} \quad L _ {h} \rightarrow - 4 \mathrm{if} \alpha = 1 \quad \mathrm{as} d \rightarrow 0\tag{26a}
$$

$$
L _ {h} \sim - \beta / d ^ {2} \mathrm{if} \alpha \neq 0 \mathrm{or} 1 \quad \mathrm{or} L _ {h} \sim 3 / d ^ {2} \mathrm{if} \alpha = 0 \quad \mathrm{as} d \to \infty\tag{26b}
$$

Moreover, equations (8b) and (11b) yield $L _ { h } = - 4 e ^ { v } { \mathrm { ~ i f ~ } } \alpha = 1$

Expressions (22) and (24) show that the relative error $e ^ { r }$ defined by (20) behaves as

$$
e / L = O (d ^ {2}) \quad \mathrm{as} d \to 0\tag{27a}
$$

$$
e / L = O (1 / d ^ {2}) \text {if} \alpha \neq 0 \quad \text {or} \quad e / L = O (\log d / d ^ {2}) \text {if} \alpha = 0 \quad \text {as} d \to \infty\tag{27b}
$$

One then has $e \ll L$ in both the near field and the far field. Expressions (22) and (25) similarly show that the relative error $e _ { z } ^ { r }$ defined by (20) behaves as

$$
e / L _ {z} = O (d ^ {3}) \text {if} \alpha \neq 0 \text {or} e / L _ {z} = O (d ^ {2}) \text {if} \alpha = 0 \text {as} d \to 0\tag{28a}
$$

$$
e / L _ {z} = O (1 / d) \text {if} \alpha \neq 0 \text {or} e / L _ {z} = O (\log d / d ^ {2}) \text {if} \alpha = 0 \text {as} d \to \infty\tag{28b}
$$

One then has $e \ll L _ { z }$ in both the near field and the far field. Expressions (23) and (26) likewise show that the relative error $e _ { h } ^ { r }$ defined by (20) behaves as

$$
e _ {*} / L _ {h} = O (d ^ {3} \log d) \text {as} d \to 0 \text {if} \alpha \neq 1 \quad e _ {*} / L _ {h} = O (1 / d) \text {as} d \to \infty \text {if} \alpha \neq 1\tag{29}
$$

Along the vertical axis $\alpha = 1$ , one has $e _ { * } \equiv 0$ , as was already noted. One then has $e _ { * } \ll L _ { h }$ in both the near field and the far field.

Computations within the entire region $0 \leq d$ show that the absolute errors e and $e _ { * }$ defined by (19) vary within the ranges $- 3 \times 1 0 ^ { - 4 } < e < 3 \times 1 0 ^ { - 4 }$ and $- 2 . 4 \times 1 0 ^ { - 4 } < e _ { * } < 2 . 6 \times 1 0 ^ { - 4 }$ Fig.9 and Fig.10 depict the errors e and $e _ { * }$ for $0 \leq \rho \leq 1$ and six values of α. Fig.9 and Fig.10 show that the errors e and $e _ { * }$ vanish both as $\rho \to 0$ and as $\rho  1$ , in accordance with (22) and (23). The errors e and $e _ { * }$ for the six values of α considered in Fig.9 and Fig.10 are of the same order of magnitude, and oscillate between positive and negative values that are distributed more or less evenly. Fig.10 shows that $e _ { * } \equiv 0$ along the vertical axis $\alpha = 1$ , as was already noted.

Fig.11 and Fig.12 depict the approximate relative errors $e ^ { \prime }$ and $e _ { z } ^ { \prime }$ for $0 \leq \rho \leq 1$ and six values of α. Computations within the entire region show that $e ^ { \prime }$ and $e _ { z } ^ { \prime }$ vary within the ranges $- 0 . 4 5 \times 1 0 ^ { - 2 } < e ^ { \prime } < 0 . 4 3 \times 1 0 ^ { - 2 }$ and $- 0 . 3 4 \times 1 0 ^ { - 2 } < e _ { z } ^ { \prime } < 0 . 3 2 \times 1 0 ^ { - 2 } .$ . Fig.13 and Fig.14 similarly depict the approximate relative error $\boldsymbol { e } _ { h } ^ { \prime }$ for $0 \leq \rho \leq 0 . 8 ~ \mathrm { o r } ~ 0 \leq \rho \leq 1$ . The errors $e ^ { \prime } , e _ { z } ^ { \prime }$ and $e _ { h } ^ { \prime }$ in Fig.11-Fig.13 are relatively small and of the same order of magnitude. Fig.14 shows that the error $\boldsymbol { e } _ { h } ^ { \prime }$ is significantly larger in the far field $0 . 8 \leq \rho \leq 1$ . Indeed, computations within the entire region show that $\boldsymbol { e } _ { h } ^ { \prime }$ vary within the range $- 4 . 3 3 \times 1 0 ^ { - 2 } < e _ { h } ^ { \prime } < 4 . 7 3 \times 1 0 ^ { - 2 }$ . However, Fig.10 shows that the absolute error $e _ { * }$ that corresponds to the relative error $\boldsymbol { e } _ { h } ^ { \prime }$ is small in the range $0 . 8 \leq \rho \leq 1$ where $\boldsymbol { e } _ { h } ^ { \prime }$ is large. Specifically, Fig.10 shows that the absolute error $| e _ { * } |$ is smaller than $1 0 ^ { - 4 }$ for $0 . 8 \le \rho \le 1$ . Fig.11-Fig.14 show that the relative errors $e ^ { \prime } , e _ { z } ^ { \prime }$ and $e _ { h } ^ { \prime }$ vanish in both the near field $\rho \to 0$ and the far field $\rho  1$ . Moreover, Fig.13 and Fig.14 show that one has $e _ { * } \equiv 0$ and therefore $\boldsymbol { e } _ { h } ^ { \prime } \equiv 0$ along the vertical axis $\alpha = 1$

## 6 CONCLUSIONS

The Green function $G$ in the classical theory of wave difraction radiation by an ofshore structure, or a ship at low speed, in deep water is expressed in the usual manner as the sum of the fundamental free-space sigularity $- 1 / r$ , a non-oscillatory local flow $L ,$ and waves W. The gradient of G is similarly expressed as the sum of three basic components. The wave components W and $W _ { h }$ in these basic decompositions of G and G are expressed in terms of real functions of one variable, specifically the exponential function $e ^ { v }$ , the Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ and the Struve functions $\widetilde { H } _ { 0 } ( h )$ and $\widetilde { H } _ { 1 } ( h )$ . These functions are infinitely diferentiable and can be readily evaluated; e.g. Hitchcock [16], Abramowitz & Stegun [17], Luke [18], Newman [19].

The analytical approximations to the local flow components in the expressions for G and G given here are global approximations valid within the entire flow region, and only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments. The analysis of the errors associated with the approximations to the local flow components given here and in Wu et al. [14] shows that the approximations are suficiently accurate for practical purposes. These global approximations provide a particularly simple and highly eficient way of numerically evaluating G and G for difraction radiation of regular waves in deep water.

## REFERENCES

[1] Noblesse, F. The Green function in the theory of radiation and difraction of regular water waves by a body. Journal of Engineering Mathematics (1982) 16(2):137-169.

[2] Telste J.G. and Noblesse F. Numerical evaluation of the Green function of water-wave radiation and difraction. Journal of Ship Research (1986) 30(2):69-84.

[3] Newman J.N. An expansion of the oscillatory source potential. Applied Ocean Research (1984) 6(2):116-117.

[4] Newman J.N. Algorithms for the free-surface Green function. Journal of Engineering Mathematics (1985) 19(1):57-67.

[5] Wang R.S. The numerical approach of three dimensional free-surface Green function and its derivatives. Journal of Hydrodynamics (Ser.A) (1992) 7(3):277-286.

[6] Zhou Q., Zhang G. and Zhu L. The fast calculation of free-surface wave Green function and its derivatives. Chinese Journal of Computational Physics (1999) 16(2):113-120.

[7] Ponizy B., Noblesse F., Ba M. and Guilbaud M. Numerical evaluation of free-surface Green functions. Journal of Ship Research (1994) 38(3):193-202.

[8] Peter M.A. and Meylan M.H. The eigenfunction expansion of the infinite depth free surface Green function in three dimensions. Wave Motion (2004) 40(1):1-11.

[9] Yao X.L., Sun S.L., Wang S.P. and Yang S.T. The research on the highly eficient calculation method of 3-D frequency-domain Green function. Journal of Marine Science and Application (2009) 8(3):196-203.

[10] D’el´ıa J., Battaglia L. and Storti M. A semi-analytical computation of the Kelvin kernel for potential flows with a free surface. Comput. Appl. Math. (2011) 30(2):267-287.

[11] Shen Y., Yu D., Duan W. and Ling H. Ordinary diferential equation algorithms for a frequency-domain water wave Green’s function. J. Eng. Math. (2016) 100(1):53-66.

[12] Wu H., Zhang C., Ma C., Huang F., Yang C., and Noblesse F. Errors due to a practical Green function for steady ship waves. Eur. J. Mech. B/Fluids (2016) 55:162-169.

[13] Noblesse F., Delhommeau G., Huang F. and Yang C. Practical mathematical representation of the flow due to a distribution of sources on a steadily advancing ship hull. Journal of Engineering Mathematics (2011) 71(4):367-392.

[14] Wu H., Zhang C., Zhu Y., Li W., Wan D. and Noblesse F. A global approximation to the Green function for difraction radiation of water waves. (2017) Submitted.

[15] Wu H., Ma C., Zhu Y., Yang Z., Li W. and Noblesse F. Approximations of the Green function for difraction radiation of water waves. The 26th International Ocean and Polar Engineering Conference, Rhodes, Greece, (2016) 134-139.

[16] Hitchcock A.J.M. Polynomial approximations to Bessel functions of order zero and one and to related functions. Mathematics of Computation (1957) 11(58):86-88.

[17] Abramowitz M. and Stegun I.A. Handbook of mathematical functions. Dover, New York.

[18] Luke Y.L. Mathematical functions and their approximations. Academic Press, New York.

[19] Newman J.N. Approximations for the Bessel and Struve functions. Mathematics of Computation (1984) 43(168):551-556.