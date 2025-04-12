# -*- coding: utf-8 -*-

from rh.apd.models import PeriodicEvaluationPerformance, Configuration

import unittest


class PeriodicEvaluationPerformanceTestCase(unittest.TestCase):

    # @unittest.skip("skipping test")
    def test(self):
        cf = Configuration.objects.first()
        print("deadline_begin %s" % cf.deadline_begin)
        print("deadline_blocking %s" % cf.deadline_blocking)
        print("deadline_appeal %s" % cf.deadline_appeal)
        print("deadline_judge_resource %s" % cf.deadline_judge_resource)
        print("deadline_reconsideration %s" % cf.deadline_reconsideration)
        print("deadline_rectify_evaluation %s" % cf.deadline_rectify_evaluation)
        print(
            "deadline_rectification_commission %s"
            % cf.deadline_rectification_commission
        )
        print(
            "deadline_science_resul_evaluation %s"
            % cf.deadline_science_resul_evaluation
        )
        for pep in (
            PeriodicEvaluationPerformance.objects.filter(status=1)
            .filter(
                # employee__servidor__matricula__in=[124014, 73107]
                # employee__servidor__matricula__in=[91608, 1489]
                # employee__servidor__matricula__in=[100010, 35201]
            )
            .order_by("end_date")
        ):
            pep.deadline

    @unittest.skip("skipping test_days_to_bloke")
    def test_days_to_bloke(self):
        cf = Configuration.objects.first()
        print("deadline_begin %s" % cf.deadline_begin)
        print("deadline_blocking %s" % cf.deadline_blocking)
        print("deadline_appeal %s" % cf.deadline_appeal)
        print("deadline_judge_resource %s" % cf.deadline_judge_resource)
        print("deadline_reconsideration %s" % cf.deadline_reconsideration)
        print("deadline_rectify_evaluation %s" % cf.deadline_rectify_evaluation)
        print(
            "deadline_rectification_commission %s"
            % cf.deadline_rectification_commission
        )
        print(
            "deadline_science_resul_evaluation %s"
            % cf.deadline_science_resul_evaluation
        )
        for pep in (
            PeriodicEvaluationPerformance.objects.filter(status=1)
            .filter(
                # employee__servidor__matricula__in=[124014, 73107]
            )
            .order_by("end_date")
        ):
            if pep.days_to_bloke_old != pep.days_to_bloke:
                # if pep.is_bloke_old != pep.is_bloke:
                print(pep, pep.days_to_bloke_old, pep.days_to_bloke)
