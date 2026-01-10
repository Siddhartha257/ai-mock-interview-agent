from services.resume_parser import get_user_profile
from services.jd_parser import get_job_profile
from services.resume_score import get_resume_score

user_profile = get_user_profile("resources/siddu's resume.pdf").model_dump()
job_profile = get_job_profile("resources/jd.txt").model_dump()

print(user_profile)
print(job_profile)

score = get_resume_score(user_profile , job_profile['summary'] , user_profile['skills'] , job_profile['skills'])
print(score)