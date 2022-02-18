# IoTvizium: Interactive Web-based Visualization for IoT Ontology Concept Clustering

## Overview
This toolchain provides a user-friendly interactive web application visualization tool for 
exploring IoT ontology concept clustering results.
IoTvizium encodes the visualization with three aspects (concept color, concept size, and semantic distance) and incorporates three visualization methods (wordclouds, force directed graph with bounding circle and force directed graph with bounding box).

## Requirements
- Python 3.9.0
- Numpy
- Sklearn

## Usage
If you just want to test the application:
```console
$ git clone https://github.com/DaOnlyOwner/MethodVisualization.git
```
- Navigate into box_collision or circle_collision and open visualize.html. It works right out of the box with a sample input.

If you also want to try to generate input, this should be done with the toolchain. 
However if you want to do generate input yourself, look into example_input. 2analysis_classes.txt contains among other things the frequency. 3words_with_vectors.pkl contains the words with their vector representation and 4clusters-50.yml lists the different clusters.   


## References
If you want to use or extend our toolchain, please consider citing the related publications:  

[1] Noura, Mahda; Gyrard, Amelie; Heil, Sebastian; Gaedke, Martin: Automatic Knowledge Extraction to build Semantic Web of Things Applications. IEEE Internet of Things Journal, 2019.

[2] Noura, Mahda; Gyrard, Amelie; Heil, Sebastian; Gaedke, Martin: Concept Extraction from Web of Things Knowledge Bases. Proceedings of 17th International Conference WWW/Internet (ICWI2018), pp. 11-18, 2018.

[3] Noura, Mahda; Gyrard, Amelie; Klotz, Benjamin; Troncy, Raphael; Datta, Soumya; Gaedke, Martin: How to understand better "smart vehicle"? Knowledge Extraction for the Automotive Sector Using Web of Things. Semantic IoT: Theory and Applications - Interoperability, Provenance and Beyond, pp. 303-321, 2021.

