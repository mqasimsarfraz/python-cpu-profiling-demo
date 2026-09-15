# Python CPU profiling demo

A deliberately CPU-heavy Python process for demonstrating how profiling
reveals an algorithmic performance problem. It continuously finds duplicate
values using either:

- `slow`: nested loops with quadratic time complexity, `O(n^2)`
- `fast`: set lookups with linear time complexity, `O(n)`

Both implementations return the same result. Kubernetes runs one `slow` pod
and one `fast` pod under the same CPU and memory limits. Each pod performs one
identical unit of work every 500 milliseconds. There is no HTTP
server or external load generator, so profiles contain only the workload and
Python runtime frames.

## Run locally

```bash
docker build -t python-cpu-profiling-demo .
docker run --rm -e IMPLEMENTATION=slow python-cpu-profiling-demo
docker run --rm -e IMPLEMENTATION=fast python-cpu-profiling-demo
```

Each process reports completed iterations per second every five seconds.

## Deploy to Kubernetes

The public image is published as:

```text
ghcr.io/mqasimsarfraz/python-cpu-profiling-demo:latest
```

Deploy both continuous workloads:

```bash
kubectl apply -k kubernetes
kubectl rollout status deployment/cpu-profile-demo-slow -n cpu-profile-demo
kubectl rollout status deployment/cpu-profile-demo-fast -n cpu-profile-demo
kubectl get pods -n cpu-profile-demo
```

Target the application container with your CPU profiler using the label:

```text
app.kubernetes.io/name=cpu-profile-demo
```

### Inspektor Gadget continuous profile

The `gadget/profile-cpu.yaml` ConfigMap creates a `profile_cpu` gadget instance.
It targets both application pods, collects Python user-space stacks, and
exports profiles through the `pyroscope-exporter` OpenTelemetry exporter.

After installing Inspektor Gadget and configuring that exporter, apply the
profile:

```bash
kubectl apply -f gadget/profile-cpu.yaml
kubectl get configmap cpu-profile-demo-profiles -n gadget
```

In Pyroscope, filter or compare profiles using the `k8s.podName` profile
attribute:

- `cpu-profile-demo-slow-*` spends nearly all CPU in
  `find_duplicates_slow`.
- `cpu-profile-demo-fast-*` performs the same work in `find_duplicates_fast`
  with almost no on-CPU time and sleeps until the next scheduled iteration.

Use a comparison/diff view over the same time range. The distinct pod names
keep both profiles available simultaneously and avoid changing deployments
between captures.

Remove the demo:

```bash
kubectl delete -f gadget/profile-cpu.yaml
kubectl delete -k kubernetes
```

## Run tests

```bash
python -m unittest discover -s tests
```
