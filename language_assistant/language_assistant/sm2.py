from datetime import datetime, timedelta


def sm2(ease, reps, interval, quality):
    if quality >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ease)

        ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease = max(1.3, ease)  # Ease should not go below 1.3
        reps += 1
    else:
        reps = 0
        interval = 1  # review again soon

    next_review = (datetime.now() + timedelta(days=interval)).date()
    return ease, reps, interval, next_review
