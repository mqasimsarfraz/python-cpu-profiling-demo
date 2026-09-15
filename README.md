# Python CPU profiling demo

A deliberately CPU-heavy FastAPI workload for demonstrating how profiling
reveals an algorithmic performance problem. The application finds duplicate
values using either:

- `slow`: nested loops with quadratic time complexity, `O(n^2)`
- `optimized`: set lookups with linear time complexity, `O(n)`

Both implementations return the same result. The Kubernetes deployment starts
in `slow` mode and includes two load-generator replicas.

## Run locally

```bash
docker build -t python-cpu-profiling-demo .
docker run --rm -p 8000:8000 python-cpu-profiling-demo
curl 'http://localhost:8000/analyze?size=5000'
curl 'http://localhost:8000/analyze?size=5000&implementation=optimized'
```

The response includes the implementation and elapsed processing time.

## Deploy to Kubernetes

The public image is published as:

```text
ghcr.io/mqasimsarfraz/python-cpu-profiling-demo:latest
```

Deploy the application, Service, and continuous load generator:

```bash
kubectl apply -k kubernetes
kubectl rollout status deployment/cpu-profile-demo -n cpu-profile-demo
kubectl get pods -n cpu-profile-demo
```

Target the application container with your CPU profiler using the label:

```text
app.kubernetes.io/name=cpu-profile-demo
```

The slow profile should show most user-space CPU samples in
`find_duplicates_slow`.

Switch to the optimized implementation without changing the load:

```bash
kubectl set env deployment/cpu-profile-demo \
  -n cpu-profile-demo IMPLEMENTATION=optimized
kubectl rollout status deployment/cpu-profile-demo -n cpu-profile-demo
```

Capture another profile and compare CPU consumption, request latency, and the
stack samples. Restore the slow implementation with:

```bash
kubectl set env deployment/cpu-profile-demo \
  -n cpu-profile-demo IMPLEMENTATION=slow
```

Remove the demo:

```bash
kubectl delete -k kubernetes
```

## Run tests

```bash
python -m pip install --requirement requirements.txt
python -m unittest discover -s tests
```
