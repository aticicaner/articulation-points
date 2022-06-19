## Introduction

An alternate way to study connectivity in a graph is to see if there are articulation points on it. If there are a low number of articulation points, the graph can be said to be strongly connected. An articulation point is a vertex, which, if removed (along with the edges that connect it), will disconnect the graph.

If there are no alternate paths between two clusters in a graph apart from a specific vertex, then that vertex is an articulation point, if when we remove it the two clusters aren’t connected anymore.

This project discusses ways to detect articulation points in a graph, which is homomorphically encrypted using Microsoft’s Eva platform.

Microsoft SEAL library is used for encryptions and validation under the hood, and Eva Language is to be used to implement the algorithm. There are several operations we can use in Eva to achieve our goal and those are:

Negate
Add
Subtract
Multiply
Rotate left
Rotate right
Relinearize*
Mod switch*
Rescale*

Last three of which cannot be used on inputs(*).

The challenge comes when traditional tools like comparison or conditional operations in higher level languages are no longer available. It can be very difficult or impossible to implement some of the algorithms in their core form, there needs to be a time-complexity trade-off (not including the time for encryption & decryption) to account for the time lost circumventing these operations.

This paper is about explaining and showing my attempt on implementing articulation point detection using Eva, the thought processes and progress on the topic.

## Background and Related Work

A Graph is a non-linear data structure consisting of vertices and edges. Vertices are the meaningful data points with information and they are connected via edges. 


The focus of this project is to identify articulation points on the graphs using Eva. If removed, the articulation points leave the graph disconnected, for example again in Figure 1, it is easy to identify vertex 4 as the articulation point because it is the only one connecting vertex 6 to the rest of the graph. If we remove any other node, the connectivity doesn’t change for the remaining vertices.

Here are some alternative methods to identify an articulation point on a graph, each having different levels of success, and performance benefits:

Identify clusters or nodes that have a single edge going to the rest of the graph, the vertex on the receiving end of that single edge will be an articulation point. For the identification, it is possible to go recursively through the graph and keep a list of vertices and the edges that fall outside of the vertices in our list. If the number of nodes outside the cluster is 1, that node is connected to an articulation point.
A brute force approach would be, for each vertex a, remove a from the graph. Check the connectivity using BFS or DFS. If the number of vertices are different in BFS and DFS outputs, we can say that vertex a was an articulation point.

The two methods discussed above will be about the same time complexity, both lead to the naive approach from different angles (O(V * (V + E))).  There is a better option for us which is Tarjan’s approach:

There is a vertex v, in a graph g, that can be reached by vertex u, through some intermediate nodes using a DFS traversal. If v can also be reached by a, an ancestor of u without passing through u, then u is not an articulation point. O(V+E) time complexity due to efficient space complexity trade-offs.
## Main Contributions
Before we can dive into the application of our algorithm, firstly it is essential to analyze and understand what operations are available in Eva platform. Previously we mentioned the operations available to us are:

Negate: negates each element of the argument
Add: adds arguments, element-wise
Subtract: subtracts right argument from the left one (element-wise)
Multiply: multiply arguments element-wise (and multiply scales)
Rotate left: rotate elements to the left by given number of indices
Rotate right: rotate elements to the right by given number of indices
Relinearize: apply relinearization
Mod Switch: switch to the next modulus in the modulus chain.
Rescale: rescale the ciphertext (and divide scale) with the scalar

Eva platform’s main motivation is the use of fully-homomorphic encryption, meaning the data being processed in the backend without ever needing to reveal the information that is encrypted. However, due to the nature of this algorithm, there needs to be a mechanism to check for equalities and nodes connectivity information.

To check for articulation points we need to do a DFS traversal while omitting each node one at a time. Before we try to implement the articulation point detection algorithm, it is wise to first start with a DFS implementation. The inability to acquire connectivity information of a node without decryption is a big challenge. I wasn’t able to figure out a way to implement DFS without checking for edges in the unencrypted zone (client side). So there needs to be a back and forth between the client and the server for each node, and this will result in the topography being revealed during the operation.

Another big challenge is to compare outputs of the traversals, so that we can look for differences and classify articulation points. Eva doesn’t support direct comparisons so this is also a chore that needs to be handled in the unencrypted client side.

With an architecture like this, we would be off loading simple comparison operations and connectivity information queries to the front-end with each iteration and this is not a desirable approach. This will yield a lot of network connectivity information being transferred over the network and against the main motivation of this project.

## Results and Discussion
### Methodology
For the project there were no finalized methods to complete all required operations under homomorphic encryption. Unfortunately, the task at hand is too difficult or impossible with the toolkit. The inability to do equality checks for the outputs of DFS under encryption or getting next vertex information during the traversal is a challenge. The backtracking traversal can be implemented by keeping a stack inside encryption but to get the next node, implementation had to rely on querying the unencrypted area.

For the detection of articulation points, each node must be individually removed from the graph and the remainder of the graph has to be put through DFS, then the outputs have to be compared. Unfortunately, even if DFS was implemented the output of the DFSs have to be compared outside of the encryption.

For the purposes of seeing if this version is viable for Eva implementation in any real capacity, let's imagine an average latency of network request-response time of 300 ms for the encrypted and unencrypted areas of the system and a graph of 200 nodes. For DFS best case let’s say this graph is connected like a chain, this is also the worst case for articulation points since all the nodes in the graph are now articulation points. So, for this case, this means N^2 queries which means, just for network latency we have 20 minutes of back and forth time. This is without any encryption or decryption or even execution time.

### Results
Benchmark results shown below for a single DFS traversal using the methodology earlier described. This is because doing an articulation point detection increases times multiplied by number of nodes, so the relationships would seem polynomial if the outer iteration were to be included in the benchmarking. The results plotted are average values for 200 iterations over a connected watts-strogatz graph with different node counts. 

## Conclusion
For the purposes of implementing an articulation point discovery method under homomorphic encryption, this project was not successful. All the proposed solutions required many iterations over the same data structure that corruption of the data under encryption became a big problem. Not only a traversal of the graph but also doing that for N times meant this project by its nature requires many “decryption and checking outside encryption iterations” over the same graph.


For the goals of Eva, the idea is to encrypt the data on the front-end client and operate on the data and morph it on the back-end server without decrypting or messing up the encryption, so when the data is sent back to the client, it can decrypt and read the confidential data.

For this project there weren’t any meaningful ways to apply this. Best attempt was to iterate and ask for the next node and do the DFS comparisons on the front-end. This resulted in very large execution times. However, it was possible to do meaningful DFS only with the condition of going to an unencrypted client on every neighbor hop and backtracking.
