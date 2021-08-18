The project is a python (PyQt) application for analyzing APT data. It has the following functionalities.
1.	The application helps map the peaks of Atom Probe Tomography data with additional controls over binning and peak resizing. 
2.	One can export the binned file and do additional analysis in other software that supports the HDF format.
3.	It can find out the dimensions of monolayers within the data using a graphical visualization tool that can do binning along any direction. The ions in the monolayers can be extracted as a doc file, with or without decomposition.
4.	Similarly, it can identify an abstract 3D ion cloud within the data and apply DBSCAN to remove noises. The 'convex hull' algorithm then prepares the contour, extracting the ions present in it.
5.	It can find the GM-SRO parameter of the data among two species (or collection) of ions. The methodology is based on the literature cited in the reference. The output is a graph across shells surrounding the atoms.
6.	It can extract and plot a composition part using a mix of critical radius and nearest neighbor list.

The project is still under development. Anybody wishing to contribute can contact me directly. In the future, we will be primarily looking into optimizing the thread-safety, voxelizing data, and a better visualizing tool rather than matplotlib (which is very slow for such large data). I developed the project under Prof Tong Li with support from Ruhr University Bochum. 

References:
1.	Anna V. Ceguerra , Michael P. Moody , Leigh T. Stephenson , Ross K.W. Marceau & Simon P. Ringer (2010) A three-dimensional Markov field approach for the analysis of atomic clustering in atom probe data, Philosophical Magazine, 90:12, 1657-1683, DOI: 10.1080/14786430903441475
2.	Leigh T. Stephenson, Michael P. Moody, Peter V. Liddicoat, and Simon P. Ringer (2007) New Techniques for the Analysis of Fine-Scaled Clustering Phenomena within Atom Probe Tomography (APT) Data, Microsc. Microanal. 13, 448–463, 2007, DOI: 10.1017/S1431927607070900 
3.	Anna V. Ceguerra, Michael P. Moody, Rebecca C. Powles, Timothy C. Petersen, Ross K. W. Marceau and Simon P. Ringer (2012) Short-range order in multicomponent materials, Acta Cryst. (2012). A68, 547–560
4.	Leigh T. Stephenson, Anna V. Ceguerra, Tong Li, Tanaporn Rojhirunsakool, Soumya Nag, Rajarshi Banerjee, Julie M. Cairney, Simon P. Ringer (2014), Point-by-point compositional analysis for atom probe tomography, MethodsX 1 (2014) 12–18
