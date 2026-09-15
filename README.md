# Python CPU profiling demo

A deliberately CPU-heavy Python process for demonstrating how profiling
reveals which parts of an application consume the most CPU. One process
continuously performs three named operations:

- `sort_values`: sorts 200,000 integers.
- `find_duplicates_slow`: finds duplicates with quadratic `O(n^2)` loops.
- `build_histogram`: groups values into histogram buckets.

The same image also includes the optimized `find_duplicates_fast` implementation
using linear `O(n)` set lookups. Kubernetes runs a single pod with the slow
version enabled initially. There is no HTTP server or external load generator,
so profiles contain only the workload and Python runtime frames.

## Run locally

```bash
docker build -t python-cpu-profiling-demo .
docker run --rm python-cpu-profiling-demo
```

The process reports the duration of every operation once per second.

## Deploy to Kubernetes

The public image is published as:

```text
ghcr.io/mqasimsarfraz/python-cpu-profiling-demo:latest
```

Deploy the continuous workload:

```bash
kubectl apply -k kubernetes
kubectl rollout status deployment/cpu-profile-demo -n cpu-profile-demo
kubectl get pods -n cpu-profile-demo
```

Target the application container with your CPU profiler using the label:

```text
app.kubernetes.io/name=cpu-profile-demo
```

### Inspektor Gadget continuous profile

The `gadget/profile-cpu.yaml` ConfigMap creates a `profile_cpu` gadget instance.
It targets the application pod, collects Python user-space stacks, and exports
profiles through the `pyroscope-exporter` OpenTelemetry exporter.

After installing Inspektor Gadget and configuring that exporter, apply the
profile:

```bash
kubectl apply -f gadget/profile-cpu.yaml
kubectl get configmap cpu-profile-demo-profiles -n gadget
```

The first profile should make the relative cost of each operation clear:

- `find_duplicates_slow` should be the widest and hottest function.
- `sort_values` should consume a smaller but visible portion.
- `build_histogram` should consume the least CPU.

After capturing the slow profile, enable the optimized duplicate function:

```bash
kubectl set env deployment/cpu-profile-demo -n cpu-profile-demo \
  DUPLICATE_IMPLEMENTATION=fast
kubectl rollout status deployment/cpu-profile-demo -n cpu-profile-demo
```

Capture a second profile and use Pyroscope's comparison view. The duplicate
function should shrink substantially, making sorting or histogram construction
the next visible optimization candidate. Restore the initial version with:

```bash
kubectl set env deployment/cpu-profile-demo -n cpu-profile-demo \
  DUPLICATE_IMPLEMENTATION=slow
```

Remove the demo:

```bash
kubectl delete -f gadget/profile-cpu.yaml
kubectl delete -k kubernetes
```

## Run tests

```bash
python -m unittest discover -s tests
```
