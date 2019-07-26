import dramatiq
from account.models import User
from problem.models import Problem
from submission.models import JudgeStatus, Submission
from judge.dispatcher import JudgeDispatcher
from contest.models import Contest, ContestRuleType, OIContestRank, ACMContestRank
from utils.api import logging
from utils.shortcuts import DRAMATIQ_WORKER_ARGS

logger = logging.getLogger("")


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def contest_rejudge_task(cid, pid):
    try:
        problem = Problem.objects.get(id=pid, contest_id=cid) if cid \
            else Problem.objects.get(id=pid, contest_id__isnull=True)
    except Problem.DoesNotExist as e:
        logger.exception(e)
        return
    try:
        submissions = Submission.objects.filter(problem_id=pid)
    except Submission.DoesNotExist:
        return
    user_exist = []
    for submission in submissions:
        if User.objects.get(id=submission.user_id):
            user_exist.append(submission.user_id)
    submissions = submissions.filter(user_id__in=user_exist).order_by("create_time")
    ce_cnt = dict()
    for submission in submissions:
        if submission.result == JudgeStatus.COMPILE_ERROR:
            now_cnt = ce_cnt.get(submission.user_id, 0)
            ce_cnt[submission.user_id] = now_cnt + 1
    problem.statistic_info = {}
    problem.accepted_number = 0
    problem.submission_number = 0
    problem.save()
    if cid:
        contest = Contest.objects.get(id=cid)
        if contest.rule_type == ContestRuleType.ACM:
            ranks = ACMContestRank.objects.filter(contest_id=cid)
            for rank in ranks:
                if rank.submission_info:
                    problem_info = rank.submission_info.get(str(pid))
                    if problem_info:
                        user = User.objects.get(id=rank.user_id)
                        user.userprofile.acm_problems_status["contest_problems"].pop(str(pid))
                        user.userprofile.save()
                        rank.submission_number -= problem_info["error_number"]
                        if rank.user_id in ce_cnt:
                            rank.submission_number -= ce_cnt[rank.user_id]
                            ce_cnt.pop(rank.user_id)
                        if problem_info["is_ac"]:
                            rank.submission_number -= 1
                            rank.accepted_number -= 1
                            rank.total_time = rank.total_time - problem_info["error_number"] * 20 * 60
                            rank.total_time = rank.total_time - int(problem_info["ac_time"])
                        rank.submission_info.pop(str(pid))
                        rank.save()
        else:
            ranks = OIContestRank.objects.filter(contest_id=cid)
            # todo: clear the rank for single problem
            pass
    for submission in submissions:
        submission.info = {}
        submission.statistic_info = {}
        submission.result = JudgeStatus.PENDING
        submission.save()
    for submission in submissions:
        JudgeDispatcher(submission.id, problem.id).judge()
