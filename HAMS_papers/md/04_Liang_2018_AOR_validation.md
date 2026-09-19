# Validation of a global approximation for wave diffraction-radiation in deep water

![](images/0a309e72f1d013366b5fbafcadb660274a02ef163f9317bdec2438287b55ecc2.jpg)

Hui Liang<sup>a</sup>, Huiyu Wu<sup>b</sup>, Francis Noblesse<sup>b,∗</sup>

<sup>a</sup> Deepwater Technology Research Centre (DTRC), Bureau Veritas 117674, Singapore <sup>b</sup> State Key Laboratory ofOcean Engineering, Collaborative Innovation Centerfor Advanced Ship and Deep-Sea Exploration, School ofNaval Architecture, Ocean & Civil Engineering, ShanghaiJiao Tong University, Shanghai, China

## a r t i c l e i n f o

Article history: Received 5 January 2018 Received in revised form 15 February 2018 Accepted 27 February 2018

Keywords: Wave diffraction/radiation Green function Global approximation

## a b s t r a c t

Computations of linear wave loads and second-order mean drift forces for a hemisphere and a freely floating FPSO show that global analytical approximations, given by Wu et al. in 2017, to the local flow components in the Green function and its gradient yield numerical predictions that closely agree with numerical results obtained via a highly-accurate Green function, as well as analytical results for a hemisphere. The computations reported here provide strong evidence that the global analytical approximations, valid within the entire flow region, are sufficiently accurate to compute linear and mean drift wave loads in practice.

© 2018 Elsevier Ltd. All rights reserved.

## 1. Introduction

Boundary integral equations related to the linear potential flow theory of diffraction-radiation of regular (time-harmonic) water waves are routinely solved to predict wave loads and wave-induced motions of large floating structures [1–5]. An essential ingredient of that classical method is the Green function that satisfies the linearized boundary condition at the free surface and the radiation condition [6]. Practical, reliable predictions of wave loads and wave-induced motions require that the Green function, and its gradient, be evaluated efficiently and with sufficient accuracy.

The Green function can be expressed as the sum ofthe free-space singularity (Rankine source) and a component that accounts for the free surface. This free-surface component can be further decomposed into a non-oscillatory local flow component and a wave component, which is dominant in the far field [7]. The wave component in this basic decomposition is defined in terms of special (real) functions (Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H } _ { 1 }$ and Bessel functions J andJ ) of a single variable. These functions are finite and smooth everywhere, and can be evaluated accurately and efficiently [8–11].

The non-oscillatory local flow components in the expressions for the Green function and its gradient are real functions of two variables and are defined by single integrals. Nearfield and farfield analytical approximations to these local flow components are given in [7] and used in [12]. These analytical approximations can also be used to remove the nearfield singularities and to reduce the unbounded region to a finite region, and thus make it possible to use polynomial approximations within contiguous flow regions [13,14] or table interpolation [15].

The nearfield and farfield analytical approximations to the local flow components in the Green function and its gradient are also used in [16] to obtain global analytical approximations that are valid within the entire flow region. These global approximations are less accurate than the approximations based on series expansions [12], polynomial approximations within contiguous flow regions [13,14] or table interpolation [15] previously given in the literature, but are a particularly simple and intellectually satisfying alternative. Moreover, global approximations offer a significant practical advantage because they avoid the need for “ifstatements”, required if different approximations are used within complementary contiguous regions, and are then especially well suited for highly efficient parallel computations.

The error analysis given in [16] suggests that the global analytical approximations given in that study could be expected to be sufficiently accurate for most practical applications. However, the error analysis given in [16] is limited and insufficient. Indeed, a more solid conclusion requires computations of linear wave loads and second-order mean drift forces. Such computations are reported here for a hemisphere and a Floating Production Storage and Offloading (FPSO) unit.

## 2. Green function and basic decomposition

Thus, the Green function related to diffraction-radiation of regular (time-harmonic) water waves in the lower half space $Z \le 0$ is now considered. A Cartesian coordinate system XYZ is defined. The XY plane coincides with the undisturbed free surface and the Z axis points upward. Time-harmonic flows associated with flow potentials of the form

$$
\Re \left[ \Phi (\mathbf {X}) e ^ {- i \omega T} \right]\tag{1}
$$

are considered, and nondimensional coordinates are defined as

$$
(x, y, z) \equiv (X, Y, Z) \omega^ {2} / g\tag{2}
$$

Here, ω denotes the circular frequency and g is the acceleration of gravity. The Green function $G ( { \pmb x } , { \pmb \xi } )$ , where $\pmb { x } \equiv ( x , y , z \leq 0 )$ and ${ \pmb \xi } \equiv \left( \xi , \eta , \zeta \leq 0 \right)$ denote a flow-field point and a source point, is  expressed in [6] as

$$
4 \pi G = \frac {- 1}{r} - \frac {1}{d} - 2 \left[ \int_ {0} ^ {\infty} \frac {\mathrm{e} ^ {k v}}{k - 1} J _ {0} (k h) d k + \mathrm{i} \pi \mathrm{e} ^ {v} J _ {0} (h) \right]\tag{3}
$$

where $h , \nu , r$ and d are defined as

$$
h \equiv \sqrt {\left(x - \xi\right) ^ {2} + (y - \eta) ^ {2}}, \quad \nu \equiv z + \zeta \leq 0,\tag{4a}
$$

$$
r \equiv \sqrt {h ^ {2} + (z - \zeta) ^ {2}}, d \equiv \sqrt {h ^ {2} + (z + \zeta) ^ {2}} = \sqrt {h ^ {2} + v ^ {2}},\tag{4b}
$$

and $J _ { 0 } ( \cdot )$ is the zeroth-order Bessel function of the first kind

The Green function G can be expressed as

$$
4 \pi G = - 1 / r - 1 / d + L + W\tag{5}
$$

where L represents a non-oscillatory local flow component and W is a wave component. The basic decomposition (5) of the Green function is not unique. Several alternative representations are considered in [7]. The representation (5.11) in [7] is adopted here. The wave component W in this representation is given by

$$
W = 2 \pi \mathrm{e} ^ {\nu} \left[ \tilde {H} _ {0} (h) - \mathrm{i} J _ {0} (h) \right]\tag{6}
$$

where $\tilde { H } _ { 0 } ( \cdot )$ denotes the zeroth-order Struve function. The local flow component L in (5) is given by

$$
L = - \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \Re \left[ e ^ {M} E _ {1} (M) \right] d \theta \quad \text { where } \quad M \equiv \nu + i h \cos \theta\tag{7}
$$

and E (·) denotes the complex exponential-integral function. The gradient of the Green function is given by

$$
4 \pi G _ {z} = \frac {z - \zeta}{r ^ {3}} + \frac {\nu}{d ^ {3}} + L _ {z} + W \quad \text { where } \quad L _ {z} = \frac {- 1}{d} + L\tag{8a}
$$

$$
4 \pi G _ {h} = \frac {h}{r ^ {3}} + \frac {h}{d ^ {3}} + L _ {h} + W _ {h}\tag{8b}
$$

$$
4 \pi G _ {x} = \frac {x - \xi}{h} G _ {h} \quad \mathrm{and} \quad 4 \pi G _ {y} = \frac {y - \eta}{h} G _ {h}\tag{8c}
$$

The derivatives $W _ { h } \equiv \partial W / \partial h$ and $L _ { h } \equiv \partial L / \partial h$ are given by

$$
W _ {h} = 2 \pi \mathrm{e} ^ {\nu} [ 2 / \pi - \tilde {H} _ {1} (h) + \mathrm{i} J _ {1} (h) ]\tag{9}
$$

where $\tilde { H } _ { 1 } ( \cdot )$ and $J _ { 1 } ( \cdot )$ denote the first-order Struve function and the first-order Bessel function of the first kind, respectively, and

$$
L _ {h} = \frac {4}{\pi} \int_ {0} ^ {\frac {\pi}{2}} \Im \left[ e ^ {M} E _ {1} (M) - \frac {1}{M} \right] \cos \theta d \theta\tag{10}
$$

The wave components Wand $W _ { h }$ defined by (6) and (9) are indefinitely differentiable. Practical polynomial approximations to the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H } _ { 1 }$ and the Bessel functions $J _ { 0 }$ and ${ . J _ { 1 } }$ are given in e.g. [8,9], and the wave component W and its derivative $W _ { h }$ in (5) and (8) can then be evaluated efficiently and very simply.

The local flow components $L ( h , \nu )$ and $L _ { h } ( h , \nu )$ ) defined by (7) and (10) vanish as $d \to \infty$ and are singular as $d \to 0 .$ . In particular, in the limit $d \to 0 , [ 7 , 1 6 ]$ show that one has

$$
L \sim 2 \left(\log \frac {d - v}{2} + \gamma\right) \quad \text { and } \quad L _ {h} \sim \frac {2 h}{d - v} \left(\frac {1}{d} + 1\right) - 4\tag{11}
$$

where $\gamma \approx 0 . 5 7 7$ is Euler’s constant. The functions $L ( h , \nu )$ and $L _ { h } ( h , \nu )$ are depicted in Figs. 8 and 9 of [16].

## 3. Global approximations to the local components L and $\mathbf { L } _ { h }$

The local flow components L and $L _ { h }$ can be evaluated, very simply and efficiently, via the global analytical approximations obtained in [16] by extending the nearfield and farfield approximations given in [7]. These practical global approximations, valid within the entire flow region $( 0 \leq h , \nu \leq 0 )$ ), are now considered. The three parameters

$$
0 \leq \alpha \equiv \frac {- v}{d} \leq 1, \quad 0 \leq \beta \equiv \frac {h}{d} \leq 1, \quad 0 \leq \rho \equiv \frac {d}{1 + d} <   1\tag{12}
$$

are used.

The local flow component L defined by the integral (7) is approximated in [16] as

$$
L \approx L ^ {a} \equiv 2 P / (1 + d ^ {3}) + 2 \rho (1 - \rho) ^ {3} R \text { where }\tag{13a}
$$

$$
P \equiv \mathrm{e} ^ {\nu} \left(\log \frac {d - \nu}{2} + \gamma - 2 d ^ {2}\right) + d ^ {2} - \nu \text { and }\tag{13b}
$$

$$
R \equiv (1 - \beta) A - \beta B - \frac {\alpha C}{1 + 6 \alpha \rho (1 - \rho)} + \beta (1 - \beta) D\tag{13c}
$$

A, B, C and D in (13c) are polynomials in $\rho$ defined as

$$
\begin{array}{r c l} A & \equiv & + 1. 2 1 - 1 3. 3 2 8 \rho + 2 1 5. 8 9 6 \rho^ {2} - 1 7 6 3. 9 6 \rho^ {3} + 8 4 1 8. 9 4 \rho^ {4} \\ & & - 2 4 3 1 4. 2 1 \rho^ {5} + 4 2 0 0 2. 5 7 \rho^ {6} - 4 1 5 9 2. 9 \rho^ {7} \\ & & + 2 1 8 5 9 \rho^ {8} - 4 8 3 8. 6 \rho^ {9} \end{array}\tag{14a}
$$

$$
\begin{array}{r c l} B & \equiv & + 0. 9 3 8 + 5. 3 7 3 \rho - 6 7. 9 2 \rho^ {2} + 7 9 6. 5 3 4 \rho^ {3} - 4 7 8 0. 7 7 \rho^ {4} \\ & & + 1 7 1 3 7. 7 4 \rho^ {5} - 3 6 6 1 8. 8 1 \rho^ {6} + 4 4 8 9 4. 0 6 \rho^ {7} \\ & & - 2 9 0 3 0. 2 4 \rho^ {8} + 7 6 7 1. 2 2 \rho^ {9} \end{array}\tag{14b}
$$

$$
\begin{array}{r c l} C & \equiv & + 1. 2 6 8 - 9. 7 4 7 \rho + 2 0 9. 6 5 3 \rho^ {2} - 1 3 9 7. 8 9 \rho^ {3} + 5 1 5 5. 6 7 \rho^ {4} \\ & & - 9 8 4 4. 3 5 \rho^ {5} + 9 1 3 6. 4 \rho^ {6} - 3 2 7 2. 6 2 \rho^ {7} \end{array}\tag{14c}
$$

$$
\begin{array}{r c l} D & \equiv & + 0. 6 3 2 - 4 0. 9 7 \rho + 6 6 7. 1 6 \rho^ {2} - 6 0 7 2. 0 7 \rho^ {3} + 3 1 1 2 7. 3 9 \rho^ {4} \\ & & - 9 6 2 9 3. 0 5 \rho^ {5} + 1 8 1 8 5 6. 7 5 \rho^ {6} - 2 0 5 6 9 0. 4 3 \rho^ {7} \\ & & + 1 2 8 1 7 0. 2 \rho^ {8} - 3 3 7 4 4. 6 \rho^ {9} \end{array}\tag{14d}
$$

The local flow velocity component $L _ { h }$ defined by (10) is similarly approximated in [16] as

$$
L _ {h} \approx L _ {h} ^ {a} \equiv 2 P _ {*} / (1 + d ^ {3}) - 4 Q _ {*} + 2 \rho (1 - \rho) ^ {3} R _ {*}\tag{15a}
$$

$$
\text { where } \quad P _ {*} \equiv (\beta + h) / (d - v) - 2 \beta + 2 d e ^ {v} - h,\tag{15b}
$$

$$
Q _ {*} \equiv \mathrm{e} ^ {- d} (1 - \beta) \left(1 + \frac {d}{1 + d ^ {3}}\right) \quad \text { and }\tag{15c}
$$

![](images/7e93824641770e3d60b2845b19eb897422850235ae7e12950ea93bfdde9c885f.jpg)  
Fig. 1. Errors $L - L ^ { a } \left( \mathrm { t o p } \right)$ and $L _ { h } - L _ { h } ^ { a }$ (bottom) associated with the global approximations L<sup>a</sup> and $L _ { h } ^ { a }$ to the local flow components L and $L _ { h }$ for $0 { \le } h { \le } 5$ and $- 5 \leq \nu \leq 0 .$

$$
R _ {*} \equiv \beta A _ {*} - (1 - \alpha) B _ {*} + \beta (1 - \beta) \rho (1 - 2 \rho) C _ {*}\tag{15d}
$$

A , B and C in (15d) are polynomials in $\rho$ defined as

$$
\begin{array}{r c l} A _ {*} & \equiv & + 2. 9 4 8 - 2 4. 5 3 \rho + 2 4 9. 6 9 \rho^ {2} - 7 5 4. 8 5 \rho^ {3} - 1 1 8 7. 7 1 \rho^ {4} \\ & & + 1 6 3 7 0. 7 5 \rho^ {5} - 4 8 8 1 1. 4 1 \rho^ {6} + 6 8 2 2 0. 8 7 \rho^ {7} \\ & & - 4 6 6 8 8 \rho^ {8} + 1 2 6 2 2. 2 5 \rho^ {9} \end{array}\tag{16a}
$$

$$
\begin{array}{r c l} B _ {*} & \equiv & + 1. 1 1 + 2. 8 9 4 \rho - 7 6. 7 6 5 \rho^ {2} + 1 5 6 5. 3 5 \rho^ {3} - 1 1 3 3 6. 1 9 \rho^ {4} \\ & & + 4 4 2 7 0. 1 5 \rho^ {5} - 9 7 0 1 4. 1 1 \rho^ {6} + 1 1 8 8 7 9. 2 6 \rho^ {7} \\ & & - 7 6 2 0 9. 8 2 \rho^ {8} + 1 9 9 2 3. 2 8 \rho^ {9} \end{array}\tag{16b}
$$

$$
\begin{array}{r c l} C _ {*} & \equiv & + 1 4. 1 9 - 1 4 8. 2 4 \rho + 8 4 7. 8 \rho^ {2} - 2 3 1 8. 5 8 \rho^ {3} \\ & & + 3 1 6 8. 3 5 \rho^ {4} - 1 5 9 0. 2 7 \rho^ {5} \end{array}\tag{16c}
$$

The errors $L ( h , \nu ) - L ^ { a } ( h , \nu )$ and $L _ { h } ( h , \nu ) - L _ { h } ^ { a } ( h , \nu )$ associated with the global approximations $L ^ { a }$ and $L _ { h } ^ { a }$ to the local flow components L and $L _ { h }$ are depicted in Fig. 1. This figure shows that the errors are very small in both the nearfield $d \ll 1$ and the farfield $1 \ll d ,$ but are appreciable and vary between positive and negative values of the order of $3 \times 1 0 ^ { - 3 }$ for intermediate distances d in the vicinity of d = 2 for L or d = 1 for $L _ { h }$

![](images/0bc17620df316cd18d2f6fa426dabfb1a64b304c05d1282013871315a62e128c.jpg)  
Fig. 2. Mesh used to discretize a hemisphere via 1761 nodes and 1720 quadrilateral elements.

## 4. Computation of wave loads

Computations of linear and mean drift wave loads are now considered for a hemisphere and a freely floating FPSO. A constant panel (zeroth-order) boundary element method based on combined source and dipole distributions is used. Irregular frequencies are removed via extension ofthe flow region to the waterplane area [17–19]. Specifically, the integral equations

$$
\begin{array}{r l} & {\frac {1}{2} \phi (\boldsymbol {x}) + \iint_ {\Sigma^ {H}} \phi (\boldsymbol {\xi}) \frac {\partial G (\boldsymbol {x} , \boldsymbol {\xi})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S + \iint_ {\Sigma^ {I}} \mu (\boldsymbol {\xi}) \frac {\partial G (\boldsymbol {x} , \boldsymbol {\xi})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S} \\ & {\qquad = \iint_ {\Sigma^ {H}} G (\boldsymbol {x}, \boldsymbol {\xi}) \frac {\partial \phi (\boldsymbol {\xi})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S \text {on} \Sigma^ {H} \text {and}} \\ & {\mu (\boldsymbol {x}) + \iint_ {\Sigma^ {H}} \phi (\boldsymbol {\xi}) \frac {\partial G (\boldsymbol {x} , \boldsymbol {\xi})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S + \iint_ {\Sigma^ {I}} \mu (\boldsymbol {\xi}) \frac {\partial G (\boldsymbol {x} , \boldsymbol {\xi})}{\bar {n} _ {\boldsymbol {\xi}}} \mathrm{d} S} \\ & {\qquad = \iint_ {\Sigma^ {H}} G (\boldsymbol {x}, \boldsymbol {\xi}) \frac {\partial \phi (\boldsymbol {\xi})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S \text {on} \Sigma^ {I}} \end{array}\tag{17a}
$$

(17b)

are solved to determine the flow potential  on the hull surface $\Sigma ^ { H }$ of the floating body and the density $\mu$ of the dipole distribution over the interior free surface <sup>I</sup>. The singular Rankine source component $1 / r + 1 / d \mathrm { i n } ( 5 )$ and its gradient in (8) are analytically integrated over a flat panel [20,21], and the weakly-singular local flow component L and its gradient in (5) or (8) are numerically integrated via a Gaussian quadrature rule with 4 Gaussian points in the nearfield and 1 point in the farfield.

Numerical solutions of the integral equations (17) in which a highly-accurate method based on [7,13,12], with errors of order $1 0 ^ { - 6 }$ , is used to evaluate the local flow components L and $L _ { h } ,$ or the less accurate global analytical approximations L<sup>a</sup> and $L _ { h } ^ { a }$ are used, are compared below for a hemisphere and a freely floating FPSO.

## 4.1. Wave radiation and diffraction by a hemisphere

Wave radiation by a floating hemisphere, for which an analytical solution exists [22], is considered first. The hemisphere is discretized via 1720 quadrilateral elements as in Fig. 2. The addedmass coefficients $a _ { 1 1 }$ and $a _ { 3 3 }$ for surge and heave are adimensional with respect to $2 \pi \rho R ^ { 3 } / 3$ , and the corresponding wave-damping coefficients $b _ { 1 1 }$ and $b _ { 3 3 }$ are adimensional with respect to 2 $\rho \omega R ^ { 3 } / 3$ where $\rho$ denotes the water density, R is the radius ofthe hemisphere and ω is the circular frequency of its time-harmonic oscillatory motions.

These adimensional added-mass and wave-damping coefficients are depicted in Fig. 3 and listed in Tables 1–4for adimensional wavenumbers $0 { < } k _ { 0 } R { \le } 1 0$ where $k _ { 0 } \equiv \omega ^ { 2 } / g .$ . Fig. 3 shows that the numerical solutions ofthe integral equations (17) in which the local flow components in G and ∇G are evaluated via the global analytical approximations (13) and (15) are in excellent agreement with Hulme’s analytical results [22].

Table 2  
![](images/40530badab8870ae1a38cab60eddfae5b88c7f21380011c4969930124642284d.jpg)

![](images/57c2d156e6004a3b0fcf9bdff372ce3f6b75c8fe3bd707fd1cb0a7edd861574b.jpg)  
Fig. 3. Adimensional added-mass and wave-damping coefficients $a _ { 1 1 }$ and $b _ { 1 1 }$ for surge (top), and corresponding coefficients a and $b _ { 3 3 }$ for heave (bottom), predicted by Hulme’s analytical solution [22] or a panel method where the local flow components in G and ∇G are evaluated via the global analytical approximations given in [16].

Variation of the adimensional surge added-mass coefficient $a _ { 1 1 }$ with respect to the adimensional wavenumber k R.

<table><tr><td> $k_0R$ </td><td> $a_{11}^{\text{Hulme}}$ </td><td> $a_{11}^{\text{Accurate}}$ </td><td> $a_{11}^{\text{Global}}$ </td><td> $E^{\text{Accurate}}$ </td><td> $E^{\text{Global}}$ </td></tr><tr><td>0.1</td><td>0.5223</td><td>0.5228</td><td>0.5228</td><td> $5.25 \times 10^{-4}$ </td><td> $5.18 \times 10^{-4}$ </td></tr><tr><td>0.2</td><td>0.5515</td><td>0.5520</td><td>0.5520</td><td> $4.88 \times 10^{-4}$ </td><td> $5.25 \times 10^{-4}$ </td></tr><tr><td>0.3</td><td>0.5848</td><td>0.5852</td><td>0.5852</td><td> $4.40 \times 10^{-4}$ </td><td> $4.41 \times 10^{-4}$ </td></tr><tr><td>0.4</td><td>0.6175</td><td>0.6179</td><td>0.6179</td><td> $3.74 \times 10^{-4}$ </td><td> $3.96 \times 10^{-4}$ </td></tr><tr><td>0.5</td><td>0.6439</td><td>0.6442</td><td>0.6443</td><td> $3.21 \times 10^{-4}$ </td><td> $4.01 \times 10^{-4}$ </td></tr><tr><td>0.6</td><td>0.6586</td><td>0.6589</td><td>0.6590</td><td> $3.46 \times 10^{-4}$ </td><td> $4.27 \times 10^{-4}$ </td></tr><tr><td>0.7</td><td>0.6582</td><td>0.6586</td><td>0.6587</td><td> $3.74 \times 10^{-4}$ </td><td> $4.62 \times 10^{-4}$ </td></tr><tr><td>0.8</td><td>0.6421</td><td>0.6425</td><td>0.6427</td><td> $4.48 \times 10^{-4}$ </td><td> $5.76 \times 10^{-4}$ </td></tr><tr><td>0.9</td><td>0.6127</td><td>0.6132</td><td>0.6133</td><td> $4.77 \times 10^{-4}$ </td><td> $6.47 \times 10^{-4}$ </td></tr><tr><td>1.0</td><td>0.5740</td><td>0.5746</td><td>0.5747</td><td> $5.51 \times 10^{-4}$ </td><td> $7.38 \times 10^{-4}$ </td></tr><tr><td>1.2</td><td>0.4860</td><td>0.4867</td><td>0.4869</td><td> $7.15 \times 10^{-4}$ </td><td> $8.58 \times 10^{-4}$ </td></tr><tr><td>1.4</td><td>0.4038</td><td>0.4045</td><td>0.4046</td><td> $7.28 \times 10^{-4}$ </td><td> $7.92 \times 10^{-4}$ </td></tr><tr><td>1.6</td><td>0.3371</td><td>0.3379</td><td>0.3379</td><td> $7.80 \times 10^{-4}$ </td><td> $7.94 \times 10^{-4}$ </td></tr><tr><td>1.8</td><td>0.2866</td><td>0.2873</td><td>0.2873</td><td> $6.66 \times 10^{-4}$ </td><td> $6.71 \times 10^{-4}$ </td></tr><tr><td>2.0</td><td>0.2493</td><td>0.2499</td><td>0.2500</td><td> $6.42 \times 10^{-4}$ </td><td> $6.71 \times 10^{-4}$ </td></tr><tr><td>3.0</td><td>0.1720</td><td>0.1721</td><td>0.1723</td><td> $1.04 \times 10^{-4}$ </td><td> $2.58 \times 10^{-4}$ </td></tr><tr><td>4.0</td><td>0.1620</td><td>0.1626</td><td>0.1627</td><td> $6.38 \times 10^{-4}$ </td><td> $6.72 \times 10^{-4}$ </td></tr><tr><td>5.0</td><td>0.1679</td><td>0.1686</td><td>0.1686</td><td> $6.92 \times 10^{-4}$ </td><td> $7.05 \times 10^{-4}$ </td></tr><tr><td>6.0</td><td>0.1772</td><td>0.1773</td><td>0.1773</td><td> $1.35 \times 10^{-4}$ </td><td> $8.50 \times 10^{-5}$ </td></tr><tr><td>7.0</td><td>0.1865</td><td>0.1864</td><td>0.1865</td><td> $6.80 \times 10^{-5}$ </td><td> $2.60 \times 10^{-5}$ </td></tr><tr><td>8.0</td><td>0.1949</td><td>0.1956</td><td>0.1955</td><td> $7.03 \times 10^{-4}$ </td><td> $6.00 \times 10^{-4}$ </td></tr><tr><td>9.0</td><td>0.2022</td><td>0.2026</td><td>0.2024</td><td> $4.06 \times 10^{-4}$ </td><td> $2.13 \times 10^{-4}$ </td></tr><tr><td>10.0</td><td>0.2085</td><td>0.2085</td><td>0.2083</td><td> $1.80 \times 10^{-5}$ </td><td> $1.80 \times 10^{-4}$ </td></tr></table>

Tables 1–4 compare Hulme’s analytical solution, identified as <sup>Hulme</sup>, and numerical solutions of the integral equations (17) in which the local flow components in G and ∇G are evaluated via a highly-accurate method or via the global approximations (13) and (15). The absolute errors between these alternative numerical predictions, identified as <sup>Accurate</sup> or <sup>Global</sup>, are also listed in Tables 1–4 where they are denoted as E<sup>Accurate</sup> or E<sup>Global</sup>.

Variation of the adimensional surge wave-damping coefficient $b _ { 1 1 }$ with respect to the adimensional wavenumber k R.

<table><tr><td> $k_0R$ </td><td> $b_{11}^{\text{Hulme}}$ </td><td> $b_{11}^{\text{Accurate}}$ </td><td> $b_{11}^{\text{Global}}$ </td><td> $E^{\text{Accurate}}$ </td><td> $E^{\text{Global}}$ </td></tr><tr><td>0.1</td><td>0.0011</td><td>0.0011</td><td>0.0011</td><td> $7.04 \times 10^{-6}$ </td><td> $7.05 \times 10^{-6}$ </td></tr><tr><td>0.2</td><td>0.0082</td><td>0.0081</td><td>0.0081</td><td> $6.15 \times 10^{-5}$ </td><td> $6.14 \times 10^{-5}$ </td></tr><tr><td>0.3</td><td>0.0255</td><td>0.0255</td><td>0.0255</td><td> $1.50 \times 10^{-6}$ </td><td> $1.40 \times 10^{-6}$ </td></tr><tr><td>0.4</td><td>0.0557</td><td>0.0556</td><td>0.0556</td><td> $8.25 \times 10^{-5}$ </td><td> $8.23 \times 10^{-5}$ </td></tr><tr><td>0.5</td><td>0.0987</td><td>0.0985</td><td>0.0985</td><td> $2.13 \times 10^{-4}$ </td><td> $2.18 \times 10^{-4}$ </td></tr><tr><td>0.6</td><td>0.1516</td><td>0.1513</td><td>0.1513</td><td> $3.15 \times 10^{-4}$ </td><td> $3.26 \times 10^{-4}$ </td></tr><tr><td>0.7</td><td>0.2092</td><td>0.2088</td><td>0.2088</td><td> $3.88 \times 10^{-4}$ </td><td> $3.94 \times 10^{-4}$ </td></tr><tr><td>0.8</td><td>0.2653</td><td>0.2649</td><td>0.2649</td><td> $4.18 \times 10^{-4}$ </td><td> $4.13 \times 10^{-4}$ </td></tr><tr><td>0.9</td><td>0.3145</td><td>0.3141</td><td>0.3141</td><td> $4.14 \times 10^{-4}$ </td><td> $4.10 \times 10^{-4}$ </td></tr><tr><td>1.0</td><td>0.3535</td><td>0.3530</td><td>0.3530</td><td> $4.70 \times 10^{-4}$ </td><td> $4.85 \times 10^{-4}$ </td></tr><tr><td>1.2</td><td>0.3978</td><td>0.3975</td><td>0.3974</td><td> $3.50 \times 10^{-4}$ </td><td> $4.36 \times 10^{-4}$ </td></tr><tr><td>1.4</td><td>0.4061</td><td>0.4058</td><td>0.4057</td><td> $2.88 \times 10^{-4}$ </td><td> $4.10 \times 10^{-4}$ </td></tr><tr><td>1.6</td><td>0.3929</td><td>0.3927</td><td>0.3926</td><td> $1.85 \times 10^{-4}$ </td><td> $2.82 \times 10^{-4}$ </td></tr><tr><td>1.8</td><td>0.3695</td><td>0.3694</td><td>0.3693</td><td> $1.20 \times 10^{-4}$ </td><td> $1.58 \times 10^{-4}$ </td></tr><tr><td>2.0</td><td>0.3424</td><td>0.3424</td><td>0.3424</td><td> $6.00 \times 10^{-6}$ </td><td> $1.50 \times 10^{-5}$ </td></tr><tr><td>3.0</td><td>0.2237</td><td>0.2239</td><td>0.2239</td><td> $1.96 \times 10^{-4}$ </td><td> $1.82 \times 10^{-4}$ </td></tr><tr><td>4.0</td><td>0.1511</td><td>0.1518</td><td>0.1518</td><td> $7.33 \times 10^{-4}$ </td><td> $6.68 \times 10^{-4}$ </td></tr><tr><td>5.0</td><td>0.1073</td><td>0.1074</td><td>0.1073</td><td> $6.40 \times 10^{-5}$ </td><td> $4.20 \times 10^{-5}$ </td></tr><tr><td>6.0</td><td>0.0794</td><td>0.0794</td><td>0.0794</td><td> $1.01 \times 10^{-5}$ </td><td> $3.77 \times 10^{-5}$ </td></tr><tr><td>7.0</td><td>0.0608</td><td>0.0615</td><td>0.0615</td><td> $6.81 \times 10^{-4}$ </td><td> $6.71 \times 10^{-4}$ </td></tr><tr><td>8.0</td><td>0.0479</td><td>0.0481</td><td>0.0480</td><td> $1.89 \times 10^{-4}$ </td><td> $9.25 \times 10^{-5}$ </td></tr><tr><td>9.0</td><td>0.0386</td><td>0.0385</td><td>0.0385</td><td> $1.33 \times 10^{-4}$ </td><td> $1.28 \times 10^{-4}$ </td></tr><tr><td>10.0</td><td>0.0317</td><td>0.0319</td><td>0.0319</td><td> $1.89 \times 10^{-4}$ </td><td> $2.41 \times 10^{-4}$ </td></tr></table>

Variation of the adimensional heave added-mass coefficient a with respect to th adimensional wavenumber $k _ { 0 } R .$

<table><tr><td> $k_0R$ </td><td> $a_{33}^{\text{Hulme}}$ </td><td> $a_{33}^{\text{Accurate}}$ </td><td> $a_{33}^{\text{Global}}$ </td><td> $E^{\text{Accurate}}$ </td><td> $E^{\text{Global}}$ </td></tr><tr><td>0.1</td><td>0.8627</td><td>0.8634</td><td>0.8634</td><td> $6.84 \times 10^{-4}$ </td><td> $6.80 \times 10^{-4}$ </td></tr><tr><td>0.2</td><td>0.7938</td><td>0.7945</td><td>0.7945</td><td> $7.24 \times 10^{-4}$ </td><td> $7.20 \times 10^{-4}$ </td></tr><tr><td>0.3</td><td>0.7157</td><td>0.7164</td><td>0.7164</td><td> $6.86 \times 10^{-4}$ </td><td> $7.15 \times 10^{-4}$ </td></tr><tr><td>0.4</td><td>0.6452</td><td>0.6459</td><td>0.6460</td><td> $6.95 \times 10^{-4}$ </td><td> $7.56 \times 10^{-4}$ </td></tr><tr><td>0.5</td><td>0.5861</td><td>0.5868</td><td>0.5868</td><td> $6.63 \times 10^{-4}$ </td><td> $6.96 \times 10^{-4}$ </td></tr><tr><td>0.6</td><td>0.5381</td><td>0.5388</td><td>0.5388</td><td> $6.52 \times 10^{-4}$ </td><td> $7.17 \times 10^{-4}$ </td></tr><tr><td>0.7</td><td>0.4999</td><td>0.5005</td><td>0.5006</td><td> $5.80 \times 10^{-4}$ </td><td> $7.06 \times 10^{-4}$ </td></tr><tr><td>0.8</td><td>0.4698</td><td>0.4704</td><td>0.4705</td><td> $5.62 \times 10^{-4}$ </td><td> $7.18 \times 10^{-4}$ </td></tr><tr><td>0.9</td><td>0.4464</td><td>0.4469</td><td>0.4471</td><td> $5.30 \times 10^{-4}$ </td><td> $6.72 \times 10^{-4}$ </td></tr><tr><td>1.0</td><td>0.4284</td><td>0.4289</td><td>0.4290</td><td> $5.16 \times 10^{-4}$ </td><td> $6.27 \times 10^{-4}$ </td></tr><tr><td>1.2</td><td>0.4047</td><td>0.4051</td><td>0.4052</td><td> $4.21 \times 10^{-4}$ </td><td> $4.94 \times 10^{-4}$ </td></tr><tr><td>1.4</td><td>0.3924</td><td>0.3927</td><td>0.3927</td><td> $2.50 \times 10^{-4}$ </td><td> $3.46 \times 10^{-4}$ </td></tr><tr><td>1.6</td><td>0.3871</td><td>0.3873</td><td>0.3875</td><td> $2.46 \times 10^{-4}$ </td><td> $3.76 \times 10^{-4}$ </td></tr><tr><td>1.8</td><td>0.3864</td><td>0.3865</td><td>0.3866</td><td> $1.06 \times 10^{-4}$ </td><td> $2.40 \times 10^{-4}$ </td></tr><tr><td>2.0</td><td>0.3884</td><td>0.3884</td><td>0.3885</td><td> $1.80 \times 10^{-5}$ </td><td> $9.30 \times 10^{-5}$ </td></tr><tr><td>3.0</td><td>0.4111</td><td>0.4114</td><td>0.4113</td><td> $2.68 \times 10^{-4}$ </td><td> $1.93 \times 10^{-4}$ </td></tr><tr><td>4.0</td><td>0.4322</td><td>0.4323</td><td>0.4330</td><td> $1.49 \times 10^{-4}$ </td><td> $8.43 \times 10^{-4}$ </td></tr><tr><td>5.0</td><td>0.4471</td><td>0.4471</td><td>0.4484</td><td> $6.00 \times 10^{-6}$ </td><td> $1.32 \times 10^{-3}$ </td></tr><tr><td>6.0</td><td>0.4574</td><td>0.4576</td><td>0.4587</td><td> $1.55 \times 10^{-4}$ </td><td> $1.35 \times 10^{-3}$ </td></tr><tr><td>7.0</td><td>0.4647</td><td>0.4648</td><td>0.4653</td><td> $1.23 \times 10^{-4}$ </td><td> $6.34 \times 10^{-4}$ </td></tr><tr><td>8.0</td><td>0.4700</td><td>0.4701</td><td>0.4695</td><td> $8.70 \times 10^{-5}$ </td><td> $5.23 \times 10^{-4}$ </td></tr><tr><td>9.0</td><td>0.4740</td><td>0.4741</td><td>0.4723</td><td> $1.33 \times 10^{-4}$ </td><td> $1.70 \times 10^{-3}$ </td></tr><tr><td>10.0</td><td>0.4771</td><td>0.4773</td><td>0.4743</td><td> $1.79 \times 10^{-4}$ </td><td> $2.77 \times 10^{-3}$ </td></tr></table>

These four tables show that the global analytical approximations (13) and (15) or a highly-accurate evaluation of L and $L _ { h }$ yield numerical predictions of added-mass and wave-damping coefficients that are practically identical, except for the heave added-mass coefficient $a _ { 3 3 }$ at $4 { \le } k _ { 0 } R$ for which the differences between $a _ { 3 3 } ^ { \mathrm { G l o b a l } }$ and $a _ { 3 3 } ^ { \mathrm { A c c u r a t e } }$ are slightly larger. The largest absolute error $E ^ { \mathrm { G l o b a l } }$ , found in Table 3 for $k _ { 0 } R = 1 0$ , corresponds to a relative error approximately equal to 0.6%.

Tables 1–4 also show that, in most cases, the differences between the two sets of numerical predictions of the added-mass and wave-damping coefficients are appreciably smaller than the corresponding differences between the numerical predictions and Hulme’s analytical solution. Specifically, the root mean square (RMS) of the differences between Hulme’s analytical results and the numerical predictions based on a highly accurate Green function, approximately equal to $5 . 1 \times 1 0 ^ { - 4 } , 3 . 1 \times 1 0 ^ { - 4 }$ and $3 \times 1 0 ^ { - 4 }$ for the coefficients $a _ { 1 1 } , b _ { 1 1 }$ and $b _ { 3 3 } ,$ , are appreciably larger than the corresponding RMS of the differences between the numerical predictions based on a highly accurate Green function or the less accurate global approximation, which are approximately equal to $1 \times 1 0 ^ { - 4 } , 5 . 3 \times 1 0 ^ { - 5 }$ and $6 . 3 \times 1 0 ^ { - 5 }$ . The corresponding RMS of the differences for the heave added mass coefficient $a _ { 3 3 }$ are $5 . 1 \times 1 0 ^ { - 4 }$ and $1 . 9 \times 1 0 ^ { - 4 }$ if the results for $4 { \le } \mathrm { k } _ { 0 } \mathrm { R } { \le } 1 0$ are excluded, and are $4 . 4 \times 1 0 ^ { - 4 }$ and $8 . 5 \times 1 0 ^ { - 4 }$ for $0 . 1 { \le } \mathrm { k } _ { 0 } \mathrm { R } { \le } 1 0$

Table 4  
Variation of the adimensional heave wave-damping coefficient $b _ { 3 3 }$ with respect to the adimensional wavenumber $k _ { 0 } R .$

<table><tr><td> $k_0R$ </td><td> $b_{33}^{\text{Hulme}}$ </td><td> $b_{33}^{\text{Accurate}}$ </td><td> $b_{33}^{\text{Global}}$ </td><td> $E^{\text{Accurate}}$ </td><td> $E^{\text{Global}}$ </td></tr><tr><td>0.1</td><td>0.1816</td><td>0.1816</td><td>0.1816</td><td> $2.60 \times 10^{-5}$ </td><td> $2.60 \times 10^{-5}$ </td></tr><tr><td>0.2</td><td>0.2793</td><td>0.2794</td><td>0.2794</td><td> $6.70 \times 10^{-5}$ </td><td> $6.90 \times 10^{-5}$ </td></tr><tr><td>0.3</td><td>0.3254</td><td>0.3255</td><td>0.3255</td><td> $8.90 \times 10^{-5}$ </td><td> $8.70 \times 10^{-5}$ </td></tr><tr><td>0.4</td><td>0.3410</td><td>0.3412</td><td>0.3412</td><td> $2.07 \times 10^{-4}$ </td><td> $1.91 \times 10^{-4}$ </td></tr><tr><td>0.5</td><td>0.3391</td><td>0.3393</td><td>0.3393</td><td> $2.07 \times 10^{-4}$ </td><td> $2.13 \times 10^{-4}$ </td></tr><tr><td>0.6</td><td>0.3271</td><td>0.3274</td><td>0.3274</td><td> $3.24 \times 10^{-4}$ </td><td> $3.33 \times 10^{-4}$ </td></tr><tr><td>0.7</td><td>0.3098</td><td>0.3101</td><td>0.3101</td><td> $3.48 \times 10^{-4}$ </td><td> $3.20 \times 10^{-4}$ </td></tr><tr><td>0.8</td><td>0.2899</td><td>0.2903</td><td>0.2902</td><td> $3.69 \times 10^{-4}$ </td><td> $2.98 \times 10^{-4}$ </td></tr><tr><td>0.9</td><td>0.2691</td><td>0.2695</td><td>0.2694</td><td> $3.85 \times 10^{-4}$ </td><td> $2.96 \times 10^{-4}$ </td></tr><tr><td>1.0</td><td>0.2484</td><td>0.2488</td><td>0.2487</td><td> $4.22 \times 10^{-4}$ </td><td> $3.48 \times 10^{-4}$ </td></tr><tr><td>1.2</td><td>0.2096</td><td>0.2100</td><td>0.2100</td><td> $4.23 \times 10^{-4}$ </td><td> $4.24 \times 10^{-4}$ </td></tr><tr><td>1.4</td><td>0.1756</td><td>0.1761</td><td>0.1761</td><td> $4.84 \times 10^{-4}$ </td><td> $5.41 \times 10^{-4}$ </td></tr><tr><td>1.6</td><td>0.1469</td><td>0.1473</td><td>0.1474</td><td> $4.28 \times 10^{-4}$ </td><td> $4.91 \times 10^{-4}$ </td></tr><tr><td>1.8</td><td>0.1229</td><td>0.1233</td><td>0.1234</td><td> $4.49 \times 10^{-4}$ </td><td> $4.89 \times 10^{-4}$ </td></tr><tr><td>2.0</td><td>0.1031</td><td>0.1035</td><td>0.1035</td><td> $4.10 \times 10^{-4}$ </td><td> $4.29 \times 10^{-4}$ </td></tr><tr><td>3.0</td><td>0.0452</td><td>0.0456</td><td>0.0454</td><td> $3.77 \times 10^{-4}$ </td><td> $1.80 \times 10^{-4}$ </td></tr><tr><td>4.0</td><td>0.0219</td><td>0.0221</td><td>0.0221</td><td> $2.30 \times 10^{-4}$ </td><td> $2.15 \times 10^{-4}$ </td></tr><tr><td>5.0</td><td>0.0116</td><td>0.0118</td><td>0.0118</td><td> $2.07 \times 10^{-4}$ </td><td> $2.28 \times 10^{-4}$ </td></tr><tr><td>6.0</td><td>0.0066</td><td>0.0068</td><td>0.0069</td><td> $2.18 \times 10^{-4}$ </td><td> $3.22 \times 10^{-4}$ </td></tr><tr><td>7.0</td><td>0.0040</td><td>0.0041</td><td>0.0042</td><td> $8.55 \times 10^{-5}$ </td><td> $1.57 \times 10^{-4}$ </td></tr><tr><td>8.0</td><td>0.0026</td><td>0.0026</td><td>0.0026</td><td> $9.66 \times 10^{-6}$ </td><td> $5.53 \times 10^{-6}$ </td></tr><tr><td>9.0</td><td>0.0017</td><td>0.0018</td><td>0.0019</td><td> $8.97 \times 10^{-5}$ </td><td> $1.56 \times 10^{-4}$ </td></tr><tr><td>10.0</td><td>0.0012</td><td>0.0012</td><td>0.0012</td><td> $3.60 \times 10^{-6}$ </td><td> $3.14 \times 10^{-5}$ </td></tr></table>

Thus, the RMS of the differences between Hulme’s analytical results and the numerical predictions obtained via a highly accurate Green function are significantly larger than the RMS of the differences between the numerical predictions based on a highly accurate Green function or the less accurate global approximation, except for $a _ { 3 3 }$ at $4 { \le } \mathrm { k } _ { 0 } \mathrm { R } { \le } 1 0$

This result suggests that the errors associated with the numerical predictions in fact may not predominantly stem from inaccuracies related to the evaluation of the Green function and its gradient, but likely are mostly due to other sources of inaccuracies (e.g., the discretization of the hull surface, or the numerical integration of G and ∇G over the hull panels).

The horizontal and vertical wave exciting forces on the hemisphere in regular waves of amplitude a and frequency ω are now considered. The incident wave potential is defined as

$$
\phi^ {I} = (\mathrm{i} a g / \omega) \exp \{k _ {0} [ z + \mathrm{i} (x \cos \beta_ {0} + y \sin \beta_ {0}) ] \}\tag{18}
$$

The horizontal and vertical wave exciting forces $F _ { x }$ and $F _ { Z }$ are adimensional with respect to $2 \pi \rho g R ^ { 3 } k _ { 0 } a / 3$ or $\pi \rho g R ^ { 2 } a / 2$ in Fig. 4.

This figure shows that the numerical predictions obtained by means ofthe high-order boundary element method with very accurate evaluation of the Green function based on [23], identified as “HOBEM”, and the numerical predictions obtained by means of the constant panel method in which the local flow components in G and ∇G are evaluated very accurately or via the global approximations (13) and (15), identified as “Global” or “Accurate”, cannot be distinguished.

## 4.2. RAOs ofa FPSO

The response amplitude operators (RAO) associated with the motions of a freely-floating FPSO in incoming regular waves at an incidence angle $\beta _ { 0 } = 4 5 ^ { \circ }$ are now considered. The main dimensions

![](images/e70514fe17393888dd3a1d2d0c6e3524855ad19db8b03e7f6c4bdb5d2f68a9b2.jpg)

![](images/ce78e6640ec569bc6309b7f8ea1d7b226bdc76448b2b8c04b0e23036f26c2217.jpg)  
Fig. 4. Adimensional horizontal and vertical wave exciting forces F (top) and F (bottom) predicted by a high-order boundary element method [23] or a constant panel method in which the local flow components in G and ∇G are evaluated very accurately or via the global approximations (13) and (15).

## Table 5

Main dimensions and hydrostatic characteristics of the FPSO considered for validation purposes.

<table><tr><td>Length (m)</td><td>300</td></tr><tr><td>Breath (m)</td><td>50</td></tr><tr><td>Draft (m)</td><td>25</td></tr><tr><td>Reference point (m)</td><td>(151.492, 0.000, -5.000)</td></tr><tr><td>Centre of buoyancy (m)</td><td>(151.492, 0.000, -12.381)</td></tr><tr><td>Displacement (m3)</td><td> $3.5725 \times 10^{5}$ </td></tr><tr><td>Waterplane area (m2)</td><td> $1.4474 \times 10^{4}$ </td></tr><tr><td>GMxx(m)</td><td>0.63</td></tr><tr><td>GMyy(m)</td><td>277.22</td></tr><tr><td>Roll radius of gyration Rxx(m)</td><td>20</td></tr><tr><td>Pitch radius of gyration Ryy(m)</td><td>60</td></tr><tr><td>Yaw radius of gyration Rzz(m)</td><td>60</td></tr></table>

![](images/2e5cd755eaa2b5c53dc6d62ef2a8dc3954e96ef05b39b3fe276379ea88d8de09.jpg)  
Fig. 5. Mesh used to represent the hull surface of the FPSO considered in the study. 503 quadrilateral panels are used to approximate half of the hull surface

and hydrostatic characteristics of the FPSO are defined in Table 5. The FPSO is discretized as in Fig. 5.

![](images/4a29dc73ffc16d84c5d749bfdffc80da6b7d7337339aadaec3c61f4146fb8733.jpg)

![](images/9dd69cf69e8a14af29cbb1c43096951e619ee89deb4814b02eabe685d41c5031.jpg)  
Fig. 6. RAOs for surge, sway, heave motions (top) and for roll, pitch, yaw motions (bottom) ofthe FPSO defined in Table 5 and Fig. 5 in incoming waves at an incidence angle $\beta _ { 0 } = 4 5 ^ { \circ }$

The equations of motions [24,25] in the kth mode where 1≤k≤6 are expressed as

$$
\sum_ {j = 1} ^ {6} \left\{- \omega^ {2} \left[ M _ {k j} + A _ {k j} (\omega) \right] - \mathrm{i} \omega B _ {k j} (\omega) + C _ {k j} \right\} X _ {j} = F _ {k} ^ {\mathrm{ex}} (\omega)\tag{19}
$$

where $M _ { k j } , A _ { k j } , B _ { k j }$ and $C _ { k j }$ are components of the mass, addedmass, wave-damping and hydrostatic restoring-force matrices, and $F _ { k } ^ { \mathrm { e x } }$ represent wave exciting forces and moments. The information required to determine the components $M _ { k j }$ and $C _ { k j }$ is given in Table 5.

Fig. 6 depicts the variations of the RAOs for surge, sway, heave, roll, pitch and yaw motions, in oblique waves at an incidence angle $\beta _ { 0 } = 4 5 ^ { \circ }$ , with respect to the adimensional wavenumber $k _ { 0 } L / 2$ where L is the length of the ship hull, $k _ { 0 } = \omega ^ { 2 } / g$ and ω is the circular frequency of the incoming waves. The unit of RAOs for angular motions is radian per wave slope $( k _ { 0 } a )$

Fig. 6 shows that the RAOs predicted by the BV software HydroStar with $G$ and ∇G evaluated with high accuracy (with errors of order $1 0 ^ { - 6 } )$ do not differ appreciably from the predictions obtained when the less accurate global analytical approximations (13) and (15) are used. These simple global approximations can then be used in practice to calculate linear wave-induced motions.

## 4.3. Mean drift loads

The second-order mean drift forces and moment related to the quadratic terms in Bernoulli’s equation are now considered for the hemisphere and the FPSO defined previously. The far-field formulation based on conservation of fluid momentum given in [26] and [27] expresses the horizontal mean drift forces and moment as

$$
\frac {\bar {F} _ {x}}{\rho} = \frac {- k _ {0} ^ {2}}{8 \pi} \int_ {0} ^ {2 \pi} | H (\gamma) | ^ {2} \cos \gamma d \gamma + \frac {\omega a}{2} \Re [ H (\gamma) ] \cos \beta_ {0}\tag{20a}
$$

$$
\frac {\bar {F} _ {y}}{\rho} = \frac {- k _ {0} ^ {2}}{8 \pi} \int_ {0} ^ {2 \pi} \left| H (\gamma) \right| ^ {2} \sin \gamma d \gamma + \frac {\omega a}{2} \Re [ H (\gamma) ] \sin \beta_ {0}\tag{20b}
$$

$$
\frac {\bar {M} _ {z}}{\rho} = \frac {- k _ {0}}{8 \pi} \Im \int_ {0} ^ {2 \pi} H ^ {*} (\gamma) H ^ {\prime} (\gamma) \mathrm{d} \gamma + \frac {\omega a}{2 k _ {0}} \Im \left[ H ^ {\prime} (\beta_ {0}) \right]\tag{20c}
$$

![](images/5b17bc8ecb85312f958cdfb3dd2fcdb7440c91395ee62d3c6ef1550e7d2525a0.jpg)  
Fig. 7. Adimensional mean drift force $\bar { F } _ { x }$ acting on a fixed hemisphere of radius R in incoming waves of amplitude a at an incidence angle $\beta _ { 0 } = 0 ^ { \circ }$

![](images/dd60ef6f8f550dd4c745876c476a97c49ad8adac3cd3a6da75fadece7f950862.jpg)

![](images/2866c2a9c6898324dd07dee486770e0c29ea772207a20feaf33b16117bb0932c.jpg)  
Fig. 8. Mean drift forces $\bar { F } _ { x }$ and $\bar { F } _ { y }$ and moment $\bar { M } _ { z }$ acting on a freely floating FPSO of length L in incoming waves of amplitude a at an incidence angl $\beta _ { 0 } = 4 5$

where $H ( \gamma )$ denotes the Kochin function defined as

$$
\begin{array}{l} H (\gamma) = \iint_ {\Sigma^ {H}} \left[ \frac {\partial \phi (\xi)}{\partial n _ {\xi}} - \phi (\xi) \frac {\partial}{\partial n _ {\xi}} \right] \\ \cdot \exp \left[ k _ {0} \zeta - \mathrm{i} k _ {0} (\xi \cos \gamma + \eta \sin \gamma) \right] \mathrm{d} S. \end{array}\tag{21}
$$

Here,  accounts for both diffraction and radiation, and is given by

$$
\phi = \phi^ {D} + \sum_ {j = 1} ^ {6} \left(- \mathrm{i} \omega \eta_ {j} \varphi_ {j}\right)\tag{22}
$$

where $\phi ^ { D }$ denotes the diffraction potential, $\eta _ { j }$ is the amplitude ofthe motion in thej-th mode and $\varphi _ { j }$ is the corresponding radiation potential.

Fig. 7 depicts the mean drift force $\bar { F } _ { x }$ acting on a fixed hemisphere, and Fig. 8 depicts the mean drift forces $\bar { F } _ { x }$ and $\bar { F } _ { y }$ and the mean drift moment $\bar { M } _ { z }$ acting on the FPSO that is depicted in Fig. 5.

These figures show that the predictions given by HydroStar, in which G and ∇G are evaluated with high accuracy, and the numerical solutions of the integral equations (17) in which the local flow components in G and ∇G are evaluated very accurately or less accurately via the global approximations (13) and (15), are in excellent agreement. The global approximations (13) and (15) can then be used in practice to predict mean drift loads.

The very small differences that can be observed between the HydroStar predictions and the numerical solutions of the integral equations (17) with highly-accurate evaluations of G and ∇G stem from the fact that combined source and dipole distributions are considered in (17) whereas only sources are used in HydroStar.

## 5. Conclusion

The computations of linear wave loads and second-order mean drift loads for a hemisphere and a freely floating FPSO reported in the study show that the global analytical approximations (13) and (15) to the local flow components in the Green function G and its gradient ∇G yield numerical predictions that are in very close agreement with analytical results for a hemisphere as well as predictions obtained via a highly-accurate Green function.

This finding provides strong evidence that the global analytical approximations, valid within the entire flow region, to G and ∇G given in [16] are sufficiently accurate to compute linear and mean drift wave loads in practice.

This conclusion is consistent with the finding of [28] that the remarkably simple global analytical approximation to the local flow component in the expression for the Green function in the linear potential flow theory of steady ship waves that is given in [29–31] is sufficiently accurate for most practical applications, as is further illustrated in [32,33].

The findings that very accurate approximations to the local flow components in the expressions for the Green function and its gradient are not required for the problem of wave diffraction-radiation without forward speed or the problem of ship waves in calm water that are considered here and in [28] are important and encouraging because they suggest that a relatively crude approximation to the local flow component might also be useful for the much more complicated problem of ship motions in regular waves.

## References

[1] O.M. Faltinsen, F.C. Michelsen, Motions of large structures in waves at zero Froude number, in: The International Symposium on the Dynamics of Marine Vehicles and Structures in Waves, London, UK, 1974, pp. 91–106.

[2] A. Papanikolaou, On integral-equation-methods for the evaluation of motions and loads of arbitrary bodies in waves, Arch. Appl. Mech. 55 (1) (1985) 17–29.

[4] X.B. Chen, Hydrodynamics in offshore and naval applications, in: The 6th International Conference on Hydrodynamics, Perth Australia 2004

[5] C.H. Lee, J.N. Newman, Computation of wave effects using the panel method, in: Numerical Models in Fluid–Structure Interaction, WIT Press, Southampton, 2005, pp. 211–251.

[6] J.V. Wehausen, E.V. Laitone, Surface waves, in: Handbuch der Physik, vol. 9, Springer-Verlag, Berlin, 1960, pp. 446–778.

[7] F. Noblesse, The Green function in the theory of radiation and diffraction of regular water waves by a body, J. Eng. Math. 16 (2) (1982) 137–169.

[8] M. Abramowitz, I.A. Stegun, Handbook of Mathematical Functions, Dover, New York, 1965

[9] J.N. Newman, Approximations for the Bessel and Struve functions, Math. Comp. 43 (168) (1984) 551–556.

[10] J. Jin, S. Zhang, Computation of Special Functions, Wiley, New York, 1996.

[11] F.W.J. Olver, Asymptotics and Special Functions, Academic press, New York, 1974.

[12] J.G. Telste, F. Noblesse, Numerical evaluation of the Green function of water-wave radiation and diffraction, J. Ship Res. 30 (2) (1986) 69–84.

[13] J.N. Newman, Algorithms for the free-surface Green function, J. Eng. Math. 19 (1) (1985) 57–67.

[14] J.N. Newman, The approximation of free-surface Green functions, in: Wave Asymptotics, Cambridge University Press, Cambridge, 1992, pp. 107–135.

[15] B. Ponizy, F. Noblesse, M. Ba, M. Guilbaud, Numerical evaluation of free-surface Green functions, J. Ship Res. 38 (3) (1994) 193–202

[16] H. Wu, C. Zhang, Y. Zhu, W. Li, D. Wan, F. Noblesse, A global approximation to the Green function for diffraction radiation of water waves, Eur. J. Mech. B Fluids 65 (2017) 54–64.

[17] C.H. Lee, J.N. Newman, X. Zhu, An extended boundary integral equation method for the removal of irregular freguency effects. Int. I. Numer. Methods Fluids 23 (7) (1996) 637–660.

[18] S.<sup>ˇ</sup> Malenica, X.B. Chen, On the irregular frequencies appearing in wave diffraction-radiation solutions, Int. J. Offshore Polar Eng. 8 (02) (1998) 110–114.

[19] H. Liang, X.B. Chen, A new multi-domain method based on an analytical control surface for linear and second-order mean drift wave loads on floating bodies, J. Comput. Phys. 347 (2017) 506–532.

[20] J.L. Hess, A.M.O. Smith, Calculation of potential flow about arbitrary bodies, Prog. Aerosp. Sci. 8 (1967) 1–138.

[21] J.N. Newman, Distributions of sources and normal dipoles over a quadrilateral panel, J. Eng. Math. 20 (2) (1986) 113–126.

[22] A. Hulme, The wave forces acting on a floating hemisphere undergoing forced periodic oscillations, J. Fluid Mech. 121 (1982) 443–463.

[23] X.B. Chen, L. Diebold, Y. Doutreleau, New Green-function method to predict wave-induced ship motions and loads, in: The Twenty-Third Symposium on Naval Hydrodynamics, Val de Reuil, France, 2000, pp. 66–81.

[24] O.M. Faltinsen, Sea Loads on Ships and Offshore Structures, Cambridge university press, Cambridge, 1993.

[25] B. Molin, Hydrodynamique des Structures Offshore, Editions Technip, Paris, 2002.

[26] H. Maruo, The drift of a body floating on waves, J. Ship Res. 4 (3) (1960) 1–10.

[27] J.N. Newman, The drift force and moment on ships in waves, J. Ship Res. 11 (1) (1967) 51–60.

[28] H. Wu, C. Zhang, C. Ma, F. Huang, C. Yang, F. Noblesse, Errors due to a practical Green function for steady ship waves, Eur. J. Mech. B Fluids 55 (2016) 162-169.

[29] F. Noblesse, G. Delhommeau, F. Huang, C. Yang, Practical mathematical representation of the flow due to a distribution of sources on a steadily advancing ship hull, J. Eng. Math. 71 (4) (2011) 367–392.

[30] F. Noblesse, F. Huang, C. Yang, The Neumann–Michell theory of ship waves, J. Eng. Math. 79 (1) (2013) 51–71.

[31] F. Huang, C. Yang, F. Noblesse, Numerical implementation and validation of the Neumann–Michell theory of ship waves, Eur. J. Mech. B Fluids 42 (2013) 47–68.

[32] C. Ma, C. Zhang, F. Huang, C. Yang, X. Gu, W. Li, F. Noblesse, Practical evaluation of sinkage and trim effects on the drag of a common generic freely floating monohull ship, Appl Ocean Res, 65 (2017) 1–11

[33] C. Ma, Y. Zhu, J. He, C. Zhang, D. Wan, C. Yang, F. Noblesse, Nonlinear corrections of linear potential-flow theory of ship waves, Eur. J. Mech. B Fluids 67 (2018) 1–14.