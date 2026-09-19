# Wave component in the Green function for di<sup>f</sup>raction radiation of regular water waves

![](images/1f72fdb69069f44fbc99091b0106d5cc7c5799eb7364f9e66fef0ad73a1ea20d.jpg)

Huiyu Wu<sup>a</sup>, Hui Liang<sup>b</sup>, Francis Noblesse<sup>a,</sup>

<sup>a</sup> State Key Laboratory of Ocean Engineering, Collaborative Innovation Center for Advanced Ship and Deep-Sea Exploration, School of Naval Architecture, Ocean & Civil Engineering, Shanghai Jiao Tong University, Shanghai, China

<sup>b</sup> Deepwater Technology Research Centre (DTRC), Bureau Veritas 117674, Singapore

## A R T I C L E I N F O

Keywords: Regular water waves Di<sup>f</sup>raction radiation Green function Wave component Global approximation

## A B S T R A C T

The Green function for di<sup>f</sup>raction radiation of regular waves in deep water is considered. The Green function G and its gradient ∇G involve non-oscillatory local-flow components L and ∇L, for which simple global approximations valid within the entire flow region exist, and wave components W and ∇W. The waves W and ∇W in this basic decomposition involve the intrinsic Fortran Bessel functions $J _ { 0 } ( h )$ and J (h), where h denotes the horizontal distance between the source and <sup>fl</sup>ow-<sup>fi</sup>eld points in the Green function, and the Struve functions $\tilde { H } _ { 0 } ( h )$ and H h<sup>˜</sup> ( ) for which complementary approximations valid within the near<sup>fi</sup>eld or far<sup>fi</sup>eld ranges 0 ≤ h ≤ 3 or 3 < h exist. These complementary approximations to $\tilde { H } _ { 0 } ( h )$ and $\tilde { H } _ { 1 } ( h )$ defeat the global nature of the approximations to the local-flow components L and ∇L. This issue, however, is readily remedied if practical approximations, given by Aarts and Janssen in 2016, that relate the Struve functions $\tilde { H } _ { 0 } ( h )$ and H h<sup>˜</sup> ( ) to the Bessel functions J (h) and J (h) are used. The resulting approximations to the waves W and ∇W given here, and the global approximations to the local-flow components I. and ∇I. given previously vield practical and parti: cularly simple approximations to G and ∇G that are valid within the entire flow region, can be evaluated simply and efficiently, and are sufficiently accurate for practical applications.

## 1. Introduction

Di<sup>f</sup>raction radiation of time-harmonic water waves by an o<sup>f</sup>shore structure within the framework of linear potential <sup>fl</sup>ow theory and the Green function method is widely used to predict added-mass and wavedamping coe<sup>fi</sup>cients, motions, and wave loads. Wave di<sup>f</sup>raction radiation by a ship that travels at low forward speed in regular waves is also widely analyzed via the zero-speed Green function at the encounter frequency. This Green function, related to the potential of the <sup>fl</sup>ow created by a pulsating point source as is well known, is an essential element of the theory of wave di<sup>f</sup>raction radiation. Accordingly, the Green function has been widely studied in a broad literature, especially for the simplest case of deep water that is considered here. A brief review of this literature can be found in [1,2].

The Green function G can be expressed as the sum of the fundamental free-space singularity and a <sup>fl</sup>ow component that accounts for free-surface e<sup>f</sup>ects. This free-surface component is formally decom posed into a wave component W that represents the waves radiated by the pulsating source and a non-oscillatory local-<sup>fl</sup>ow component L in [3], where several integral representations and complementary analytical approximations (near<sup>fi</sup>eld series, far<sup>fi</sup>eld asymptotic expansions, and one-dimensional Taylor series) to G and ∇G are given. These alternative approximations are the foundation of the method for computing G and ∇G given in [4]. Alternative mathematical representations and computational methods (notably polynomial approximations in complementary contiguous regions, and table interpolation associated with function and coordinate transformations) for approximating G and ∇G have been given in the literature, reviewed in [1,2] as was already noted.

In particular, the method for computing the local-<sup>fl</sup>ow components L and ∇L given in [4] requires subdivision of the flow region into five contiguous regions of space within which di<sup>f</sup>erent analytical approximations are used. Other methods given in the literature are similarly based on complementary polynomial approximations in contiguous subdomains.

A signi<sup>fi</sup>cantly di<sup>f</sup>erent approach is adopted in [1] where analytical approximations valid within the entire <sup>fl</sup>ow domain, i.e. global approximations, are given for the local-flow components L and ∇L. These global analytical approximations to L and ∇L are shown in [2] to be su<sup>fi</sup>ciently accurate for practical applications.

Simple practical global approximations (valid within the entire <sup>fl</sup>ow region) to the exact expressions for W and ∇W, used in [1,2], are given here. These approximations to W and ∇W are based on the approximations, given in [5], that express the Struve functions $\tilde { H } _ { 0 } ( h )$ and $\tilde { H } _ { 1 } ( h )$ in terms of the Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$

The global analytical approximations to the wave components W and $W _ { h } ,$ together with the global analytical approximations to the local-<sup>fl</sup>ow components L and $L _ { h }$ given in [1,2], provide practical global analytical approximations to the Green function G and its gradient ∇G for di<sup>f</sup>raction radiation of regular water waves. These global analytical approximations are particularly simple, well suited for parallel computations, and are shown to be su<sup>fi</sup>ciently accurate for practical applications.

## 2. The Green function and its gradient

A Cartesian system of coordinates $\mathbf { X } \equiv ( X , Y , Z )$ is used. The Z axis is vertical and points upward, and the undisturbed free surface is taken as the plane $Z = 0$ . Di<sup>f</sup>raction radiation of time harmonic waves with radian frequency ω and wavelength $\lambda = 2 \pi g / \omega ^ { 2 }$ , where g denotes the gravitational acceleration, is considered. Nondimensional coordinates $\mathbf { x } \equiv ( x , y , z ) \equiv \mathbf { X } \omega ^ { 2 } / g$ are de<sup>fi</sup>ned.

The Green function G ( ,x x˜) is the spatial component of a non dimensional velocity potential Re $[ G ( \mathbf { x } , \tilde { \mathbf { x } } ) e ^ { - \mathrm { i } \omega T } ]$ where T denotes time, and corresponds to the potential of the <sup>fl</sup>ow created at the point $\mathbf { x } \equiv ( x ,$ $y , z \leq 0 )$ by a pulsating source located at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } < 0 )$ , or <sup>fl</sup>ux through the free surface at the point $\tilde { \mathbf { x } } \equiv ( \tilde { x } , \tilde { y } , \tilde { z } = 0 )$

The nondimensional distances between the <sup>fl</sup>ow-<sup>fi</sup>eld point x and the source point x˜ or its mirror image $\tilde { \mathbf { x } } _ { 1 } \equiv ( \tilde { x } , \tilde { y } , - \tilde { z } )$ with respect to the undisturbed free-surface plane $z = 0$ are denoted as r and d, and are given by

$$
r \equiv \sqrt {h ^ {2} + (z - \tilde {z}) ^ {2}} \quad \text { and } \quad d \equiv \sqrt {h ^ {2} + v ^ {2}} \quad \text { where }\tag{1a}
$$

$$
0 \leq h \equiv \sqrt {(x - \tilde {x}) ^ {2} + (y - \tilde {y}) ^ {2}} \quad \text { and } \quad v \equiv z + \tilde {z} \leq 0\tag{1b}
$$

are the horizontal and vertical components of the distance d between the points x and $\tilde { \mathbf { x } } _ { 1 } .$

The Green function G and its gradient $\nabla G \equiv ( G _ { x } , G _ { y } , G _ { z } )$ are expressed in [1–3] as

$$
4 \pi G = - 1 / r + L + W\tag{2a}
$$

$$
4 \pi G _ {z} = (z - \tilde {z}) / r ^ {3} + v / d ^ {3} - 1 / d + L + W\tag{2b}
$$

$$
4 \pi G _ {h} = h / r ^ {3} + L _ {h} + W _ {h}\tag{2c}
$$

$$
G _ {x} = G _ {h} (x - \tilde {x}) / h \quad \mathrm{and} \quad G _ {y} = G _ {h} (y - \tilde {y}) / h\tag{2d}
$$

where the term −1/r and its derivatives correspond to the free-space Green function, and the functions $L ( h , \nu ) , L _ { h } ( h , \nu ) , W ( h , \nu )$ and $W _ { h } ( h , \nu )$ account for free-surface e<sup>f</sup>ects. The terms L and $L _ { h }$ correspond to a non-oscillatory local <sup>fl</sup>ow, and the terms W and $W _ { h }$ represent circular surface waves radiated by the source.

## 3. Local-flow components L and ${ \mathbf { L } } _ { h }$

Simple analytical approximations to the local-<sup>fl</sup>ow terms L and $L _ { h }$ in (2a)–(2c) are given in [1]. These approximations are valid within the entire <sup>fl</sup>ow domain $( 0 \leq h , \nu \leq 0 )$ , i.e. are global approximations, unlike the alternative approximations in complementary contiguous regions given in the literature. The approximations to the local-<sup>fl</sup>ow compo nents L and $L _ { h }$ given in [1] only involve elementary continuous functions (algebraic, exponential, logarithmic) of real arguments, and pro vide a particularly simple practical method for numerically evaluating the local-flow components L and ∇L in G and ∇G. These local-flow approximations are shown in [2] to be su<sup>fi</sup>ciently accurate for practical applications.

## 4. Wave components W and ${ \pmb W } _ { \pmb h }$

The wave component W in (2a) and (2b) and its derivative $W _ { h }$ in (2c) are expressed in [1–3] as

$$
W (h, v) = 2 \pi [ \tilde {H} _ {0} (h) - \mathrm{i} J _ {0} (h) ] e ^ {v}\tag{3a}
$$

$$
W _ {h} (h, v) = 2 \pi \left[ 2 / \pi - \tilde {H} _ {1} (h) + \mathrm{i} J _ {1} (h) \right] e ^ {v}\tag{3b}
$$

where $J _ { 0 } ( h ) , J _ { 1 } ( h )$ and $\tilde { H } _ { 0 } ( h ) , \tilde { H } _ { 1 } ( h )$ denote the common Bessel or Struve functions. The Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ are intrinsic Fortran functions and are then readily evaluated. As is noted in [1], several approximations for the Struve functions $\tilde { H } _ { 0 } ( h )$ and $\tilde { H } _ { 1 } ( h )$ can be found in the literature; $\operatorname { E } g .$ , complementary approximations valid in the regions $0 \leq h \leq 3$ or $3 \ : < \ : h$ are given in [6].

These complementary approximations in contiguous regions defeat the global nature of the approximations to the local-<sup>fl</sup>ow components L and ∇L given in [1]. This drawback of the exact expressions (3) for the wave functions W and ∇W is remedied if one uses the analytical approximations for $\tilde { H } _ { 0 }$ and $\tilde { H } _ { 1 }$ given in [5]. Speci<sup>fi</sup>cally, these approximations are

$$
\begin{array}{c} \tilde {H} _ {0} (h) \approx J _ {1} (h) + A _ {0} (1 - \cos h) / h - B (\sin h - h \cos h) / h ^ {2} \\ - C (h ^ {*} - \sin h ^ {*}) / h ^ {2} \end{array}\tag{4a}
$$

$$
\begin{array}{c} 2 / \pi - \tilde {H} _ {1} (h) \approx J _ {0} (h) - A _ {1} (\sin h) / h - B (1 - \cos h) / h ^ {2} \\ + C (1 - \cos h ^ {*}) / h ^ {2} \end{array}\tag{4b}
$$

where $A _ { 0 } , A _ { 1 } , B , C$ and $h ^ { * }$ are de<sup>fi</sup>ned as

$$
A _ {0} \equiv 1. 1 3 4 8 1 7 7 0 0; A _ {1} \equiv 0. 0 4 0 4 9 8 3 8 2 7\tag{5a}
$$

$$
B \equiv 1. 0 9 4 3 1 9 3 1 8 1; \quad C \equiv 0. 5 7 5 2 3 9 0 8 4 0\tag{5b}
$$

$$
h ^ {*} \equiv 0. 8 8 3 0 4 7 2 9 0 3 h\tag{5c}
$$

The approximate relations (4) express the Struve functions $\tilde { H } _ { 0 }$ and H<sup>˜</sup> in terms of trigonometric functions and the Bessel functions $J _ { 1 }$ and $J _ { 0 } .$ The approximate relations (4)-(5) are shown in [5] to be su<sup>fi</sup>ciently accurate for practical purposes.

## 5. Illustrative numerical applications

For purposes of illustration and validation, linear and mean drift wave loads are computed here for a hemisphere and a freely <sup>fl</sup>oating FPSO, as in [2]. The local-<sup>fl</sup>ow components L and $L _ { h }$ in the Green function G and its gradient ∇G are evaluated via the global approximations given in [1]. These approximations are shown in [2] to be su<sup>fi</sup>ciently accurate for practical purposes. The Struve functions ${ \tilde { H } } _ { 0 } ( h )$ and $\tilde { H } _ { 1 } ( h )$ in the wave components W and ∇W are evaluated via Newman's approximations [6] or via the global approximations (4)-(5).

Wave radiation by a <sup>fl</sup>oating hemisphere, for which an analytical solution exists [7], is considered <sup>fi</sup>rst. The hemisphere is discretized as in Fig. 1. The added-mass coe<sup>fi</sup>cients $a _ { 1 1 }$ and $a _ { 3 3 }$ for surge and heave are adimensional with respect to $2 \pi \rho R ^ { 3 } / 3 ,$ , and the corresponding wavedamping coe<sup>fi</sup>cients $b _ { 1 1 }$ and $b _ { 3 3 }$ are adimensional with respect to 2πρωR<sup>3</sup>/3, where $\rho$ denotes the water density, R is the radius of the hemisphere, and ω is the circular frequency of the time-harmonic oscillatory motions of the hemisphere.

The added-mass and wave-damping coe<sup>fi</sup>cients $a _ { 1 1 } , a _ { 3 3 }$ and $b _ { 1 1 } , b _ { 3 3 }$ are depicted in Fig. 2 for adimensional wavenumbers $0 . 1 \le k _ { 0 } R \le$ 10 where $k _ { 0 } \equiv \omega ^ { 2 } / g .$ Fig. 2 shows that the numerical predictions in which the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H } _ { 1 }$ in expressions (3) for the wave components W and $W _ { h }$ are evaluated via Newman's approximations given in [6] or via the global approximations (4)-(5) cannot be distinguished, and are in excellent agreement with Hulme's analytical results [7].

The second-order mean drift forces and moment related to the quadratic terms in Bernoulli's equation are now evaluated for the hemisphere already considered in Fig. 2 and for a FPSO, discretized as in Fig. 3. The incident waves acting on the hemisphere or the FPSO are determined by the potential

![](images/fb82d12547cb1cac414b89ddc8faa590363e2fc9601e65333ec588a4183c6fab.jpg)  
Fig. 1. Mesh used to discretize a hemisphere via 1761 nodes and 1720 quadrilateral elements.

![](images/66ead04c36e5470cf2f0484edc3a52c655806d90a6506e48affb0800b943ffb1.jpg)

![](images/bd0691d4054e659029caac408a3d19510a1451866b3bce2748f4bef9a7953ac2.jpg)  
Fig. 2. Adimensional added-mass and wave-damping coe<sup>fi</sup>cients $a _ { 1 1 }$ and $b _ { 1 1 }$ for surge (top), and corresponding coe<sup>fi</sup>cients $a _ { 3 3 }$ and $b _ { 3 3 }$ for heave (bottom), predicted by Hulme's analytical solution $[ 7 ] ,$ , or a panel method where the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H _ { 1 } }$ in the wave components $W$ and $W _ { h }$ are evaluated via Newman's approximations [6] or via the global approximations (4)-(5).

![](images/5bc53a7e888223b825ff58067f7f5d7a0598b39ee789dd7a34e4a5faea0731b4.jpg)  
Fig. 3. Mesh used to represent the hull surface of the FPSO considered in the study. 503 quadrilateral panels are used to approximate half of the hull surface.

![](images/41a3c4c881af0f7e2dd5250f8d49cea7cf1170b00de5d159de96643bf780de8e.jpg)  
Fig. 4. Mean drift force $\bar { F } _ { x }$ acting on a <sup>fi</sup>xed hemisphere in incoming regular waves of amplitude a at an incidence angle $\beta = 0 ^ { \circ }$ , where $\bar { F } _ { x }$ is predicted by HydroStar or by a panel method in which the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H _ { 1 } }$ in the wave components W and $W _ { h }$ are evaluated via Newman's approximations [6] or via the global approximations (4)-(5).

![](images/26817e5b92174bc7915584ab3bf9c0d06578d89f566ee1c09868014cc59cef1b.jpg)

![](images/b9c3f679cb391562a92085ff0eefbf63ad4f50493842de8b5c99d3194823289e.jpg)  
Fig. 5. Mean drift forces ${ \bar { F } } _ { x }$ and $\bar { F } _ { y }$ and moment $\bar { M } _ { z }$ acting on a freely <sup>fl</sup>oating FPSO of length L in incoming waves of amplitude a at an incidence angle $\beta = 4 5 ^ { \circ }$ <sup>∘</sup>, where $\bar { F } _ { x } , \bar { F } _ { y }$ and $\bar { M } _ { z }$ are predicted by HydroStar or a panel method in which the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H _ { 1 } }$ in the wave components W and $W _ { h }$ are evaluated via Newman's approximations or the global approximations $_ { ( 4 ) - ( 5 ) }$

$$
\phi^ {I} = (\mathrm{i} a g / \omega) e ^ {k _ {0} [ z + \mathrm{i} (x \cos \beta + y \sin \beta) ]}\tag{6}
$$

where $^ { a , }$ ω and $\beta$ denote the wave amplitude, frequency and incidence angle.

Fig. 4 depicts the mean drift force $\bar { F } _ { x } / ( \rho \mathrm { g a } ^ { 2 } R / 2 )$ acting on the hemisphere for adimensional wavenumbers $0 < k _ { 0 } R \leq 4 .$ . Similarly, Fig. 5 depicts the mean drift forces $( \bar { F } _ { x } , \bar { F } _ { y } ) / ( \rho \mathrm { g a } ^ { 2 } L / 2 )$ and the mean drift moment $\bar { M } _ { z } / ( \rho \mathrm { g a } ^ { 2 } L ^ { 2 } / 2 )$ acting on the FPSO in oblique waves at an in cidence angle $\beta = 4 5 ^ { \circ }$ for adimensional wavenumbers $0 . 1 \leq k _ { 0 } L /$ $2 \leq 1 0 .$ , where L is the length of the FPSO.

Figs. 4 and 5 show that the predictions in which the Struve functions $\tilde { H } _ { 0 }$ and H<sup>˜</sup> in expressions (3) for the wave components W and $W _ { h }$ are evaluated via Newman's approximations given in [6] or via the global approximations (4)-(5) cannot be distinguished, and are in excellent agreement with the predictions given by the Bureau Veritas (BV) software HydroStar, in which G and ∇G are evaluated with high accuracy. The very small di<sup>f</sup>erences between the HydroStar predictions and the predictions associated with the approximations $W _ { \mathrm { N e w m a n } }$ and $W _ { \mathrm { G l o b a l } }$ to

W and $W _ { h }$ mainly stem from the fact that combined source and dipole distributions are adopted in the computations considered here, whereas only sources are used in HydroStar.

The numerical results depicted in $\mathrm { F i g s . ~ 2 , ~ 4 }$ and 5 show that the global approximations (3)-(5) to the wave components W and $W _ { h }$ in the Green function and its gradient are su<sup>fi</sup>ciently accurate for practical applications.

The computing times required to evaluate the wave components W and $W _ { h }$ via Newman's approximations [6] or via the global approx imations (3)-(5) are now compared. These alternative approximation to W and W are implemented in FORTRAN90 and compiled with Intel Fortran. The computations are performed on a laptop with processor of Intel(R) Core(TM) i7-7700HQ @ 2.8 GHz.

The CPU times for $1 0 ^ { 7 }$ evaluations of the global approximations to the local-<sup>fl</sup>ow functions L and $L _ { h }$ given in [1] and the global approximations (3)-(5) to the wave functions W and $W _ { h }$ given here are about 1.25 or 1.7 seconds, respectively, and thus represent about 42% or 58% of the CPU time required to evaluate both the local-<sup>fl</sup>ow and the wave components, i.e. the Green function and its gradient. The larger computing time required for the wave functions W and $W _ { h }$ is due to the fact that expressions $( 3 ) - ( 5 )$ involve the exponential function $e ^ { \nu } ,$ the two Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$ , and the four trigonometric functions cosh, sinh, cosh<sup>\*</sup>, sinh<sup>\*</sup>, whereas the global approximations for the local-<sup>fl</sup>ow functions L and $L _ { h }$ given in [1,2] involve one logarithmic function, two exponential functions and polynomials.

If Newman's approximations to the Struve functions $\tilde { H } _ { 0 }$ and $\tilde { H } _ { 1 }$ are used in $( 3 ) _ { ; }$ , the CPU times for $1 0 ^ { 7 }$ evaluations of the wave components W and $W _ { h }$ are about 1.4 or 3.3 s for $h \leq 3 \ \mathrm { o r } \ 3 \ < \ h ,$ whereas the CPU time is about 1.7 s for every values of h and v if the global approximations (4)-(5) are used in (3) as was already noted. Thus, numerical evaluation of W and $W _ { h }$ via Newman's approximations for the Struve functions is about 18% faster or 94% slower for $h \leq 3$ or $3 \ : < \ : h$ than if the global approximations (3)-(5) are used. These tests are based on single-core computations and involve an ‘if statement’ to determine if $h \leq 3 \ \mathrm { o r } \ 3 \ < \ h$ for Newman's approximations for the Struve functions.

## 6. Conclusion

Although the approximations (4) may arguably be regarded as a trivial modi<sup>fi</sup>cation of the exact expressions (3) for the wave compo nents $W ( h , \nu )$ and $W _ { h } ( h , \nu )$ , this modi<sup>fi</sup>cation is useful for practical applications because it yields global approximations to W and $W _ { h } .$ Indeed, expressions (3)-(4) for W and $W _ { h }$ only involve elementary functions of real arguments and the intrinsic Fortran Bessel functions $J _ { 0 } ( h )$ and $J _ { 1 } ( h )$

These global analytical approximations to the wave components $W ( h , \nu )$ and $W _ { h } ( h , \nu )$ and the global analytical approximations to the local-<sup>fl</sup>ow components $L ( h , \nu )$ and $L _ { h } ( h , \nu )$ given in [1,2] provide particularly simple approximations to $G$ and ∇G that are valid for $0 \leq h$ and $\nu \leq 0 ,$ , i.e. within the entire <sup>fl</sup>ow region. These global approximations can be evaluated simply and e<sup>fi</sup>ciently, and are especially wel suited for parallel computations because they avoid the ‘if statements’ that are required if di<sup>f</sup>erent approximations are used in complementary contiguous subregions of the <sup>fl</sup>ow region $0 \leq h$ and $\nu \leq 0 .$

The illustrative numerical applications given in [2] and here provide solid evidence that the global approximations to the Green function G and its gradient are su<sup>fi</sup>ciently accurate for practical applications. Notably, the contribution of the singular terms in the local-<sup>fl</sup>ow components L and ∇L can be evaluated accurately because these singular terms are explicitly apparent in (2) and in the analytical approximations for L and $L _ { h }$ given in [1,2].

## Acknowledgments

This study was motivated by the observation, reported by Chunmei Xie (Ecole Centrale de Nantes) in a study submitted to Applied Ocean Research, that the approach based on the approximations for the Struve functions $\tilde { H } _ { 0 }$ and H<sup>˜</sup> given in [6], which is used in [1,2] to evaluate the wave components W and $W _ { h } ,$ is not computationally e<sup>fi</sup>cient for $3 \ < \ h .$ The authors thank Chunmei Xie for her useful work.

## References

[1] H. Wu, C. Zhang, Y. Zhu, W. Li, D. Wan, F. Noblesse, A global approximation to the Green function for difraction radiation of water waves, Eur. J. Mech. – B/Fluids 65 (2017) 54–64.

[2] H. Liang, H. Wu, F. Noblesse, Validation of a global approximation to the Green function of difraction radiation in deep water, Appl. Ocean Res. 74 (2018) 80–86

[3] E. Noblesse, The Green function in the theory of radiation and diffraction of regular water waves by a body. J. Eng. Math. 16 (2) (1982) 137–169

[4] J.G. Telste, F. Noblesse, Numerical evaluation of the Green function of water-wave radiation and difraction, J. Ship Res. 30 (2) (1986) 69–84.

[5] R.M. Aarts, A.J.E.M. Janssen, E<sup>fi</sup>cient approximation of the Struve functions H occurring in the calculation of sound radiation quantities, J. Acoust. Soc. Am. 140 (2016).4154-4160

[6] J.N. Newman, Approximations for the Bessel and Struve functions, Math. Comput. 43 (168) (1984) 551–556.

[7] A. Hulme, The wave forces acting on a <sup>fl</sup>oating hemisphere undergoing forced periodic oscillations, J. Fluid Mech. 121 (1982) 443–463.