# Problem expression

## Shared meaning

The primary `budget_value_8` case evaluates eight public supplier candidates against a frozen business predicate composed from two numeric comparisons. The platforms receive the same candidate order, fields, and predicate meaning.

The comparison deliberately begins above the circuit level:

```text
public rows + public decision predicate
                     |
          +----------+----------+
          |                     |
 QDSV public specification   Qrisp native program
          |                     |
 Bridge materialization      technical-user construction
          |                     |
       artifact               artifact
          +----------+----------+
                     |
           common semantic replay
                     |
           common normalization
```

## QDSV expression path

The user supplies rows and a structured predicate through the public SDK. Bridge selects and materializes a supported logical realization, returns evidence and digests, and may deliver canonical and optimized logical artifacts.

The notebook contains a local specification-forming layer. It does not contain the private QDSV scoring formula and does not implement Bridge's materialization logic.

## Qrisp expression path

The technical user supplies native Qrisp construction code for field allocation, candidate preparation, reversible loading, comparisons, Boolean composition, temporary values, cleanup, compilation, and export. Qrisp then compiles the supplied native construction.

This is not characterized as a defect. It is the evaluated public programming model and is part of the abstraction boundary the benchmark intends to document.

## Ground-truth separation

Expected candidate outcomes are frozen independently and are used only after artifact construction for neutral replay. They are not used to select a circuit, construct the predicate, optimize either artifact, or repair an observed result.
