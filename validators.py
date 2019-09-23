from datetime import timedelta, datetime


WEEK = 7
TWO_WEEKS = 14
TWO_YEARS = 365*2


def check_pp_55(ticket, category):
    if category.pp:
        return True
    else:
        return False


def check_tst(ticket, category):
    if category.tst:
        return True
    else:
        return False


def check_day_period(ticket, day_period):
    now = datetime.now()
    sale_date = ticket.sale_date + timedelta(day_period + 1)

    if sale_date < now:
        return True
    else:
        return False


def check_one_week(ticket, category):
    answer = check_day_period(ticket, WEEK)
    return answer


def check_two_week(ticket, category):
    answer = check_day_period(ticket, TWO_WEEKS)
    return answer


def check_two_years(ticket, category):
    answer = check_day_period(ticket, TWO_YEARS)
    return answer


VALIDATORS = {
    'check_pp_55': check_pp_55,
    'check_tst': check_tst,
    'check_one_week': check_one_week,
    'check_two_week': check_two_week,
    'check_two_years': check_two_years,
}
