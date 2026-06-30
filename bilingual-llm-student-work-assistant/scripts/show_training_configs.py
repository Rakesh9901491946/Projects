from bilingual_productivity_llm.train.config import (
    load_eval_config,
    load_pretrain_config,
    load_task_tune_config,
    summarize_training_stack,
)


def main() -> None:
    pretrain = load_pretrain_config("configs/pretrain.json")
    task_tune = load_task_tune_config("configs/task_tune.json")
    evaluation = load_eval_config("configs/eval.json")
    summary = summarize_training_stack(pretrain, task_tune)
    for key, value in summary.items():
        print(f"{key}\t{value}")
    print(f"eval_metrics\t{evaluation.metrics}")
    print(f"eval_thresholds\t{evaluation.thresholds}")


if __name__ == "__main__":
    main()
