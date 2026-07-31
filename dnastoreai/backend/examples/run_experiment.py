"""Example research experiment script."""

from dnastoreai.experiments.runner import Experiment


def main() -> None:
    experiment = Experiment.from_dataset(
        dataset_type="mixed",
        count=5,
        encoding="gc_balanced",
        ecc="reed_solomon",
        sequencing="illumina",
        name="benchmark-gc-balanced-rs-illumina",
    )
    result = experiment.run()
    print(f"Experiment {result.experiment_id} completed")
    print(f"Summary: {result.summary}")


if __name__ == "__main__":
    main()
