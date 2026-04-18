# Reference for env.toml file

## Slurm

Use this sample when jobs are launched through a Slurm login node and the cluster provides a shared filesystem.

Required fields:
- `container_image`
- `host`
- `user`
- `account`
- `partition`
- `remote_job_dir`

Common failures:
- wrong `partition`
- remote job directory not writable
- container image unavailable on the cluster

## Run:AI

Use this sample when the platform team exposes Kubernetes-backed GPU jobs through Run:AI.

Required fields:
- `container_image`
- `cluster`
- `project`

Optional fields:
- `node_pool`

Notes:
- include PVC mount definitions if data is not baked into the image

Common failures:
- wrong project name
- PVC not mounted at the expected path
- node pool incompatible with requested GPU count

## Lepton

Use this sample when jobs run through DGX Cloud via Lepton and you already know the target node group and mounted storage path.

Required fields:
- `container_image` or `container`
- `node_group`

Optional fields:
- `resource_shape`

Notes:
- include at least one mount for model or data access

Common failures:
- wrong `node_group`
- missing mount for data
- container image tag mismatch
