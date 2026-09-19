# Introduction of the Open-Source Boundary Element Method Solver HAMS to the Ocean Renewable Energy Community

Liu, Yingyi Research Institute for Applied Mechanics, Kyushu University

https://hdl.handle.net/2324/4753050

# Introduction of the Open-Source Boundary Element Method Solver HAMS to the Ocean Renewable Energy Community

Yingyi Liu\*

Abstract—A floating offshore renewable energy (ORE) device, such as an offshore wind turbine or wave energy converter, often consists of a floating foundation anchored by a mooring system. Wave interactions with the substructure are essential to its survivability and performance. In the recent decade, an open-source numerical solver HAMS has been developed based on the potential flow theory in analyzing wave-interactions with a three-dimensional arbitrarily-shaped floating or submerged body. The hybrid source-dipole boundary integral equation provides a high degree of accuracy. The so-called irregular frequencies are removed by applying the least-squares method, avoiding the additional numerical work in resolving the wave potentials on the water-plane cross-section. The lower–upper (LU) decomposition method is then used to solve the complex linear algebraic system. Planes of symmetry and parallelism techniques are employed to speed up the computation. Wave diffraction forces, radiation hydrodynamic coefficients and response amplitude operators (RAOs) are evaluated after the wave potentials are obtained. The freesurface elevation and the wave pressure field are also available at the users’ choice. A numerical benchmark of the DeepCwind semisubmersible platform is supplied for illustration of using the solver.

Index Terms—marine hydrodynamics, offshore engineering, ocean renewable energy, potential flow theory, boundary element method

## I. INTRODUCTION

N the recent decade, ocean renewable energies, such as offshore wind energy, wave energy, and tidal energy, etc., are becoming promising alternatives for the traditional fossil energies. The substructure of these energy converters (either floating or bottommounted) experiences substantially wave loads from time to time. On the one hand, the sea circumstances vary depending on the site location, weather condition, and many other factors. On the other hand, safety and performance are considered as the first priorities for structures in operation. It is preferable to have a reliable tool (ideally open-source packaged) to assess the survivability and the performance before the construction or operation of the substructures.

To date, primarily considering the computational cost, the boundary element method (BEM) based on the potential flow theory is still widely accepted as an essential tool in contrast to the computational fluid dynamics (CFD) methods based on the Navier-Stokes (N-S) equations (despite CFD’s high accuracy), especially when carrying out assessment over wide-ranged selective sea states. This is due to the fact that the viscous part in the N-S equations is not dominant to large marine structures when the cross-section diameter D far exceeds 0.15L (in which L is the wavelength) [1].

The BEM method can be dated back to the 1980s, after which many numerical solvers based on the method were invented one after another. However, most of them are for commercial purpose only. In Jan. 2014, Ecole Centrale de Nantes (ECN) announced the release of the World 1st open-source BEM code Nemoh. Thereafter, many researches regarding ocean renewable energies, particularly the wave energy, were frequently performed with the aid of Nemoh. Unfortunately, it is reported [2] that Nemoh has a noticeable problem that up to present it is still not capable of removing the so-called ”irregular frequencies”. Moreover, its ancient coding style also prevents further developments by the user community to many applications.

To help fix these issues, a new BEM solver named HAMS (abbr. for Hydrodynamic Analysis of Marine Structures) [3] was released on GitHub (https:// github.com/YingyiLiu/HAMS) in Oct. 2020. The code was written using the Fortran 90 language and has a modern structure favorable for further developments. HAMS can completely remove irregular frequencies and can be run in the parallel mode on multi-processor machines. This article will give a short but condensed introduction to many aspects of using the open-source solver.

## II. THEORETICAL BACKGROUND

## A. Boundary integral equations

Within the potential flow framework, the flow is assumed to be inviscid, irrotational, incompressible, and time harmonic with a factor of ${ e ^ { - \mathrm { i } \omega t } }$ . Based on the perturbation theory, the linear wave potential is a summation of the incident wave potential, and scattered (diffracted and radiated) wave potentials. The scattered wave potentials are subjected to the Laplace equation and all the boundary conditions of the fluid domain. In HAMS, the BIE (boundary integral equation) for the scattered wave potentials is

$$
\begin{array}{l} 2 \pi \phi_ {j} (\boldsymbol {x}) + \iint_ {S _ {\mathrm{B}}} \phi_ {j} (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S _ {\boldsymbol {\xi}} \\ = \iint_ {S _ {\mathrm{B}}} V _ {\mathrm{n}, j} (\boldsymbol {\xi}) G (\boldsymbol {\xi}; \boldsymbol {x}) \mathrm{d} S _ {\boldsymbol {\xi}}, (j = 1, 2, \dots , 7), \end{array}\tag{1}
$$

where $( j = 1 \sim 6 )$ and $( j = 7 )$ stands for radiated and diffracted potentials, respectively; ${ \pmb \xi } = ( \xi , \eta , \zeta )$ refers to the source point on the body surface and $\pmb { x } = ( x , y , z )$ is the field point in the fluid domain or on the body surface; $V _ { \mathrm { n } }$ denotes the respective normal velocity on the body surface. In HAMS, the normal direction is defined positive outwards the fluid domain.

Most recently, HAMS adds another BIE as a second option to solve the diffracted potential

$$
2 \pi \phi_ {S} (\boldsymbol {x}) + \iint_ {S _ {\mathrm{B}}} \phi_ {S} (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S _ {\boldsymbol {\xi}} = 4 \pi \phi_ {I} (\boldsymbol {x}),\tag{2}
$$

where φ<sub>S</sub> represents a summation of the incident wave potential $\phi _ { I }$ and the diffracted wave potential $\phi _ { D } . \mathrm { E q }$ (2) is believed to be more accurate and efficient than Eq. (1).

## B. Removal of irregular frequencies

Directly solving Eq. (1) or Eq. (2) leads to substantial errors in the neighborhood of the so-called “irregular frequencies”. This phenomenon is caused by the waterplane section of the members of floating bodies that intersects the free water surface. The irregular frequencies actually coincide with the eigenfrequencies of the corresponding sloshing modes of the interior tank (assuming flow filling inside the tank).

There are at least two mainstream approaches to prevent these numerical errors. Ref. [4] gives a comprehensive comparison between the extended integral equation method (being applied in WAMIT™) and the overdetermined integral equation method, concluding that the latter is more computationally efficient as it only requires a few discrete points on the waterplane area, in contrast to hundreds and thousands waterplane panels in the extended integration method.

HAMS adopts the overdetermined integral equation method, assuming that the potentials on the interior water plane are zero. By applying Green’s theorem in the interior domain of the floating body, the additional boundary integral equation to supplement Eq. (3) is

$$
\begin{array}{l} \iint_ {S _ {\mathrm{B}}} \phi (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\boldsymbol {\xi}}} \mathrm{d} S _ {\boldsymbol {\xi}} = \iint_ {S _ {\mathrm{B}}} V _ {\mathrm{n},} (\boldsymbol {\xi}) G (\boldsymbol {\xi}; \boldsymbol {x}) \mathrm{d} S _ {\boldsymbol {\xi}}, \\ (\boldsymbol {x} \in S _ {\mathrm{WP}}, \boldsymbol {\xi} \in S _ {\mathrm{B}}), \end{array}\tag{3}
$$

where S denotes the interior waterplane area. By choosing several discrete points (say, M points) on $S _ { \mathrm { W P } }$ , a set of over-determined linear algebraic equations can be constructed which finally leads to the following linear algebraic system:

$$
\begin{array}{l} \sum_ {n = 1} ^ {N} \left\{\sum_ {m = 1} ^ {M + N} A _ {m n} A _ {m p} \right\} \phi_ {k} \left(\boldsymbol {x} _ {n}\right) = \sum_ {m = 1} ^ {M + N} A _ {m p} B _ {k} \left(\boldsymbol {x} _ {m}\right), \\ (p = 1, 2, \dots , N), \end{array}\tag{4}
$$

where N is the number of panels on the wetted body surface. Eq. (4) can be regularly solved. In addition to the advantage of less computational cost, the overdetermined integration method also avoids evaluation of the logarithmic singularity of free-surface Green’s function occurring in the limiting case when the panel is on the free surface. The supplemental equation for Eq. (2) can be constructed in a similar manner.

## C. Evaluation offree-surface Green’s functions

In the above boundary integral equations, freesurface Green function is an essential component as it needs to be numerically evaluated millions of times per frequency in a typical case of over 1000 unknowns. The Green function for the deepwater condition is expressed by

$$
G = \frac {1}{r} + \frac {1}{r _ {1}} + 2 v \int_ {0} ^ {\infty} \frac {e ^ {\mu (z + \zeta)}}{\mu - v} J _ {0} (\mu R) \mathrm{d} \mu\tag{5}
$$

The Green function for finite-depth conditions is expressed by

$$
\begin{array}{l} G = \frac {1}{r} + \frac {1}{r _ {2}} \\ + 2 \int_ {0} ^ {\infty} \frac {(\mu + v) \cosh \mu (z + h) \cosh \mu (\zeta + h)}{\mu \sinh \mu h - v \cos h \mu h} e ^ {- \mu h} J _ {0} (\mu R) \mathrm{d} \mu \end{array}\tag{6}
$$

where v is the deepwater wave number; h is the water depth; $r , r _ { 1 } , r _ { 2 }$ correspond to the distance from the field point to the source point, the image of the source point with respect to the free surface, and the image of the source point with respect to the sea bottom.

There have been numerous works on developing efficient and accurate algorithms for free-surface Green’s functions. HAMS adopts two latest open-source codes: Green-function-in-deep-water developed by Dr. Hui Liang in Ref. [5] and FinGreen3D developed by Dr. Yingyi Liu in Ref. [6], for the deepwater and the finitedepth conditions, respectively.

## D. Wave forces and RAOs of motion

After resolving the wave potentials, the wave forces are calculated by integrating the dynamic pressure over the wetted body surface. The wave excitation force is

$$
F _ {E x c, i} = \mathrm{i} \omega \rho \iint_ {S _ {B}} (\phi_ {0} + \phi_ {7}) n _ {i} \mathrm{d} S _ {\pmb {\xi}},\tag{7}
$$

where $( i \ = \ 1 \sim \ 6 )$ . The added mass and the wave radiation damping correspond to

$$
A _ {i, j} = \mathrm{Re} \left[ \mathrm{i} \rho \iint_ {S _ {B}} \phi_ {j} n _ {i} \mathrm{d} S _ {\pmb {\xi}} \right]\tag{8}
$$

and

$$
B _ {i, j} = \mathrm{Im} \left[ \mathrm{i} \omega \rho \iint_ {S _ {B}} \phi_ {j} n _ {i} \mathrm{d} S _ {\pmb {\xi}} \right]\tag{9}
$$

where $( i , j = 1 \sim 6 )$ . Note that $A _ { i , j }$ and $B _ { i , j }$ should be interpreted as the wave radiation force of the ith DoF (Degree of Freedom) due to the jth DoF of the body motion. The body motion is solved from the following motion equations

$$
\begin{array}{l} \sum_ {j = 1} ^ {6} \left[ - \omega^ {2} \left(M _ {i j} + A _ {i j}\right) - \mathrm{i} \omega \left(B _ {i j} + B _ {i j} ^ {E}\right) + \left(C _ {i j} + C _ {i j} ^ {E}\right) \right] \xi_ {j} \\ = F _ {E x c, i}, (i = 1 \sim 6) \end{array} \tag {1.3}\tag{10}
$$

where $M _ { i j }$ and $C _ { i j }$ represents the body mass matrix and the hydrostatic restoring matrix; the superscript $^ \prime \mathrm { E } ^ { \prime \prime }$ stands for the ”External” damping and restoring matrices.

## E. Field pressure and free-surface elevation

In the linear potential flow theory, the dynamic pressure at a field point x due to either diffracted or radiated waves can be evaluated as

$$
p _ {j} (\boldsymbol {x}) = \mathrm{i} \omega \rho \phi_ {j} (\boldsymbol {x}).\tag{11}
$$

The wave elevation at a field point x on the free-surface corresponds to

$$
\eta_ {j} (\boldsymbol {x}) = \frac {\mathrm{i} \omega}{g} \phi_ {j} (\boldsymbol {x}).\tag{12}
$$

In Eqs. 11 and 12, the wave potential at a field point in the fluid domain is calculated by

$$
\phi_ {j} (\boldsymbol {x}) = \frac {1}{4 \pi} \iint_ {S _ {\mathrm{B}}} [ V _ {\mathrm{n}, j} (\boldsymbol {\xi}) G (\boldsymbol {\xi}; \boldsymbol {x}) - \phi_ {j} (\boldsymbol {x}) \frac {\partial G (\boldsymbol {\xi} ; \boldsymbol {x})}{\partial n _ {\boldsymbol {\xi}}} ] \mathrm{d} S _ {\boldsymbol {\xi}}.\tag{13}
$$

At present, this functionality is only available in the WAMIT™ output format. The users need to specify the locations of the field point where they want to output the field pressure or free-surface elevation.

## III. CURRENT FEATURES OF HAMS

## A. Input and output frequency option

HAMS allows for various options of the frequency type, in both input and output files, including: (1) deepwater wave number v; (2) finite-depth wave number k; (3) wave angular frequency ω; (4) wave period T; (5) wave length λ. Their mutual relations are respectively as follows

$$
k \tanh k h = v,\tag{14}
$$

$$
v = \frac {\omega^ {2}}{g},\tag{15}
$$

$$
k = \frac {2 \pi}{\lambda},\tag{16}
$$

and

$$
\omega = \frac {2 \pi}{T}.\tag{17}
$$

These various options provide the users with the convenience of the input and output of their specific purposes.

## B. Body symmetry

The computation burden can be dramatically decreased in case the body symmetries are exploited. At present, HAMS allows for one symmetry with respect to either the xoz plane or the yoz plane. In addition, using body symmetry can eliminate unnecessary numerical errors due to the asymmetry of the geometrical discretization. In another word, applying body symmetry can improve the computational accuracy.

## C. Resolving linear algebraic system

A direct solver such as Gauss elimination is generally robust but require $O ( N ^ { 3 } )$ computations (N denotes matrix size), while some iterative methods can reduce the effort to $O ( N ^ { 2 } )$ operations. For a large-scale computation of three-dimensional offshore structures, a direct inversion or inefficient iteration of such a large, dense system of linear equations with $O ( N ^ { 4 } )$ unknowns for a set of wave frequencies is seemingly prohibitively time consuming even with modern computers. HAMS employs the ”ZGETRF” and ”ZGETRS” subroutines of LAPACK (applying the LU decomposition) to solve the linear algebraic system.

## D. OpenMP parallelism

The problems to be solved are often of a very large size such that resolving the resultant linear systems requires huge computational resources. Nowadays, with the facility of a fast multi-core computer, it is natural to maximize the advantages of the current hardware technology in our computations. HAMS employs the OpenMP (Open Multi-Processing) parallelization technique as it is considered to be an appropriate option for a BEM solver in marine hydrodynamics on multiple processors. Another advantage is that OpenMP needs much less effort than MPI (Message Passing Interface) in modifying the code architecture.

## E. Output format and interface to others

There are three output formats available in HAMS, including two compatible with the commercial software WAMIT™ and Hydrostar™. This feature allows the users to connect with many other commercial and open-source software in ocean engineering and marine renewable energies, such as FAST or OpenFAST and most recently RAFT in the offshore wind energy, and WEC-Sim in the ocean wave energy, etc. The users are encouraged to interface HAMS with other apps.

## IV. PRE- AND POST- PROCESSING SOFTWARE

Here below is a list of existing and potential commercial or open-source freeware. The users can choose some of them to do pre- or post-processing when using HAMS:

## A. Building the CAD model

• Gmsh, open-source

• SALOME , open-source

• Autodesk Inventor, commercial

Rhinoceros, commercial

B. Meshing the geometry

• Gmsh, open-source

• SALOME , open-source

• BEMRosetta, open-source

Rhinoceros, commercial

## C. Visualizing the results

• BEMRosetta, open-source

• BEMIO, open-source

• Matplotlib, open-source

• Veusz, open-source

• Gnuplot, open-source

• MATLAB, commercial

It is particularly noted that BEMRosetta is pretty useful as it enables one to construct a waterplane mesh from a wetted body mesh, helping the users to reduce the mesh-generation burden. Beside BEMRosetta and BEMIO, most of the above tools are for general purposes. The users are encouraged to develop interfaces between them and share with the community.

## V. HOW TO USE HAMS

## A. Preparing BEM mesh files

Before using HAMS, the users need to prepare the requisite mesh file(s) for their BEM computation. The users can firstly construct a geometrical model using a CAD software as listed in Section IV. Then by importing the CAD model to a meshing software, the users can easily generate the mesh file(s) in flat panels. Note that some CAD software also has the capability of generating a mesh.

## B. Mesh format conversion and hydrostatic preprocessing

The above generated mesh usually cannot be immediately used by HAMS as the BEM solver has its own mesh format. The users need to convert the mesh format and precalculate the body mass matrix and hydrostatic restoring matrix by themselves beforehand. Worth mention here is that HAMS has a built-in mesh converter named WAMIT MeshTran which can transform the WAMIT™ \*.gdf mesh to that of HAMS at present. The tool can automatically dispart an entire mesh (involving both the body surface and the waterplane area) into the separate WaterplaneMesh.pnl and HullMesh.pnl files. It can also output the hydrostatic matrices for the body motion calculation in HAMS. Besides, WAMIT MeshTran is expected to include more formats like Gmsh in the future release.

## C. BEM computation in HAMS

Copy the WaterplaneMesh.pnl and HullMesh.pnl mesh files to the Input Folder of HAMS. Make appropriate settings in the ControlFile.in file. There are several places that need attention:

1 ) Number of frequencies: following the WAMIT tradition, when a positive value is specified, the next line immediately after should read a set of discrete wave frequencies (or wave periods, wave numbers, wave lengths, etc.); otherwise, the next two lines should read respectively the Minimum frequency Wmin and the Frequency step.

2) Number of headings: following a similar WAMIT™

TABLE I  
VARIABLES USED IN THE COMPUTATION AND THE PLOTS

<table><tr><td>Symbol</td><td>Quantity</td><td>Value</td><td>Unit</td></tr><tr><td> $\rho$ </td><td>Sea water density</td><td>1025</td><td>kg/m3</td></tr><tr><td>V</td><td>Platform displacement</td><td> $1.3683 \times 10^{4}$ </td><td>m3</td></tr><tr><td> $\omega$ </td><td>Wave angular frequency</td><td>0.0 ~ 3.0</td><td>1/s</td></tr><tr><td>h</td><td>Water depth</td><td>50.0</td><td>m</td></tr><tr><td> $x_{r}$ </td><td>Rotation center coordinates</td><td>(0.0, 0.0, 0.0)</td><td>m</td></tr></table>

tradition as that of Number of frequencies.

3 ) Number of field points: this is to specify how many field points the users want to output the field pressure or elevation. Immediately after this line, the coordinates of these field points are expected to be input, one after another.

4 ) If remove irr freq: set 1 if the user wants to remove the irregular frequencies and set 0 if not.

5) Wave diffrac solution: set 1 if users want to use Eq. (1) for the wave diffraction and set 2 in case of Eq. (2).

## D. Results visualization

HAMS outputs its results in two formats compatible with the commercial software WAMIT™ and Hydrosta $\mathbf { \mathbf { \mathbf { { r } } ^ { \mathrm { { T M } } } } }$ . The users can use many existing tools (utilities) to view and visualize the results, e.g., BEMRosetta (open-source), StarViewer™ (commercial), etc.

## VI. NUMERICAL EXAMPLES

The followings show an example of running HAMS. The floating structure given below is the DeepCwind semi-submersible platform as defined in Ref. [7]. The variables used in the computation and the normalization of the plots are given in Table VI.

Fig. 1 displays the body mesh (1479 panels) and the waterplane mesh (138 panels) used in the subsequent computation having one body symmetry regarding the xoz plane. By running the built-in WAMIT MeshTran program, we can easily perform an hydrostatic preanalysis of the DeepCwind platform. The body mass matrix is calculated as (herein e denotes 10) <sup>1</sup>

<table><tr><td>M = \begin{bmatrix} 1.40e^{7} &amp; 0.00 &amp; 0.00 &amp; 0.00 &amp; 0.00 &amp; 0.00 \\ 0.00 &amp; 1.40e^{7} &amp; 0.00 &amp; 0.00 &amp; 0.00 &amp; 0.00 \\ 0.00 &amp; 0.00 &amp; 1.40e^{7} &amp; 0.00 &amp; 0.00 &amp; 0.00 \\ 0.00 &amp; 0.00 &amp; 0.00 &amp; 8.54e^{9} &amp; 0.00 &amp; 1.26e^{2} \\ 0.00 &amp; 0.00 &amp; 0.00 &amp; 0.00 &amp; 8.54e^{9} &amp; 0.00 \\ 0.00 &amp; 0.00 &amp; 0.00 &amp; 1.26e^{2} &amp; 0.00 &amp; 1.07e^{10} \end{bmatrix},\]</td></tr></table>

and the hydrostatic restoring matrix is

![](images/b8b6372058b04bed85a87316be26fb361755c92a1a535ec869f0ffd577d545ff.jpg)  
Fig. 1. A BEM mesh of the DeepCwind semi-submersible platform displayed in Rhinoceros using the body symmetry.

![](images/021d46230e5035cc3bc20b141b2a2c77377502b2a83904c55bc7cb14b19f6776.jpg)  
Fig. 2. Added mass and radiation damping.

<table><tr><td> $C = \begin{bmatrix} 0.00 & 0.00 & 0.00 & 0.00 & 0.00 & 0.00 \\ 0.00 & 0.00 & 0.00 & 0.00 & 0.00 & 0.00 \\ 0.00 & 0.00 & 3.77e^{6} & 0.00 & 0.00 & 0.00 \\ 0.00 & 0.00 & 0.00 & -3.59e^{8} & 0.00 & 2.98e^{6} \\ 0.00 & 0.00 & 0.00 & 0.00 & -3.59e^{8} & 0.00 \\ 0.00 & 0.00 & 0.00 & 0.00 & 0.00 & 0.00 \end{bmatrix}$ </td></tr></table>

Besides, the users can specify other external restoring matrices, e.g., the mooring stiffness matrix, to the Hydrostatic. in file under the HAMS Input folder.

After making appropriate settings in the primary control file, the users can run HAMS simply by clicking the RunHAMS.bat file in Windows systems. The added mass, radiation damping, wave excitation force and motion RAOs are shown in Figs. 2 ∼ 4.

## VII. CONCLUSION

The present paper briefly summarizes all aspects of the open-source BEM solver HAMS, from the theoretical to the technical perspectives. Any feed backs and questions can be posted on the HAMS official GitHub site. The users are encouraged to share the tools (utilities) that are developed by themselves in the HAMS users’ community. More features are expected to be included in the future releases of HAMS.

![](images/c94e0be3ab414de3801d82b6c23d9417bc1f0d38fa7df111c2e79093b515d1a6.jpg)  
Fig. 3. Wave excitation force.

![](images/eeb63b65e960cc452221abbde4769c14a08545b4e0d21b68ab677f6dd2c873d3.jpg)  
Fig. 4. Motion RAOs of the platform.

## ACKNOWLEDGEMENT

The author thanks Inaki Zabala (SENER Ingenier˜ ´ıa) for developing the pre- and post-processing interface in BEMRosetta for HAMS, and Garrett Barter (NREL) for developing PyHAMS as a Linux version of HAMS.

## REFERENCES

[1] T. Sarpkaya, Wave forces on offshore structures. Cambridge University Press, 2010.

[2] M. Penalba, T. Kelly, and J. Ringwood, “Using nemoh for modelling wave energy converters: A comparative study with wamit,” 2017.

[3] Y. Liu, “HAMS: a frequency-domain preprocessor for wavestructure interactions—theory, development, and application,” Journal of Marine Science and Engineering, vol. 7, no. 3, p. 81, 2019.

[4] H. Liang, C. Ouled Housseine, X. B. Chen, and Y. Shao, “Efficient methods free of irregular frequencies in wave and solid/porous structure interactions,” Journal of Fluids and Structures, vol. 98, p. 103130.2020

[5] H. Liang, H. Wu, and F. Noblesse, “Validation of a global approximation for wave diffraction-radiation in deep water,” Applied Ocean Research, vol. 74, pp. 80–86, 2018.

[6] Y. Liu, S. Yoshida, C. Hu, M. Sueyoshi, L. Sun, J. Gao, P. Cong, and G. He, “A reliable open-source package for performance evaluation of floating renewable energy systems in coastal and offshore regions,” Energy Conversion and Management, vol. 174, pp. 516–536, 2018.

[7] A. Robertson, J. Jonkman, M. Masciola, H. Song, A. Goupee, A. Coulling, and C. Luan, “Definition of the semisubmersible floating system for phase ii of oc4,” National Renewable Energy b ( ) ld ( d ) h