from core.token_detector import TokenDetector


def test():
    detector = TokenDetector()

    sample_logs = [
        "Program log: Instruction: InitializeMint",
        "Program log: Instruction: AddLiquidity",
    ]

    event = detector.detect_event(sample_logs)

    print("Detected Event:", event)


if __name__ == "__main__":
    test()