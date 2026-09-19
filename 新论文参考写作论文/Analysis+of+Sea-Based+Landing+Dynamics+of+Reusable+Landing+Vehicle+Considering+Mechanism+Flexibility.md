# Analysis of Sea-Based Landing Dynamics of Reusable Landing Vehicle Considering Mechanism Flexibility 

YANG Shaofei ${ }^{1}$, ZHANG Ming ${ }^{1,2^{*}}$, RUAN Shuang ${ }^{3}$, LEI Bo ${ }^{1}$<br>1. State Key Laboratory of Mechanics and Control for Aerospace Structures, Nanjing University of Aeronautics and Astronautics, Nanjing 210016, P. R. China; 2. Key Laboratory of Fundamental Science for National Defense-Advanced Design Technology of Flight Vehicle, Nanjing University of Aeronautics and Astronautics, Nanjing 210016, P. R. China; 3. System Design Institute of Hubei Aerospace Technology Academy, Wuhan, 430040, P. R. China

(Received 6 November 2025; revised 27 January 2026; accepted 28 March 2026)


#### Abstract

Vertical landing and recovery of a launch vehicle at sea can further reduce the launch cost of commercial space-flight, so this paper investigates the issue of reusable launch vehicle landing at sea. A vehicle landing dynamics model considering mechanism flexibility is established, and vehicle drop tests under various operating conditions are conducted. By comparing the vehicle drop test, the simulations of the dynamics model are consistent with test results, and the vehicle landing dynamics model considering the landing mechanism flexibility can simulate the vertical landing process of the vehicle more effectively than the rigid body dynamics model, which is more meaningful to guide the design of the reusable vehicle landing mechanism. Based on the vehicle landing dynamics model, a deck motion model and wind disturbance model are added to simulate the vehicle vertical landing dynamics at sea. The simulation results show that the sea landing causes the peak acceleration response of the vehicle, the main strut load and the buffer compression stroke to become larger, and there is a significant decrease in the landing stability of the vehicle.


Key words: reusable landing vehicle; landing dynamics; drop test; rigid-flexible coupling model; sea-based landing
CLC number : V44 Document code : A Article ID : 1005-1120(2026)02-0238-13

## 0 Introduction

The expended first and second stages of traditional multistage rockets suffer impact damage upon uncontrolled terrestrial impact, incurring prohibitively high refurbishment costs. Effective recovery of launch vehicle stages presents a critical pathway to substantially reduce spacecraft launch expenditures ${ }^{[1]}$. Recent successes in booster recovery- $\mathrm{Ex}^{-}$ emplified by SpaceX' s Falcon series ${ }^{[2]}$, Starship Super Heavy boosters ${ }^{[3]}$ have catalyzed renewed momentum in reusable launch vehicle (RLV) $\mathrm{de}^{-}$ velopment.

Concurrently, China's space sector has entered a phase of accelerated advancement, wherein reusable launch technology constitutes a strategic research priority. Precision vertical soft landing represents a foundational enabling technology for RLV reusability ${ }^{[4]}$. Within this paradigm, landing impact attenuation systems perform the essential functions of mitigating impact loads and ensuring airframe stabilization. However, at present, reusable rockets in China have not been successfully recovered, and there is still a long time for China's RLV technology ${ }^{[5]}$.

Multiple Chinese aerospace institutions have initiated research efforts and experimental campaigns on landing gear systems, predominantly adopting deployable leg-type configurations as primary recovery mechanisms for vertical rocket landings. Consequently, investigating the dynamic response of landing legs during the recycling process

[^0]remains imperative for advancing vertical recovery capabilities.

Lei et al. ${ }^{[6]}$ designed a two-stage pneumatic-aluminum honeycomb shock absorber for a RLV and established a corresponding rigid-body landing $\mathrm{dy}^{-}$ namics model. Yue et al. ${ }^{[7]}$ utilized a multidisciplinary optimization approach to optimize the design parameters of a RLV shock absorber and analyzed its performance. Tian et al. ${ }^{[8]}$ designed a novel fourlink landing gear through a single-degree-of-freedom topological scheme and conducted limit landing simulations using a rigid-body model. Lei et al. ${ }^{[9]}$ performed multidisciplinary optimization on the geometric parameters of RLV landing leg mechanisms and shock absorber parameters, followed by prototype landing tests on the optimized legs. Blue Origin designed a six-legged landing gear structure ${ }^{[10]}$ to mitigate the impact of single-leg failure. And the New Glenn rocket successfully completed the sea recovery mission ${ }^{[11]}$. The landing legs of lunar landers share similarities with RLV attenuation mechanisms, making research on lunar lander legs instructive. Liang et al. ${ }^{[12]}$ employed nonlinear finite element analysis with a cap drucker-prager lunar soil model to simulate the landing impact of a lunar lander. Chen et al. ${ }^{[13]}$ investigated the influence of various parameters on the lunar lander landing process.

Literature review shows that research on RLVs primarily focuses on terrestrial landing processes. However, studies concerning vertical landing recovery at sea remain limited. Unlike terrestrial platforms, sea-based platforms, such as barges, possess constrained deck surface area, imposing stringent requirements on landing precision. Vertical landing on the ocean surface presents additional challenges. It demands stricter vehicle attitude control under dynamic conditions, while complex sea states including wind, waves, and vessel motion pose significant risks to landing stability and recovery success. However, sea-based recovery offers distinct operational advantages. Performing landings on a sea-based platform obviates the need for a return-tolaunch-site trajectory, thereby conserving propellant and substantially reducing associated launch costs ${ }^{[14]}$. Therefore, the development of reliable seabased landing and recovery technology represents a critical strategic pathway for enhancing cost efficiency within the commercial aerospace sector ${ }^{[15]}$.

Given this context, this study designs a dedicated landing mechanism for RLVs. A coupled rigidflexible dynamics model incorporating the structural flexibility of landing legs is established. Furthermore, a specialized RLV drop test is constructed to validate the accuracy of the landing dynamics $\bmod ^{-}$ el. Leveraging the validated model, sea-landing simulations are subsequently performed. The simulations specifically investigate the technical feasibility of utilizing the designed mechanism to achieve stable vertical recovery for RLVs operating under marine conditions.

## 1 Flexible Multibody Dynamics Modeling of Reusable Launch Vehicle Landing Mechanisms

An inverted four-leg landing mechanism is designed in this paper, as shown in Fig. 1 and Fig.2. The mechanism is mainly composed of the main support struct, pneumatic shell, auxiliary beam, foot pad and buffer. The structure of the main support struct is shown in Fig.2, which is mainly composed of three telescopic sleeves and locking mechanism between sleeves. During launch, the main support strut and buffer are enclosed in a pneumatic housing to reduce the aerodynamic drag of the vehicle during ascent. Before the rocket lands vertically, the telescopic sleeve is fully extended, and the locking mechanism is in a locked state to connect three sleeves as a whole. During landing, foot pads make direct contact with the ground and rely on buffers to absorb energy. The design index of the landing im-

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-02.jpg?height=343&width=660&top_left_y=2414&top_left_x=1163)
Fig. 1 Overall structure of the four-leg landing mechanism

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-03.jpg?height=140&width=636&top_left_y=352&top_left_x=317)
Fig. 2 Main support strut

pact of the landing mechanism is as follows: The peak vertical acceleration of the rocket is less than $4 g$; main support strut load less than $1.8 \times 10^{5} \mathrm{~N}$; maximum stroke of the buffer is 185 mm.

## 1. 1 Force analysis of the landing attenuation mechanism

## 1. 1. 1 Dynamic equations for the buffer pillar

The oleo-pneumatic shocker with a single air cavity is selected, whose force can be expressed as

$$
\begin{equation*}
F_{1}=F_{\mathrm{s}}+F_{\mathrm{a}}+F_{\mathrm{h}}+F_{\mathrm{f}} \tag{1}
\end{equation*}
$$

where $F_{\mathrm{h}}$ is the oil damping force, $F_{1}$ the total force on the shock absorber, $F_{\mathrm{a}}$ the air spring force, $F_{\mathrm{f}}$ the friction force, and $F_{\mathrm{s}}$ the structural support force.

The oil damping force can be expressed as

$$
F_{\mathrm{h}}= \begin{cases}\frac{\rho_{\mathrm{o}} A_{\mathrm{h}}^{3} \dot{S}_{\mathrm{a}}^{2}}{2 C_{\mathrm{d}}^{2} A_{+}^{2}} & \dot{S}_{\mathrm{a}} \geqslant 0  \tag{2}\\ -\frac{\rho_{\mathrm{o}} A_{\mathrm{h}}^{3} \dot{S}_{\mathrm{a}}^{2}}{2 C_{\mathrm{d}}^{2} A_{-}^{2}} & \dot{S}_{\mathrm{a}}<0\end{cases}
$$

where $\rho_{\mathrm{o}}$ is the density of the oil, $A_{\mathrm{h}}$ the compressed oil area, $A_{+}$the orifice of the compression stroke, $A_{-}$the orifice of the extension stroke, $C_{\mathrm{d}}$ the coefficient of contraction, and $S_{\mathrm{a}}$ the stroke of the piston.

The air spring force can be expressed as

$$
\begin{equation*}
F_{\mathrm{a}}=A_{\mathrm{a}}\left[P_{0}\left(\frac{1}{1-\left(1 / H_{0}\right) S_{\mathrm{a}}}\right)^{\gamma}-P_{\mathrm{atm}}\right] \tag{3}
\end{equation*}
$$

where $H_{0}$ is the initial air chamber height, $P_{0}$ the initial air pressure, $P_{\text {atm }}$ the atmospheric pressure, $A_{\mathrm{a}}$ the area of compressed air, and $\gamma$ the gas change index.

The friction force inside the buffer mainly considers the friction caused by the piston seal ring, and its magnitude is

$$
\begin{equation*}
F_{\mathrm{f}}=\frac{f \pi D_{\mathrm{o}} D_{i}}{1-\mu_{1}}\left[0.2 \pi \lambda l_{\mathrm{r}}+\mu_{1}\left(1+\mu_{1}\right) \Delta_{\mathrm{r}}\right] \tag{4}
\end{equation*}
$$

where $f$ is the friction coefficient between envelope and sealing ring, $D_{\circ}$ the outer diameter of sealing ring, $D_{i}$ the sectional diameter of sealing ring, $\lambda$ the precompression of sealing ring, $l_{\mathrm{r}}$ the elastic modulus of sealing ring, $\mu_{1}$ the Poisson ratio, and $\Delta_{\mathrm{r}}$ the precompression of sealing ring.

In the state of full extension and full compres ${ }^{-}$ sion of the buffer, the internal structure constrains the stroke of the piston, the structural support force can be expressed as

$$
F_{\mathrm{s}}= \begin{cases}K_{\mathrm{s}} S_{\mathrm{a}} & S_{\mathrm{a}}<S_{\mathrm{a} 0}  \tag{5}\\ 0 & S_{\mathrm{a} 0} \leqslant S_{\mathrm{a}} \leqslant S_{\mathrm{a} \max } \\ K_{\mathrm{S}}\left(S_{\mathrm{a}}-S_{\mathrm{a} \max }\right) & S_{\mathrm{a}}>S_{\mathrm{a} \max }\end{cases}
$$

where $S_{\mathrm{a} 0}$ is the initial stroke of the piston, $S_{\mathrm{a} \text { max }}$ the maximum stroke of the piston, and $K_{\mathrm{S}}$ the contact stiffness between the piston and the envelope.

### 1.1.2 Contact force model between footpad and ground

The impact function model and the coulomb friction model are used to monitor and solve the interaction force between the footpad and the ground.

$$
\begin{equation*}
\text { impact }=k \cdot g^{r}+\operatorname{STEP}\left(g, 0,0, d_{\max }, c_{\max }\right) \cdot \frac{\mathrm{d} g}{\mathrm{~d} t} \tag{6}
\end{equation*}
$$

where $g$ is the penetration depth, $k$ the spring stiffness, and $r$ the shape index; STEP refers to the step function; $d_{\text {max }}$ is the maximum allowable penetration depth, and $c_{\text {max }}$ the maximum damping value applied at maximum penetration depth.

Coulomb friction force is shown in Eq. (7) , and its function characteristic is illustrated in Fig.3.

$$
\left\{\begin{array}{l}
F_{\text {contactf }}=\mu \cdot \text { impact }  \tag{7}\\
\mu= \begin{cases}0 & v=0 \\
-\mu_{\mathrm{d}} & v=v_{\mathrm{d}} \\
-\mu_{\mathrm{s}} & v=v_{\mathrm{s}} \\
\mu_{\mathrm{d}} & v=-v_{\mathrm{d}} \\
\mu_{\mathrm{d}} & v=-v_{\mathrm{s}} \\
-\operatorname{sign}(v) \cdot \mu_{\mathrm{d}} & |v|>v_{\mathrm{d}} \\
-\operatorname{STEP}\left(|v|, v_{\mathrm{d}}, \mu_{\mathrm{d}}, v_{\mathrm{s}}, \mu_{\mathrm{s}}\right) \cdot \operatorname{sign}(v) & v_{\mathrm{d}}>|v|>v_{\mathrm{s}} \\
\operatorname{STEP}\left(v, v_{\mathrm{d}},-\mu_{\mathrm{s}},-v_{\mathrm{s}}, \mu_{\mathrm{s}}\right) & -v_{\mathrm{s}}<v<v_{\mathrm{s}}\end{cases}
\end{array}\right.
$$

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-03.jpg?height=415&width=457&top_left_y=2344&top_left_x=1263)
Fig. 3 Friction coefficient curve

where $\mu$ is the friction coefficient, $\mu_{\mathrm{s}}$ the static friction coefficient, $\mu_{\mathrm{d}}$ the dynamic friction coefficient, $v_{\mathrm{s}}$ the static transition velocity, and $v_{\mathrm{d}}$ the dynamic transition velocity.

## 1. 2 Multi-body dynamics of flexible bodies

In the flexible multibody dynamics model, the position of any point on a flexible body changes continuously over time. Consequently, elastic coordinate systems must be employed to describe points on the flexible body, meaning that the motion of any arbitrary point on the flexible body comprises the rigid-body motion of the moving coordinate system combined with elastic deformation. For an arbitrary point $P$ on the flexible body, its position vector is given by ${ }^{[16]}$

$$
\begin{equation*}
\boldsymbol{r}=\boldsymbol{r}_{0}+\boldsymbol{A}_{B G}\left(\boldsymbol{s}_{P}+\boldsymbol{u}_{P}\right) \tag{8}
\end{equation*}
$$

where $r$ is the spatial position vector of point $P$ in the inertial coordinate system, $\boldsymbol{r}_{0}$ the spatial position vector of the floating frame origin in the inertial coordinate system, $\boldsymbol{A}_{B G}$ the direction cosine matrix transforming from floating frame $B$ to inertial frame $G$, $\boldsymbol{s}_{P}$ the spatial vector of point $P$ in the floating frame under undeformed conditions, and $\boldsymbol{u}_{P}$ the relative deformation vector of the flexible body.

Thus, the velocity vector and acceleration vector of an arbitrary point $P$ on the flexible body are given by Eq.(9).

$$
\left\{\begin{array}{l}
\dot{r}=\dot{r}_{0}+\dot{A}\left(s_{P}+u_{P}\right)+A \Phi_{P} \dot{q}_{\mathrm{f}}  \tag{9}\\
\ddot{r}=\ddot{r}_{0}+\ddot{A}\left(s_{P}+u_{P}\right)+2 \dot{A} \Phi_{P} \dot{q}_{\mathrm{f}}+A \Phi_{P} \ddot{q}_{\mathrm{f}}
\end{array}\right.
$$

where $\boldsymbol{\Phi}_{P}$ is the assumed modes matrix satisfying RITZ vector requirements for point $P$ and $\boldsymbol{q}_{\mathrm{f}}$ the generalized coordinates of deformation.

The equations of motion for the flexible body are derived according to Lagrange's Eq.(10).

$$
\begin{align*}
& \boldsymbol{M} \ddot{\xi}+\dot{\boldsymbol{M}} \dot{\xi}-\frac{1}{2}\left(\frac{\partial \boldsymbol{M}}{\partial \xi} \dot{\xi}\right)^{\mathrm{T}} \dot{\xi}+\boldsymbol{K} \xi+f_{\mathrm{g}}+Z \dot{\xi}+ \\
& \quad\left(\frac{\partial \boldsymbol{\psi}}{\partial \xi}\right)^{\mathrm{T}} \lambda=\boldsymbol{Q} \tag{10}
\end{align*}
$$

where $\ddot{\xi}, \dot{\xi}, \xi$ correspond to the generalized coordinates of the flexible body and their first and second time derivatives, respectively; $\boldsymbol{M}$ is the mass $\mathrm{ma}^{-}$ trix and $\dot{\boldsymbol{M}}$ the time derivative of the mass matrix; $\boldsymbol{K}$ signifies the stiffness matrix, $\boldsymbol{f}_{\mathbf{g}}$ the generalized gravitational force, $Z$ the modal damping matrix. $\boldsymbol{\psi}$ corresponds to the constraint equations, $\lambda$ the $\mathrm{La}^{-}$ grange multipliers, and $\boldsymbol{Q}$ the generalized force vector.

### 1.3 Flexible body dynamics model of landing buffer mechanism

First, import the digital prototype of the landing mechanism design into Abaqus computer aided engineering (CAE) and partition the mesh for each component. Since the foot pad section is an irregular geometric shape and to improve the computational efficiency during contact collisions, the foot pad mesh is set to quadratic tetrahedral elements (C3D10), which is shown in Fig.4, while the remaining component meshes are set to eight-node linear hexahedral elements (C3D8R). Second, establish connection points and constraint conditions between the components. Third, import the processed mnf file into ADAMS to set up the dynamic model. The schematic diagram of the dynamic model is shown in Fig.5. Set up a rotational joint connection between the main support struct and the rocket. Set up a cylindrical joint connection between the main support struct and the buffer, and add buffer pillar

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-04.jpg?height=387&width=447&top_left_y=1711&top_left_x=1268)
Fig. 4 Finite element model of landing leg

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-04.jpg?height=578&width=601&top_left_y=2179&top_left_x=1189)
Fig. 5 Landing dynamics modeling block diagram

forces according to Eq. (1). Set up a rotational joint connection between the buffer and the footpad, and add contact forces between the footpad and the ground according to Eqs.(6-7). Set up a spherical joint connection between the auxiliary beam and the rocket. Set up a fixed joint connection between the auxiliary beam and the footpad.

To optimize computational efficiency while preserving simulation fidelity, the following model reductions are proposed:
(1) The locked three-section telescopic sleeve assembly is reduced to a monolithic rigid body. Local dimensional adjustments are implemented to approximate the mass distribution and inertial properties of the physical prototype, ensuring mechanical equivalence under quasi-static conditions.
(2) Given its negligible contribution to struc- tural dynamics during landing events, the aerodynamic shell is excluded from the model. This component, composed of lightweight carbon fiber composite material, experiences minimal impact loading and does not influence the system's rigid-body kinematics. Its removal reduces model complexity and enhances computational throughput without compromising simulation validity.

## 2 Drop Test of the Rocket with Landing Mechanism

To validate the effectiveness of the established dynamic model for the landing mechanism's flexible body, a rocket with the landing mechanism assembly is assembled, and a drop test is conducted. The parameters of test are shown in Table 1. And the critical landing conditions are shown in Fig.6.

Table 1 Critical landing conditions
| Landing parameter | Condition 1 | Condition 2 | Condition 3 |
| :--- | :--- | :--- | :--- |
| Rocket weight/t | 5.2 | 5.2 | 5.2 |
| Pitch angle/( ${ }^{\circ}$ ) | 0 | 3 | 3 |
| Vertical touchdown velocity/ $\left(\mathrm{m} \cdot \mathrm{s}^{-1}\right)$ | 2 | 2 | 2 |
| Horizontal touchdown velocity/ $\left(\mathrm{m} \cdot \mathrm{s}^{-1}\right)$ | 0 | 0 | 0 |
| Landing form | Simultaneously landing of all legs | 1-2-1 | 2-2 |
| Ground form | Cement floor | Cement floor | Cement floor |


![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-05.jpg?height=461&width=634&top_left_y=1776&top_left_x=317)
Fig. 6 Schematic diagram of landing form

In reusable rocket recovery operations, vertical deceleration is achieved through engine throttling while attitude control is governed by grid-fin actuators. This study employs a drop-test methodology focused on simulating the free-fall phase to evaluate landing gear performance. During testing, critical parameters including vertical acceleration, buffer stroke displacement and main structural load are instrumentally recorded upon ground impact. The $\mathrm{ex}^{-}$ perimental setup features a factory bridge crane elevating the test article to predetermined altitude. A 10 t electromechanical decoupler, as shown in Fig.7, remotely triggered via tether release, facilitates instantaneous separation between the crane hook and test vehicle. This configuration achieves terminal velocities emulating actual landing dynamics. Differential leg-height adjustment enables controlled simulation of asymmetric touchdown scenarios, including but not limited to: Single-leg-first (1-2-1 condition) and Dual-leg-synchronous (2-2 condition). According to the law of conservation of energy, the $\mathrm{re}^{-}$ quired height of the rocket from the ground to achieve the specified vertical velocity at the time of arrival can be calculated as

$$
\begin{equation*}
H=\frac{v_{t}}{2 g} \tag{11}
\end{equation*}
$$

where $v_{\mathrm{t}}$ is the target vertical velocity at impact and $g$ gravitational acceleration $\left(9.81 \mathrm{~m} / \mathrm{s}^{2}\right)$.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-06.jpg?height=385&width=443&top_left_y=354&top_left_x=415)
Fig. 7 Principle of vehicle drop test

The experimental measurement system consists of four WPS-S cable displacement sensors, one 1A106 piezoelectric accelerometer and several strain gauges. Four cable displacement sensors are installed between the outer tube and the piston rod of the hydraulic buffer to measure the compression stroke of the buffer. A unidirectional accelerometer is installed at the center of the rocket's top to measure the acceleration in the direction of the rocket $\mathrm{ax}^{-}$ is during landing. During the rocket's landing impact process, it is necessary to measure the load on the main support column. Using tension and compression load sensors directly will inevitably damage the integrity of the buffer support column and increase the complexity of the mechanism. Therefore, in this experimental plan, strain gauges are used to measure the strain of the corresponding structure. Three strain gauges are uniformly distributed at 120 degree intervals and pasted at the same height at a certain position in the middle of each main buffer support column. The DH8902 dynamic signal measurement and analysis system from Donghua Company is used for data collection. The installation positions of each sensor are shown in Fig.8.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-06.jpg?height=459&width=778&top_left_y=352&top_left_x=1102)
Fig. 8 General installation diagram of sensors

## 3 Comparison of Simulation and Test Results

When the rocket lands with 1-2-1 condition, the main support struct that first touches the ground bears the maximum load, and the compression stroke of the buffer is also the largest. When the rocket all legs land at the same time, the load on the four main support columns and the compression stroke of the buffer are the same. Therefore, by analyzing the measurement results of the No. 1 landing leg (the landing leg that first touches the ground) , the difference between the dynamic simulation and experimental results can be compared to verify the effectiveness of the dynamic model.

From Table 2, it can be seen that under the condition of landing with four legs simultaneously, the vertical acceleration peak of the vehicle is the maximum, with a flexible body model of $3.06 g$ and a relative experimental error of 5.15\%, while the rigid body model is $3.26 g$ with a relative experimental error of 11.2\%. Under the landing condition of

Table 2 Comparison of dynamic simulation and test results
| Condition | Data type | Flexible body model result (Error/\%) | Rigid body model result (Error/\%) | Test result |
| :--- | :--- | :--- | :--- | :--- |
| Simultaneously landing of all legs | Peak vertical acceleration of the vehicle/ $\left(\mathrm{m} \cdot \mathrm{s}^{-2}\right)$ | $3.06 g$ (5.15) | $3.26 g$ (11.2) | $2.91 g$ |
|  | Maximum load of the main support strut / $10^{5} \mathrm{~N}$ | 1.061 (10.7) | 1.121 (11.3) | 0.988 |
|  | Maximum buffer stroke /mm | 93.2 (6.6) | 93.3 (6.5) | 99.8 |
| 1-2-1 | Peak vertical acceleration of the vehicle/ $\left(\mathrm{m} \cdot \mathrm{s}^{-2}\right)$ | $2.03 g$ (10.6) | $2.26 g$ (0.5) | $2.27 g$ |
|  | Maximum load of the main support strut $/ 10^{5} \mathrm{~N}$ | 1.141 (1) | 1.226 (10.7) | 0.115 |
|  | Maximum buffer stroke /mm | 121.5 (5) | 121.7 (4.9) | 127.9 |
| 2-2 | Peak vertical acceleration of the vehicle/ $\left(\mathrm{m} \cdot \mathrm{s}^{-2}\right)$ | $2.75 g$ (6.8) | $3.26 g$ (11.1) | $2.95 g$ |
|  | Maximum load of the main support strut $/ 10^{5} \mathrm{~N}$ | 1.106 (3.1) | 1.203 (10.5) | 1.141 |
|  | Maximum buffer stroke /mm | 114.0 (4.9) | 114.2 (4.8) | 119.9 |


1-2-1, the main support column bears the maximum load, with a flexible body model of $1.141 \times 10^{5} \mathrm{~N}$ and a relative experimental error of 1\%, while the rigid body model is $1.226 \times 10^{5} \mathrm{~N}$ with a relative $\mathrm{ex}^{-}$ perimental error of $10.7 \%$. At the same time, under the 1-2-1 landing condition, the compression stroke of the buffer is also the maximum, with a flexible body model of 121.5 mm and a relative experimental error of 5\%, while the rigid body model is 121.7 mm with a relative experimental error of 4.9\%.

From Figs.(9-11), it can be seen that the vertical acceleration of the rocket and the load on the main support column of the dynamic model undergo a sudden change at the moment of landing, while in the experiment, the change is relatively slow and accompanied by small vibrations. The main reason for this phenomenon is that rigid connections between components in the dynamic model lack the nonlinear contact between components. However, compared to the rigid body model, the flexible body model has flexible deformation and structural damping of the landing legs. The peak values of the vertical acceleration of the rocket and the load on the main support column are smaller and change more smoothly at the moment of contact with the ground, which is more consistent with the results of the drop shock test. During the landing process of the rocket, the gas in the buffer is compressed with a non-steadystate gas polytropic exponent, and the friction of the foot pad is different between dynamic simulation and experiment. Therefore, there are errors in the angle between the main support column of the landing leg and the rocket when the rocket stabilizes and

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-07.jpg?height=445&width=1631&top_left_y=1305&top_left_x=247)
Fig. 9 Vehicle impact response under simultaneously landing of all legs

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-07.jpg?height=958&width=1622&top_left_y=1811&top_left_x=252)
Fig. 11 Vehicle impact response under 2-2 condition

stops in the dynamic simulation and the experiment. Therefore, there is about a 10\% error in the compression stroke of the buffer when the rocket is balanced, which is considered reasonable.

## 4 Simulation of Vehicle Vertical Sea-Based Landing

When studying the problems of carrier-based aircraft and sea landing, the ship' s motion caused by wind and waves, i.e. deck motion, is usually encountered. Deck motion includes linear motion in three directions: Heave, sway, and surge, as well as rotational motion in three directions: Roll, pitch, and yaw. The direction of deck motion is shown in Fig.12. When studying the landing problem, the amplitude of the ship's sway, heave, and yaw motion is very small, and the impact on the landing is small. Therefore, only the pitch, roll and heave motion are usually considered ${ }^{[15-16]}$. Compared with carrierbased aircraft landing, during the landing process of the spacecraft, the recovery barge is not in a forward state ${ }^{[17]}$ and the carrier does not have the process of sliding along the deck, that is, the $x$ and $z \mathrm{di}^{-}$ rections are not distinguished on the horizontal plane ${ }^{[18]}$. Therefore, in the vertical landing simulation of the rocket on the sea, only the heave motion of the deck and the pitch motion in the direction of the rocket's tilt are considered.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-08.jpg?height=459&width=720&top_left_y=1976&top_left_x=273)
Fig. 12 Schematic diagram of the deck motion with 6 degree of freedoms

## 4. 1 Deck motion model based on power spectrum

In recent years, deck motion has been extensively studied both domestically and abroad. There are two common models for deck motion, one based on a deterministic model using trigonometric functions ${ }^{[19]}$ and the other based on a stochastic model using power spectra ${ }^{[20]}$. The second modeling method is more in line with actual ship motion ${ }^{[21]}$, so the stochastic model based on power spectra for deck motion modeling is adapted in this paper.

In the stochastic process theory, a stochastic process can be considered stationary when the trigger conditions of a random phenomenon do not go through significant changes for a certain period of time. During the vehicle landing at sea, the mass and moment of inertia of the recovery barge are large, and the landing process is short, so the $\mathrm{mo}^{-}$ tion of the recovery barge can be regarded as a stationary stochastic process. For this stationary stochastic process, the recovery barge' s heave displacement and pitch angle can be generated using white noise through a shaping filter ${ }^{[22]}$, as shown in Fig.13. Referring to the heave and pitch motion of the US Essex aircraft carrier in sea state $5^{[23]}$, the transfer function of the filter can be calculated as

$$
\frac{\Delta h}{\mathrm{WN}}=\frac{0.354 s(s+0.04)}{\left(s^{2}+0.16 s+0.4^{2}\right)\left(s^{2}+0.22 s+0.55^{2}\right)}
$$

$$
\begin{equation*}
\frac{\Delta \theta}{\mathrm{WN}}=\frac{0.00583 s}{\left(s^{2}+0.22 s+0.55^{2}\right)\left(s^{2}+0.384 s+0.64^{2}\right)} \tag{12}
\end{equation*}
$$

where WN denotes the white noise.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-08.jpg?height=385&width=615&top_left_y=2037&top_left_x=1184)
Fig. 13 Deck motion trajectory diagram

## 4. 2 Wind disturbance model of the vehicle at sea

During launch vehicle operation, the significantly larger dimensions of the rocket body compared to the landing legs necessitate calculating solely the aerodynamic forces acting on the rocket body
under crosswind conditions. This research employs the Euler equations to solve unsteady inviscid flow. Computational results demonstrate that employing the Euler equations yields minimal deviation from Navier-Stokes solutions while achieving high-precision aerodynamic force/moment coefficients. The method significantly enhances computational efficiency through accelerated convergence rates. The FlowCart solver within Cart3D software is utilized with central differencing scheme for Euler equation discretization and explicit temporal advancement via 4 order Runge-Kutta method. Finally, comprehensive rocket body flow field solution is obtained ${ }^{[24]}$.

The Euler equation ${ }^{[25]}$ has the form in

$$
\begin{equation*}
\frac{\partial \beta}{\partial t}+\frac{\partial \gamma}{\partial x}+\frac{\partial \boldsymbol{\Omega}}{\partial y}=0 \tag{14}
\end{equation*}
$$

where $\boldsymbol{\beta}$ is the conserved variable, while $\boldsymbol{\gamma}$ and $\boldsymbol{\Omega}$ denote fluxes.

$$
\beta=\left[\begin{array}{c}
\rho  \tag{15}\\
\rho u \\
\rho v \\
E
\end{array}\right], \gamma=\left[\begin{array}{c}
\rho u \\
\rho u^{2}+p \\
\rho u v \\
(E+p) v
\end{array}\right], \boldsymbol{\Omega}=\left[\begin{array}{c}
\rho v \\
\rho u v \\
\rho v^{2}+p \\
(E+p) v
\end{array}\right]
$$

where $u$ and $v$ are the velocities in the $x$ and $y$ direc $^{-}$ tions; $\rho$ is the fluid density, $p$ the fluid pressure, and $E$ the internal energy of the fluid. When solving the flow domain, its boundary is divided into two regions, namely

$$
\begin{equation*}
\Gamma=\Gamma_{\infty}+\Gamma_{\mathrm{B}} \tag{16}
\end{equation*}
$$

where $\Gamma_{\infty}$ represents the far-field boundary and $\Gamma_{\mathrm{B}}$ the body surface boundary. Assuming the free stream at infinity is undisturbed as

$$
\left\{\begin{array}{l}
\rho_{\infty}=1  \tag{17}\\
v_{\infty}=\left[\begin{array}{c}
M a_{\infty} \cdot \cos \alpha \\
M a_{\infty} \cdot \sin \alpha
\end{array}\right] \\
p_{\infty}=1
\end{array}\right.
$$

In the Eq.(14), $\rho_{\infty}$ and $p_{\infty}$ are the free-stream density and pressure, serving as non-dimensional parameters. $\boldsymbol{v}_{\infty}$ is the free-stream velocity, $M a_{\infty}$ the free-stream Mach number, and $\alpha$ the free-stream angle of attack. The aerodynamic force coefficients and moment coefficients of the rocket under 5-level crosswind (10 m/s) are computed using Cart3D, as shown in Fig.14.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-09.jpg?height=394&width=620&top_left_y=354&top_left_x=1182)
Fig. 14 Aerodynamic force and moment coefficient curves of rocket

The aerodynamic force and moment induced by crosswind are given by

$$
\left\{\begin{array}{l}
F=C_{\mathrm{F}} \cdot q_{\infty} \cdot S  \tag{18}\\
m=C_{m} \cdot q_{\infty} \cdot L \cdot S
\end{array}\right.
$$

where $F$ and $m$ denote the aerodynamic force and moment; $C_{\mathrm{F}}$ is the aerodynamic force coefficient, $C_{m}$ the moment coefficient, $q_{\infty}$ the dynamic pressure, and $L$ the reference length; $S$ corresponds to the reference area.

## 4. 3 Criteria for vehicle landing stability

During the vehicle landing at sea, the recovery barge experiences heave and sway motions due to the wave, which can cause excessive rocking of the landing process or even serious accidents such as capsizing. Therefore, the stability of rocket landing is crucial for its sea landing and recovery.

To determine the stability of rocket landing, the distance from the arrow's center of gravity to the stability boundary is used as the stability criterion. First, the adjacent pad centers are connected by a straight line, and a vertical plane passing through this line is set up. Four vertical planes generated by four pads are the stability boundaries in the rocket landing process, as shown in Fig.15.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-09.jpg?height=424&width=797&top_left_y=2340&top_left_x=1095)
Fig. 15 Stability boundary of the vehicle

Therefore, the quantitative criterion for landing stability is defined as the minimum distance from the horizontal projection of the rocket' s center of mass to the four stability boundary planes ${ }^{[26]}$, denoted as $D=\min \left(D_{1}, D_{2}, D_{3}, D_{4}\right)$. Here, $D_{1}$ can be expressed as

$$
\begin{gather*}
D_{1}=\frac{2 \sqrt{L_{D}\left(L_{D}-a_{1}\right)\left(L_{D}-a_{2}\right)\left(L_{D}-c\right)}}{c}  \tag{19}\\
L_{D}=\frac{1}{2}\left(a_{1}+a_{2}+c\right) \tag{20}
\end{gather*}
$$

The curves of the stability criterion obtained from landing simulations under three operational conditions in Chapter 3 are shown in Fig.16. From Fig.16, it can be seen that the stability of the rocket landing under the three conditions is good, with no risk of capsizing during land-based landing. Compared with the other two landing forms, the 1-2-1 landing form has the smallest stability margin, which means that the center of gravity of the rocket is closest to the stability boundary in this condition and is most likely to capsize. Therefore, the 1-2-1 landing condition is chosen for the sea vertical landing simulation of the rocket.

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-10.jpg?height=478&width=618&top_left_y=352&top_left_x=1182)
Fig. 16 Vehicle landing stability curves under three operating conditions

## 4. 4 Simulation of the vehicle sea-based landing under dangerous condition

Since the mass and moment of inertia of the recovery barge are far greater than those of the rocket, the influence of the rocket landing on the attitude of the recovery barge during the landing process is ignored. Based on the flexible-body model of the landing mechanism described earlier, a power spectrumbased deck motion model and a wind disturbance model based on Euler' s equations are added to simulate sea-based 1-2-1 landing. From Fig.17, it can be seen that due to the deck motion, the maximum

![](https://cdn.mathpix.com/cropped/f289ff48-7611-4373-9fac-201b727a2377-10.jpg?height=1046&width=1415&top_left_y=1720&top_left_x=357)
Fig. 17 Sea landing simulation results under 1-2-1 condition

load on the landing main strut of the rocket increases to $1.28 \times 10^{5} \mathrm{~N}$, which is $12.3 \%$ higher than that during land-based landing. At this time, the vertical acceleration of the rocket reaches a maximum of $2.36 g$, and the maximum compression stroke of the buffer reaches 137 mm , which is 12.8\% higher than that during land-based landing. At the same time, the deck motion significantly reduces the landing stability of the rocket, but the outward-folding landing mechanism designed in this study has high stability redundancy. Even when the deck motion is most severe, the distance between the center of mass of the rocket and the stability boundary is still 2.4 m, and there is no risk of capsizing.

## 5 Conclusions

(1) Compared to rigid-body models, the multibody dynamic model considering landing mechanism flexibility more accurately simulates rocket landing. In drop impact tests, prediction errors of the flexible-body model for the peak vertical acceleration of the rocket body, main strut loads, and buffer compression strokes (average 5\%-10\%) are significantly lower than those of the rigid-body $\bmod ^{-}$ el (average 10\%-12\%), aligning more closely with experimental results.
(2) Deck motion (heave and pitch) caused by waves on the sea recovery platform, combined with wind disturbance, exacerbates landing dynamic responses. Compared to land-based landings, peak vertical acceleration of the rocket body increases by 12.3\%. Main strut loads increase by 12.8\%. Buffer compression strokes increase by 12.8\%. Concurrently, the stability margin significantly decreases, with the minimum distance from the center of gravity to the stability boundary reduced to 2.4 m.
(3) The designed inverted four-leg landing mechanism maintains redundant stability even under extreme sea conditions (Sea state 5). Employing the most stability-challenging, 1-2-1 landing form (single leg first contact) , the minimum distance from the rocket body's center of gravity to the stability boundary remains 2.4 m, eliminating the risk of overturning.

## References

[1] LI Liqun, MA Chong, WANG Erliang. Overview on the current situation and future development of space launch technology at home and abroad[J]. Aerospace Shanghai (Chinese \& English), 2024, 41(2): 1-6, 170. (in Chinese)
[2] THOMAS D. SpaceX starships reusability revolution: Mitigating engine failure risks through advanced failure analysis[J]. Journal of Failure Analysis and Prevention, 2024, 24(4): 1501-1503.
[3] BAO Weimin. A review of reusable launch vehicle technology development[J]. Acta Aeronautica et Astronautica Sinica, 2023, 44(23): 629555. (in Chinese)
[4] XING C. The first vertical take-off and landing flight test of the Zhuqu-3 reusable rocket was successful[J]. International Space, 2024(2): 10-11.
[5] JIA Xuan. Unsuccessful recovery of Suzaku-3' s first flight into orbit, technical breakthrough[J]. China Economic Weekly, 2025, 23: 50-52. (in Chinese)
[6] LEI Bo, ZHANG Ming, YUE Shuai. Design and optimization of a crashworthy damper used for reusable launch vehicles[J]. Journal of Astronautics, 2019, 40 (9): 996-1005. (in Chinese)
[7] YUE Shuai, NIE Hong, ZHANG Ming, et al. Analysis on performance of a damper used for vertical landing reusable launch vehicle[J]. Journal of Astronautics, 2016, 37(6): 646-656. (in Chinese)
[8] TIAN Baolin, YU Haitao, GAO Haibo, et al. Configuration design and scale optimization of the support legs of a vertical take-off and landing vehicle[J]. Journal of Mechanical Engineering, 2021, 57(15): 33-44. (in Chinese)
[9] LEI B, ZHANG M, LIN H Y, et al. Optimization design containing dimension and buffer parameters of landing legs for reusable landing vehicle[J]. Chinese Journal of Aeronautics, 2022, 35(3): 234-249.
[10] ZHANG Xuesong, NEMO. New Glenn rocket with Blue Origin[J]. Satellite \& Network, 2017, 4: 6869. (in Chinese)
[11] ZHANG Chen. Rocket recycling adds "General" and "New Glenn" sends two stars to Mars[J]. Space $\mathrm{Ex}^{-}$ ploration, 2025, 12: 42-47. (in Chinese)
[12] LIANG Dongping, CHAI Hongyou, ZENG Fuming. Nonlinear finite element modeling and simulation for landing leg of lunar lander[J]. Journal of Beijing University of Aeronautics and Astronautics, 2013, 39(1): 11-15. (in Chinese)

[13] CHEN Jinbao, WAN Junlin, LI Lichun, et al. Analysis on the influencing factors of performance in lunar lander[ J ]. Journal of Astronautics, 2010, 31( 3 ) : 669-673. (in Chinese)
[14] LONG Xuedan, QU Jing, YANG Kai. Analysis on the maiden flight and the application prospect of falcon heavy[J]. Space International, 2018, 3: 16-22. (in Chinese)
[15] LI D G, ZHOU J. Another attempt to retrieve the Falcon-9 rocket[J]. Aerodynamic Missile Journal, 2016, 375(3):9-13, 22.
[16] KRISHNAN G L, SAJIKUMAR K S. Modelling and analysis of vertical landing reusable launch vehicle with spring damper[C]//Proceedings of the 10th National Conference on Recent Developments in Mechanical Engineering. Pune, India: AIP, 2023: 20-24.
[17] JIAO J L, CHEN Z W, CHEN Y M, et al. Numerical simulation of ship hydroelastic responses in 3D realistic ocean waves with occurrence of freak waves[J]. Journal of Fluids and Structures, 2026, 140: 104448.
[18] BEN Liangliang. The environmental disturbance influence and response analysis on approaching of ship-board aircraft[D]. Nanjing: Nanjing University of Aeronautics and Astronautics, 2013.
[19] WANG Y, LIU K, CHEN P Y, et al. Adaptive fuzzy fixed-time tracking control for maritime quadrotor UAV landing onto a moving USV with deck motion prediction[J]. Nonlinear Dynamics, 2025, 113(13): 16857-16876.
[20] MA Kun, ZHEN Ziyang, QIN Haiqun. Research on preview control based deck motion tracking control[J]. Electronics Optics \& Control, 2017, 24(11): 74-77, 99. (in Chinese)
[21] PENG Zheng. Research on carrier landing control technology of the large fixed-wing UAV[D]. Nanjing: Nanjing University of Aeronautics and Astronautics, 2020.
[22] ZHANG Yonghua. Research on deck motion modeling and deck motion compensation for carrier landing[D]. Nanjing: Nanjing University of Aeronautics and Astronautics, 2012.
[23] DURAND T S, WASICKO R J. An analysis of carrier landing: AIAA-65-791[R]. [S.1.]: AIAA, 1965.
[24] MAO Guoyong, XIE Jiang, ZHANG Wu. Numerical simulation and parallel computation of airplane using Cart3D[J]. Computer Engineering and Applications, 2008, 44(27): 207-208, 215. (in Chinese)
[25] JAMESON A, BAKER T, WEATHERILL N. Calculation of inviscid transonic flow over a complete air-craft[C]//Proceedings of the 24th Aerospace Scienc-es Meeting. Reno, USA: AIAA, 1986.
[26] YAN Zhen. Design and analysis of the leg buffer for vertical take-off and landing reusable launch vehicle [D]. Harbin: Harbin Institute of Technology, 2019.

Acknowledgements This research was supported by the National Natural Science Foundation of China (No. 12502042) , the Postdoctoral Fellowship Program of China Postdoctoral Science Foundation (No. GZC20252752) , and Jiangsu Funding Program for Excellent Postdoctoral Talent.

## Authors

The first author Mr. YANG Shaofei received the B.S. degree in aircraft propulsion engineering from Civil Aviation University of China, Tianjin, in 2021. He is currently pursuing the Ph. D. degree in Nanjing University of Aeronautics and Astronautics. His research interests include vertical take-off and vertical landing, landing mechanism of reusable launch vehicle, buffer material.

The corresponding author Prof. ZHANG Ming received the Ph.D. degree in aircraft design from Nanjing University of Aeronautics and Astronautics, China, in 2009. In June 2009, he joined the Key Laboratory of Fundamental Science for National Defense-Advanced Design Technology of Flight Vehicle, College of Aerospace Engineering, Nanjing, China. His research interests include aircraft design, dynamics and landing gear system.

Author contributions Mr. YANG Shaofei designed the study, analyzed the study and wrote the manuscript. Prof. ZHANG Ming implemented the model and revised the manuscript. Mr. RUAN Shuang contributed to the discussion and background of the study. Mr. LEI Bo analyzed the result. All authors commented on the manuscript draft and approved the submission.

Competing interests The authors declare no competing interests.

# 考虑机构柔性的可重复使用运载器海上着陆动力学分析 

## 杨少斐 ${ }^{1}$ ，张 明 ${ }^{1,2}$ ，阮 爽 ${ }^{3}$ ，雷 波 ${ }^{1}$

（1．南京航空航天大学航空航天结构力学及控制全国重点实验室，南京210016，中国；2．南京航空航天大学飞行器先进设计技术国防重点学科实验室，南京210016，中国；3．湖北航天技术研究院总体设计所，武汉430040，中国）

摘要：运载器海上垂直着陆回收可以进一步减少商业航天的发射成本，因此对可重复使用运载器海上着陆问题进行了研究。首先建立了考虑着陆机构柔性化的运载器着陆动力学模型，并进行了多种工况下的运载器落震试验。通过对比运载器落震试验，动力学模型仿真与试验结果具有一致性，且考虑着陆机构柔性化的运载器着陆动力学模型相比刚体动力学模型可以更有效地模拟运载器垂直着陆过程，对可重复使用运载器着陆机构的设计更具有指导意义。在运载器着陆动力学模型基础上，添加了基于功率谱的甲板运动模型和运载器风扰模型，进行了运载器海上垂直着陆动力学仿真。仿真结果表明，海上着陆会使运载器加速度响应峰值、主支柱载荷与缓冲器压缩行程变大，且运载器的着陆稳定性有明显下降。
关键词：可重复使用运载器；着陆动力学；落震试验；刚柔耦合模型；海上着陆
研究亮点：
1．设计了一种四腿外翻式运载火箭着陆机构，建立了计及机构柔性效应的着陆动力学模型。
2．开展了5．2t级运载器多工况着陆试验，验证了柔性模型的准确性；通过与刚性模型对比，揭示了机构柔性对着陆过程的影响规律。
3．构建了运载火箭海上着陆的理论分析方法，研究了甲板运动对着陆性能的影响，验证了所设计着陆机构在5级海况下的着陆回收能力。


[^0]:    *Corresponding author,E-mail address:zhm6196@nuaa.edu.cn.
    How to cite this article: YANG Shaofei, ZHANG Ming, RUAN Shuang, et al. Analysis of sea-based landing dynamics of reusable landing vehicle considering mechanism flexibility[J]. Transactions of Nanjing University of Aeronautics and Astronautics, 2026,43(2):238-250.
    http://dx.doi.org/10.16356/j.1005-1120.2026.02.006

