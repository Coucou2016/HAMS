# A calculation method for finite depth free-surface green function

Yingyi Liu<sup>1</sup>, Hidetsugu Iwashita<sup>2</sup> and Changhong Hu<sup>3</sup>

<sup>1</sup>Interdisciplinary Graduate School of Engineering Science, Kyushu University, Kasuga, Fukuoka, Japan <sup>2</sup>Falculty of Engineering, Hiroshima University, Kagamiyama, Higashi-Hiroshima, Japan <sup>3</sup>Research Institute for Applied Mechanics, Kyushu University, Kasuga, Fukuoka, Japan

ABSTRACT: An improved boundary element method is presented for numerical analysis of hydrodynamic behavior of marine structures. A new algorithm for numerical solution of the finite depth free-surface Green function in three dimensions is developed based on multiple series representations. The whole range of the key parameter R/h is divided into four regions, within which different representation is used to achieve fast convergence. The well-known epsilon algorithm is also adopted to accelerate the convergence. The critical convergence criteria for each representation are investigated and provided. The proposed method is validated by several well-documented benchmark problems.

KEY WORDS: Boundary element method; Free-surface green function; Fast numerical solution.

## INTRODUCTION

Prediction of the hydrodynamic performance of a floating platform for ocean renewable energy has been an important issue in recent years. Although extensive researches have been carried out on offshore oil platforms, many new research topics arise in the development of offshore renewable energy platform due to the different cost requirement and the existence of wind turbines on the deck. The present research is aiming to develop a new and efficient analysis tool for such ocean renewable energy platforms. A Boundary Element Method (BEM) has been developed for calculation of hydrodynamic loads on the platform. This paper presents a new algorithm for numerical solution of the finite depth free-surface Green function in three dimensions which is used in the proposed method.

Among various numerical methods nowadays, the boundary element method based on potential flow theory is one of the most popular methods due to its fast and efficient computation. Under the assumption that the fluid is incompressible, inviscid and irrotational, the BEM uses an appropriate Green function together with Green’s theorem to formulate the boundary integral equations with appropriate boundary conditions. Numerical algorithms of BEM include discretization of the body surface into some low-order elements or higher-order elements, distribution of the sources/dipoles on the submerged part of the hull surface, and calculation of the influence coefficients between arbitrary two sources/dipoles. In this method, the numerical solution of the free-surface Green function consumes a large portion of CPU time.

An alternative approach for simple-shape bodies is the multipole expansion method which was first investigated by Ursell (1949) and Havelock (1955). These multipoles, generally contain two parts, i.e., the wave-free term which vanishes in the far field away from the structure, and the wave-source term which travels radially outwards at infinity (Liu et al., 2012). While the wave-free term consists of some infinite series which are easy for evaluation, the wave-source term including the free-surface Green function is hard to be numerically calculated. Therefore, no matter which method is used, efficient numerical implemen tation of the free-surface Green function remains the major task (Newman, 1992).

Numerous work has been done on the subject of the free-surface Green function. John (1949; 1950) first derived a variety of representations in both two and three dimensions with the consideration of both infinite and finite water depth. Infinite series expansion method for Green function under finite depth was presented by Wehausen and Laitone (1960). Thorne (1953), Mei (1983) and Linton and McIver (2001) also have important contribution. As to its numerical evaluation, several scholars have done many important works from 1980s, in which Newman (Newman, 1985; 1992) developed several efficient algorithms for both frequency domain and time domain Green functions in zero forward speed, which have been wildly used in this field. Pidcock (1985) derived several valuable expressions of the frequency domain Green function in finite depth, using series expansions. Linton (1999) suggested a novel set of representations for Green functions of Laplace's equation, which converges rapidly provided the optimal value of a parameter a is properly given.

There are mainly three schemes for solution of Green functions: separation of the local and the far-field component and tabulation; numerical integration and Chebyshev approximation; utilization of series representations and acceleration. The first scheme usually needs to seek elaborate mathematical derivations. The second scheme requires computation of the principal integral, which is usually not numerically stable by an adaptive integration method. In addition, it is difficult to choose the optimal subdivision of regions for Chebyshev approximation. The last scheme is much easier for programming, but requires different series representations in different regions with respect to the ratio R/h (R is the horizontal distance between source and field point, and h is the water depth). As to the authors' knowledge, there are still rooms to do research on improvement of methods based on the first or the third scheme for evaluating finite-depth free surface Green function. John's eigenfunction expansion representation (John, 1950) converges rapidly except for relatively small R/h. Pidcock's representations (Pidcock, 1985) are invalid for large wave numbers when R/h is small, and it is difficult to find an appropriate convergence criterion for the summation of the series terms. Linton's rapidly convergent representation (Linton, 1999) converges in the whole domain of R/h. However, it needs careful selection of the parameter a according to the ratio R/h and the wave number v, which is not a trivial work.

In this paper, we propose an efficient boundary element method that can be used to predict hydrodynamic property of an ocean renewable energy platform. The major contribution of this research is that a new algorithm for numerical solution method of the free surface Green function is developed. According to the ratio R/h, the computation domain is divided into four subdomains in which different series expansion scheme is used. The well-known epsilon algorithm is adopted to accelerate the convergence. A rapidly convergent expression scheme, which is based on the Chebyshev approximation method, is derived by substitution of its counterpart into Pidcock's representation. The optimal selection method of the parameter a is also given for small R/h in Linton's representation. In addition, the critical convergence criteria for each representation are also studied and some practical linear approximations are given. To remove the irregular frequencies in the wave interaction problem of surface piercing bodies, the partial extended boundary integral equation method originates from Lau and Hearn (1989) is applied. Several validation examples are presented to demonstrate the performance of the method. Finally, as an example of engineering application, numerical results by the proposed method are shown with the comparison to other numerical methods.

## SOLUTION OF THE BOUNDARY VALUE PROBLEMS

## Mixed-source/dipole BEM formulation

Denote the coordinate system to be right-handed Cartesian coordinate system (x,y,z) with its x-y plane taken as the undis turbed sea level and the z-axis taken vertically upwards. Consider an incident wave transmitting along the direction positive, and a rigid body floating or being submerged in water of constant depth with a free surface. Under the usual assumptions of an inviscid, irrorational and incompressible flow, the problem can be described by a velocity potential

$$
\Phi (x, y, z, t) = \operatorname{Re} \left(\phi_ {0} (x, y, z) e ^ {- i \omega t}\right) + \operatorname{Re} \left(- \mathrm{i} \omega \sum_ {j = 1} ^ {6} \phi_ {j} (x, y, z) \xi_ {j} e ^ {- i \omega t}\right) + \operatorname{Re} \left(\phi_ {7} (x, y, z) e ^ {- i \omega t}\right),\tag{1}
$$

where $\phi _ { 0 }$ stands for the incident wave potential, $\phi _ { 1 } \sim \phi _ { 6 }$ stands for the radiation potential of six degrees, respectively, and $\phi _ { 7 }$ stands for the diffraction potential; $\xi _ { j }$ stands for the complex amplitude of the body motion in each of the six degrees of freedom; $e ^ { - \mathrm { i } \omega t }$ is a time-harmonic factor with a circular frequency ω.

Application of Green’s theorem provides a mixed-source/dipole boundary integral equation for solving the values of the potential on the immersed body surface $S _ { \mathrm { B } } \mathrm { : }$

$$
2 \pi \phi_ {j} (\mathbf {P}) + \iint_ {S _ {B}} \phi_ {j} (\mathbf {Q}) \frac {\partial G (\mathbf {P} , \mathbf {Q})}{\partial n _ {Q}} \mathrm{d} S _ {Q} = \iint_ {S _ {B}} V _ {j} (\mathbf {Q}) G (\mathbf {P}, \mathbf {Q}) \mathrm{d} S _ {Q} \quad (\mathbf {P} \in S _ {B}, \mathbf {Q} \in S _ {B})\tag{2}
$$

where $P ( x , y , z )$ and $\it Q ( \xi , \eta , \zeta )$ represent the field point and the source point, respectively. The Green function $G$ can be further decomposed into the following form in order to subtract its singularity:

$$
G = 1 / r + \tilde {G} _ {\mathrm{,}}
$$

where $r$ is the Euclidean distance between the field point P and the source point $Q .$ By assuming the potential to be constant on each flat quadrilateral/triangle panel and applying the collocation method at the centroid of each panel, Eq. (2) may be written in the discrete form

$$
\begin{array}{l} 2 \pi \phi_ {j} (\mathbf {P} _ {m}) + \sum_ {n = 1} ^ {N} \phi_ {j} (\mathbf {Q} _ {n}) \left[ D _ {m n} + \left\{\frac {\partial}{\partial n _ {Q}} \tilde {G} (\mathbf {P} _ {m}, \mathbf {Q} _ {n}) \right\} \Delta S _ {n} \right] \\ = \sum_ {n = 1} ^ {N} V _ {j} (\mathbf {Q} _ {n}) \left[ S _ {m n} + \left\{\tilde {G} (\mathbf {P} _ {m}, \mathbf {Q} _ {n}) \right\} \Delta S _ {n} \right], \quad (m = 1, 2, \dots , N) \end{array}\tag{3}
$$

where N is the number of elements on the body surface, and

$$
S _ {m n} = \iint_ {S _ {n}} \frac {1}{r} \mathrm{d} S _ {Q}\tag{4a}
$$

$$
D _ {m n} = \iint_ {S _ {n}} \frac {\partial}{\partial n _ {Q}} \left(\frac {1}{r}\right) d S _ {Q}\tag{4b}
$$

are the singular integrations of the source and dipole distributions over each panel, which are successfully evaluated by the analytical algorithm of Newman (1986).

After solving the standard boundary value problems, various hydrodynamic quantities including added mass, wave damping coefficient and free-surface elevation, etc, may be obtained by direct integration.

## Free-surface green function in constant depth

The free-surface Green function physically means the influence of an oscillating source at the source point to the potential at the field point, which must satisfy

$$
\left(\frac {\partial^ {2}}{\partial x ^ {2}} + \frac {\partial^ {2}}{\partial y ^ {2}} + \frac {\partial^ {2}}{\partial z ^ {2}}\right) G (x, y, z) = \delta (x - \xi) \delta (y - \eta) \delta (z - \zeta) \text { in } \Omega\tag{5}
$$

and all the same boundary conditions except that on the body surface, where δ is the Dirac delta function.

John (1950) has first deduced the original integral representation of Green function, whose three-dimensional finite water depth form can be written as

$$
G = \frac {1}{r} + \frac {1}{r _ {2}} + 2 \int_ {0} ^ {\infty} \frac {(\mu + v) \cosh \mu (z + h) \cosh \mu (\zeta + h)}{\mu \sinh \mu h - v \cosh \mu h} e ^ {- \mu h} J _ {0} (\mu R) d \mu\tag{6}
$$

where the path of the contour integral in Eq. (6) passes below the pole at $\mu { = } k _ { , } r _ { 2 }$ is the distance between the field point and the image of the source point with respect to the sea bottom, i.e.,

$$
r _ {2} = \left\{\left(x - \xi\right) ^ {2} + (y - \eta) ^ {2} + (z + \zeta + 2 h) ^ {2} \right\} ^ {1 / 2};
$$

k is the positive root of the dispersion equation

$$
k \tanh k h = v,\tag{7a}
$$

and $\mu _ { m } ( m { = } 0 , 1 , 2 . . . )$ satisfy the following equation

$$
\mu_ {m} \tan \mu_ {m} h = - v,\tag{7b}
$$

where $\mu _ { 0 }$ is imaginary, $\mu _ { 0 } = - \mathrm { i } k ,$ and $\mu _ { m } \left( m = 1 , 2 . . . \right)$ are positive.

It should be noted that, Eq. (6) is not a convenient form for numerical evaluation of the Green function, since the oscillating and singular nature of its integrand brings too much trouble for direct integration, which also seems be of high expensive computation cost. One of the appropriate ways for doing the evaluation is to use the series or asymptotic expan sions. Therefore, an integrated strategy is proposed through our various numerical tests. With the definition domain of the parameter R/h being divided into four regions, a family of series expansions or asymptotic expansions are used. The details are given as follows.

## EVALUATION OF THE GREEN FUNCTION

## Region A: R/h ≥0.5

In this first region, Newman (1985) suggested the use of eigenfunction expansion, which was first derived by John (1950)

$$
\begin{array}{l} G = 2 \pi \mathrm{i} \frac {k ^ {2} - v ^ {2}}{\left(k ^ {2} - v ^ {2}\right) h + v} \cosh k (z + h) \cosh k (\zeta + h) H _ {0} ^ {(1)} (k R) \\ + 4 \sum_ {m = 1} ^ {\infty} \frac {\mu_ {m} ^ {2} + v ^ {2}}{\left(\mu_ {m} ^ {2} + v ^ {2}\right) h - v} \cos \mu_ {m} (z + h) \cos \mu_ {m} (\zeta + h) K _ {0} (\mu_ {m} R) \end{array}\tag{8}
$$

where $H _ { 0 } ^ { ( 1 ) }$ is Hankel function of the first kind, $H _ { 0 } ^ { ( 1 ) } \left( k R \right) = J _ { 0 } \left( k R \right) + \mathrm { i } Y _ { 0 } \left( k R \right)$ $J _ { 0 }$ and $Y _ { 0 }$ are Bessel function of the first and second kind, respectively.

The above form avoids evaluation of Bessel function for complex arguments, however, nowadays by utilizing existing computer subroutine for complex Bessel functions, Eq. (8) can be compressed into another alternative form

$$
G = \sum_ {m = 0} ^ {\infty} \frac {2 K _ {0} (\mu_ {m} R)}{h N _ {m} ^ {2}} \cos \mu_ {m} (z + h) \cos \mu_ {m} (\zeta + h),\tag{9a}
$$

where

$$
N _ {m} ^ {2} = \frac {1}{2} \left(1 + \frac {\sin 2 \mu_ {m} h}{2 \mu_ {m} h}\right),\tag{9b}
$$

For $k R > > 1$ , the non-oscillatory local flow component vanishes, only left with the propagating wave mode which may be written as (Mei, 1983)

$$
G = 2 \pi \mathrm{i} \frac {k ^ {2} - v ^ {2}}{\left(k ^ {2} - v ^ {2}\right) h + v} \cosh k (z + h) \cosh k (\zeta + h) \left(\frac {2}{\pi k R}\right) ^ {1 / 2} e ^ {\mathrm{i} (k R - \pi / 4)}\tag{10}
$$

where the asymptotic behavior of the Hankel function is used. By making use of this advantage, the computation speed will be improved.

The number of terms required for a given accuracy of Eq. (9a) is proportional to the ratio $h / R ,$ thus [6h/R] is an appropriate number of terms for achieving 6D accuracy, as pointed out by Newman (1985). In our program, from the second term in Eq. (9a), a convergence condition is used, which guarantees the loop stop at the condition when absolute values of $\mathbf { \Delta } G , G _ { R }$ and $G _ { z }$ are all less than 1.e-8. Therefore, satisfactory results for 6D accuracy are achieved throughout the whole region with a maximum number of terms 10. When $R / h < 1 . 0 $ , comparatively more terms are needed to achieve 6D accuracy until the maximum number of terms is found at $R / h = 0 . 5$ . When $R / h > 1 . 0$ , the terms needed for 6D accuracy are even less, one or two terms (except the zeroth term) are enough provided R/h is sufficient large.

## Region B: 0.05≤ R/h <0.5

The eigenfunction expansion needs more terms to achieve the convergence as the parameter R/h becomes smaller. A non linear series accelerating method named epsilon algorithm is adopted in this region to increase the rate of convergence of the eigenfunction expansion sequence. This algorithm, also named as Wynn’s epsilon method, first discovered by Wynn (1956), is generally considered as an improved version of the similar Shank’s transformation.

Denoting $S _ { m }$ to be the sum of the first m terms $( m { = } 1 , 2 , . . . ,$ except m=0) in Eq. (9a), and $\boldsymbol { \varepsilon } _ { k } ^ { m }$ to be the transformation of $S _ { m }$ by epsilon algorithm, it comprises the following initialization and iterative phases:

Initialization: let $\mathcal { E } _ { 0 } ^ { ( m ) } = S _ { m }$ , and set artificially $\mathcal { E } _ { - 1 } ^ { ( m ) } = 0$ , for $m { = } 0 , 1 , 2$

Iteration: $\mathcal { E } _ { k + 1 } ^ { ( m ) } = \mathcal { E } _ { k - 1 } ^ { ( m + 1 ) } + \left[ \mathcal { E } _ { k } ^ { ( m + 1 ) } - \mathcal { E } _ { k } ^ { ( m ) } \right] ^ { - 1 }$ , for k, $\ m { = } 0 , 1 , 2 . . .$

Through our numerical test, with the acceleration of epsilon algorithm, only 10\~50 terms are needed in this region for 5D accuracy (10 for $R / h = 0 . 5$ and 50 for $R / h = 0 . 0 5 )$ , locally 6D accuracy can be achieved. To achieve at least 5D accuracy with the lowest cost of computation, we suggest the following formula for the number of the terms needed with respect to the para meter R/h

$$
M = - 8 8. 8 9 R / h + 5 4. 4 5.\tag{11}
$$

## Region C: 0.0005≤ R/h <0.05

In region $C ,$ the eigenfunction expansion becomes almost useless even with simultaneous implementation of the epsilon algorithm. This urges us to search for another possible way of accelerating the convergence of the sequence. By utilizing the improved expansion proposed in Pidcock (1985) by subtracting a simpler series with same asymptotic form for large $m ,$ the Green function is formulated as

$$
G = 4 \sum_ {m = 1} ^ {\infty} \left[ a _ {m} K _ {0} (\mu_ {m} R) - a _ {m} ^ {*} K _ {0} (\mu_ {m} ^ {*} R) \right] + \mathrm{i} \Lambda H _ {0} ^ {(1)} (k R) + \frac {2}{h} \left[ \gamma + \log \left(\frac {R}{4 h}\right) \right] + \frac {1}{r} + \frac {1}{r ^ {\prime}} + \Sigma_ {G},\tag{12a}
$$

where

$$
a _ {m} = \frac {\mu_ {m} ^ {2} + v ^ {2}}{\left(\mu_ {m} ^ {2} + v ^ {2}\right) h - v} \cos \mu_ {m} (z + h) \cos \mu_ {m} (\zeta + h),\tag{12b}
$$

$$
a _ {m} = \frac {1}{h} \cos \mu_ {m} ^ {*} (z + h) \cos \mu_ {m} ^ {*} (\zeta + h),\tag{12c}
$$

$$
\Sigma_ {G} = \sum_ {l = 1} ^ {\infty} \left(b _ {l} ^ {+} + b _ {l} ^ {-} + c _ {l} ^ {+} + c _ {l} ^ {-} - \frac {2}{l h}\right),\tag{12d}
$$

$$
b _ {l} ^ {\pm} = \left\{R ^ {2} + \left[ 2 l h \pm (z - \zeta) \right] ^ {2} \right\} ^ {- 1 / 2},\tag{12e}
$$

$$
c _ {l} ^ {\pm} = \left\{R ^ {2} + \left[ 2 l h \pm (z + \zeta + 2 h) \right] ^ {2} \right\} ^ {- 1 / 2},\tag{12f}
$$

$$
\Lambda = \frac {2 \pi (k ^ {2} - v ^ {2}) \cosh k (z + h) \cosh k (\zeta + h)}{(k ^ {2} - v ^ {2}) h + v}.\tag{12g}
$$

where $K _ { 0 }$ is modified Bessel function of the second kind; $\gamma = 0 . 5 7 7 2 1 5 6 6 4 9 0 1 5 3 2 8 .$ $\mu _ { m } ^ { * }$ is an approximation of $\mu _ { m }$ when m is large, $\mu _ { m } ^ { * } = m \pi / h$ . Eq. (12a) converges more quickly than Eq. (9a) for small $R / h ,$ nevertheless, a significant improvement in the convergence rate can still be made. Pidcock (1985) suggested the following formula to be used for l≥3

$$
b _ {l} ^ {+} + b _ {l} ^ {-} + c _ {l} ^ {+} + c _ {l} ^ {-} - \frac {2}{l h} \sim \sum_ {n = 3} ^ {\infty} \frac {\lambda_ {n}}{l _ {n}},
$$

where $\lambda _ { n }$ are constants. However, the values of these constants have not been given in Pidcock (1985) and it seems not a trivial task. Here, we derive a convenient and useful representation for calculating Eq. (12d):

$$
\begin{array}{l} \frac {1}{r} + \frac {1}{r ^ {\prime}} + \Sigma_ {G} = \sum_ {l = 1} ^ {1} \left\{\frac {1}{\sqrt {R ^ {2} + [ (z - \zeta) + 2 l h ] ^ {2}}} + \frac {1}{\sqrt {R ^ {2} + [ (z + \zeta + 2 h) + 2 l h ] ^ {2}}} \right\}, \\ - \frac {2}{h} + \frac {1}{h} \sum_ {m, n} a _ {m, n} \left(\frac {r}{h}\right) ^ {2 m} \left[ \left(\frac {z - \zeta}{h}\right) ^ {2 n} + \left(\frac {z + \zeta + 2 h}{h}\right) ^ {2 n} \right] \end{array}\tag{13}
$$

where $a _ { m , n }$ are Chebyshev coefficients corresponding to the integral defined in Eq. (7.5) of Newman (1992), in which the values of these coefficients are also listed. Actually, only up to $m { = } 4$ and $n { = } 4$ terms of the Chebyshev expansion in Eq. (13) are needed to obtain at least 6D accuracy.

To further accelerate the computation, the epsilon algorithm described in section 4 is also utilized in this region. Based on our numerical test, with this improved Pidcock’s formula, 50\~100 terms are needed in region C for 6D accuracy (50 for $R / h =$ 0.05 and 100 for $R / h { = } 0 . 0 0 0 5 )$ . To achieve such an accuracy with the lowest cost of computation, we also suggest the following formula for the number of the terms needed with respect to the parameter R/h

$$
M = - 1 0 1 0. 1 0 R / h + 1 0 0. 5 0.\tag{14}
$$

## Region D: R/h <0.0005

With the even less parameter R/h, Eq. (12a) will not be a good option since it will require a large number of terms (even thousands) to achieve a given accuracy. In Pidcock (1985), a special formula is also given for the case of $R = 0 ,$

$$
G = - 4 \sum_ {m = 1} ^ {\infty} \left(a _ {m} \log \left(\mu_ {m}\right) - a _ {m} ^ {*} \log \left(\mu_ {m} ^ {*}\right)\right) + \mathrm{i} \Lambda J _ {0} (k R) - \frac {2}{h} \left[ \log (2 h) + \frac {\Lambda h}{\pi} \log (k) \right] + \frac {1}{r} + \frac {1}{r ^ {\prime}} + \Sigma_ {G},\tag{15}
$$

where the symbols here are already defined in Eq. (12a)\~Eq. (12f). However, as we can see, Eq. (15) is obtained based on the assumptions that for small values of $\mu _ { m } R , K _ { 0 } ( \mu _ { m } R ) \sim - \log ( \mu _ { m } R / 2 ) + \gamma ,$ and $Y _ { 0 } ( \mu _ { m } \ : R ) \sim ( 2 / \pi ) [ \log ( \mu _ { m } \ : R / 2 ) + \gamma ] .$ . These two assumptions require both small value for $\mu _ { m }$ and R, which means that Eq. (15) is invalid if $\mu _ { m }$ or R is of a bit large value (for instance, even for $\mu _ { m } { \geq } 0 . 5 , R { \geq } 0 . 1 )$ . Actually, according to our numerical check, Eq. (15) is best valid for $\mu _ { m } < 0 . 5 , R / h <$ 0.0005 with an accuracy of 5D. This leads to our searching for other practical formulae for all relevant values of $\mu _ { m }$

The rapidly convergent representation for free-surface Green function proposed by Linton (1999) based on Ewald’s method (Ewald, 1921) is used in region D since its good convergence in the neighbourhood of $R / h = 0$

$$
\begin{array}{l} G = \mathrm{i} \frac {\pi}{N _ {0}} J _ {0} (k R) \cosh k (z + h) \cosh k (\zeta + h) + \sum_ {m = 0} ^ {\infty} \frac {\Lambda_ {m}}{N _ {m}} \cosh k _ {m} (z + h) \cosh k _ {m} (\zeta + h) \\ + \frac {1}{r} \operatorname{erfc} \left(\frac {r}{a h}\right) + \frac {1}{r ^ {\prime}} \operatorname{erfc} \left(\frac {r ^ {\prime}}{a h}\right) + \sum_ {n = 0} ^ {\infty} (- 1) ^ {n} L _ {n} \end{array} ,\tag{16a}
$$

where

$$
\Lambda_ {0} = - \pi Y _ {0} (k R) - \int_ {0} ^ {a ^ {2} h ^ {2} / 4} \frac {e ^ {- R ^ {2} / 4 t}}{t} e ^ {k ^ {2} t} d t,\tag{16b}
$$

$$
\Lambda_ {m} = \int_ {a ^ {2} h ^ {2} / 4} ^ {\infty} \frac {e ^ {- R ^ {2} / 4 t}}{t} e ^ {- k _ {m} ^ {2} t} d t.\tag{16c}
$$

Linton (1999) has proved that the contributions from $L _ { n } \left( n { = } 2 , 3 . . . \right)$ are much less than the desired accuracy for $G ,$ which therefore are neglected, leaving only the first term as

$$
L _ {1} = - \sum_ {i = 1} ^ {4} \frac {\operatorname{erfc} \left[ (a h) ^ {- 1} \left(R ^ {2} + \chi_ {1 , i} ^ {2}\right) ^ {1 / 2} \right]}{\left(R ^ {2} + \chi_ {1 , i} ^ {2}\right) ^ {1 / 2}} - \int_ {0} ^ {a h / 2} \frac {e ^ {k ^ {2} t ^ {2} - R ^ {2} / 4 t ^ {2}}}{t} \sum_ {i = 1} ^ {4} e ^ {- K \chi_ {1, i}} \operatorname{erfc} \left(\frac {\chi_ {1 , i}}{2 t} - K t\right) \frac {\mathrm{d} t}{t},\tag{16d}
$$

where

$$
\chi_ {n, 1} = 2 (n - 1) h - \zeta - z, \chi_ {n, 2} = 2 n h - \zeta + z,
$$

$$
\chi_ {n, 3} = 2 n h + \zeta - z \quad \text { and } \quad \chi_ {n, 4} = 2 (n + 1) h + \zeta + z.
$$

As we can see, the three integrals in Eq. (16b), Eq. (16c) and Eq. (16d) are not easy to compute. However, by developing a global adaptive Gauss-Kronrod quadrature subroutine, these integrals are well computed accurately (Liu, 2012). Numerica integration still causes large time consumption, an improvement for the calculation will be the utilization of series expansion in some local areas. The following formula suggested by Linton (1999) is used for Eq. (16b) whenever R/a≤0.5:

$$
\begin{array}{c} \Lambda_ {0} = - \gamma - 2 \log \left(\frac {\mu a h}{2}\right) + E _ {n + 1} \left(\frac {R ^ {2}}{a ^ {2} h ^ {2}}\right) \sum_ {n = 1} ^ {\infty} \left[ \frac {(- 1) ^ {n}}{n n !} \left(\frac {R}{a h}\right) ^ {2 n} - \frac {1}{n !} \left(\frac {\mu a h}{2}\right) ^ {2 n} \right. \\ \left. - \frac {2 (- 1) ^ {n}}{(n !) ^ {2}} \left(\frac {\mu R}{2}\right) ^ {2 n} \left(\log \left(\frac {\mu R}{2}\right) + \gamma - \sum_ {p = 1} ^ {n} \frac {1}{p}\right) \right] \end{array} ,\tag{17a}
$$

while the following formula is used for Eq. (16c) whenever R/a≤1.0:

$$
\Lambda_ {m} = \sum_ {n = 0} ^ {\infty} \frac {(- 1) ^ {n} (R / a h) ^ {2 n}}{n !} E _ {n + 1} \left(\mu_ {m} ^ {2} a ^ {2} h ^ {2} / 4\right).\tag{17b}
$$

Both Eq. (17a) and Eq. (17b) can be derived through the Taylor expansion, variable substitution, integration term by term analytically, and substitution with the definition of series expansion of the exponential integral. Especially, for the extreme case when $R / h = 0$ , the following equations is recommended (Linton, 1999):

$$
\Lambda_ {0} = - \operatorname{Ei} \left(\frac {\mu^ {2} a ^ {2} h ^ {2}}{4}\right),\tag{18a}
$$

$$
\Lambda_ {m} = E _ {1} \left(\frac {\mu_ {m} ^ {2} a ^ {2} h ^ {2}}{4}\right).\tag{18b}
$$

where the two kinds of exponential functions are defined as the same in Abramowitz and Stegun (1965). Eq. (18a) and Eq.

(18b) can be obtained through the substitution of the integration definition of the exponential integral with the integrals in Eq. (16b) and Eq. (16c).

However, it should be noted that, no matter whether the integral form (Eq. (16b) and Eq. (16c)) or the series expansion form (Eq. (17a) and Eq. (17b)) is used, the computation of the coefficients for $\varLambda _ { 0 }$ and $A _ { m }$ will not lead to an accurate result, even will not converge, if an inappropriate value of the parameter a is chosen. Unfortunately, the selection of parameter a is not given in Linton (1999). Indeed, the optimal value for a varies with two factors, the wave number v and the ratio of horizontal distance to water depth R/h, which leads to difficulty of programming. In region $\mathrm { D } ,$ nevertheless, due to the narrow variation of the factor R/h, the contribution from R/h can be neglected. Therefore, by polynomial approximation, the following formulae are recom mended for the optimal selection of a with only the variation of factor v

$$
a = \frac {c}{v h},\tag{19a}
$$

where

$$
c = 3 3 2 4. 2 v ^ {3} - 2 5 8. 8 9 v ^ {2} + 8. 3 9 5 8 v + 1. 3 2 0 8, \text {   when   } v \in [ 0, 0. 0 2 ],\tag{19b}
$$

$$
c = - 3 0. 3 0 3 v ^ {3} - 2. 8 1 3 8 v ^ {2} + 2. 7 7 4 0 v + 0. 0 5 0 5 2, \text {   when   } v \in [ 0. 0 2, 0. 1 ],\tag{19c}
$$

$$
c = 1. 5 6 9 9 v ^ {3} - 2. 5 0 7 5 v ^ {2} + 1. 8 3 1 6 v + 0. 1 0 7 7 0, \text {   when   } v \in [ 0. 1, 1. 0 ],\tag{19d}
$$

$$
c = - 0. 0 0 0 0 6 9 6 4 1 v ^ {3} - 0. 0 0 1 7 0 8 2 v ^ {2} + 0. 4 5 5 6 6 v + 0. 8 0 5 5 1, \text {   when   } v \in [ 1. 0, 2 5. 0 ].\tag{19e}
$$

By utilizing this Linton’s formula with the optimal selection of parameter a as described above, generally less than 10 terms are sufficient throughout region D to achieve at least 6D accuracy.

## NUMERICAL RESULTS AND DISCUSSION

## Validation of the evaluation of Green function

In this section, numerical computations are performed to validate the proposed method of free-surface Green function calculation. The algorithm of infinite water depth Green function described in Kashiwagi et al (2003) and the algorithm of finite water depth Green function described in Newman (1985) are adopted to validate the present method.

Fig. 1 shows the variation of the real part of Green function and its derivatives over R/h for a relatively small wave number. The horizontal distance R is divided by the finite depth h as well for infinite depth Green function for the purpose of comparison. The three sub-figures Figs. 1(a)\~(c) at the left side are the local magnificent for small R/h of the right-side sub-figures. It is observed that for both small and large value of $R / h ,$ the present results coincide very well with the method of finite depth Green function by Newman (1985). In addition, under present location of the source point and the field point, finite depth effect can be observed for the real part of Green function, while for the derivatives they can not be observed, by comparison with results of the infinite depth Green function.

![](images/b261baa06c7762fcd77dafc4c2cb8cbf5e59c357f2897be6c200623685451d4a.jpg)  
(a)

![](images/32fe22b3388e1ea766bf921ea277ed6d03443260c1806c350769a6d42e156df1.jpg)  
(b)

![](images/4b0a5b9bf896357a3a8364ef323653d0000c15728a00bc0565a34c99672bff61.jpg)  
(c)

![](images/7f6605d19e6f61140ed3f79bce6cb9a938511fdd8bee5b2ef305f1087d48b358.jpg)  
(d)

![](images/ae856a9783540fc774821309536d5c11e1155a3718d5f0490d9f7e77703a5eb9.jpg)  
(e)

![](images/8081894c6364d39ed638336e35a603d47e0a10d6099288b5f557c506caa0be68.jpg)  
(f)  
Fig. 1 Comparison of Green function and its derivatives for a small wave number $( \nu = 0 . 0 0 5 ~ m ^ { - 1 } , h = 2 . 0 ~ m , \zeta = - 0 . 2 ~ m , z = - 0 . 3 ~ m ) .$

Fig. 2 shows the variation of the real part of Green function and its derivatives over R/h for a relatively large wave number. It is also observed that for both small and large value of R/h, the present results obtain high agreement with the results of Newman (1985). In addition, in this case, finite depth effect can be observed obviously for the real part of G and its z-derivative in the local magnified sub-figures, while for the x-derivative they can not be observed.

![](images/8dca1da8401ce8e6c0ca200646cc7d4c91d340c71214fabff96d3e44103bfb70.jpg)  
(a)

![](images/132b153a92f02fad7b91fee104849e2d510c8688566fadb8eb0dc7cce7659df0.jpg)  
(b)

![](images/46670e5ff3f6543aab3af5830ece250c87cc3141cbaea5398cf5c232d75f862d.jpg)  
(c)

![](images/ab50e3f2ca2db19c0f7cbab20890c4e5a7e8d1d4bd9d21700b23734b32070d81.jpg)  
(d)

![](images/439eebe6aff23065346af7bea1cd1da3b217f841abf7285c0c657a16956f27b4.jpg)  
(e)

![](images/6907e8d2c32fffcc0191cd74dfc20a4386798fc17053cfa3f2fb332020f8ac6a.jpg)  
(f)  
Fig. 2 Comparison of Green function and its derivatives for a large wave number $( \nu = 2 . 0 \ m ^ { - I } , h = 1 . 0 \ m , \zeta = - 0 . 1 \ m , z = 0 . 0 \ m ) .$

## Numerical example for a circular dock in finite water depth

A circular dock is used as the numerical example to validate the present numerical method in hydrodynamic computation. The hull surface is meshed by $4 0 { \times } 2 0 { \div } 4 0 { \times } 2 0$ constant panels (40 in annular and 20 in both radial and draft directions), with additional 40×20 panels (40 in annular and 20 in radial) in the waterplane to suppress the irregular frequencies, in totally 2400 elements. For convergence test, another mesh in 600 panels is also used, with a half decrease in each direction. Both of meshes are shown in Fig. 3. The radius R is $^ { a , }$ the ratio of draft D to the radius and the ratio of finite depth to the radius are 0.5 and 0.75, respectively. The finite water depth h is a. The analytical eigenfunction method of Garret (1971) is adopted to validate the pre sent model. Non-dimensional numerical results are shown in Fig. 4 and Fig. 5

![](images/8d0617fc29d2a17a819ca4ef30846d6194410124b10e9b9919073ea9dab7bb50.jpg)  
(a) Mesh of dock in 600 panels.

![](images/554e5e9c8a4cc0942eda1c3a1527117e8cbea273a8bb55bc82d6008401a51e75.jpg)  
(b) Mesh of dock in 2400 panels.  
Fig. 3 Mesh for the circular dock.

Fig. 4 shows comparison of modulus of complex exciting wave forces against dimensionless radius ka. It is observed that for both the horizontal force, the vertical force, and the torque, the present results agree well with the analytical results obtained by eigenfunction method. The comparison also show that, with the increase of number of panels, results of present numerica method approach that by analytical method.

![](images/03b3764b4cdaebaa2cc2606eeb11c4270f54c4097ae383edf0040fad84dfb608.jpg)  
(a) Horizontal exciting force.

![](images/878937024448ebbd53110290519de4cbca55ed826534ce188501d153ac776a3a.jpg)  
(b) Vertical exciting force.

![](images/8a81e89a2ef177946deb2ce5a1f4811efb1b113419eebd2bb0b24d29c259a551.jpg)  
(c) Exciting torque.  
Fig. 4 Modulus of the complex exciting wave forces of a circular dock.

Fig. 5 shows computation of the hydrodynamic quantities and effect of the irregular freque- ncies. All the quantities are normalized by the volume of submerged part of dock, i.e., $V = D \pi a ^ { 2 }$ . In the neighborhood of the irregular frequencies, the “Unremoved” method has sharp leap and decline within small intervals, leading to ignorable numerical errors. While the “Removed” method based on the modified boundary integral equation, has been smooth in the entire neighborhood.

![](images/8c1f80ca8a38f0d7778f940c4caf1f0e549ee664efe49d86c2713fc7088e9491.jpg)  
(a) Surge added mass.

![](images/0d2bcc380c2a725f105bd0f9a4f29030ffc7331d240d1159adc0311a342ea444.jpg)  
(b) Heave added mass.

![](images/b86a222241e0d69eacf6132ae72a97ad37490b5de440db1889f8569ad6663023.jpg)  
(c) Surge damping.

![](images/6cbcafcf0fe60521b5bce48de558d3dd8b158776d09a7af32cfa3907174a77a4.jpg)  
(d) Heave damping.  
Fig. 5 Added mass and damping coefficient of a circular dock.

Figs. 6\~8 show a variety of validation results with the variation of water depth and draft of the dock. The panel number used in the following computation is 600 for all the cases. The rotation center of torque is defined at the center of bottom of the dock, as the same definition in Garret (1971). It is observed that for both the shallow and the deep water, the present results coincide with the analytical results of Garret (1971). In addition, with the change of the draft, the wave forces varies obviously, while the agreement between the results of present method and analytical method does not change.

![](images/dc2cbdc3e289644570f64ad13a29aa25d50ab55150ef5a0aa9fe8b7de795a97a.jpg)  
(a) $h / a = 0 . 7 5 .$

![](images/5ba43f09be8359a6d780836d91a690b5a2f691114bd9696e4124b638fb0f6d39.jpg)  
(b) $h / a = 1 . 5 .$  
Fig. 6 Modulus of the horizontal exciting wave force on the circular dock.

![](images/dc518b71a488c1c2ca8682961a10ce4b35b1b7aef059576cc7d75c82908c39f7.jpg)  
(a) $h / a = 0 . 7 5 .$

![](images/c7e600ccf97639a373ea5a84a7d44a0d1e477353dfc7147871fd2b8ea2416f7b.jpg)  
(b) $h / a = 1 . 5 .$

Fig. 7 Modulus of the vertical exciting wave force on the circular dock.  
![](images/c2a380694a78f7eb2d3c9400f32df2c61c88a4b17cdc82c49693381a827d72e9.jpg)  
(a) $h / a = 0 . 7 5 .$

![](images/74fa2b226fd92fd602f805f100d822315863e16e28d3aa1babc05fb2108186fa.jpg)  
(b) $h / a = 1 . 5 .$  
Fig. 8 Modulus of the exciting wave torque on the circular dock.

Fig. 9 shows the computational time (unit: sec.) of the numerical example against various numbers of discretization panels. The computation is implemented with a single 2.2 GHz Intel processor, on a 64-bit Windows operating system. The com putation is carried out in double precision. For the solution of the resulting matrix system, the GMRES method is adopted with an iteration tolerance of $1 0 ^ { - 5 } .$ . From Fig. 9, it can be seen that the total computing time is nearly quadratic with increase of the number of panels. A general computation of a 5000-unknowns problem requires approximately 400 seconds, which facilitates the hydrodynamic computation of practical marine structures.

![](images/6e4336debbdb434ca546ea3e79d8720e22fb62a7375c3f712c244e6ed0b7cdb4.jpg)  
Fig. 9 Computational time (s) of the numerical example against panel number.

## CONCLUSIONS

In this paper, an improved boundary element method for solving wave-body interaction problems in finite water depth is presented. The newly developed numerical algorithm for evaluation of the Green function and its derivatives is described in detail. The major advantage of the algorithm is its computational simplicity. The accuracy of algorithm is validated by compari son of Green function and its derivatives with the Chebyshev polynomial approximated method (Newman, 1985). Numerical simulations by using the proposed method are carried out on a circular dock in finite water depth. The irregular frequency phenomenon and the effect of the panel number are discussed.

## ACKNOWLEDGEMENTS

The first author gratefully acknowledges the financial support provided by MEXT Scholarship of Japanese Government during the three-year PhD research

## REFERENCES

Abramowitz, M. and Stegun, I.A., 1965. Handbook of mathematical functions. New York: Dover Press.

Ewald, P.P., 1921. Die berechnung optischer und electrostatischer gitterpotentiale. Annalen der Physik, 369(3), pp.253-287.

Garret, C.J.R., 1971. Wave forces on a circular dock. Journal of Fluid Mechanics, 46(1), pp.129-139.

Havelock, T.H., 1955. Waves due to a floating sphere making periodic heaving oscillations. Proceedings of The Royal Society A: Mathematical, Physical and Engineering Sciences, 231(1184), pp.1-7.

John, F., 1949. On the motion of floating bodies I. Communications on Pure and Applied Mathematics, 2(1), pp.13-57.

John, F., 1950. On the motion of floating bodies II. Communications on Pure and Applied Mathematics, 3(1), pp.45-101.

Kashiwagi, M., Takagi, K., Yoshida, H., Murai, M. and Higo, Y., 2003. Fluid dynamics of floating bodies in practice: Part 1 Numerical computation method of the motion response problems. Tokyo: Seizando Press.

Lau, S.M. and Hearn, G.E., 1989. Suppression of irregular frequency effects in fluid-structure interaction problems using a combined boundary integral equation method. International Journal for Numerical Methods in Fluids, 9(7), pp.763-782.

Linton, C.M., 1999. Rapidly convergent representations for Green functions for Laplace's equation. Proceedings of The Royal Society A: Mathematical, Physical and Engineering Sciences, 455(1985), pp.1767-1797.

Linton, C.M. and Mclver, P., 2001. Handbook of mathematical techniques for wave/structure interactions. London: Chapman and Hall/CRC Press.

Liu, Y.Y., Teng, B., Cong, P.W., Liu, C.F. and Gou, Y., 2012. Analytical study of wave diffraction and radiation by a sub merged sphere in infinite water depth. Ocean Engineering, 51, pp.129-141.

Liu, Y.Y., 2012. Application of multipole expansion method to linear hydrodynamic computation of marine structures in deep oceans. M.S. Thesis. College of Hydraulic Engineering, Dalian University of Technology.

Mei, C.C., 1989. The applied dynamics of ocean surface waves (Advanced series on ocean engineering, Vol. 1). Singapore: World Scientific.

Newman, J.N., 1985. Algorithms for free-surface Green function. Journal of Engineering Mathematics, 19(1), pp.57-67.

Newman, J.N., 1986. Distributions of sources and normal dipoles over a quadrilateral panel. Journal of Engineering Math ematics, 20(2), pp.113-126.

Newman, J.N., 1992. The approximation of free-surface Green functions. Retirement Meeting for Professor Fritz Ursell, University of Manchester, published in ‘Wave Asymptotics,’ edited by P. A. Martin & G. R. Wickham, pp.107-135. Cambridge: Cambridge University Press.

Pidcock, M.K., 1985. The calculation of Green functions in three dimensional hydrodynamic gravity wave problems. Inter national Journal for Numerical Methods in Fluids, 5(10), pp.891-909.

Thorne, R.C., 1953. Multipole expansions in the theory of surface waves. Proceedings of Cambridge Philosophical Society, 49(4), pp.707-716.

Ursell, F., 1949. On the heaving motion of a circular cylinder on the surface of a fluid. Quarterly Journal of Mechanics and Applied Mathematics, 2(2), pp.218-231.

Wehausen, J.V. and Laitone, E.V., 1960. Surface waves. In “Encyclopedia of Physics”, 9. Berlin: Springer Verlag Press.

Wynn, P., 1956. On a Device for Computing the $e _ { m } ( S _ { n } )$ Transformation. Mathematical Tables and Other Aids to Computation, 10(54), pp.91-96.