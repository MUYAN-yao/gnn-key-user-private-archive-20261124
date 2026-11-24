# Verified design basis

The figure summarizes the wiki-Vote default-tolerance PageRank-4k diagnostic at `W=1280`.

- The frozen graph stores arcs from voters to users voted upon; simulated propagation follows that stored direction.
- Default PageRank-4k has 20 candidates with mean in-degree 249.75 and mean out-degree 56.2.
- Degree-4k has mean in-degree 70.3 and mean out-degree 489.25.
- PageRank-4k covers 0 of 5 full-reference seeds on each of the five paths.
- Its independently evaluated mean incremental-spread difference is -40.69334 nodes, equivalent to a 73.0107% incremental loss.

These facts are consistent with a direction-and-coverage pathway. They do not identify direction as the unique cause, and the experiment did not reverse graph orientation.
