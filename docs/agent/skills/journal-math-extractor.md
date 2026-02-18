# Journal Math Extractor

**Category:** Paper Publishing (Sub-skill)
**Invoked By:** Journal Master (Lutapi)

---

## Purpose
Scans code for mathematical logic, algorithms, and statistical models, converting them into formal LaTeX notation for research papers.

---

## Functionality
1. **Detection:** Locates functions involving calculations, statistical models, or logic gates.
2. **extraction:** Ignores trivial code (loops, basic assignments) to focus on core logic.
3. **Formalization:** Converts Python logic into LaTeX equations.
4. **Output:** Generates `mathematics.md` in the module's paper directory.

## Output Format
```latex
$$
\text{Algorithm}(x) = \sum_{i=1}^{n} w_i \cdot x_i + b
$$
```

## Constraints
- Focuses on core detection algorithms relevant to M.Tech projects.
- Invoked automatically by `Lutapi` during module analysis.
