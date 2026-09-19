Article

# The Impact Modeling and Experimental Verification of a Launch Vehicle with Crushing-Type Landing Gear

Yingchao Wang <sup>1</sup>, Haitao Yu <sup>1,</sup>\* , Jianghui Xie <sup>2</sup>, Zhen Yan <sup>1</sup>, Baolin Tian <sup>1</sup> and Haibo Gao <sup>1</sup>

State Key Laboratory of Robotics and System, Harbin Institute of Technology, Harbin 150001, China; 17b908061@stu.hit.edu.cn (Y.W.); 19b908094@stu.hit.edu.cn (B.T.)

Wuhan Second Ship Design and Research Institute, Wuhan 430205, China; xjhwj666@163.com

Correspondence: yht@hit.edu.cn

Abstract: In order to investigate the landing process of a vertical landing reusable vehicle, a dynamic model with a complex nonlinear dissipative element is established based on the discrete impulse step approach, which includes a three-dimensional multi-impact model considering friction and material compliance, and a multistage aluminum honeycomb theoretical model. The normal two-stiffness spring model is adopted in the foot–ground impact model, two motion patterns (stick and slip) are considered on the tangential plane and the structural changes caused by buffering behavior are included, and the energy conversion during the impact follows the law of conservation of energy. The state transition method is used to solve the dynamic stability convergence problem of the vehicle under the coupling effect of impact and buffering deformation in the primary impulse space. Landing experiments on a scaled physical reusable vehicle prototype are conducted to demonstrate that the theoretical results exhibit good agreement with the experimental data.

Keywords: landing process; impact–buffering coupling; inverted-triangle landing gear; multistage aluminum honeycomb; vertical landing reusable vehicle

![](P6_Wang_2023_Actuators_images/93c5319b593a09b9a01dee99ff460e3a5122200b64145d9fb22a0a9eb39a18a1.jpg)

Citation: Wang, Y.; Yu, H.; Xie, J.; Yan, Z.; Tian, B.; Gao, H. The Impact Modeling and Experimental Verification of a Launch Vehicle with Crushing-Type Landing Gear. Actuators 2023, 12, 307. https:// doi.org/10.3390/act12080307

Academic Editor: Ronald M. Barrett

Received: 3 July 2023 Revised: 21 July 2023 Accepted: 24 July 2023 Published: 26 July 2023

![](P6_Wang_2023_Actuators_images/959858affc736a0163983722d9d9a8f031404db7528aba166c3d93f23f6414ee.jpg)

Copyright: © 2023 by the authors. Licensee MDPI, Basel, Switzerland. This article is an open access article distributed under the terms and conditions of the Creative Commons Attribution (CC BY) license (https:// creativecommons.org/licenses/by/ 4.0/).

## 1. Introduction

In the field of engineering, when a mechanical system collides during movement, substantial impact energy will be generated instantaneously. If there is no material or device in the system that can absorb the impact energy, the internal structure of the mechanical system will be subjected to serious deformation and even fracture [1,2]. Therefore, a buffer is often added to a mechanical system that may encounter collisions. When the impact occurs, the buffer device adopts its own specific kind of deformation to absorb the impact energy effectively to protect the mechanical system. In the literature [3], a lander without buffering material was designed by imitating the landing process of a locust through its legs; during this landing, the impact energy is transformed into viscoelastic deformation and leg structure deformation due to viscoelastic feet and a joint torsion spring. In Reference [4], a six-legged lunar lander that can be repeatedly used was designed to absorb impact energy via structural deformation during landing, and its effectiveness was verified through simulations and experiments. To sum up, large deformation and a structural configuration change will invariably occur when multibody systems encounter impact.

The landing process of a vehicle is a complex dynamics process influenced by many factors [5–7]. Among them, the structural change of the system caused by buffering has an important impact on the collision behavior. References [8,9] compared the buffering effect of different landing structures, indicating that the different structural deformation modes caused by buffering lead to varying landing results. A discrete element method (DEM)–finite element method (FEM)–multibody dynamics (MBD) model was proposed in Reference [10], the dynamic landing process of a lunar lander considering the charac teristics of lunar soil was simulated, and the influence mechanism of key parameters on the landing process was analyzed. In the literature [11], two landing modes, shutdownbefore-touchdown and shutdown-at-touchdown, were proposed in consideration of the two conditions of the Mars lander’s engines during landing, and the landing stability and impact on the collision under these two modes were analyzed. Therefore, considering the coupling effect of collision and buffering is an important factor to simulate the landing process of a vehicle with the inverted-triangle landing gear [12].

As for impact, in correlational studies of landing, even in the engineering field, there are usually two modeling approaches: (1) The discrete approach, taking the energy and velocity before and after the impact as objectives, and assuming that the position and structure of the impact body remain unchanged during the impact [13,14]. However, this modeling approach is incapable of simulating cases when series of impacts happen. (2) The continuous approach, which establishes the force–displacement relationship between two colliding objects [15–19] to simulate the complete impact process, which is widely used. This method allows for multiple impacts, and can provide the complete impact force history, but cannot guarantee the energy conservation of the impact process.

The buffering material used in the four-legged landing gear of vehicles is two-stage aluminum honeycomb. Aluminum honeycomb material is not only environmentally friendly, low-cost, and easy to shape, but also has the advantages of light weight, high strength, good buffering performance [1,20,21], high surface flatness, etc.; these characteristics satisfy all the requirements for the buffering material of the legged landing gear of a vehicle [6,22]. In the literature [23], scholars established a landing process model of the lunar lander with carbon nanopaper and two-stage aluminum honeycomb as the buffer materials, respectively, and compared the buffering characteristics of the two materials under three extreme landing conditions. Jinhua Zhou [24] and other scholars carried out a parameter optimization design of an aluminum honeycomb buffer, obtaining better landing performance with the lander. In order to optimize the center overload of the lunar lander with inverted-triangle landing gear, scholars proposed a multiobjective optimization method to optimize the material and structural parameters of the three-stage aluminum honeycomb buffer [25]. Based on the above, two-stage aluminum honeycomb can be used as the buffering material in the landing process of a vehicle with legged landing gear.

In this paper, due to the intercoupling characteristics of multiple impacts and large buffering deformation during the landing of a vertical landing reusable vehicle, the landing dynamics process can be equivalent to the convergence process of a complex discrete nonlinear system, which consists of multiple states, each of which can be transformed into the other under certain dynamic conditions. Then, in each state of the discrete system, according to the coupling relationship between the impact and buffer behavior, the primary impulse is selected, and the relationship network between the remaining impulses and the primary impulse is established, then substituted into the landing equations in a certain state; through the above steps, the complex coupling mechanism between the multi-impact process and the buffering process of the landing vehicle is simulated in the discrete impulse space with the hope that this modeling method can accurately predict the landing behavior of the vertical landing vehicle.

## 2. Landing Model of a Vehicle Considering the Impact–Buffering Coupling Effect 2.1. Vertical Landing Process of the Vehicle

The landing process of a vehicle with inverted-triangle landing gear involves the vehicle freefalling in the aerial state until the feet touch the ground, then entering the touchdown state until it lands stably or tips over. After the vehicle touches the ground, the foot of the landing gear may experience multiple impacts with the ground; during this period, the buffering behavior and the impact process will be coupled with each other and collectively affect the landing process of the vehicle. However, when the vehicle transfers from the touchdown state to the aerial state under certain conditions, at which time the feet of the landing gear will leave the ground, the buffering behavior may act solely on the nonlinear vehicle system. When the release of a small amount of elastic energy of the buffer ends, it may enter the state of freefalling again or return to the state of touchdown again under certain conditions. In addition, in the process of touching the ground, the structure damping of the landing gear will absorb some of the impact energy, and finally, the entire vehicle system will converge through damped periodic oscillation; in other words, the vehicle finally lands stably.

In establishing an impact–buffering multibody system model for a vertical landing <sub>vehicle, inverted-triangle landing gear was used. First of all, the vehicle was divided into</sub><sup>vehicle,</sup> <sup>inverted-triangle</sup> <sup>landing</sup> <sup>gear</sup> <sup>was</sup> <sup>used.</sup> <sup>First</sup> <sup>of</sup> <sup>all,</sup> <sup>the</sup> <sup>vehicle</sup> <sup>was</sup> <sup>divided</sup> <sup>into</sup> <sub>two</sub> <sub>parts:</sub> <sub>the</sub> <sub>mass</sub> <sub>of</sub> <sub>the</sub> <sub>main</sub> <sub>body,</sub> <sub>the</sub> <sub>upper</sub> <sub>parts</sub> <sub>of</sub> <sub>the</sub> <sub>main</sub> <sub>pillars,</sub> <sub>and</sub> <sub>the</sub> <sub>auxiliary</sub><sup>two</sup> <sup>parts:</sup> <sup>the</sup> <sup>mass</sup> <sup>of</sup> <sup>the</sup> <sup>main</sup> <sup>body,</sup> <sup>the</sup> <sup>upper</sup> <sup>parts</sup> <sup>of</sup> <sup>the</sup> <sup>main</sup> <sup>pillars,</sup> <sup>and</sup> <sup>the</sup> <sup>auxiliary</sup> <sub>pillars</sub> <sub>are</sub> <sub>concentrated</sub> <sub>in</sub> <sub>the</sub> <sub>center</sub> <sub>of</sub> <sub>mass</sub> <sub>of</sub> <sub>the</sub> <sub>vehicle,</sub> <sub>while</sub> <sub>the</sub> <sub>mass</sub> <sub>of</sub> <sub>the</sub> <sub>lower</sub><sup>pillars</sup> <sup>are</sup> <sup>concentrated</sup> <sup>in</sup> <sup>the</sup> <sup>center</sup> <sup>of</sup> <sup>mass</sup> <sup>of</sup> <sup>the</sup> <sup>vehicle,</sup> <sup>while</sup> <sup>the</sup> <sup>mass</sup> <sup>of</sup> <sup>the</sup> <sup>lower</sup> part of the main pillar to the foot is on the center of mass of the foot, as shown in Figure 1.<sup>part</sup> <sup>of</sup> <sup>the</sup> <sup>main</sup> <sup>pillar</sup> <sup>to</sup> <sup>the</sup> <sup>foot</sup> <sup>is</sup> <sup>on</sup> <sup>the</sup> <sup>center</sup> <sup>of</sup> <sup>mass</sup> <sup>of</sup> <sup>the</sup> <sup>foot,</sup> <sup>as</sup> <sup>shown</sup> <sup>in</sup> <sup>Figure</sup> Furthermore, the force exerted on the auxiliary strut of the inverted-triangle landing gear<sup>1.</sup> <sup>Furthermore,</sup> <sup>the</sup> <sup>force</sup> <sup>exerted</sup> <sup>on</sup> <sup>the</sup> <sup>auxiliary</sup> <sup>strut</sup> <sup>of</sup> <sup>the</sup> <sup>inverted-triangle</sup> <sup>landing</sup> will also impose constraints in the collision–buffering coupling process; hence, the auxiliary<sup>gear</sup> <sup>will</sup> <sup>also</sup> <sup>impose</sup> <sup>constraints</sup> <sup>in</sup> <sup>the</sup> <sup>collision–bufering</sup> <sup>coupling</sup> <sup>process;</sup> <sup>hence,</sup> <sup>the</sup> <sub>strut</sub> <sub>was</sub> <sub>simplified</sub> <sub>into</sub> <sub>a</sub> <sub>massless</sub> <sub>spring</sub> <sub>element.</sub><sup>auxiliary</sup> <sup>strut</sup> <sup>was</sup> <sup>simplified</sup> <sup>into</sup> <sup>a</sup> <sup>massless</sup> <sup>sprin</sup>

![](P6_Wang_2023_Actuators_images/d052c64a5a2f53920bb4766854575f9f0960f603da7d1388ab6c686b2dd4bc58.jpg)  
Figure 1. Schematic diagram of the theoretical model of the vehicle with inverted-triangle land ing gear.

Based on the landing process state machine, the vehicle can be considered as a nonlin-<sup>Based</sup> <sup>on</sup> <sup>the</sup> <sup>landing</sup> <sup>process</sup> <sup>state</sup> <sup>machine,</sup> <sup>the</sup> <sup>vehicle</sup> <sup>can</sup> <sup>be</sup> <sup>considered</sup> <sup>as</sup> <sup>a</sup> <sup>non-</sup>ear system in the states where the buffering behavior is activated, while in the remaining linear system in the states where the bufering behavior is activated, while in the remain-<sub>states, the vehicle can be regarded as a rigid body system without structural deforma-</sub> <sup>ing</sup> <sup>states,</sup> <sup>the</sup> <sup>vehicle</sup> <sup>can</sup> <sup>be</sup> <sup>regarded</sup> <sup>as</sup> <sup>a</sup> <sup>rigid</sup> <sup>body</sup> <sup>system</sup> <sup>without</sup> <sup>structural</sup> <sup>defor-</sup>tion. Transitions between different states can occur under specific dynamic conditions, mation. Transitions between diferent states can occur under specific dynamic conditions,<sub>forming a complex nonlinear dissipative system within the discrete impulse space, as</sub> forming a complex nonlinear dissipative system within the discrete impulse space, as il-<sub>illustrated</sub> <sub>in</sub> <sub>Figure</sub> <sub>2.</sub> <sub>The</sub> <sub>behavior</sub> <sub>of</sub> <sub>the</sub> <sub>system</sub> <sub>will</sub> <sub>vary</sub> <sub>with</sub> <sub>the</sub> <sub>system</sub> <sub>parameters</sub> <sup>lustrated</sup> <sup>in</sup> <sup>Figure</sup> <sup>2.</sup>and initial conditions.

<sup>initial</sup> <sup>conditions.</sup>The meanings of the variables of Figure 2 are as follows:

$\operatorname { E } _ { \mathrm { b } i }$ and $\mathrm { E } _ { z s i }$ —the elastic energy of the buffer in the main pillar of leg I and the elastic energy of the normal spring of the foot–ground impact I, respectively.

$v _ { z i }$ and $v _ { \mathrm { b } i }$ —the normal velocity of the foot–ground impact I and the buffering velocity of the main pillar of leg $i ,$ respectively.

![](P6_Wang_2023_Actuators_images/a752da339d304b424acf4cb038d8f32812af37406b5f6f60aab7b4782ef136d1.jpg)  
Figure 2. State machine of the vertical landing process of the vehicle.Figure 2. State machine of the vertical landing process of the vehicle.

The mv and $v _ { 2 1 } .$ ngs of the variables of Figure 2 are as follows: —the velocity of the main body and foot 1, respectively.

$Z _ { \mathrm { f } i } -$ d Ezsi—the elastic energy of the bufethe normal displacement of the foot i.

$F _ { \mathrm { b 1 } } , F _ { \mathrm { a 1 } } , F _ { y 1 }$ mal s, and $F _ { z 1 } \mathrm { - } \mathrm { t h e }$ he foot–ground impact I, respectively. force of main pillar 1, auxiliary pillar 1, and the y and z v<sub>zi</sub> and v<sub>bi</sub>—the normal velospring of foot–ground impact 1.

e main pillar of leg i, respectively. The impulse space dynamics equations of the landing process of the reusable vehicle for all landing states (S1\~S4) are as follows:

Zfi—the normal displace• Nonlinear system states.

<sup>Fb1,</sup> <sup>Fa1,</sup> <sup>Fy1,</sup> <sup>a</sup>Main body:

$$
m _ {1} \dot {v} _ {1} = \sum_ {i = 1} ^ {4} F _ {\mathrm{b} i} + \sum_ {i = 1} ^ {4} F _ {\mathrm{a} i} + \sum_ {i = 1} ^ {4} F _ {\mathrm{l} i}\tag{1}
$$

ll lanFoot:

$$
m _ {2 i} \dot {v} _ {2 i} = F _ {\mathrm{b} i} + F _ {\mathrm{a} i} + F _ {z i} + F _ {y i}\tag{2}
$$

Main body: • Rigid-body system states.

$$
m _ {1} \dot {v} _ {1} = \sum_ {i = 1} ^ {4} F _ {z i} + \sum_ {i = 1} ^ {4} F _ {y i}\tag{3}
$$

Among them, $F _ { \mathbf { b } i }$ represents the main pillar force, $F _ { \mathbf { a } i }$ is the auxiliary pillar force, $F _ { \mathrm { l } i }$ �<sub>ଶ௜</sub>�ሶ<sub>ଶ௜</sub> = �<sub>ୠ௜</sub> + �<sub>ୟ௜</sub> + �<sub>௭௜</sub> + �<sub>௬௜</sub> <sub>represents</sub> <sub>the</sub> <sub>lateral</sub> <sub>force</sub> <sub>exerted</sub> <sub>by</sub> <sub>the</sub> <sub>supporting</sub> <sub>leg</sub> <sub>on</sub> <sub>the</sub> <sub>main</sub> <sub>body,</sub> $F _ { z i }$ <sup>(2)</sup>is the normal force exerted on the foot’s center of mass by the ground, and $F _ { y i }$ is the tangential force exerted on the foot’s centroid by the ground.

## <sup>ଵ ଵ</sup>   <sup>௭௜ୀଵ</sup> 2.2. Three-Dimensional Impact Model with Friction

Among them, �<sub>ୠ௜</sub> represents the main pillar force, �<sub>ୟ௜</sub> is the auxiliary pillar force, <sub>The impact between the foot and the ground during landing can be regarded as an</sub> �<sub>୪௜</sub> represents the lateral force exerted by the supporting leg on the main body, �<sub>௭௜</sub> is the <sub>elastic–plastic impact. As shown in the enlarged picture of the foot–ground impact in</sub>

Figure 1, three mutually perpendicular springs (the normal direction is vertical upward)used to simulate the normal impact behavior between the foot and the ground, it has two are set up at the impact point as the primary impact model [26,27]. The bi-stiffness springstates: compression and restitution, and the upward direction is set as the positive direcis used to simulate the normal impact behavior between the foot and the ground, it hastion. At the end of compression, part of the impact energy will be consumed by plastic two states: compression and restitution, and the upward direction is set as the positivedeformation; simultaneously, the spring stifness increases by a fixed proportional coefidirection. At the end of compression, part of the impact energy will be consumed bycient, which is directly related to the coeficient of restitution and determined by the colplastic deformation; simultaneously, the spring stiffness increases by a fixed proportional<sub>lision</sub> <sub>characteristics</sub> <sub>between</sub> <sub>the</sub> <sub>foot</sub> <sub>and</sub> <sub>the</sub> <sub>ground,</sub> <sub>which</sub> <sub>ensures</sub> <sub>the</sub> <sub>conservation</sub> <sub>of</sub> coefficient, which is directly related to the coefficient of restitution and determined by the<sub>the</sub> <sub>energy</sub> <sub>during</sub> <sub>the</sub> <sub>impact.</sub> <sub>Additionally,</sub> <sub>the</sub> <sub>tangential</sub> <sub>plane</sub> <sub>springs</sub> <sub>can</sub> <sub>be</sub> <sub>either</sub> collision characteristics between the foot and the ground, which ensures the conservation<sub>compressed</sub> <sub>or</sub> <sub>elongated,</sub> <sub>assuming</sub> <sub>that</sub> <sub>the</sub> <sub>direction</sub> <sub>of</sub> <sub>the</sub> <sub>virtual</sub> <sub>spring</sub> <sub>is</sub> <sub>positive</sub> of the energy during the impact. Additionally, the tangential plane springs can be either<sub>when</sub> <sub>it</sub> <sub>is</sub> <sub>compressed.</sub> compressed or elongated, assuming that the direction of the virtual spring is positive when it is compressed.

## <sub>2.2.1.</sub> <sub>Impulses</sub> <sub>of</sub> <sub>the</sub> <sub>Three-Dimensional</sub> <sub>ImpactLet</sub> <sub>tan</sub> k <sub>represent</sub> <sub>the</sub> <sub>stifness</sub> <sub>of</sub> <sub>the</sub> <sub>tange</sub>

Letact $k _ { \mathrm { t a n } }$ <sub>represent the stiffness of the tangent plane spring. In the coordinate of the</sub>t �<sup>௜</sup>of foot i (Figure 3), the vertical upward direction is defined as the normal impact point $q ^ { i }$ of foot i (Figure 3), the vertical upward direction is defined as the normalz y positive direction <sub>the</sub> <sub>two</sub> <sub>opposite</sub> ${ \vec { z } } ;$ <sup>within</sup> <sup>the</sup> <sup>tangent</sup> <sup>plane,</sup> <sup>the</sup> s, and the direction pointing t $\vec { y }$ <sup>axis</sup> <sup>is</sup> <sup>in</sup> <sup>the</sup> <sup>plane</sup> <sup>composed</sup> <sup>by</sup>he main body is positive; and the <sup>the</sup> <sup>two</sup> <sup>opposite</sup> <sup>legs,</sup> <sup>and</sup> <sup>the</sup> <sup>direction</sup> <sup>pointing</sup> <sup>to</sup> <sup>the</sup> <sup>main</sup> <sup>body</sup> <sup>is</sup> <sup>positive;</sup> <sup>and</sup> <sup>the</sup>x y direction of the $\vec { x }$ axis is perpendicular to the $\vec { y }$ axis in the tangent plane according to the right-hand rule.

![](P6_Wang_2023_Actuators_images/ef60d881e3ffd77494f9629a839d1682368a4655640ee22be844adec2a8d36bf.jpg)  
Figure 3. The coordinate of the impact point and the center of mass (CoM) of the footFigure 3. The coordinate of the impact point and the center of mass (CoM) of the foot.

Based on the above, the following expressions of the three-dimensional impact model are valid:

$$
\begin{array}{c} F _ {z} = - k z \geq 0, F _ {x} = - k _ {\tan} x, F _ {y} = - k _ {\tan} y \\ E _ {z} = \frac {1}{2} k z ^ {2}, E _ {x} = \frac {1}{2} k _ {\tan} x ^ {2}, E _ {y} = \frac {1}{2} k _ {\tan} y ^ {2} \end{array}\tag{4}
$$

<sub>2 2 2</sub>1 1 1 <sup>(4)</sup><sub>when the normal spring impulse is selected to be the independent variable, the relationship</sub> <sup>tan</sup> <sup>tan</sup> 2 2 2        <sup>z x</sup> <sup>y</sup>   between the other variables and the normal spring impulse is established for the iterative calculation of $d I _ { z s }$

$$
\begin{array}{r} E _ {z s} ^ {\prime} = \frac {d E _ {z s}}{d I _ {z s}} = \frac {\dot {E} _ {z s}}{\dot {I} _ {z s}} = \frac {k z \dot {z}}{- k z} = - \dot {z} = - v _ {z}, \\ \dot {I} _ {z s} = F _ {z s} = \sqrt {2 k E _ {z s}}, \dot {I} _ {x} = F _ {x} = - \alpha \sqrt {2 k _ {\mathrm{tan}} E _ {x}}, \dot {I} _ {y} = F _ {y} = - \beta \sqrt {2 k _ {\mathrm{tan}} E _ {y}} \end{array}\tag{5}
$$

where α and $\beta$ represent the x and y virtual spring states, respectively; their corresponding value is 1 when the spring is compressed. Otherwise, it will be set as −1.

$$
\begin{array}{r} z = \sqrt {\frac {2 E _ {z s}}{k}}, x = \sqrt {\frac {2 E _ {x}}{k _ {\mathrm{tan}}}}, y = \sqrt {\frac {2 E _ {y}}{k _ {\mathrm{tan}}}} I _ {x} ^ {\prime} = \frac {\dot {I} _ {x}}{\dot {I} _ {z s}} = - \alpha \zeta \sqrt {\frac {E _ {x}}{E _ {z s}}}, \\ I _ {y} ^ {\prime} = \frac {\dot {I} _ {y}}{\dot {I} _ {z s}} = - \beta \zeta \sqrt {\frac {E _ {y}}{E _ {z s}}} \end{array}\tag{6}
$$

Among them, $\begin{array} { r } { \zeta ^ { 2 } = \frac { k _ { \mathrm { t a n } } } { k } } \end{array}$ ; the subscript zs symbolizes the direction of $\vec { z }$ visual spring, and the subscript tan represents the tangential.

The total impulse of the impact of the foot and ground is $\stackrel {  } { I } = I _ { x } \stackrel {  } { x } + I _ { y } \stackrel {  } { y } + I _ { z } \stackrel {  } { z }$

## 2.2.2. Tangential Motion Patterns

To determine whether the two perpendicular springs on the tangential plane are in the compressed or stretched state, it is necessary to obtain the real-time deformation of the two virtual springs:

$$
\begin{array}{r} x = \int_ {0} ^ {t} \dot {x} d t = \int_ {0} ^ {I _ {z}} \dot {x} d \left(\frac {I _ {z s}}{F _ {z s}}\right) = \int_ {0} ^ {I _ {z s}} \frac {\dot {x}}{F _ {z s}} d I _ {z s} = \int_ {0} ^ {I _ {z s}} \frac {\dot {x}}{(1 + \chi \dot {z}) \sqrt {2 k E _ {z s}}} d I _ {z s}, \\ y = \int_ {0} ^ {I _ {z}} \frac {\dot {y}}{(1 + \chi \dot {z}) \sqrt {2 k E _ {z s}}} d I _ {z} \end{array}\tag{7}
$$

wherein $\begin{array} { r } { d t = d \Big ( \frac { I _ { z } } { F _ { z } } \Big ) = \frac { 1 } { F _ { z } } d ( I _ { z } ) } \end{array}$ holds under the assumption that $F _ { z }$ remains constant within every infinitesimal time period dt.

$G _ { x }$ and $G _ { y }$ are brought in to represent the deformation of the spring to determine the displacement direction of the impact point on the tangent plane, that is, to determine whether it is in a state of compression or restitution:

$$
G _ {x} = \left\{ \begin{array}{c l} \int_ {0} ^ {I _ {z s}} \frac {\dot {x}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} & i f I _ {z s} \in [ 0, I _ {c} ] \\ \int_ {0} ^ {I _ {c}} \frac {\dot {x}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} + \int_ {I _ {c}} ^ {I _ {z s}} \sqrt {1 - \gamma} \frac {\dot {x}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} & i f I _ {z s} \in [ I _ {c}, I _ {r} ] \end{array} \right.\tag{8}
$$

$$
G _ {y} = \left\{ \begin{array}{c l} \int_ {0} ^ {I _ {z s}} \frac {\dot {y}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} & i f I _ {z s} \in [ 0, I _ {c} ] \\ \int_ {0} ^ {I _ {c}} \frac {\dot {y}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} + \int_ {I _ {c}} ^ {I _ {z s}} \sqrt {1 - \gamma} \frac {\dot {y}}{(1 + \chi \dot {z}) \sqrt {E _ {z s}}} d I _ {z s} & i f I _ {z s} \in [ I _ {c}, I _ {r} ] \end{array} \right.\tag{9}
$$

whereIEW $\begin{array} { r } { \int _ { 0 } ^ { I _ { c } } \frac { \dot { x } } { \left( 1 + \chi \dot { z } \right) \sqrt { E _ { z s } } } d I _ { z s } } \end{array}$ and $\begin{array} { r } { \int _ { 0 } ^ { I _ { c } } \frac { \dot { y } } { \left( 1 + \chi \dot { z } \right) \sqrt { E _ { z s } } } d I _ { z s } } \end{array}$ represent the integral of the entire com-7 of 24 pression process of the $x , y$ visual spring.

The relationship between $G _ { x } , \bar { G _ { y } }$ and x, y is $G _ { x } = \sqrt { 2 k } x \ / , G _ { y } = \sqrt { 2 k } y \ / ,$ , and the relationship <sub>between the strain energy of the virtual springs is</sub><sup>normal</sup> <sup>virtual</sup> <sup>spring</sup> <sup>enters</sup> <sup>the</sup> <sup>restitution</sup> <sup>stat</sup> $\begin{array} { r } { E _ { x } = \frac 1 2 k _ { \mathrm { t a n } } x ^ { 2 } = \frac { { G _ { x } } ^ { 2 } } { 4 \zeta ^ { 2 } } , E _ { y } = \frac 1 2 k _ { \mathrm { t a n } } y ^ { 2 } = \frac { { G _ { y } } ^ { 2 } } { 4 \zeta ^ { 2 } } } \end{array}$ After obtaining<sup>accumulated</sup> <sup>i</sup> $G { _ x } ^ { \prime }$ <sub>and</sub><sup>mpr</sup> ${ G _ { y } } ^ { \prime } ,$ , the tangential spring deformation, namely tangential material<sup>n</sup> <sup>will</sup> <sup>be</sup> <sup>dissipated</sup> <sup>as</sup> <sup>a</sup> <sup>form</sup> <sup>of</sup> <sup>plastic</sup> <sup>deformation,</sup> <sup>mean-</sup> <sub>compliance, can be acquired. When the impact state of the normal virtual spring enters the</sub><sup>while</sup> <sup>the</sup> <sup>material</sup> <sup>will</sup> <sup>be</sup> <sup>hardened</sup> <sup>at</sup> <sup>the</sup> <sup>same</sup> <sup>time;</sup> <sup>in</sup> <sup>this</sup> <sup>case,</sup> <sup>the</sup> <sup>normal</sup> <sup>stifness</sup> <sup>will</sup> restitution state, part of the foot–ground impact energy accumulated in compression will <sub>be dissipated as a form of plastic deformation, meanwhile the material will be hardened at</sub>1 − <sub>γ</sub> the same time; in this case, the normal stiffness will increase from k to $\frac { k } { 1 - \gamma }$

## 2.2.3. Tangential Velocities

The tangential velocity refers to the slipping velocity of the impact point $q$ and is related to the motion pattern in the tangential plane. When the tangential motion pattern is slip, the velocity is given by<sup>is</sup> <sup>slip,</sup> <sup>the</sup> <sup>velocity</sup> <sup>is</sup> <sup>given</sup> <sup>b</sup> ${ \bf v } _ { \mathrm { s } } = { \bf v } _ { \tan } - \dot { x } \stackrel {  } { \mathrm { x } } - \dot { y } \stackrel {  } { \mathrm { y } } ( \mathrm { F i g u r e \ 4 } )$ <sub>, meanwhile the tangential</sub><sup>,</sup> <sup>meanwhile</sup> <sup>the</sup> <sup>tangential</sup> force isforce is $\mathrm { F } _ { \mathrm { t a n } } = - \mu F _ { z } \mathrm { v } _ { \mathrm { s } } = - k _ { \mathrm { t a n } } ( { \dot { x } } { \stackrel {  } { \mathrm { x } } } + { \dot { y } } { \stackrel {  } { \mathrm { y } } } )$ , where µ represents the coefficient of friction.here <sup>μ</sup> represents the coeficient of friction. When it sticks, the tangential velocity is zero:When it sticks, the tangential velocity is zero: $\mathbf { V _ { S } } = 0 .$ , in this case,, in this case $\mathrm { v } _ { \mathrm { t a n } } = \dot { x } \overrightarrow { \mathrm { x } } + \dot { y } \overrightarrow { \mathrm { y } }$

![](P6_Wang_2023_Actuators_images/b14697b88a82ec434803834d18dc38df39c3623beb789e1b7cf6b271ae41b4a7.jpg)  
Figure 4. The tangential velocityFigure 4. The tangential velocity.

After processing the aforementioned equations, the deformation velocity of tangential virtual springs under two patterns can be derived as follows:

1. Stick.

$$
\mathrm{v} _ {\tan} = x \vec {\mathrm{x}} + y \vec {\mathrm{y}}, \dot {x} = \mathrm{v} _ {\tan} \vec {\mathrm{x}} = v _ {x}, \dot {y} = v _ {y}\tag{10}
$$

2. Slip.

$$
k _ {\mathrm{tan}} (x \vec {x} + y \vec {y}) = \mu \sqrt {2 k E _ {z s}} (1 + \chi \dot {z}) \vec {v} _ {s}
$$

If you square both sides of the above equation,

$$
x ^ {2} + y ^ {2} = 2 \mu^ {2} \frac {k}{k _ {\mathrm{tan}} ^ {2}} E _ {z s} (1 + \chi \dot {z}) ^ {2}\tag{11}
$$

Equation (11) is equivalent to $\begin{array} { r } { E _ { x } + E _ { y } = \mu ^ { 2 } \frac { k } { k _ { \mathrm { t a n } } } E _ { z s } \left( 1 + \chi \dot { z } \right) ^ { 2 } = \mu ^ { 2 } \zeta ^ { 2 } E _ { z s } { \left( 1 + \chi \dot { z } \right) } ^ { 2 } , } \end{array}$ By differentiating t on both sides of Equation (11),

$$
x \dot {x} + y \dot {y} = \mu^ {2} \frac {k}{k _ {\mathrm{tan}} ^ {2}} (\dot {E} _ {z s} (1 + \chi \dot {z}) ^ {2} + 2 E _ {z s} (1 + \chi \dot {z}) \ddot {z}), \ddot {z} = \frac {F _ {z}}{m} = \frac {\sqrt {2 k E _ {z s}} (1 + \chi \dot {z})}{m}\tag{12}
$$

where m represents the mass of the touchdown foot.

By combining Equation (12) with $y \dot { x } - x \dot { y } = v _ { x } y - v _ { y } x ,$ , after processing, the velocity of deformation can be obtained as follows:

$$
\dot {x} = \frac {\mu^ {2} \frac {k}{k _ {\mathrm{tan}} ^ {2}} x \left(\dot {E} _ {z s} + \frac {2 \sqrt {2 k E _ {z s}} E _ {z s}}{m}\right) (1 + \chi \dot {z}) ^ {2} + v _ {x} y ^ {2} - v _ {y} x y}{x ^ {2} + y ^ {2}}\tag{13}
$$

$$
\dot {y} = \frac {\mu^ {2} \frac {k}{k _ {\tan} {} ^ {2}} y \left(\dot {E} _ {z s} + \frac {2 \sqrt {2 k E _ {z s}} E _ {z s}}{m}\right) (1 + \chi \dot {z}) ^ {2} + v _ {y} x ^ {2} - v _ {x} x y}{x ^ {2} + y ^ {2}}\tag{14}
$$

## 2.2.4. Determination of the Tangential Patterns

When the contact point sticks, there is $\sqrt { F _ { x } { } ^ { 2 } + F _ { y } { } ^ { 2 } } < \mu F _ { z }$ . In the form of strain energy, this inequation can be expressed as $\begin{array} { r } { E _ { x } + E _ { y } < \frac { \mu ^ { 2 } k } { k _ { \mathrm { t a n } } } E _ { z s } \left( 1 + \chi \dot { z } \right) ^ { 2 } . } \end{array}$ ; thus, when it cannot hold, the contact point is considered to be slipping.

## 2.3. Theoretical Model ofMultistage Aluminum Honeycomb

Aluminum honeycomb exhibits superior energy absorption capability while maintaining good surface flatness during the compression process. These characteristics help reduce the sudden deformation of the structure caused by the impact; thereby, aluminum honeycomb is conducive to improving the landing smoothness of the vehicle.

During the landing process of the vehicle, it is challenging to precisely control its attitude and velocity at touchdown. Therefore, to ensure a relatively smooth landing process, the landing gear is not only required to work efficiently under normal conditions, but also manage the extreme landing situation of single-leg touchdown. In this case, the buffering material within a single leg needs to possess the ability to absorb a significant portion of the vehicle’s impact energy. Hence, the two-stage aluminum honeycomb (the specific parameters are shown in Table 1) was employed in this experiment, and the theoretical energy absorption capacity of the primary aluminum honeycomb is sufficient for the general situation (vertical landing situation). Moreover, when the extreme situation occurs, both the primary and secondary aluminum honeycomb in a single leg will successively participate in energy absorption to ensure a smooth and stable landing for the vehicle.

Table 1. Specifications of the multistage aluminum honeycomb cores.

<table><tr><td>Stage Category</td><td>Length (mm)</td><td>Diameter of Section (mm)</td><td>Cell Size (mm)</td><td>Sheet Thickness (mm)</td></tr><tr><td>Primary honeycomb</td><td>72</td><td>98</td><td>8.66</td><td>0.07</td></tr><tr><td>Secondary honeycomb</td><td>125</td><td>98</td><td>5.20</td><td>0.06</td></tr></table>

As the two-stage aluminum honeycomb theoretical model shows in Figure 5, assuming<sup>2</sup> that the stiffnesses of the elastic section and the plastic section of the primary and the( )( ) ( ) ( ) ( )<sup>21</sup>k x x k x k x x x x k x x x x x+ − + + − − + − ≤ < secondary aluminum honeycomb are $k _ { b 1 } , k _ { b 2 } , k _ { b 3 }$ , and $k _ { b 4 } ,$ , respectively, and $x _ { L 1 } , x _ { L 2 } , x _ { L 3 } ,$ and $x _ { L 4 }$ represent the distance from the initial point of the multistage aluminum honeycomb,mong the above equations, the force–displacement and energy–displacement relationships of the multistage aluminum1 honeycomb are as follows:<sup>1</sup> <sup>1 1</sup>  <sup>b</sup> <sup>b L</sup>

$$
F _ {b} = \left\{ \begin{array}{c l} k _ {b 1} x _ {b} & 0 \leq x _ {b} <   x _ {L 1} \\ k _ {b 1} x _ {L 1} + k _ {b 2} (x _ {b} - x _ {L 1}) & x _ {L 1} \leq x _ {b} <   x _ {L 2} \\ k _ {b 1} x _ {L 1} + k _ {b 2} (x _ {L 2} - x _ {L 1}) + k _ {b 3} (x _ {b} - x _ {L 2}) & x _ {L 2} \leq x _ {b} <   x _ {L 3} \\ k _ {b 1} x _ {L 1} + k _ {b 2} (x _ {L 2} - x _ {L 1}) + k _ {b 3} (x _ {L 3} - x _ {L 2}) + k _ {b 4} (x _ {b} - x _ {L 3}) & x _ {L 3} \leq x _ {b} <   x _ {L 4} \end{array} \right.
$$

$$
E _ {b} = \left\{ \begin{array}{c l} \frac {1}{2} k _ {b 1} x _ {b} ^ {2} & 0 \leq x _ {b} <   x _ {L 1} \\ E _ {b 1} ^ {p} + \frac {1}{2} k _ {b 2} (x _ {b} - x _ {L 1}) ^ {2} + k _ {b 1} x _ {L 1} (x _ {b} - x _ {L 1}) & x _ {L 1} \leq x _ {b} <   x _ {L 2} \\ E _ {b 2} ^ {p} + (k _ {b 2} (x _ {L 2} - x _ {L 1}) + k _ {b 1} x _ {L 1}) (x _ {b} - x _ {L 2}) + \frac {1}{2} k _ {b 3} (x _ {b} - x _ {L 2}) ^ {2} & x _ {L 2} \leq x _ {b} <   x _ {L 3} \\ E _ {b 3} ^ {p} + (k _ {b 2} (x _ {L 2} - x _ {L 1}) + k _ {b 1} x _ {L 1} + k _ {b 3} (x _ {L 3} - x _ {L 2})) (x _ {b} - x _ {L 2}) + \frac {1}{2} k _ {b 4} (x _ {b} - x _ {L 3}) ^ {2} & x _ {L 3} \leq x _ {b} <   x _ {L 4} \end{array} \right.
$$

![](P6_Wang_2023_Actuators_images/f9c5daef8aa9ae335de96a68b408fe83404fa83f08dd4c384689f55e597d26af.jpg)

![](P6_Wang_2023_Actuators_images/6b9d41a383998cb6f1805ab19da0d0e54f8861b4dbb0124c0b0f6cf373c49572.jpg)  
Figure 5. Experimental and finite element analysis (FEA) simulation results of the multistage aluminum num honeycomb and theoretical model of mechanical properties of the multistage aluminum hon-honeycomb and theoretical model of mechanical properties of the multistage aluminum honeycomb.

Among the above equations,

$$
E _ {b 1} ^ {p} = \frac {1}{2} k _ {b 1} x _ {L 1} ^ {2},
$$

$$
E _ {b 2} ^ {p} = \frac {1}{2} k _ {b 1} x _ {L 1} ^ {2} + \frac {1}{2} k _ {b 2} (x _ {L 2} - x _ {L 1}) ^ {2} + k _ {b 1} x _ {L 1} (x _ {L 2} - x _ {L 1}),
$$

$$
\begin{array}{r} E _ {b 3} ^ {p} = \frac {1}{2} k _ {b 1} x _ {L 1} ^ {2} + \frac {1}{2} k _ {b 2} (x _ {L 2} - x _ {L 1}) ^ {2} + k _ {b 1} x _ {L 1} (x _ {L 2} - x _ {L 1}) + \\ (k _ {b 2} (x _ {L 2} - x _ {L 1}) + k _ {b 1} x _ {L 1}) (x _ {L 3} - x _ {L 2}) + \frac {1}{2} k _ {b 3} (x _ {L 3} - x _ {L 2}) ^ {2} \end{array}
$$

where the superscript p represents the impact energy stored in the previous stage by the=0k aluminum honeycomb.

<sup>In the model simulation of the vertical landing process of the vehicle, set</sup> that is, assuming that the plastic section of the multistage aluminum honey $k _ { b 2 } = 0 _ { , }$ $k _ { b 4 } = 0 ,$ , that is, assuming that the plastic section of the multistage aluminum honeycomb<sub>plastic</sub> <sub>behavior.</sub> has ideal plastic behavior.

## 2.4. Coupling of the Multi-Impact and Buffering

In each state of the vehicle landing process, the primary impulse needs to be selected in the first place, followed by a network of relationships between the primary impulse and all kinds of secondary impulses. When only either the foot–ground impact or buffering behavior is activated (state S3 or state S4) in a state, the elastic impulse is preferred as the primary impulse; in this case, no coupling occurs between the buffering behavior and the foot–ground impact. However, the duration of this situation is relatively short.

In the state where both foot–ground impact and buffering are activated, as shown in Figure 6, the normal impulse of foot–ground impact<sup>௭௦</sup> $I _ { z s }$ is prioritized as the primary impulse, while the buffering impulse <sup>ulse,</sup> <sup>while</sup> <sup>the</sup> <sup>bufering</sup> <sup>impulse</sup> <sup>ୠ,</sup> <sup>au</sup> ${ \mathit { I } } _ { \mathrm { b } } ,$ auxiliary pillar impulse <sup>iary</sup> <sup>pillar</sup> <sup>impulse</sup> <sup>ୟ,</sup> <sup>tan</sup> ${ \cal I } _ { \mathrm { a } } ,$ tangential impact<sup>ntial</sup> <sup>impact</sup> <sup>im-</sup> impulse I<sub>t</sub>, and normal damping impulse<sup>௧ ௭ௗ</sup> $I _ { z d }$ act as secondary impulses.

![](P6_Wang_2023_Actuators_images/07aa22f488ba0e427e7e7adc581054962d6eb2041ba69fbbc02c42db0c0dbc61.jpg)  
Figure 6. The coupling of the foot–ground impact and aluminum honeycomb buffering of the <sup>gure</sup> <sup>6.</sup> <sup>The</sup> <sup>coupling</sup> <sup>of</sup> <sup>the</sup> <sup>fo</sup>inverted-triangle landing leg.

## 3. Implementation and Results of Simulation and Experiment of the Vertical Landing Implementation and Process of the Vehicle

## ocess of the Vehicle 3.1. Simulation of the Vertical Landing Process

ulation of the Vertical Landing Process During the experimental process, the friction at the joints and aluminum honeycomb sleeves of the landing gear, as well as the presence of installation clearances, can absorb part of the impact energy in the landing process, which will have an uncertain effect on the experimental data. Therefore, in the axial direction of the main pillar, a damping force $\left( F _ { b d } = \mathrm { D } _ { b } v _ { b } F _ { b h } \right)$ was added to simulate this damping effect and friction loss. Additionally, the force–displacement characteristics of an aluminum honeycomb may also change under multiple impacts; however, in the simulation, it was assumed that the force–displacement relationship of the aluminum honeycomb under multiple impact remains the same as it was during the initial loading. The structure parameters of the vehicle used in the simulation of landing process are shown in Figure 7, and the simulation calculation process is shown in Figure 8.

![](P6_Wang_2023_Actuators_images/747c0fa3b804904058451f9859105a658474e71d5d70d2b1fb69d6ba83b3b6f2.jpg)  
Figure 7. Theoretical model of the vertical landing vehicleFigure 7. Theoretical model of the vertical landing vehicle.<sup>Figure</sup> <sup>7.</sup> <sup>Theoretical</sup> <sup>model</sup> <sup>of</sup> <sup>the</sup> <sup>vertical</sup> <sup>landing</sup> <sup>vehicle</sup>

![](P6_Wang_2023_Actuators_images/53cf2089b77c2fe3854f35f695683fe7aa99a235bfa36d4a5f429ab4c9c971a5.jpg)  
Figure 8. Calculation flow of vertical landing process.Figure 8. Calculation flow of vertical landing process.

The symbols, meanings, and values of parameters used in the simulation of vertical landing process of the vehicle are shown in Table 2.

1  
Table 2. The parameters used in the simulation.

<table><tr><td>Symbol</td><td>Value</td><td>Symbol</td><td>Value</td></tr><tr><td> $\theta_{bi}$ </td><td>58.70</td><td> $x_{L2}$ </td><td>57.60</td></tr><tr><td> $\theta_{ai}$ </td><td>35.11</td><td> $x_{L3}$ </td><td>58.23</td></tr><tr><td>h</td><td>0.092</td><td> $x_{L4}$ </td><td>183.23</td></tr><tr><td> $H_1$ </td><td>0.25</td><td>k</td><td> $2 \times 10^6$ </td></tr><tr><td> $H_2$ </td><td>1.55</td><td> $k_{tan}$ </td><td> $7 \times 10^4$ </td></tr><tr><td>R</td><td>0.60</td><td>μ</td><td>0.50</td></tr><tr><td> $L_{h0}$ </td><td>3.19</td><td>γ</td><td>0.50</td></tr><tr><td> $L_{b0}$ </td><td>0.18</td><td>χ</td><td> $2 \times 10^{-4}$ </td></tr><tr><td> $L_{a0}$ </td><td>2.04</td><td> $D_b$ </td><td>1.50</td></tr><tr><td> $x_{L1}$ </td><td>0.47</td><td> $H_{height}$ </td><td>0.2</td></tr></table>

By applying the proposed impact–buffering coupling model, the mass of the main�<sub>௅ଵ</sub> 0.47 H<sub>height</sub> 0.2 body was set as 1120 kg, while the mass of foot was 1 kg, the vertical landing process of the vehicle was simulated, and the results are presented below. The normal and tangential<sup>By</sup> <sup>applying</sup> <sup>the</sup> <sup>proposed</sup> <sup>impact–bufering</sup> <sup>coupling</sup> <sup>model,</sup> <sup>the</sup> <sup>mass</sup> <sup>of</sup> <sup>the</sup> <sup>mai</sup> velocity, as well as the transformation of the tangential motion pattern of the center of mass of the foot, are shown in Figure 9. From the figure, it can be observed that the vehicle makes initial contact with the ground at 0.2 s; the first impact between the vehicle and the groundmass of the foot, are shown in Figure 9. From the figure, it can be observed that the vehicl occurs at this moment, until the vehicle leaves the ground around 0.38 s, signifying the endmakes initial contact with the ground at 0.2 s; the first impact between the vehicle and th of the first impact.<sup>g</sup> $\operatorname { A t } 0 . 4 3 \ : s ,$ the vehicle experiences the second impact with the ground,<sup>s</sup> <sup>at</sup> <sup>this</sup> <sup>moment,</sup> <sup>until</sup> <sup>the</sup> <sup>vehicle</sup> <sup>leaves</sup> <sup>the</sup> <sup>ground</sup> <sup>around</sup> <sup>0.38</sup> <sup>s,</sup> <sup>signify</sup> which lasts until 0.53 s. Finally, at 0.54 s, the vehicle undergoes its third final touchdown.<sup>ing</sup> <sup>the</sup> <sup>end</sup> <sup>of</sup> <sup>the</sup> <sup>first</sup> <sup>impact.</sup> <sup>At</sup> <sup>0.43</sup> <sup>s,</sup> <sup>the</sup> <sup>vehicle</sup> <sup>experiences</sup> <sup>the</sup> <sup>second</sup> <sup>impact</sup> <sup>wit</sup> Subsequently, the vehicle’s landing process nonlinear system enters a damped periodic oscillation until it reaches a completely stable state.damped periodic oscillation until it reach

![](P6_Wang_2023_Actuators_images/009ae8f40e9234eb303e21f313b46ef6c42a6870468c5cc6520c2dc652d75300.jpg)  
(a)

2  
![](P6_Wang_2023_Actuators_images/b98d08fd7cbdf013aea4c87d7acda80a0beb6df05ac0b869cf8bc1e4d9088295.jpg)

(b)  
![](P6_Wang_2023_Actuators_images/99a8f0c7e0b785586211f336da5767564f395d84e1eff9f4a062000d598c2659.jpg)  
(c)  
Figure 9. Velocity of foot and tangential motion patterns in the first impact: (a) normal velocity, (b) tangential velocity, and (c) tangential spring velocity and centroid velocity of foot.

It can be seen from Figure 9 that, during the first impact between the vehicle and the ground, the impact number between the foot and the ground is the largest; during this period, the velocity of foot decreases from the initial value of −2 m/s to −0.21 m/s. Additionally, there is a sudden change in the amplitude of the foot velocity at 0.28 s, which is attributed to the compression of the secondary aluminum honeycomb in the buffering device. The indicator factor in Figure 9b represents different tangential motion patterns, where a value of 1 indicates the impact point is slipping, 0 means that it sticks, and 0.5 means that the vehicle is not in contact with the ground. Based on the above, it can be observed from Figure 9c that during the first impact, the predominant pattern of tangential motion of the contact point remains stuck, with only two brief periods of slipping. In addition, the two periods of slipping are slightly different in behavior; they all happen in the later stage of the two aluminum honeycombs’ compressing process, but the second slipping is more continuous. The slipping of the impact point in the second impact is very brief and happens just before the vehicle leaves the ground; thereafter, the tangential motion pattern of the impact point always remains stuck.

From Figure 10a,b, in the first impact, a turning point caused by different stages of<sup>From</sup> <sup>Figure</sup> <sup>10a,b,</sup> <sup>in</sup> <sup>the</sup> <sup>first</sup> <sup>impact,</sup> <sup>a</sup> <sup>turning</sup> <sup>point</sup> <sup>caused</sup> <sup>by</sup> <sup>difere</sup> aluminum honeycombs during landing can be found. In Figure 10b, together with the<sup>aluminum</sup> <sup>honeycombs</sup> <sup>during</sup> <sup>landing</sup> <sup>can</sup> <sup>be</sup> <sup>found.</sup> <sup>In</sup> <sup>Figure</sup> <sup>10b,</sup> <sup>toget</sup> detailed view, the inclination angle of the foot position decreases continuously from the<sup>detailed</sup> <sup>view,</sup> <sup>the</sup> <sup>inclination</sup> <sup>angle</sup> <sup>of</sup> <sup>the</sup> <sup>foot</sup> <sup>position</sup> <sup>decreases</sup> <sup>continuou</sup> first to the third impact, indicating that the first impact of the foot will create the deepest pit<sup>first</sup> <sup>to</sup> <sup>the</sup> <sup>third</sup> <sup>impact,</sup> <sup>indicating</sup> <sup>that</sup> <sup>the</sup> <sup>first</sup> <sup>impact</sup> <sup>of</sup> <sup>the</sup> <sup>foot</sup> <sup>will</sup> <sup>create</sup> on the ground, and the depth and sliding distance will progressively decrease successively<sup>pit</sup> <sup>on</sup> <sup>the</sup> <sup>ground,</sup> <sup>and</sup> <sup>the</sup> <sup>depth</sup> <sup>and</sup> <sup>sliding</sup> <sup>distance</sup> <sup>will</sup> <sup>progressively</sup> <sup>decr</sup> in the later impact.<sup>sively</sup>

![](P6_Wang_2023_Actuators_images/7a9a83ef828dc52245cc55e762e47241369dc57541ccebb70b6136c26198908b.jpg)

(a)  
![](P6_Wang_2023_Actuators_images/f9200f1017c7bf5791a4067dbcf1e57c03af280c6ae4d407a90623f1eae2105c.jpg)  
(b)  
Figure 10. Foot position: (a) normal and tangential position of the touch-down foot; Figure 10. Foot position: (a) normal and tangential position of the touch-down foot; (b) history of <sup>position</sup> <sup>of</sup> <sup>the</sup> <sup>center</sup> <sup>of</sup> <sup>mass</sup> <sup>(Co</sup>position of the center of mass (CoM) of the foot.

Based on phase diagram Figure 11, it can be observed that in the early stage of the three collisions between the vehicle and the ground, the motion of the foot exhibits limited convergence behavior, and there may even be a slight tendency to deviate from the <sub>stable</sub> <sub>point</sub> <sub>in</sub> <sub>the</sub> <sub>medium</sub> <sub>stage.</sub> <sub>However,</sub> <sub>in</sub> <sub>the</sub> <sub>late</sub> <sub>stage</sub> <sub>of</sub> <sub>the</sub> <sub>impact,</sub> <sub>a</sub> <sub>significant</sub>point in the medium stage. However, in the late stage of the impact, a significant improveimprovement in convergence is observed.ment in convergence is observed.

![](P6_Wang_2023_Actuators_images/8ef8dae735ca2cf0e45d28e1e898c6e09be07887cb3c8fadb0fc2bdb21bd5c4b.jpg)

![](P6_Wang_2023_Actuators_images/f5b20f5a4a2fd177e38c9e2a69e38432cf7e84dcf69272feb65df8266bcaf91b.jpg)

![](P6_Wang_2023_Actuators_images/97d6f936f8cfc8c9d932fd71f03d9e226f12f7553e58cca084b56665e900bbdb.jpg)

![](P6_Wang_2023_Actuators_images/e237f826f9b4ac756e48a95efeca30f195104c888ea7b656261725c1a9cfd341.jpg)  
(b)  
<sup>Figure</sup> <sup>11.</sup> <sup>Velocity–position</sup> <sup>phase</sup> <sup>diagram</sup> <sup>of</sup> <sup>the</sup> <sup>foot:</sup> <sup>(a)</sup> <sup>normal;</sup> <sup>(b)</sup> <sup>tangential</sup>Figure 11. Velocity–position phase diagram of the foot: (a) normal; (b) tangential.

As shown in Figure 12, the peak acceleration of the foot reaches 148As shown in Figure 12, the peak acceleration of the foot reaches 1489 $\mathrm { m } / \mathrm { s } ^ { 2 }$ in the firstin the first impact and drops to 36impact and drops to 367 $\mathrm { m } / \mathrm { s } ^ { 2 }$ and 256and 256 $\mathrm { m } / \mathrm { s } ^ { 2 }$ n the second and third impact, respectively.in the second and third impact, respectively. Furthermore, during the first and second impact, due to the temporary participation oFurthermore, during the first and second impact, due to the temporary participation of the the secondary aluminum honeycomb in the landing, the acceleration increases suddenlysecondary aluminum honeycomb in the landing, the acceleration increases suddenly and and then levelthen levels off.

From the buffering velocity diagram (Figure 13a), the maximum buffering velocity of the first, second, and third impact is $0 . 8 \mathrm { m } / \mathrm { s } , 0 . 0 9 \mathrm { m } / \mathrm { s } ,$ , and 0.05 m/s, respectively. In the early stage of the first impact, the buffering velocity increases sharply in the early stage, making the primary aluminum honeycomb enter the plastic section rapidly; as a result, the buffering velocity exhibits a smaller oscillation amplitude and a steep trend. Unlike the aforementioned stage of the impact, at the time when the primary aluminum honeycomb is completely compressed and the compression of the secondary aluminum honeycomb starts, the elastic section of the secondary aluminum honeycomb plays a major role, and the vast majority of the kinetic energy of the vehicle has been absorbed; thus, the buffer velocity will experience continual oscillation. From Figure 13b, the buffer stroke reaches 66.5 mm after the first impact, accounting for 97.8% of the total stroke (68 mm) of the landing, which shows that the aluminum honeycomb is capable of quickly absorbing the impact energy, while also confirming the high buffering performance of the multistage aluminum honeycomb.

![](P6_Wang_2023_Actuators_images/b224128a45cc4dc7e4b65a979043b189a801a74a76bb62cfc30ef0f599d83687.jpg)

(a)  
![](P6_Wang_2023_Actuators_images/c48fb28c969766e96e9ded677dbe9fb716fb55d6d4ce94aa284b72c27a80eba6.jpg)  
(b)  
<sup>Figure</sup> <sup>12.</sup> <sup>Acceleration</sup> <sup>of</sup> <sup>foot:</sup> <sup>(a)</sup> <sup>normal;</sup> <sup>(b)</sup> <sup>tangential.</sup><sub>Figure 12. Acceleration of foot: (a) normal; (b) tangential.</sub>

From the bufering velocity diagram (Figure 13a), the maximum bufering velocity of In Figure 14, the velocity and position of the center of mass of the main body experience the first, second, and third impact is 0.8 m/s, 0.09 m/s, and 0.05 m/s, respectively. In the the largest reduction after the first impact, then gradually stabilize during the subsequent early stage of the first impact, the bufering velocity increases sharply in the early stage, two collisions. Moreover, the position–velocity phase diagram (Figure 14c) indicates that the making the primary aluminum honeycomb enter the plastic section rapidly; as a result, convergence amplitude is the largest during the first impact; after the small convergence the bufering velocity exhibits a smaller oscillation amplitude and a steep trend. Unlike process of two subsequent collisions, the vehicle system will reach a stable state after the aforementioned stage of the impact, at texperiencing a damped periodic oscillation.

is completely compressed and the compression of the secondary aluminum honey-From Figure 15, it can be seen that during the first impact, the secondary aluminum comb starts, the elastic section of the secondary aluminum honeycomb plays a major role, honeycomb also contributes to the landing of the vehicle, indicating that the primary and the vast majority of the kinetic energy of the vehicle has been absorbed; thus, the aluminum honeycomb has been fully compressed. In the second impact, the buffering force bufer velocity will experience continual oscillation. From Figure 13b, the bufer stroke <sup>also</sup> <sup>hits</sup> <sup>the</sup> <sup>threshold</sup> <sup>of</sup> <sup>the</sup> <sup>secondary</sup> <sup>aluminum</sup> <sup>honeycomb,</sup> <sup>but</sup> <sup>quickly</sup> <sup>diminishes.</sup> Moreover, only the elastic sections of the first and second aluminum honeycomb are <sub>the</sub> <sub>landing,</sub> <sub>which</sub> <sub>shows</sub> <sub>that</sub> <sub>the</sub> <sub>aluminum</sub> <sub>honeycomb</sub> <sub>is</sub> <sub>capable</sub> <sub>of</sub> <sub>quickly</sub> involved in the subsequent impact and system oscillation after the first impact.

Based on Figure 16a, it can be found that throughout the entire landing process of the vehicle, the overall energy variation in the system is consistent with the total dissipated energy, indicating that this model can ensure the conservation of energy and can track the changes in each kind of energy, as presented in Figure 16b–d, which further exhibits the effectiveness and accuracy of this model as well.

![](P6_Wang_2023_Actuators_images/38615a4c83da78beba4895340419ee0c3cca47cd6a04b91d9a2b165211bcc441.jpg)

(a)  
![](P6_Wang_2023_Actuators_images/aedaaedc898ae5f5ccf208ee00021924852c40a24a24601c11c32420ed9808d5.jpg)  
(b)

<sup>Figure</sup> <sup>13.</sup> <sup>Results</sup> <sup>of</sup> <sup>the</sup> <sup>bufer:</sup> <sup>(a)</sup> <sup>velocity;</sup> <sup>(b)</sup> <sup>bufer</sup> <sup>disp</sup>Figure 13. Results of the buffer: (a) velocity; (b) buffer displacement.  
![](P6_Wang_2023_Actuators_images/7752d4ee7859e6991dc2a870390ef17d9be1bcef49b0dfc12e5b2c77db2de8a7.jpg)  
(a)

![](P6_Wang_2023_Actuators_images/826e6874b473740b4c5f7f54823af7cb93d5ad436f272d90b6b3fdc0d1a922b9.jpg)  
(b)

![](P6_Wang_2023_Actuators_images/177447ffd77a826ccd2c80e0210d9d13a5289db39be76c2452b09b3e0c2a978a.jpg)

(c)  
![](P6_Wang_2023_Actuators_images/bc8023f5954291b60117da9520c6abfdbba50ed315a1738c119efb1d9cc0c13e.jpg)  
(d)  
<sup>Figure</sup> <sup>14.</sup> <sup>Results</sup> <sup>of</sup> <sup>main</sup> <sup>body</sup> <sup>of</sup> <sup>the</sup> <sup>vehicle:</sup> <sup>(a)</sup> <sup>velocity;</sup> <sup>(b)</sup> <sup>position</sup> <sup>of</sup> <sup>the</sup> <sup>centroid;</sup> <sup>(c)</sup> <sup>p</sup>Figure 14. Results of main body of the vehicle: (a) velocity; (b) position of the centroid; (c) position– <sup>velocity</sup> <sup>phase</sup> <sup>diagram;</sup> <sup>(</sup>velocity phase diagram; (d) acceleration.

![](P6_Wang_2023_Actuators_images/f75b6adcfd19d1f5fbcbb3e7ba9cc1d42f8d60f7366b41e61f9e39986eedf921.jpg)  
Figure 15. History of bufering force, structural damping force, foot normal force, foot tangentialFigure 15. History of buffering force, structural damping force, foot normal force, foot tangential force, and auxiliary pillar force.force, and auxiliary pillar force.

## <sub>Based</sub> <sub>on</sub> <sub>Figure</sub> <sub>16a,</sub> <sub>it</sub> <sub>can</sub> <sub>be</sub> <sub>found</sub> <sub>that</sub> <sub>throughout</sub> <sub>the</sub> <sub>entire</sub> <sub>landi</sub>3.2. Implementation of the Vertical Landing Experiment of the Physical Vehicle

cle, the overall energy variation in the system is consistent with the total dissipatedAfter successfully assembling the inverted-triangle landing gear, an experimental energy, indicating that this model can ensure the conservation of energy and can track theplatform capable of conducting the vertical landing of the vehicle was built (as shown in Figure 17). Then, the experiments were carried out. The freefalling height of the landing gear was 0.2 m, equal as the simulation height $\mathrm { ( H _ { h e i g h t } ) }$ ; the results are represented below.

By comparing the experimental results with the simulation results, it can be seen from Figure 18 that both the experimental and simulation landing processes of the vehicle experienced the situation of rebound; however, there existed differences between the theoretical model and the experimental setups as below. 1. During the first impact section, unlike the results of the experiment, the simulated force oscillated when the plastic sections of the multistage aluminum honeycomb started to contribute to the landing, as a result of the foot–ground impact. 2. The experimental force curve briefly exhibits a sharp peak before entering the plateau stage, the analytical model prediction percentage error of the impact force peak value is 9.9%, and this sharp peak difference is more obvious in the comparison of the buffering force between the experimental results and the simulation results; the percentage error was 19.72%, while the prediction percentage errors of the impact force and the buffering force in the steady values were 9.76% and 11.40%, respectively. The existence of the sharp peak was mainly because the precompression treatment of the multistage alu minum honeycomb used in the experiments could not completely eliminate the force peak before the plastic section, while in the simulation, the multistage aluminum honeycomb was assumed to be an ideal smooth transition elastic–plastic material. 3. From the data of the experiment, after the first impact, the vehicle will undergo another touchdown before entering the oscillation phase until stabilization. However, in the simulation, the vehicle rebounded twice. The one reason for this inconsistency is that the structural damping of the landing gear in the actual landing is unknown, while the structural damping imposed in the simulation is typical $( F _ { b d } = D _ { b } v _ { b } F _ { b h } )$ . Moreover, due to the incomplete rigid connection between the aluminum honeycomb and the sleeve, the rod and the foot may slip down to remain in contact with the ground when the vehicle rebounds; these all lead to differences in energy dissipation between the experimental process and the simulation.

From Figure 19, the stroke variation history of the buffer in the experiments aligns well with the simulation; the model prediction percentage error of the stroke displacements in the steady state is 0.28%. After the first impact, both the experimental and simulated buffer undergo a certain retraction; this can be attributed to the release of elastic energy absorbed by the elastic section of the multistage aluminum honeycomb as the impact approaches its end.

![](P6_Wang_2023_Actuators_images/766fe54f2998342c8dca64782dd1b69dbc1bd934db9f457484117779a93e86fb.jpg)  
(a)

![](P6_Wang_2023_Actuators_images/1a610ac99c9f2593cbaa9fc2268930279783f48eca11f3ace22b63accbdf688c.jpg)  
(b)

![](P6_Wang_2023_Actuators_images/e7deb1197bd4fd165a1c6db5b1d4e29f56193cf2fc9ce3bf77b409afa8377f1f.jpg)  
(c)

![](P6_Wang_2023_Actuators_images/934584a1d199a8fecad382c03852e8ab13cb67d26d10c46945b483132843287c.jpg)

(d)  
![](P6_Wang_2023_Actuators_images/97edc94a99b369e9c022530f410fc68228f487256a52c79110144c12f7afe9b8.jpg)  
(e)  
Figure 16. All kinds of energy of the system. (a) Total energy and total dissipated energy; (b) kinetic energy of the main body and foot; (c) elastic energy; (d) potential energy of the body and foot; (e) dissipated energy in the system.

![](P6_Wang_2023_Actuators_images/56e8fae244c6b119fbd1015aa49a68ca6b84e9fd30249790a1908dee9b3375ee.jpg)

<sub>Figure</sub> <sub>17.</sub> <sub>MeasFigure 17. Measurement units.</sub>rocess and the simulation.  
![](P6_Wang_2023_Actuators_images/07105a82e7f4ddc6dbba82dfb58f898205a11c9876a64c9466bc9e32e1ee60d3.jpg)  
ring<sub>(a)</sub>

![](P6_Wang_2023_Actuators_images/e7242cb5206caa4c3433057f3d8a4424d9a7e9d95475280ab89928879e92c547.jpg)  
(b)  
igure 18. Force results of experiment and simulation: (a) the normal impact force and (b) the buf-Figure 18. Force results of experiment and simulation: (a) the normal impact force and (b) the <sup>ring</sup> <sup>force.</sup> buffering force.

rom Figure 19, the stroke variation history of the bufer in the experiments aligns According to Figure 20a, the trends in the results of the experiment and simulation ell with the simulation; the model prediction percentage error of the stroke displace-during the first impact matched with each other well, except for the small-scale oscillation in ents in the steady state is 0.28%. After the first impact, both the experimental and simu-the simulation process. However, the peak of the acceleration measured in the experiment $( 4 3 . 5 \mathrm { m } / \mathrm { s } ^ { 2 } )$ undergo a certain retraction; this can be atributewas higher than the simulated peak acceleration $( 2 3 . 8 \ : \mathrm { m } / \mathrm { s } ^ { 2 } )$ ase of elastic , which may be a nergy absorbed by the elastic section of the multistage aluminum honeycomb as the im-result of the incomplete removal of force peaks of the aluminum honeycomb used in the act approaches its end. experiment. In addition, the timelines of the subsequent impact of the experiment and simulation were slightly misaligned due to unknown structural damping, but the trendr<sup>i</sup> was consistent, except for the peaks. From Figure 20b, it can be found that the oscillationu phase of the acceleration of the experiment during the first impact was shorter and the<sup>5</sup> frequency was lower compared to the simulation; moreover, there was no significant fluctuation in the subsequent impact. Apart from the sampling error of the equipment used in the experiment, these differences can be attributed to the simplification of the theoretical0.2 0.4 0.6 0.8 1 1.2 1.4 model, which can be elaborated as follows. Compared with the perfect elasticity in the<sup>Time</sup> <sup>(s)</sup> bi-stiffness spring model and aluminum honeycomb model of the simulation, the elastic(b) <sup>xperiment</sup> <sup>(43.5</sup> <sup>m/s2)</sup> <sup>was</sup> <sup>higher</sup> <sup>than</sup> <sup>the</sup> <sup>simulated</sup> <sup>peak</sup> <sup>acceleration</sup> <sup>(23.8</sup> <sup>m/s2),</sup> <sup>which</sup> characteristics of the foot–ground impact during the landing process will be weakened<sup>ay</sup> <sup>be</sup> <sup>a</sup> <sup>result</sup> <sup>of</sup> <sup>the</sup> <sup>incomplete</sup> <sup>removal</sup> <sup>of</sup> <sup>force</sup> <sup>peaks</sup> <sup>of</sup> <sup>the</sup> <sup>aluminum</sup> <sup>honeycomb</sup> <sub>by</sub> <sub>the</sub> <sub>friction</sub> <sub>of</sub> <sub>the</sub> <sub>mechanical</sub> <sub>structure</sub> <sub>as</sub> <sub>well</sub> <sub>as</sub> <sub>the</sub> <sub>damping</sub> <sub>between</sub> <sub>the</sub> <sub>foot</sub> <sub>and</sub>sed in the experiment. In addition, the timelines of the subsequent impact of the experithe ground during the experiment, leading to a significant reduction in oscillation upon<sup>ent</sup> <sup>and</sup> <sup>simulation</sup> <sup>were</sup> <sup>slightly</sup> <sup>misaligned</sup> <sup>due</sup> <sup>to</sup> <sup>unknown</sup> <sup>structural</sup> <sup>damping,</sup> <sup>but</sup> (during) the impact between the foot and the ground in the experiments. The verticalhe trend was consistent, except for the peaks. From Figure 20b, it can be found that the landing vehicle with the inverted-triangle landing gear was translated into a rigid–flexible<sub>well</sub> <sub>with</sub> <sub>the</sub> <sub>simulation;</sub> <sub>the</sub> <sub>model</sub> <sub>prediction</sub> <sub>percentage</sub> <sub>error</sub> <sub>of</sub> <sub>the</sub> <sub>stroke</sub> <sub>displace-</sub>scillation phase of the acceleration of the experiment during the first impact was shorter coupling multibody system, and we regarded the vertical landing process of the vehicle asnd the frequency was lower compared to the simulation; moreover, there was no signifa dynamics convergence problem of a complex nonlinear dissipative system. We broke itcant fluctuation in the subsequent impact. Apart from the sampling error of the equipdown into four subsystems—four states—correspondingly, and based on the above, we<sub>energy</sub> <sub>absorbed</sub> <sub>by</sub> <sub>the</sub> <sub>elastic</sub> <sub>section</sub> <sub>of</sub> <sub>the</sub> <sub>multistage</sub> <sub>aluminum</sub> <sub>honeycomb</sub> <sub>as</sub> <sub>the</sub> <sub>im-</sub>ent used in the experiment, these diferences can be atributed to the simplification of studied the problem using the state transition method.he theoretical model, which can be elaborated as foll

![](P6_Wang_2023_Actuators_images/338ad75f8eae9d0b729cfe28525b5cb0ec2f560111205068b3dc82fd5458c629.jpg)  
Figure 19. Stroke results of experiment and simulation. Figure 19. Stroke results of experiment and simulation.

![](P6_Wang_2023_Actuators_images/7ad64a7d830d74f0632d68b1c771b3e6ad738f23854fa19673f30a3a361601cb.jpg)  
(a)

![](P6_Wang_2023_Actuators_images/7b4094c43556ee6a1e4a725c3e09b1ab5e152853be6e8267958e14f97729bf28.jpg)

![](P6_Wang_2023_Actuators_images/8303a54b354c1c92e09ab99d8ad903dd636f6b2cd6a8a418e925403c47a013d7.jpg)  
(b)  
igure 20. Acceleration results of experiment and simulation: (a) the main body and (b) the foot. Figure 20. Acceleration results of experiment and simulation: (a) the main body and (b) the foot.

## 4. Conclusions

This paper presents the explicit modeling of a reusable vehicle at the vertical land ing stage wherein the discrete-impulse-based state transition approach is employed to characterize the intrinsic nonlinear coupling effect between the landing impact and the crushing-type buffering. In particular, a 3D multi-impact model is constructed to feature the stick and slip stages of the foot–ground collision. An experiment-guided buffering model is established to depict the crushing behaviors of the multistage aluminum honeycomb element mounted in the landing gear. The evolution of the reusable vehicle’s crucial states including the trajectory of the CoM, body attitude, as well as internal forces can be predicted by using derived explicit models in contact-rich scenarios. Analytical models with an elaborately designed state transition regime are verified via both simulation and experiments involving the 20 cm freefalling of a scaled reusable vehicle prototype. Specifically, in the foot–ground impact section, the prediction percentage errors of the impact force and the buffering force in the steady values are 9.76% and 11.40%, respectively. When it comes to the peak values, these percentage errors are 9.9% and 19.72%, respectively. In the buffering section, the prediction percentage error of the stroke displacements in the steady state is 0.28%. Eventually, the presented theoretical work provides a potential analytical tool not only to shed light on the dynamical behavior of reusable vehicles with legged landing gear in complex environments, but also guide the design and optimization of the landing gear mechanism.

Author Contributions: Conceptualization, H.Y. and H. $. \mathrm { G } . \ ;$ methodology, H.Y. and $\mathrm { Y . } W . ;$ software, Y.W.; validation, Z.Y., B.T. and $\mathrm { J . X . ; }$ formal analysis, Y.W.; investigation, Y.W. and J.X.; resources, H.Y. and H.G.; data curation, Y.W., Z.Y. and B.T.; writing—original draft preparation, Y.W.; writing— review and editing, H.Y.; visualization, H.Y.; supervision, H.Y. and H.G.; project administration, H.Y. and H.G.; funding acquisition, H.Y. and H.G. All authors have read and agreed to the published version of the manuscript.

Funding: This research received no external funding.

Data Availability Statement: Not applicable.

Conflicts of Interest: The authors declare no conflict of interest.

## Nomenclature

<table><tr><td>Z, Y, X</td><td>The geodetic coordinate system</td></tr><tr><td> $z^0,y^0,x^0$ </td><td>The main body&#x27;s initial companion coordinate system</td></tr><tr><td> $z^1,y^1,x^1$ </td><td>The main body&#x27;s companion coordinate system</td></tr><tr><td> $z_j,y_j,x_j$ </td><td>The coordinate system of the impact between the foot i and the ground</td></tr><tr><td>z, y, x</td><td>The displacement of the z, y, x visual spring of the foot-ground impact or the coordinate of the foot-ground impact (mm)</td></tr><tr><td>n, w, u</td><td>The coordinate of the main pillar</td></tr><tr><td> $\theta_k$ </td><td>k ∈ [1, 3], respectively, represents the rotation angle of each coordinate axis (°)</td></tr><tr><td> $m_1$ </td><td>The mass of the main body (kg)</td></tr><tr><td> $m_{2i}$ </td><td>The mass of the foot i (kg)</td></tr><tr><td> $q^i$ </td><td>The impact point between the foot i and the ground</td></tr><tr><td> $p^i$ </td><td>The origin of the coordinate of the main pillar i</td></tr><tr><td> $E_{bi},F_{bi},I_{bi}$ </td><td>The buffer energy, force, and impulse of leg i, respectively (J, N, N·s)</td></tr><tr><td> $E_{zsi},F_{zsi},I_{zsi}$ </td><td>The energy, force, and impulse of the normal spring of the foot-ground impact (J, N, N·s)</td></tr><tr><td> $E_{tan}$ </td><td>The elastic energy of the tangential springs (J)</td></tr><tr><td> $v_{zi}$ </td><td>The normal velocity of the foot i (m/s)</td></tr><tr><td> $v_{bi}$ </td><td>The buffering velocity of leg i (m/s)</td></tr><tr><td> $V_{tan}$ </td><td>The tangential velocity of the touchdown foot (m/s)</td></tr><tr><td> $V_s$ </td><td>The slipping velocity of the touchdown foot (m/s)</td></tr><tr><td> $Z_{fi}$ </td><td>The normal displacement of the foot i (m)</td></tr><tr><td> $F_{li}$ </td><td>The transverse force exerted on the main body by the touchdown foot i (N)</td></tr></table>

Indicator of the x and y virtual spring states; 1 means the spring is compressed $\alpha , \beta$ Otherwise, it will be set as −1 $I _ { z \mathrm { d } }$ The normal damping impulse of the foot–ground impact $\left( \mathsf { N } { \cdot } \mathsf { s } \right)$ $\theta _ { b i }$ The angle between main pillar i axis and main body axis (<sup>◦</sup>) $\theta _ { a i }$ The angle between auxiliary pillar i axis and main body axis (<sup>◦</sup>) $h$ The relative lateral distance of the auxiliary strut (m) The longitudinal distance from the center of mass of the main body to the main $H _ { 1 }$ pillar (m) $H _ { 2 }$ The longitudinal distance from main strut to auxiliary pillar (m) $R$ The radius of the body (m) $x _ { \mathrm { b } }$ The stroke of the buffer The stiffness coefficients of elastic and plastic section of the two-stage $k _ { \mathrm { b 1 } } , k _ { \mathrm { b 2 } } , k _ { \mathrm { b 3 } } , k _ { \mathrm { b 4 } }$ aluminum honeycomb $L _ { h 0 }$ The initial length of the main pillar (m) $L _ { b 0 }$ The maximum stroke of the buffer device (m) $L _ { a 0 }$ The initial length of the auxiliary pillar (m) $x _ { L 1 }$ The elastic section length of the primary aluminum honeycomb (mm) $x _ { L 2 }$ The length of primary aluminum honeycomb (mm) The length from the initial buffer point to the elastic section of the secondary $x _ { L 3 }$ aluminum honeycomb (mm) $x _ { L 4 }$ The length of two stages of aluminum honeycomb (mm) $k$ The coefficient of stiffness of the normal spring $k _ { \mathrm { t a n } }$ The coefficient of stiffness of the tangential spring $\mu$ The coefficient of friction $\gamma$ 1 minus the coefficient of restitution $\chi$ The coefficient of damping of foot–ground impact $D _ { b }$ The coefficient of damping of structure of the landing gear $\mathrm { H } _ { \mathrm { h e i g h t } }$ Free-falling height (m)

## References

1. Zhou, H.; Wang, X.; Wang, Y.; Zhan, J.; Zhang, J. Research on a coupler with arc surface contact and its effect on a train collision. J. Rail Rapid Transit 2023, 237, 479–489. [CrossRef]

2. Zhou, H.; Wang, Y.; Wang, X.; Zhan, J.; Zhang, J. Influence of the coupler and buffer device on the train collision safety. J. Rail Rapid Transit 2023, 237, 385–393.

3. Su, Y.; Hou, X.; Li, L.; Cao, G.; Chen, X.; Jin, T.; Jiang, S.; Li, M. Study on impact energy absorption and adhesion of biomimetic buffer system for space robots. Adv. Space Res. 2020, 65, 1353–1366. [CrossRef]

4. Yin, K.; Sun, Q.; Gao, F.; Zhou, F. Lunar surface soft-landing analysis of a novel six-legged mobile lander with repetitive landing capacity. J. Mech. Eng. Sci. 2022, 236, 1214–1233.

5. Hou, W.; Hao, Y.; Wang, C.; Chen, L.; Li, G.; Zhao, B.; Wang, H.; Wei, Q.; Xu, S.; Feng, K.; et al. Theoretical and experimental investigations on high-precision micro-low gravity simulation technology for lunar mobile vehicle. Sensors 2023, 23, 3458.

6. Lin, Q.; Ren, J. Investigation on the horizontal landing velocity and pitch angle impact on the soft-landing dynamic characteristics. Int. J. Aerosp. Eng. 2022, 16, 3277581. [CrossRef]

7. Yin, K.; Qi, C.; Gao, Y.; Sun, Q.; Gao, F. Landing control method of a lightweight four-legged landing and walking robot. Front. Mech. Eng. 2022, 17, 51.

8. Zhang, Z.Q.; Chen, D.S.; Chen, K.W. Analysis and comparison of three leg models for bionic locust Robot based on landing buffering performance. Technol. Sci. 2016, 59, 1413–1427.

9. Chen, D.S.; Zhang, Z.Q.; Chen, K.W. Dynamic model and performance analysis of landing buffer for bionic locust mechanism. Acta Mech Sin. 2016, 32, 551–565.

10. Ji, S.; Liang, S. DEM-FEM-MBD coupling analysis of landing process of lunar lander considering landing mode and buffering mechanism. Adv. Space Res. 2021, 68, 1627–1643.

11. Ding, J.; Liu, X.; Dong, Y.; Wang, C. Stability analysis of mars soft landing under uncertain landing conditions and two landing strategies. Aircr. Eng. Aerosp. Technol. 2022, 94, 1883–1891.

12. Yu, H.; Tian, B.; Yan, Z.; Gao, H.; Zhang, H.; Wu, H.; Wang, Y.; Shi, Y.; Deng, Z. Watt linkage-based legged deployable landing mechanism for reusable launch vehicle: Principle, prototype design, and experimental validation. Engineering 2023, 20, 120–133. [CrossRef]

13. Aghili, F. Modeling and analysis of multiple impacts in multibody systems under unilateral and bilateral constrains based on linear projection operators. Multibody Syst. Dyn. 2019, 46, 41–62.

14. Natsiavas, S.; Passas, P.; Paraskevopoulos, E. A time-stepping method for multibody system with frictional impacts based on a return map and boundary layer theory. Int. J. Non Linear Mech. 2021, 131, 103683. [CrossRef]

15. Lei, B.; Zhang, M.; Lin, H.; Nie, H. Optimization design containing dimension and buffer parameters of landing legs for reusable landing vehicle. Chin. J. Aeronaut. 2022, 35, 234–249.

16. Dong, Y.; Ding, J.; Wang, C.; Wang, H.; Liu, X. Soft landing stability analysis of a Mars Lander under uncertain terrain. Chin. J. Aeronaut. 2022, 35, 377–388. [CrossRef]

17. Arailopoulos, A.; Giagopoulos, D. Nonlinear constitutive force model selection, update and uncertainty quantification for periodically sequential impact applications. Nonlinear Dyn. 2020, 99, 2623–2646.

18. Poursina, A.-M.; Nikravesh, P.-E. Optimal damping coefficient for a class of continuous contact models. Multibody Syst. Dyn. 2020, 50, 169–188.

19. Shen, Y.; Kuang, Y.; Wang, W.; Zhao, Y.; Yang, J.; Tian, A. Frictional impact analysis of an elastoplastic multi-link robotic system using a multi-timescale modelling approach. Nonlinear Dyn. 2019, 98, 1999–2018.

20. Wang, H.; He, T.; Wang, C. A comprehensive performance optimization method for the honeycomb buffer of a legged-type lander. Aircr. Eng. Aerosp. Technol. 2021, 93, 821–831.

21. Xie, S.; Du, X.; Zhou, H.; Wang, J.; Chen, P. Crashworthiness of Nomex honeycomb-filled anti-climbing energy absorbing devices. Int. J. Crashworthiness 2021, 26, 121–132. [CrossRef]

22. Zhou, D.; Wang, X.; Zheng, Q.; Fu, T.; Wu, M.; Sun, X. A nonlinear occupant-restraint system model for human injuries caused by vertical impact. Nonlinear Dyn. 2021, 105, 3093–3115. [CrossRef]

23. Yuan, Q.; Chen, H.; Nie, H.; Zheng, G.; Wang, C.; Hao, L. Soft-landing dynamic analysis of a manned lunar lander em-ploying energy absorption materials of carbon nanotube buckypaper. Materials 2021, 14, 6202. [CrossRef]

24. Zhou, J.; Jia, S.; Qian, J.; Chen, M.; Chen, J. Improving the buffer energy absorption characteristics of movable lander-numerical and experimental studies. Materials 2020, 13, 3340. [CrossRef] [PubMed]

25. Zhou, J.; Ma, H.; Jia, S.; Tian, S. Mechanical properties of multilayer combined gradient cellular structure and its application in the WLL. Heliyon 2023, 9, e14825. [CrossRef] [PubMed]

26. Jia, Y.B. Three-dimensional impact: Energy-based modeling of tangential compliance. Int. J. Robot. Res. 2013, 32, 56–83. [CrossRef]

27. Jia, Y.B.; Mason, M.-T.; Erdmann, M.-A. Multiple impacts: A state transition diagram approach. Int. J. Robot. Res. 2013, 32, 84–114. [CrossRef]

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to people or property resulting from any ideas, methods, instructions or products referred to in the content.