from awesomedl.logic.output import ytdl_output_progress_parser


def test_ytdl_output_progress_parser():
    out = " [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09 "
    model = ytdl_output_progress_parser(out)
    if model:
        assert model.speed == "312.43KiB/s"
        assert model.total_size == "426.81MiB"
        assert model.percent_complete == "0.7%"
        assert model.eta == "23:09"
    else:
        assert False


def test_invalid_ytdl_output_progress_parser():
    out = "[download]   10.0% This is invalid output"
    model = ytdl_output_progress_parser(out)
    if model:
        assert False
    else:
        assert True

