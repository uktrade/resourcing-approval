from main.services.resourcing_request import create_full_test_resourcing_request


# TODO: Split this test up into separate tests.
def test_change_log(db, django_capture_on_commit_callbacks):
    rr = create_full_test_resourcing_request(
        job_title="Python Developer",
        project_name="JML",
        inside_ir35=True,
    )

    with django_capture_on_commit_callbacks(execute=True):
        rr.job_title = "QA"
        rr.project_name = "Testing"
        rr.save()

        rr.job_title = "QA Engineer"
        rr.profession_id = 2  # Data Science
        rr.save()

        rr.financial_information.min_day_rate = 600
        rr.financial_information.max_day_rate = 700
        rr.financial_information.save()

        rr.interim_request.equivalent_civil_servant_grade = (
            rr.interim_request.CivilServantGrade.G6
        )
        rr.interim_request.save()

    changes = rr.change_log.get_changes()

    assert changes == {
        "job_title": "QA",
        "project_name": "JML",
        "profession": "Development",
    }

    changes = rr.financial_information.change_log.get_changes()

    assert changes == {"min_day_rate": "£650", "max_day_rate": "£750"}

    changes = rr.interim_request.change_log.get_changes()

    assert changes == {"equivalent_civil_servant_grade": "G7"}
