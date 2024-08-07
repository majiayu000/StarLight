import sys
from preprocess import Channel
from workflow.cf_flow import run as user_cf
from workflow.lfm_workflow import run as lfm
from workflow.prank_workflow import run as prank


def manage():
    arg = sys.argv[1]
    if arg == "preprocess":
        Channel().process()
    elif arg == "user_cf":
        user_cf()
    elif arg == "lfm":
        lfm()
    elif arg == "prank":
        prank()
    else:
        print("Args must in ['preprocess', 'user_cf', 'lfm', 'prank']")

    sys.exit()


if __name__ == "__main__":
    manage()
